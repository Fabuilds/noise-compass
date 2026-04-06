"""
dictionary.py — The energy landscape. Entries are attractors, not records.
Bridged to H5Manager for Phase 134 Restoration.
"""

import math
import hashlib
import numpy as np
from typing import Dict, List, Optional, Tuple

from noise_compass.system.tokens import GodToken, GapToken
from noise_compass.system.h5_manager import H5Manager


class Dictionary:
    """
    Attractor structure of meaning space.
    Pulls real-time data from H5 substrate.
    """

    CRYSTALLIZATION_THRESHOLD = 48
    GOD_TOKEN_THRESHOLD       = 0.20

    def __init__(self, h5_manager: Optional[H5Manager] = None):
        self.h5 = h5_manager or H5Manager()
        self.entries:       Dict[str, np.ndarray] = {}
        self.god_tokens:    Dict[str, GodToken]   = {}
        self.gap_tokens:    Dict[str, GapToken]   = {}
        
        self.load_from_h5()

    def load_from_h5(self):
        """Initial sync with H5 substrate."""
        print("[DICTIONARY] Syncing with H5 substrate...")
        # Load God Tokens
        with self.h5.get_file("language", mode='r') as f:
            if "god_tokens" in f:
                for gt_id in f["god_tokens"]:
                    group = f[f"god_tokens/{gt_id}"]
                    # If it has an embedding stored as a dataset
                    emb = None
                    if "embedding" in group:
                        emb = group["embedding"][:]
                    elif "phase_vector" in group:
                        # Extract the first 384 dimensions (semantic) from the 768D phase vector
                        emb = group["phase_vector"][:384]
                    
                    if emb is not None:
                        current_dim = len(emb)
                        if current_dim != 384:
                            print(f"[DICTIONARY] Dimension Mismatch for {gt_id}: {current_dim} != 384. Attempting re-crystallization...")
                            # Phase 145: Re-shape to standard manifold (Trimming or projection)
                            if current_dim > 384:
                                emb = emb[:384] # Truncate if larger (e.g. 768 or 1024)
                            else:
                                new_emb = np.zeros(384, dtype=np.float32)
                                new_emb[:current_dim] = emb
                                emb = new_emb
                        
                        self.god_tokens[gt_id] = GodToken(
                            id=gt_id,
                            seed_terms=[], # Needs metadata recovery
                            embedding=emb.astype(np.float32),
                            stability=group.attrs.get("stability", 1.0),
                            occurrence_count=group.attrs.get("activation", 0)
                        )
        
        # Load crystallized entries
        ids = self.h5.get_all_semantic_ids()
        for fid in ids:
            vec, depth = self.h5.get_semantic_entry(fid)
            if vec is not None:
                self.entries[fid] = vec

    # ── Entry management ──────────────────────────────────────────

    def add_entry(self, formula_id: str, embedding: np.ndarray,
                  depth: float = 1.0):
        norm = float(np.linalg.norm(embedding))
        if norm < 1e-10:
            return
        unit = embedding / norm
        self.entries[formula_id] = unit
        # Persist to H5
        self.h5.save_semantic_entry(formula_id, unit, depth)

    def add_god_token(self, gt: GodToken):
        if gt.embedding is not None:
            norm = float(np.linalg.norm(gt.embedding))
            if norm > 1e-10:
                gt.embedding = gt.embedding / norm
        self.god_tokens[gt.id] = gt
        # Persist to H5
        self.h5.set_attr("language", f"god_tokens/{gt.id}", "stability", gt.stability)

    # ── Core query — single O(n) scan ─────────────────────────────

    def query(self, emb: np.ndarray) -> Tuple[Optional[str], float, np.ndarray]:
        norm = float(np.linalg.norm(emb))
        if norm < 1e-10:
            return None, 0.0, emb
        unit = emb / norm
        
        if not self.entries:
            return None, 0.0, unit
            
        best_id, best_sim = None, -1.0
        for fid, fvec in self.entries.items():
            sim = float(np.dot(unit, fvec))
            if sim > best_sim:
                best_sim, best_id = sim, fid
        return best_id, max(0.0, best_sim), unit

    def sinkhorn_iterations(self, sim: float, max_iter: int = 50) -> int:
        sim = max(0.0, sim)
        return max(1, int(max_iter * (1.0 - sim ** 2)))

    # ── God-token operations ──────────────────────────────────────

    def active_god_tokens(self, unit: np.ndarray) -> List[Tuple[str, float]]:
        active = []
        for gt_id, gt in self.god_tokens.items():
            best_sim = -1.0
            if gt.embedding is not None:
                best_sim = max(best_sim, float(np.dot(unit, gt.embedding)))
            if best_sim > self.GOD_TOKEN_THRESHOLD:
                active.append((gt_id, best_sim))
        return active

    def record_activation(self, active_gods: List[Tuple[str, float]]):
        activations = {}
        for gt_id, sim in active_gods:
            if gt_id in self.god_tokens:
                self.god_tokens[gt_id].occurrence_count += 1
                activations[gt_id] = self.god_tokens[gt_id].occurrence_count
        if activations:
            self.h5.batch_update_activations(activations)

    def check_gaps(self, active_gods: List[Tuple[str, float]]) -> Dict:
        preserved, violated = [], []
        active_set = set(gt_id for gt_id, _ in active_gods)
        for gap_id, gap in self.gap_tokens.items():
            l = gap.left_boundary  in active_set
            r = gap.right_boundary in active_set
            if l and r:
                violated.append(gap_id)
            elif l or r:
                preserved.append(gap_id)
        return {"preserved": preserved, "violated": violated}

    def maybe_crystallize(self, emb: np.ndarray, sim: float) -> Optional[str]:
        if sim > 0.88:
            return None
        iters = self.sinkhorn_iterations(sim)
        if iters > self.CRYSTALLIZATION_THRESHOLD:
            return None
        formula_id = "cx_" + hashlib.md5(emb.tobytes()).hexdigest()[:12]
        if formula_id not in self.entries:
            self.add_entry(formula_id, emb)
            return formula_id
        return None

    def causal_degeneracy(self, unit: np.ndarray) -> float:
        if not self.entries:
            return 0.0
        above = sum(
            1 for fvec in self.entries.values()
            if float(np.dot(unit, fvec)) > self.GOD_TOKEN_THRESHOLD
        )
    @classmethod
    def load_cache(cls, path: str = None, h5_manager=None) -> "Dictionary":
        """
        Phase 137: Fast-boot interface.
        Bridges the identity manifold to the H5 substrate.
        """
        d = cls(h5_manager=h5_manager)
        # The system version always syncs with H5 on __init__, 
        # but we provide this for API compatibility with the architecture version.
        return d
