"""
archiver.py — Structural long-term memory for the architecture.

F(x) = known(x) + i·Δ(x)

The archiver is NOT sequential memory. It is structural memory.
Two documents are related not because one came before the other,
but because they share god-tokens — they occupy the same attractor basin.

God-tokens are the retrieval keys. Any two documents sharing a god-token
are connected through it regardless of when they were processed.
The archiver is the index. The god-token cluster is the address.

Architecture:
  - Primary store:   List[ArchiverMessage]          (ordered by insertion)
  - Inverted index:  Dict[god_token_id, List[int]]  (O(1) god-token lookup)
  - Energy index:    sorted List[(energy, int)]      (binary search by energy)
  - Zone index:      Dict[zone_str, List[int]]       (direct zone lookup)
  - Sheet index:     Dict[int, List[int]]            (direct sheet lookup)

All indices store record positions (int), not copies of records.
Mutation of a record after storage is not supported — records are immutable
once stored, consistent with the archiver's role as provenance log.

Retrieval contract:
  All query methods return List[ArchiverMessage] sorted by timestamp ascending.
  The caller decides ordering. The archiver does not impose recency bias.

Persistence:
  save(path) / load(path) round-trip through JSON.
  orbital_state (np.ndarray) is serialized as list; predictive_surprise likewise.
  dtype is restored to float32 on load.
"""

import json
import math
import bisect
import os
import hashlib
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field

import sys
from pathlib import Path

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.tokens import ArchiverMessage


# ── Query result ──────────────────────────────────────────────────────────────

@dataclass
class QueryResult:
    """
    Wraps a list of ArchiverMessage records with provenance of how they
    were retrieved. Allows chaining: result.filter_by_zone("GENERATIVE").
    """
    records:     List[ArchiverMessage]
    query_desc:  str = ""
    total_in_archive: int = 0

    def __len__(self) -> int:
        return len(self.records)

    def __iter__(self):
        return iter(self.records)

    def filter_by_zone(self, zone: str) -> "QueryResult":
        return QueryResult(
            records=[r for r in self.records if r.zone == zone],
            query_desc=f"{self.query_desc} ∩ zone={zone}",
            total_in_archive=self.total_in_archive,
        )

    def filter_by_causal(self, causal_type: str) -> "QueryResult":
        return QueryResult(
            records=[r for r in self.records if r.causal_type == causal_type],
            query_desc=f"{self.query_desc} ∩ causal={causal_type}",
            total_in_archive=self.total_in_archive,
        )

    def filter_by_energy(self, max_energy: float) -> "QueryResult":
        return QueryResult(
            records=[r for r in self.records if r.energy_level <= max_energy],
            query_desc=f"{self.query_desc} ∩ energy≤{max_energy:.2f}",
            total_in_archive=self.total_in_archive,
        )

    def filter_no_gap_violations(self) -> "QueryResult":
        return QueryResult(
            records=[r for r in self.records if not r.gap_structure.get("violated")],
            query_desc=f"{self.query_desc} ∩ no_violations",
            total_in_archive=self.total_in_archive,
        )

    def sort_by_energy(self, ascending: bool = True) -> "QueryResult":
        return QueryResult(
            records=sorted(self.records, key=lambda r: r.energy_level,
                           reverse=not ascending),
            query_desc=self.query_desc,
            total_in_archive=self.total_in_archive,
        )

    def sort_by_timestamp(self, ascending: bool = True) -> "QueryResult":
        return QueryResult(
            records=sorted(self.records, key=lambda r: r.timestamp,
                           reverse=not ascending),
            query_desc=self.query_desc,
            total_in_archive=self.total_in_archive,
        )

    def summary(self) -> Dict:
        if not self.records:
            return {"count": 0, "query": self.query_desc}
        energies = [r.energy_level for r in self.records]
        zones = {}
        for r in self.records:
            zones[r.zone] = zones.get(r.zone, 0) + 1
        return {
            "count":        len(self.records),
            "query":        self.query_desc,
            "energy_mean":  f"{sum(energies)/len(energies):.3f}",
            "energy_range": f"[{min(energies):.3f}, {max(energies):.3f}]",
            "zones":        zones,
            "total_in_archive": self.total_in_archive,
        }


# ── Archiver ──────────────────────────────────────────────────────────────────

class Archiver:
    """
    Structural long-term memory.

    The archiver answers the question: "what else have we seen that is
    structurally related to this?" It does not answer "what did we see
    recently?" Sequential recency is not the organizing principle.
    Structural identity — shared god-token basins — is.

    God-tokens as memory addresses:
        archiver.by_god_token("CAUSALITY")
        → all documents that activated CAUSALITY, any time, any session

    Structural relatedness:
        archiver.related_to(msg)
        → documents sharing ≥1 god-token with msg

    Overlap strength:
        archiver.overlap_score(msg_a, msg_b)
        → Jaccard similarity of god-token clusters [0, 1]
        → 1.0 = same semantic primitive set (structurally identical)
        → 0.0 = no shared primitives (structurally orthogonal)

    Re-encounter detection:
        archiver.prior_encounters(content_hash)
        → records with matching content hash (same document seen before)
        → enables ψ(x,t) re-encounter signal comparison
    """

    def __init__(self, session_id: str = "default"):
        self.session_id = session_id

        # ── Primary store ─────────────────────────────────────────
        self._records: List[ArchiverMessage] = []

        # ── Inverted indices ──────────────────────────────────────
        # god_token_id → list of record positions
        self._gt_index:    Dict[str, List[int]] = {}
        # zone → list of record positions
        self._zone_index:  Dict[str, List[int]] = {}
        # sheet_index → list of record positions
        self._sheet_index: Dict[int, List[int]] = {}
        # causal_type → list of record positions
        self._causal_index: Dict[str, List[int]] = {}
        # content_hash → list of record positions (re-encounter detection)
        self._hash_index:  Dict[str, List[int]] = {}

        # ── Energy index: sorted (energy, position) pairs ─────────
        # Used for range queries without full scan
        self._energy_index: List[Tuple[float, int]] = []

    # ── Store ─────────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_gt_ids(cluster_or_activations) -> List[str]:
        """Normalize god_token activations/clusters to List[str].
        Handles:
        1. List[GodTokenActivation] (Phase 9 architecture)
        2. List[dict] (Phase 4 scope/magnitude dicts OR Phase 9 JSON parsed dicts)
        3. List[str] (Legacy string arrays)
        """
        if not cluster_or_activations:
            return []
            
        ids = []
        for item in cluster_or_activations:
            # Phase 9 native objects
            if hasattr(item, "id"):
                ids.append(item.id)
            # Phase 9 or Phase 4 JSON parsed dicts
            elif isinstance(item, dict):
                ids.append(item.get("id", str(item)))
            # Legacy Phase 1-3 simple strings
            elif isinstance(item, str):
                ids.append(item)
            else:
                ids.append(str(item))
        return ids

    def store(self, msg: ArchiverMessage,
              content_hash: Optional[str] = None) -> int:
        """
        Store a record. Returns its position in the archive.
        content_hash: MD5 of the raw embedding (from maybe_crystallize logic).
        Pass it to enable re-encounter detection.
        """
        pos = len(self._records)
        self._records.append(msg)

        # ── Index: god-tokens ─────────────────────────────────────
        for gt_id in self._extract_gt_ids(msg.god_token_activations):
            if gt_id not in self._gt_index:
                self._gt_index[gt_id] = []
            self._gt_index[gt_id].append(pos)

        # ── Index: zone ───────────────────────────────────────────
        zone = msg.zone or "UNKNOWN"
        if zone not in self._zone_index:
            self._zone_index[zone] = []
        self._zone_index[zone].append(pos)

        # ── Index: sheet ──────────────────────────────────────────
        si = msg.sheet_index
        if si not in self._sheet_index:
            self._sheet_index[si] = []
        self._sheet_index[si].append(pos)

        # ── Index: causal type ────────────────────────────────────
        ct = msg.causal_type or "unknown"
        if ct not in self._causal_index:
            self._causal_index[ct] = []
        self._causal_index[ct].append(pos)

        # ── Index: energy (sorted insert) ─────────────────────────
        bisect.insort(self._energy_index, (msg.energy_level, pos))

        # ── Index: content hash ───────────────────────────────────
        if content_hash:
            if content_hash not in self._hash_index:
                self._hash_index[content_hash] = []
            self._hash_index[content_hash].append(pos)

        return pos

    # ── Core retrieval ────────────────────────────────────────────────────────

    def by_god_token(self, gt_id: str) -> QueryResult:
        """
        All records that activated this god-token.
        This is the primary structural memory query.
        """
        positions = self._gt_index.get(gt_id, [])
        return QueryResult(
            records=[self._records[p] for p in positions],
            query_desc=f"god_token={gt_id}",
            total_in_archive=len(self._records),
        )

    def by_god_tokens_all(self, gt_ids: List[str]) -> QueryResult:
        """
        Records that activated ALL of the given god-tokens (AND query).
        Intersection of god-token sets — structurally precise.
        """
        if not gt_ids:
            return QueryResult([], "god_tokens_all=[]", len(self._records))
        sets = [set(self._gt_index.get(gt, [])) for gt in gt_ids]
        intersection = sets[0].intersection(*sets[1:])
        positions = sorted(intersection)
        return QueryResult(
            records=[self._records[p] for p in positions],
            query_desc=f"god_tokens_all={gt_ids}",
            total_in_archive=len(self._records),
        )

    def by_god_tokens_any(self, gt_ids: List[str]) -> QueryResult:
        """
        Records that activated ANY of the given god-tokens (OR query).
        Union — broad structural reach.
        """
        if not gt_ids:
            return QueryResult([], "god_tokens_any=[]", len(self._records))
        seen: Set[int] = set()
        for gt in gt_ids:
            seen.update(self._gt_index.get(gt, []))
        positions = sorted(seen)
        return QueryResult(
            records=[self._records[p] for p in positions],
            query_desc=f"god_tokens_any={gt_ids}",
            total_in_archive=len(self._records),
        )

    def by_zone(self, zone: str) -> QueryResult:
        """All records in the given phase zone."""
        positions = self._zone_index.get(zone, [])
        return QueryResult(
            records=[self._records[p] for p in positions],
            query_desc=f"zone={zone}",
            total_in_archive=len(self._records),
        )

    def by_energy(self, max_energy: float,
                  min_energy: float = 0.0) -> QueryResult:
        """
        Records with energy in [min_energy, max_energy].
        Uses binary search on sorted energy index — O(log n + k).
        """
        lo = bisect.bisect_left(self._energy_index,  (min_energy, -1))
        hi = bisect.bisect_right(self._energy_index, (max_energy, float("inf")))
        positions = sorted(pos for _, pos in self._energy_index[lo:hi])
        return QueryResult(
            records=[self._records[p] for p in positions],
            query_desc=f"energy=[{min_energy:.2f},{max_energy:.2f}]",
            total_in_archive=len(self._records),
        )

    def by_causal_type(self, causal_type: str) -> QueryResult:
        """All records of the given causal type."""
        positions = self._causal_index.get(causal_type, [])
        return QueryResult(
            records=[self._records[p] for p in positions],
            query_desc=f"causal_type={causal_type}",
            total_in_archive=len(self._records),
        )

    def by_sheet(self, sheet_index: int) -> QueryResult:
        """All records on the given Riemann sheet."""
        positions = self._sheet_index.get(sheet_index, [])
        return QueryResult(
            records=[self._records[p] for p in positions],
            query_desc=f"sheet={sheet_index}",
            total_in_archive=len(self._records),
        )

    def by_gap_violated(self, gap_id: Optional[str] = None) -> QueryResult:
        """
        Records with gap violations. If gap_id given, only that gap.
        Gap violations are category errors — both boundary god-tokens
        active simultaneously.
        """
        if gap_id:
            recs = [r for r in self._records
                    if gap_id in r.gap_structure.get("violated", [])]
            desc = f"gap_violated={gap_id}"
        else:
            recs = [r for r in self._records
                    if r.gap_structure.get("violated")]
            desc = "any_gap_violated"
        return QueryResult(recs, desc, len(self._records))

    def by_time_range(self, t_start: float,
                      t_end: float) -> QueryResult:
        """Records processed in [t_start, t_end]."""
        recs = [r for r in self._records
                if t_start <= r.timestamp <= t_end]
        return QueryResult(
            records=recs,
            query_desc=f"time=[{t_start:.1f},{t_end:.1f}]",
            total_in_archive=len(self._records),
        )

    # ── Structural relatedness ────────────────────────────────────────────────

    def related_to(self, msg: ArchiverMessage,
                   min_overlap: int = 1) -> QueryResult:
        """
        Documents sharing ≥ min_overlap god-tokens with msg.

        This is the temporal memory query. Two documents processed
        months apart are "related" if they share a god-token —
        if they occupy the same attractor basin.

        min_overlap=1: any shared primitive (broad reach)
        min_overlap=2: at least two shared primitives (structural alignment)
        min_overlap=len(cluster): exact same god-token set (structural identity)
        """
        cluster = set(self._extract_gt_ids(msg.god_token_activations))
        if not cluster:
            return QueryResult([], "related_to(no_god_tokens)", len(self._records))

        # Collect candidate positions from inverted index
        candidate_counts: Dict[int, int] = {}
        for gt_id in cluster:
            for pos in self._gt_index.get(gt_id, []):
                if self._records[pos] is not msg:
                    candidate_counts[pos] = candidate_counts.get(pos, 0) + 1

        positions = sorted(
            pos for pos, count in candidate_counts.items()
            if count >= min_overlap
        )
        return QueryResult(
            records=[self._records[p] for p in positions],
            query_desc=f"related_to(cluster={list(cluster)}, min_overlap={min_overlap})",
            total_in_archive=len(self._records),
        )

    def overlap_score(self, msg_a: ArchiverMessage,
                      msg_b: ArchiverMessage) -> float:
        """
        Jaccard similarity of god-token clusters.

        0.0 = structurally orthogonal (no shared primitives)
        1.0 = structurally identical (same god-token set)

        This is the structural distance metric between two documents.
        Independent of when they were processed, what they contain,
        or what domain they came from. Pure semantic primitive overlap.
        """
        a = set(self._extract_gt_ids(msg_a.god_token_activations))
        b = set(self._extract_gt_ids(msg_b.god_token_activations))
        if not a and not b:
            return 1.0  # both empty — vacuously identical
        if not a or not b:
            return 0.0
        return len(a & b) / len(a | b)

    def cluster_by_god_token(self) -> Dict[str, QueryResult]:
        """
        Partition the archive by god-token.
        Returns one QueryResult per god-token containing all records
        that activated it.

        Note: records appear in multiple partitions if they activated
        multiple god-tokens. This is correct — a document can belong
        to multiple semantic primitive basins simultaneously.
        """
        return {
            gt_id: QueryResult(
                records=[self._records[p] for p in positions],
                query_desc=f"cluster/{gt_id}",
                total_in_archive=len(self._records),
            )
            for gt_id, positions in self._gt_index.items()
        }

    # ── Re-encounter detection (ψ(x,t) support) ──────────────────────────────

    def prior_encounters(self, content_hash: str) -> QueryResult:
        """
        All prior records with this content hash.
        Empty result = first encounter.
        Non-empty = re-encounter. Use for ψ(x,t) learning signal.

        content_hash: hashlib.md5(emb.tobytes()).hexdigest()[:12]
        Same hash as crystallization ID (without "cx_" prefix).
        """
        positions = self._hash_index.get(content_hash, [])
        return QueryResult(
            records=[self._records[p] for p in positions],
            query_desc=f"prior_encounters(hash={content_hash})",
            total_in_archive=len(self._records),
        )

    def is_first_encounter(self, content_hash: str) -> bool:
        return content_hash not in self._hash_index

    # ── Aggregate analysis ────────────────────────────────────────────────────

    def phase_distribution(self) -> Dict:
        """
        SOC check across all stored records.
        Hypothesis: mean phase converges to π/4 without being designed to.
        """
        if not self._records:
            return {}
        # Reconstruct phase from zone and energy (approximate)
        # Exact phase not stored in ArchiverMessage — use zone distribution
        zone_counts = {}
        for r in self._records:
            zone_counts[r.zone] = zone_counts.get(r.zone, 0) + 1

        energies = [r.energy_level for r in self._records]
        mean_energy = sum(energies) / len(energies)

        return {
            "total_records":  len(self._records),
            "zone_counts":    zone_counts,
            "mean_energy":    f"{mean_energy:.3f}",
            "ground_fraction":      f"{zone_counts.get('GROUND', 0) / len(self._records):.2f}",
            "generative_fraction":  f"{zone_counts.get('GENERATIVE', 0) / len(self._records):.2f}",
            "turbulent_fraction":   f"{zone_counts.get('TURBULENT', 0) / len(self._records):.2f}",
        }

    def god_token_activation_profile(self) -> Dict[str, Dict]:
        """
        For each god-token: how many records activated it, mean energy
        of those records, zone distribution.
        Reveals which semantic primitives dominate the corpus.
        """
        profile = {}
        for gt_id, positions in self._gt_index.items():
            recs = [self._records[p] for p in positions]
            energies = [r.energy_level for r in recs]
            zones = {}
            for r in recs:
                zones[r.zone] = zones.get(r.zone, 0) + 1
            profile[gt_id] = {
                "activation_count": len(recs),
                "mean_energy":      round(sum(energies) / len(energies), 4),
                "zones":            zones,
                "fraction_of_corpus": round(len(recs) / len(self._records), 3)
                    if self._records else 0.0,
            }
        return dict(sorted(profile.items(),
                           key=lambda x: -x[1]["activation_count"]))

    def gap_violation_profile(self) -> Dict[str, int]:
        """
        How often each gap was violated across the corpus.
        High violation count = systematic category error pressure in the corpus.
        """
        profile: Dict[str, int] = {}
        for r in self._records:
            for gap_id in r.gap_structure.get("violated", []):
                profile[gap_id] = profile.get(gap_id, 0) + 1
        return dict(sorted(profile.items(), key=lambda x: -x[1]))

    def intervention_cluster(self) -> QueryResult:
        """
        All INTERVENTION records — documents that pushed against
        the gradient of the attractor landscape.
        These are causally interesting events.
        """
        return self.by_causal_type("intervention")

    def high_degeneracy_records(self,
                                threshold: float = 0.6) -> QueryResult:
        """
        Records with degeneracy above threshold.
        High degeneracy = multiple causal histories = confabulation risk.
        """
        recs = [r for r in self._records if r.degeneracy > threshold]
        return QueryResult(
            recs,
            f"degeneracy>{threshold}",
            len(self._records),
        )

    # ── Persistence ───────────────────────────────────────────────────────────

    def save(self, path: str) -> None:
        """
        Serialize archive to JSON.
        orbital_state and predictive_surprise (np.ndarray) → list.
        On load, restored to float32 ndarray.
        """
        path = Path(path)
        records_serialized = []
        for r in self._records:
            d = r.to_dict()
            # to_dict() already converts orbital_state to list
            # handle predictive_surprise if present (ψ(x,t) field)
            if "predictive_surprise" in d and d["predictive_surprise"] is not None:
                if isinstance(d["predictive_surprise"], np.ndarray):
                    d["predictive_surprise"] = d["predictive_surprise"].tolist()
            records_serialized.append(d)

        payload = {
            "session_id":     self.session_id,
            "record_count":   len(self._records),
            "records":        records_serialized,
            # Rebuild indices on load — don't serialize them
        }
        
        # ── Atomic Write ──
        temp_path = path.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            
            # Atomic swap
            os.replace(temp_path, path)
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise e

    @classmethod
    def load(cls, path: str) -> "Archiver":
        """
        Deserialize archive from JSON. Rebuilds all indices.
        """
        path = Path(path)
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        archiver = cls(session_id=payload.get("session_id", "loaded"))

        for d in payload["records"]:
            # Restore numpy arrays
            orbital = np.array(d.pop("orbital_state"), dtype=np.float32)
            ps = d.pop("predictive_surprise", None)
            predictive_surprise = (
                np.array(ps, dtype=np.float32) if ps is not None else None
            )

            msg = ArchiverMessage(
                orbital_state=orbital,
                **{k: v for k, v in d.items()
                   if k not in ("orbital_state", "predictive_surprise")}
            )
            # Re-attach ψ(x,t) field if present
            if hasattr(msg, "predictive_surprise"):
                msg.predictive_surprise = predictive_surprise

            archiver.store(msg)

        return archiver

    # ── Repr ──────────────────────────────────────────────────────────────────

    def __len__(self) -> int:
        return len(self._records)

    def __repr__(self) -> str:
        gt_count = len(self._gt_index)
        return (f"Archiver(session={self.session_id!r}, "
                f"records={len(self._records)}, "
                f"god_token_keys={gt_count})")

    def summary(self) -> Dict:
        return {
            "session_id":      self.session_id,
            "total_records":   len(self._records),
            "god_token_keys":  list(self._gt_index.keys()),
            "zones_indexed":   list(self._zone_index.keys()),
            "sheets_indexed":  sorted(self._sheet_index.keys()),
            "causal_types":    list(self._causal_index.keys()),
            "hash_keys":       len(self._hash_index),
        }
