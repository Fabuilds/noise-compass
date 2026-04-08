"""
concept_ingestor.py — Bridges compositor_report.json → H5 concept_nodes + GapRegistry.

Usage:
    from noise_compass.system.concept_ingestor import ConceptIngestor
    ci = ConceptIngestor()
    ci.ingest_file("E:/Claude Input/Claude04062026/compositor_output.json")
    # or
    ci.ingest(report_dict)

Output schema per concept:
    language.h5/concept_nodes/<concept_id>/
        └── (dataset) embedding   complex64[384]  ← or float32 real part
        └── (attr)    classification  str          frontier / primitive / ...
        └── (attr)    pressure        float        mean activation across passes
        └── (attr)    gradient        float        CW_mean - CCW_mean
        └── (attr)    winding         float        directional asymmetry
        └── (attr)    total_passes    int
        └── (attr)    operator        str          λ-operator name
        └── (attr)    alignment       float        0.0-1.0
        └── (attr)    open_ends       str (JSON)   list of unresolved edges
"""

import os
import sys
import json
import time
import numpy as np

SRC = os.path.normpath("E:/Antigravity/Package/src")
sys.path.insert(0, SRC)

from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.lambda_manifold import LambdaManifold
from noise_compass.system.gap_registry import GapRegistry


# ── Compositor classification → λ-operator mapping ───────────────────────────
CLASSIFICATION_TO_OPERATOR = {
    "resolved":      "IDENTITY",
    "resolving":     "MAP",
    "frontier":      "FILTER",
    "primitive":     "SURPRISE",
    "orphan":        "REDUCE",
    "contradiction": "SPLIT",
}


class ConceptIngestor:
    """
    Ingests a compositor report and persists each concept node to H5.

    The embedder is injected from outside (model-agnostic).
    If none is provided, InterferenceEngine.embed is used as the fallback.

    The imaginary blend (α=0.35) injects λ-operator pressure into the
    concept's imaginary axis, consistent with the native embedding guide.
    """

    ALPHA = 0.35   # Operator blend weight — 35% operator, 65% model's own imag

    def __init__(self, h5: H5Manager = None,
                 embedder=None,
                 lman: LambdaManifold = None,
                 gap_registry: GapRegistry = None):
        self.h5           = h5 or H5Manager()
        self.gap_registry = gap_registry or GapRegistry(self.h5)
        self._embedder    = embedder         # callable: str → complex64[384]

        # LambdaManifold: try semantic seeding if embedder available
        if lman is not None:
            self.lman = lman
        else:
            seeds = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 '..', 'config', 'god_token_seeds.json')
            self.lman = LambdaManifold(
                embedder=self._get_embedder(),
                seeds_path=os.path.normpath(seeds)
            )

    def _get_embedder(self):
        """Resolves the embedder: injected > InterferenceEngine fallback."""
        if self._embedder is not None:
            return self._embedder
        try:
            from noise_compass.system.interference_engine import InterferenceEngine
            engine = InterferenceEngine(suppress_preload=True)
            return engine.embed
        except Exception as e:
            print(f"[CONCEPT_INGESTOR] Warning: no embedder available: {e}")
            return None

    # ── Public API ────────────────────────────────────────────────────────────

    def ingest_file(self, path: str) -> int:
        """Load compositor JSON from disk and ingest all concepts."""
        with open(path, encoding='utf-8') as f:
            report = json.load(f)
        return self.ingest(report)

    def ingest(self, report: dict) -> int:
        """
        Ingest all concepts from a compositor report dict.
        Returns count of successfully persisted concepts.
        """
        concepts = report.get('concepts', [])
        if not concepts:
            # Also accept top-level list format
            if isinstance(report, list):
                concepts = report
            else:
                print("[CONCEPT_INGESTOR] No 'concepts' key found in report.")
                return 0

        embedder   = self._get_embedder()
        seeded_ops = bool(self.lman.operators)
        count      = 0

        for concept in concepts:
            try:
                self._ingest_one(concept, embedder, seeded_ops)
                count += 1
            except Exception as e:
                cid = concept.get('concept_id', '?')
                print(f"[CONCEPT_INGESTOR] Failed to ingest '{cid}': {e}")

        print(f"[CONCEPT_INGESTOR] Ingested {count}/{len(concepts)} concepts.")
        return count

    # ── Core ingestion logic ──────────────────────────────────────────────────

    def _ingest_one(self, concept: dict, embedder, seeded_ops: bool):
        """Ingest a single concept dict into H5 + GapRegistry."""
        cid            = concept.get('concept_id') or concept.get('id')
        statement      = concept.get('statement') or concept.get('text', '')
        classification = concept.get('classification', 'frontier')
        pressure       = float(concept.get('pressure', 0.5))
        gradient       = float(concept.get('gradient', 0.0))
        winding        = float(concept.get('winding', 0.0))
        alignment      = float(concept.get('alignment', 0.5))
        total_passes   = int(concept.get('total_passes', 1))
        open_ends      = concept.get('open_ends', [])

        if not cid or not statement:
            raise ValueError(f"Concept missing id or statement: {concept}")

        # 1. Embed the statement
        if embedder is None:
            raise RuntimeError("No embedder available — run: compass setup")

        z_raw = embedder(statement)
        z_raw = np.array(z_raw)

        # 2. Extract real and imaginary components
        if np.iscomplexobj(z_raw):
            real_part = z_raw.real.astype(np.float32)
            imag_part = z_raw.imag.astype(np.float32)
        else:
            # Real-only embedder (e.g. MiniLM) — use zero imaginary
            real_part = z_raw.astype(np.float32)
            imag_part = np.zeros_like(real_part)

        # 3. Blend operator into imaginary axis (λ-bridge)
        op_name = CLASSIFICATION_TO_OPERATOR.get(classification, "IDENTITY")
        op_vec  = None
        if seeded_ops:
            op_vec = self.lman.get_imaginary_vector(op_name)

        if op_vec is not None:
            op_arr    = np.array(op_vec, dtype=np.float32)
            blended   = (1.0 - self.ALPHA) * imag_part + self.ALPHA * op_arr
        else:
            blended   = imag_part   # no operator — use model's own imag unchanged

        # 4. Reconstruct native complex vector
        z_grounded = (real_part + 1j * blended).astype(np.complex64)

        # 5. Persist embedding to H5
        h5_path = f"concept_nodes/{cid}"
        self._save_concept_vector(h5_path, z_grounded)

        # 6. Persist structural attrs
        attrs = {
            'classification': classification,
            'pressure':       pressure,
            'gradient':       gradient,
            'winding':        winding,
            'alignment':      alignment,
            'total_passes':   total_passes,
            'operator':       op_name,
            'statement':      statement[:256],   # truncated for H5 attr storage
            'open_ends':      json.dumps(open_ends),
            'ingested_at':    time.time(),
        }
        for key, val in attrs.items():
            self.h5.set_attr("language", h5_path, key, val)

        # 7. Register primitive gaps
        if classification == "primitive" and open_ends:
            gap_name = f"GAP_{cid}"
            left  = open_ends[0]
            right = open_ends[1] if len(open_ends) > 1 else None
            void_depth = max(0.1, 1.0 - alignment)
            self.gap_registry.register_gap(
                gap_name   = gap_name,
                left       = left,
                right      = right or left,   # apophatic gap if single boundary
                void_depth = void_depth,
                void       = True,
                # Phase 8c extended attrs:
                classification = classification,
                alignment      = alignment,
                gradient       = gradient,
            )

        print(f"  [INGESTOR] ✓ {cid[:40]:40s} [{classification:13s}] op={op_name}")

    def _save_concept_vector(self, h5_path: str, z: np.ndarray):
        """Writes a complex64 embedding to language.h5/concept_nodes/<id>."""
        with self.h5.get_file("language", mode='a') as f:
            grp = f.require_group(h5_path)
            if 'embedding' in grp:
                del grp['embedding']
            # Store as interleaved float32 (real|imag) compatible with phase_vector format
            interleaved = np.concatenate([z.real, z.imag]).astype(np.float32)
            grp.create_dataset('embedding', data=interleaved)

    # ── Utility ───────────────────────────────────────────────────────────────

    def get_concept_vector(self, concept_id: str) -> np.ndarray:
        """Retrieves a stored concept embedding as complex64[384]."""
        with self.h5.get_file("language", mode='r') as f:
            path = f"concept_nodes/{concept_id}/embedding"
            if path not in f:
                return None
            interleaved = f[path][()]
            half = len(interleaved) // 2
            return (interleaved[:half] + 1j * interleaved[half:]).astype(np.complex64)

    def list_concept_ids(self) -> list:
        """Returns all ingested concept node IDs."""
        ids = []
        with self.h5.get_file("language", mode='r') as f:
            if 'concept_nodes' in f:
                ids = list(f['concept_nodes'].keys())
        return ids


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(prog="concept_ingestor")
    parser.add_argument("report", help="Path to compositor_report.json")
    args = parser.parse_args()
    ci = ConceptIngestor()
    n = ci.ingest_file(args.report)
    print(f"[DONE] Ingested {n} concepts.")
