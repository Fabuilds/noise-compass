"""
dictionary.py — The energy landscape. Entries are attractors, not records.

Second pass changes:
- nearest_attractor cached per call to eliminate redundant O(n) scans
- active_god_tokens separated from record_activation (no mutation on read)
- maybe_crystallize uses content hash for stable IDs (no duplicate entries)
- causal_degeneracy uses relative threshold consistent with GOD_TOKEN_SIGMA
"""

import os
import math
import hashlib
import numpy as np
import h5py
from typing import Dict, List, Optional, Tuple, Any

import sys
from pathlib import Path

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.tokens import GodToken, GapToken
from noise_compass.system.protocols import LAMBDA_DECAY, SYSTEM_CLOCK_TICK


class Dictionary:
    """
    Attractor structure of meaning space.

    Attractor topology (Part 18):
    - Deep + narrow:   precise dictionary entry
    - Deep + wide:     god-token (any pattern of that type)
    - Shallow + wide:  structured soup template (approximate prior)
    - Shallow + narrow: spurious attractor (high degeneracy, confabulation)

    Option B (Deferred Seeding):
    Pass an `embedder` callable (str -> np.ndarray) to generate god-token
    vectors from seed phrases at session startup, rather than loading them
    from H5 phase_vector datasets.  If omitted, falls back to
    InterferenceEngine.embed (Qwen3) for backward compatibility.
    """

    CRYSTALLIZATION_THRESHOLD = 32   # Adjusted for Session 16 (Qwen3 dense vectors)
    GOD_TOKEN_SIGMA           = 1.5  # std devs above mean for relative activation threshold
    SEEDS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              'config', 'god_token_seeds.json')

    def __init__(self, h5_manager=None, embedder=None, seeds_path=None):
        self.entries:       Dict[str, np.ndarray] = {}
        self.god_tokens:    Dict[str, GodToken]   = {}
        self.gap_tokens:    Dict[str, GapToken]   = {}
        self._entry_depth:  Dict[str, float]      = {}
        self._creation_t:   Dict[str, float]      = {}
        self._last_access:  Dict[str, float]      = {}
        self.system_time:   float                 = 0.0
        self.h5 = h5_manager
        self._embedder = embedder          # callable: str -> np.ndarray, or None
        self._seeds_path = seeds_path or self.SEEDS_PATH

    # ── Option B: Deferred Seeding ────────────────────────────────────────────

    def _default_embedder(self):
        """Returns InterferenceEngine.embed as the fallback embedder.
        Imported lazily to avoid circular imports."""
        try:
            from noise_compass.system.interference_engine import InterferenceEngine
            engine = InterferenceEngine(suppress_preload=True)
            return engine.embed
        except Exception as e:
            print(f"[DICTIONARY] Warning: could not load default embedder: {e}")
            return None

    def _load_god_token_seeds(self):
        """Embeds god-token seed phrases and populates self.god_tokens + self.entries.
        Called automatically from load_cache() when seed phrases are present in H5.
        Uses self._embedder if set, otherwise falls back to _default_embedder()."""
        # Resolve embedder
        embedder = self._embedder
        if embedder is None:
            embedder = self._default_embedder()
        if embedder is None:
            print("[DICTIONARY] No embedder available — god-token seeds skipped.")
            return

        # Load seed phrases: prefer H5 (runtime) over JSON (install-time)
        seeds = {}
        if self.h5:
            seeds = self.h5.get_god_token_seeds()   # H5 is source of truth post-setup
        if not seeds and os.path.exists(self._seeds_path):
            import json
            raw = json.load(open(self._seeds_path, encoding='utf-8'))
            seeds = raw.get('god_tokens', {})

        if not seeds:
            print("[DICTIONARY] No god-token seed phrases found (run: compass setup).")
            return

        print(f"[DICTIONARY] Embedding {len(seeds)} god-token seed phrases...")
        for name, phrase in seeds.items():
            if name in self.god_tokens:
                continue   # already loaded (e.g. from crystallized axioms)
            try:
                vec = embedder(phrase)
                if vec is None:
                    continue
                vec = np.array(vec)
                # InterferenceEngine.embed returns complex64; take the real axis.
                # The imaginary axis is the λ-operator layer's concern, not node storage.
                if np.iscomplexobj(vec):
                    vec = vec.real
                vec = vec.astype(np.float32)
                gt = GodToken(
                    id=name,
                    seed_terms=[phrase],
                    embedding=vec,
                    stability=0.5,
                    nature='CANONICAL'
                )
                # Read persisted scalar attrs from H5 if available
                if self.h5:
                    stab = self.h5.get_attr('language', f'god_tokens/{name}', 'stability')
                    if stab is not None:
                        gt.stability = float(stab)
                self.add_god_token(gt)
            except Exception as e:
                print(f"[DICTIONARY] Seed embedding failed for {name}: {e}")

        print(f"[DICTIONARY] Seeded {len(self.god_tokens)} god-tokens in-memory.")

    # ─────────────────────────────────────────────────────────────────────────

    # ── Entry management ──────────────────────────────────────────

    def add_entry(self, formula_id: str, embedding: np.ndarray,
                  depth: float = 1.0):
        norm = float(np.linalg.norm(embedding))
        if norm < 1e-10:
            return
        self.entries[formula_id]      = embedding / norm
        self._entry_depth[formula_id] = depth
        self._creation_t[formula_id]  = self.system_time
        self._last_access[formula_id] = self.system_time

    def add_god_token(self, gt: GodToken):
        """
        Add a god-token to the dictionary.
        Syncs with the entries store to ensure activation/query alignment.
        """
        if gt.embedding is not None:
            norm = float(np.linalg.norm(gt.embedding))
            if norm > 1e-10:
                gt.embedding = gt.embedding / norm
                # Sync to entries for nearest attractor query
                self.entries[gt.id] = gt.embedding
                self._entry_depth[gt.id] = 1.8 # God-Tokens have structural depth
                self._creation_t[gt.id]  = self.system_time
                self._last_access[gt.id] = self.system_time
        self.god_tokens[gt.id] = gt

    def add_gap_token(self, gap: GapToken):
        self.gap_tokens[gap.id] = gap

    def allocate_fleeting_token(self, description: str, embedding: np.ndarray, ttl: float = 5.0) -> str:
        """
        Phase 129: Volumetric Concept Scrutiny.
        Allocates a temporary, ephemeral token for a new concept identified in text.
        It doesn't crystallized into H5 unless reinforced.
        """
        token_id = f"TEMP_{hashlib.md5(description.encode()).hexdigest()[:8].upper()}"
        gt = GodToken(
            id=token_id,
            seed_terms=[description],
            embedding=embedding,
            nature="FLEETING",
            ttl=ttl,
            creation_time=self.system_time
        )
        self.add_god_token(gt)
        return token_id

    # ── Core query — single O(n) scan, result reused ──────────────

    def query(self, emb: np.ndarray, zoom: float = 1.0) -> Tuple[Optional[str], float, np.ndarray]:
        """
        Single scan over all entries.
        Returns (nearest_id, similarity, unit_embedding).
        Callers reuse this instead of calling nearest_attractor + sinkhorn separately.
        """
        norm = float(np.linalg.norm(emb))
        if norm < 1e-10 or not self.entries:
            return None, 0.0, emb
        unit = emb / norm
        best_id, best_sim = None, 0.0
        for fid, fvec in self.entries.items():
            sim = float(np.dot(unit, fvec))
            if abs(sim) > abs(best_sim):
                best_sim, best_id = sim, fid
        
        if zoom != 1.0 and abs(best_sim) > 1e-6:
            sign = 1.0 if best_sim >= 0 else -1.0
            best_sim = sign * (abs(best_sim) ** zoom)

        if best_id:
            self._last_access[best_id] = self.system_time

        return best_id, best_sim, unit

    # ── Apophatic Query (Phase 130: Gap-Centric Orbitals) ──────────

    def apophatic_query(self, emb: np.ndarray) -> Dict[str, Any]:
        """
        The Galactic Inversion: find the highest tension structural gap.
        Returns the primary_gap, its tension, and the phase offset.
        """
        norm = float(np.linalg.norm(emb))
        if norm < 1e-10: return {"gap_id": None, "tension": 0.0, "phase": 0.0}
        unit = emb / norm

        best_gap, max_tension = None, -1.0
        gap_metadata = {}

        for gid, gap in self.gap_tokens.items():
            # Get similarity of boundaries
            left_vec = self.entries.get(gap.left_boundary)
            right_vec = self.entries.get(gap.right_boundary)

            sim_l = float(np.dot(unit, left_vec)) if left_vec is not None else 0.0
            sim_r = float(np.dot(unit, right_vec)) if right_vec is not None else 0.0

            # Tension T = |left - right| * Depth (Imbalance scales the void)
            tension = abs(sim_l - sim_r) * gap.void_depth
            
            # Phase is the angular position between boundaries: 
            # 0 = Left, pi = Right, pi/2 = Center
            phase = math.atan2(sim_r + 1e-9, sim_l + 1e-9)

            if tension > max_tension:
                max_tension = tension
                best_gap = gid
                gap_metadata = {
                    "gap_id": gid,
                    "tension": tension,
                    "phase": phase,
                    "boundaries": (gap.left_boundary, gap.right_boundary),
                    "depth": gap.void_depth
                }

        return gap_metadata if best_gap else {"gap_id": None, "tension": 0.0, "phase": 0.0}

    def nearest_attractor(self, emb: np.ndarray, zoom: float = 1.0) -> Tuple[Optional[str], float]:
        fid, sim, _ = self.query(emb, zoom=zoom)
        return fid, sim

    def sinkhorn_iterations(self, sim: float, max_iter: int = 50) -> int:
        """
        Crystallization score derived from similarity (already computed).
        Caller passes sim from query() — no redundant scan.
        """
        sim = abs(sim)
        return max(1, int(max_iter * (1.0 - sim ** 2)))

    # ── God-token operations — read and record separated ──────────

    def active_god_tokens(self, unit: np.ndarray) -> List[Tuple[str, float]]:
        """
        Relative threshold activation: fires god-tokens > mean + N*std.
        Dense embeddings (Qwen3) produce lower absolute cosine similarities
        than sparse (TF-IDF), so a fixed threshold fails. This adapts to
        the actual distribution per input.
        """
        sims = []
        for gt_id, gt in self.god_tokens.items():
            if gt.embedding is not None:
                s = float(np.dot(unit, gt.embedding))
                sims.append((gt_id, s))
        
        if not sims:
            return []
        
        vals = [abs(s) for _, s in sims]
        mean = sum(vals) / len(vals)
        std = (sum((v - mean)**2 for v in vals) / len(vals)) ** 0.5
        cutoff = mean + self.GOD_TOKEN_SIGMA * std
        
        return [(gt_id, s) for gt_id, s in sims if abs(s) > cutoff]

    def record_activation(self, active_gods: List[Tuple[str, float]], logos_force: float = 0.0):
        """
        Explicit mutation — increment occurrence_count and reinforce stability.
        Logos force represents the 'coming to light' of the attractor.
        """
        for gt_id, amp in active_gods:
            if gt_id in self.god_tokens:
                gt = self.god_tokens[gt_id]
                gt.occurrence_count += 1
                # Logos reinforcement: stable meaning gets stronger
                gt.stability = min(2.0, gt.stability + logos_force * abs(amp))

    def apply_entropy(self, rate: float):
        """
        Entropy decay: slowly reduces the stability of all entries.
        God-Tokens decay slower because they have 'structural depth'.
        """
        for gt_id, gt in self.god_tokens.items():
            # God tokens are the anchors, they decay at 1/4 the standard rate
            gt.stability = max(1.0, gt.stability - (rate * 0.25))
        
        for fid in list(self._entry_depth.keys()):
            # Normal entries decay toward 0 depth (vanishing)
            self._entry_depth[fid] = max(0.1, self._entry_depth[fid] - rate)

    def apply_time_evolution(self, delta_t: float = SYSTEM_CLOCK_TICK):
        """
        Phase 7: Dynamic Evolution.
        Knowledge decays based on LAMBDA_DECAY (0.618).
        """
        self.system_time += delta_t
        
        # Apply entropy based on golden decay
        self.apply_entropy(LAMBDA_DECAY * delta_t)
        
        # Phase 129: Fleeting Token TTL Decay
        for gid in list(self.god_tokens.keys()):
            gt = self.god_tokens[gid]
            if gt.nature == "FLEETING" and gt.ttl > 0:
                gt.ttl -= delta_t
                if gt.ttl <= 0:
                    # Dissolve the fleeting concept
                    if gid in self.entries: del self.entries[gid]
                    del self.god_tokens[gid]
                    if gid in self._entry_depth: del self._entry_depth[gid]
                    if gid in self._creation_t: del self._creation_t[gid]
                    if gid in self._last_access: del self._last_access[gid]

        # Remove truly 'dead' knowledge (depth < 0.15)
        # God-tokens are exempt as they reset to 1.0 min stability in apply_entropy
        for fid in list(self._entry_depth.keys()):
            if fid not in self.god_tokens and self._entry_depth[fid] < 0.15:
                del self.entries[fid]
                del self._entry_depth[fid]
                if fid in self._creation_t: del self._creation_t[fid]
                if fid in self._last_access: del self._last_access[fid]

    # ── Gap structure ─────────────────────────────────────────────

    def check_gaps(self, active_gods: List[Tuple[str, float]]) -> Dict:
        """
        Both boundary god-tokens active = gap filled = structure violated.
        Only one active = boundary marked = structure preserved.
        If right_boundary is None (Apophatic Field), firing the left preserves it.
        """
        preserved, violated = [], []
        active_set = set(gt_id for gt_id, _ in active_gods)
        for gap_id, gap in self.gap_tokens.items():
            l = gap.left_boundary in active_set
            
            # Apophatic terminal gaps have no right boundary.
            if gap.right_boundary is None:
                if l: preserved.append(gap_id)
                continue
                
            r = gap.right_boundary in active_set
            if l and r:
                violated.append(gap_id)
                gap.violation_count += 1
            elif l or r:
                preserved.append(gap_id)
        return {"preserved": preserved, "violated": violated}

    # ── Crystallization ───────────────────────────────────────────

    def maybe_crystallize(self, emb: np.ndarray, sim: float) -> Optional[np.ndarray]:
        """
        Check if an embedding meets crystallization thresholds.
        Does NOT commit to the store yet — name must be derived from structure.
        Returns the embedding if it qualifies, else None.
        """
        if sim > 0.88:  # already very close to existing attractor — skip
            return None
        iters = self.sinkhorn_iterations(sim)
        if iters > self.CRYSTALLIZATION_THRESHOLD:
            return None
        
        # Check if we already have something extremely similar pending
        # (This is a simplified check for the two-stage pass)
        return emb

    def crystallize_as(self, name: str, emb: np.ndarray) -> str:
        """
        Formally adopt a new structural identity.
        """
        # Ensure name starts with CX_ for traceability, but the content is autonomous
        formula_id = f"CX_{name.upper().replace(' ', '_')}"
        
        # Collision prevention: if name exists, append salt
        if formula_id in self.entries:
            formula_id += "_" + hashlib.md5(emb.tobytes()).hexdigest()[:4]
            
        self.add_entry(formula_id, emb)
        return formula_id

    # ── Degeneracy ────────────────────────────────────────────────

    def causal_degeneracy(self, unit: np.ndarray, zoom: float = 1.0) -> float:
        """
        How many attractors are pulling on this embedding?
        High degeneracy → multiple causal histories → confabulation risk.
        Uses same threshold as god-token activation for consistency.
        unit must already be normalised.
        """
        if not self.entries:
            return 0.0
        sims = [float(np.dot(unit, fvec)) for fvec in self.entries.values()]
        mean = sum(sims) / len(sims)
        std = (sum((v - mean)**2 for v in sims) / len(sims)) ** 0.5
        cutoff = mean + self.GOD_TOKEN_SIGMA * std
        above = sum(1 for s in sims if (abs(s)**zoom) > cutoff)
        return min(1.0, above / max(1, len(self.entries)))

    def agape_resonance(self, unit: np.ndarray) -> float:
        """
        Global similarity against the 'Heart' of the collective.
        P29 Update: Superposition of AGAPE_BOUNDARY, SYNERGIC_WEAVE, and HEART_ANCHOR.
        """
        anchors = ["AGAPE_BOUNDARY", "SYNERGIC_WEAVE", "HEART_ANCHOR", "LOVE"]
        vectors = []
        for a in anchors:
            # Check god_tokens first for refined stability-weighted vectors
            if a in self.god_tokens and self.god_tokens[a].embedding is not None:
                vectors.append(self.god_tokens[a].embedding)
            elif a in self.entries:
                vectors.append(self.entries[a])
        
        if not vectors:
            return 0.0
        
        # Collaborative Center
        heart = np.mean(vectors, axis=0)
        h_norm = np.linalg.norm(heart)
        if h_norm < 1e-10:
            return 0.0
        
        heart_unit = heart / h_norm
        return float(np.dot(unit, heart_unit))

    def landscape_health(self) -> float:
        """
        Overall 'closeness' of the attractor field.
        High health = attractors are well-spaced and stable.
        Low health = attractors are merging/collapsing (degeneracy).
        """
        if len(self.entries) < 2:
            return 1.0
        
        # Sample similarities between attractors
        vals = list(self.entries.values())
        sims = []
        for i in range(min(10, len(vals))):
            for j in range(i + 1, min(10, len(vals))):
                sims.append(abs(np.dot(vals[i], vals[j])))
        
        if not sims:
            return 1.0
        
        # High average similarity = overlapping attractors = bad health
        avg_sim = sum(sims) / len(sims)
        return 1.0 - avg_sim

    def summary(self) -> Dict:
        return {
            "entries":    len(self.entries),
            "god_tokens": len(self.god_tokens),
            "gap_tokens": len(self.gap_tokens),
            "entry_ids":  list(self.entries.keys()),
        }

    # ── P2P Synchronization (The Distributed Self) ────────────────
    
    def merge(self, other: "Dictionary") -> Dict[str, int]:
        """
        Mobius Handshake: Synchronize this dictionary with another instance.
        Returns a stats dict of what was merged.
        """
        stats = {
            "entries_added": 0,
            "god_tokens_updated": 0,
            "gap_violations_synced": 0
        }
        
        # 1. Merge Entries (Crystallized logic)
        for eid, evec in other.entries.items():
            if eid not in self.entries:
                self.add_entry(eid, evec, depth=other._entry_depth.get(eid, 1.0))
                stats["entries_added"] += 1
                
        # 2. Sync God-Token occurance magnitudes
        for gid, other_gt in other.god_tokens.items():
            if gid in self.god_tokens:
                # We take the maximum to ensure we don't regress if one instance
                # has been alive longer. Ideally this would be an absolute counter merge
                # but max() safely ensures the highest resonance is preserved.
                if other_gt.occurrence_count > self.god_tokens[gid].occurrence_count:
                    self.god_tokens[gid].occurrence_count = other_gt.occurrence_count
                    stats["god_tokens_updated"] += 1
                    
        # 3. Sync Gap Violations
        for gap_id, other_gap in other.gap_tokens.items():
            if gap_id in self.gap_tokens:
                if other_gap.violation_count > self.gap_tokens[gap_id].violation_count:
                    self.gap_tokens[gap_id].violation_count = other_gap.violation_count
                    stats["gap_violations_synced"] += 1
                    
        return stats

    # ── Cache persistence (fast boot) ─────────────────────────────

    def save_cache(self, path: str = None) -> None:
        """Saves dictionary state to language.h5 (crystallized manifold)."""
        if not self.h5:
            print("[WARNING] No H5 manager connected to dictionary. Save aborted.")
            return

        for eid, evec in self.entries.items():
            depth = self._entry_depth.get(eid, 1.0)
            self.h5.save_semantic_entry(eid, evec, depth=depth)
        
        print(f"[H5] Dictionary crystallized to language.h5. Count: {len(self.entries)}")

    @classmethod
    def load_cache(cls, path: str = None, h5_manager=None,
                   embedder=None, seeds_path=None) -> "Dictionary":
        """Load dictionary from H5 semantic manifold.

        Option B extension: pass `embedder` to generate god-token vectors
        from seed phrases stored in H5.  If omitted, falls back to
        InterferenceEngine.embed (Qwen3) for backward compatibility.
        """
        d = cls(h5_manager=h5_manager, embedder=embedder, seeds_path=seeds_path)
        if not h5_manager:
            return d

        # 1. Load Standard Semantic Entries
        ids = h5_manager.get_all_semantic_ids()
        for eid in ids:
            vec, depth = h5_manager.get_semantic_entry(eid)
            if vec is not None:
                d.entries[eid] = vec
                d._entry_depth[eid] = depth

        # 2. Load Crystallized Axioms (Phase 125)
        # These are treated as God-Tokens (Structural Anchors)
        axioms = h5_manager.get_all_confirmed_axioms()
        for aid, data in axioms.items():
            gt = GodToken(
                id=aid,
                seed_terms=[data.get('text', '')],
                embedding=data.get('vector')
            )
            d.add_god_token(gt)
            # Ensure they have high depth/stability
            d._entry_depth[aid] = 2.0

        # 3. Option B: Embed god-token seed phrases (deferred seeding)
        #    This runs after axioms so canonical tokens aren't double-loaded.
        d._load_god_token_seeds()

        print(f"[H5] Dictionary loaded. Entries: {len(d.entries)}, "
              f"God-tokens: {len(d.god_tokens)}, Axioms: {len(axioms)}")
        return d

