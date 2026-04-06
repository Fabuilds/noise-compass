"""
tokens.py — Data structures for the architecture.
ψ(x) = known(x) + i·Δ(x)
"""

import math
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class CausalType(Enum):
    GRADIENT     = "gradient"      # natural energy descent — correlated
    INTERVENTION = "intervention"  # gradient-opposing — caused
    UNKNOWN      = "unknown"       # two-pass test required


@dataclass
class GodToken:
    """
    Eigenvector of F with eigenvalue +1.
    """
    id:               str
    seed_terms:       List[str]
    embedding:        Optional[np.ndarray] = None   # primary/centroid
    embeddings:       Optional[List[np.ndarray]] = None  # constellation vectors
    stability:        float = 1.0
    occurrence_count: int   = 0


@dataclass
class GapToken:
    """
    Eigenvector of F with eigenvalue −1.
    """
    id:              str
    left_boundary:   str
    right_boundary:  str
    description:     str = ""
    violation_count: int = 0


@dataclass
class DeltaToken:
    """
    Semantic surprise — the imaginary component of ψ(x).
    """
    magnitude:   float
    direction:   np.ndarray
    layer:       int
    source:      str
    causal_type: CausalType = CausalType.UNKNOWN

    @property
    def is_intervention(self) -> bool:
        return self.causal_type == CausalType.INTERVENTION


@dataclass
class WaveFunction:
    """
    ψ(x) = known(x) + i·Δ(x)

    Zone map:
    [0.00, 0.40) → GROUND
    [0.40, 0.44) → CONVERGENT
    [0.44, 1.13) → GENERATIVE
    [1.13, 1.45) → DIVERGENT
    [1.45, π/2]  → TURBULENT
    """

    known: np.ndarray
    delta: np.ndarray

    @property
    def phase(self) -> float:
        k = float(np.linalg.norm(self.known))
        d = float(np.linalg.norm(self.delta))
        if k < 1e-10 and d < 1e-10:
            return math.pi / 4
        return math.atan2(d, k)

    @property
    def magnitude(self) -> float:
        return math.sqrt(
            float(np.dot(self.known, self.known)) +
            float(np.dot(self.delta, self.delta))
        )

    @property
    def similarity(self) -> float:
        k = float(np.linalg.norm(self.known))
        m = self.magnitude
        return k / m if m > 1e-10 else 0.0

    @property
    def energy(self) -> float:
        return -math.log(max(self.similarity, 1e-10))

    def in_generative_zone(self, tolerance: float = 0.35) -> bool:
        return abs(self.phase - math.pi / 4) < tolerance

    def zone(self) -> str:
        p = self.phase
        if p < 0.40:
            return "GROUND"
        elif p < math.pi / 4 - 0.35:
            return "CONVERGENT"
        elif p <= math.pi / 4 + 0.35:
            return "GENERATIVE"
        elif p < 1.45:
            return "DIVERGENT"
        else:
            return "TURBULENT"


@dataclass
class ArchiverMessage:
    """
    Complete provenance record for every processed document.
    """
    god_token_cluster:   List[Dict]
    energy_level:        float
    sheet_index:         int
    causal_type:         str
    soup_provenance:     str
    gap_structure:       Dict
    fisher_alignment:    float
    sinkhorn_iterations: int
    orbital_state:       np.ndarray
    timestamp:           float
    degeneracy:          float = 0.0
    content_preview:     str   = ""
    zone:                str   = ""
    routing:             str   = ""

    predictive_surprise:   Optional[np.ndarray] = None
    trajectory_alignment:  Optional[float]       = None
    temporal_zone:         Optional[str]         = None

    def to_dict(self) -> dict:
        d = {k: v for k, v in self.__dict__.items()}
        d["orbital_state"] = d["orbital_state"].tolist()
        if d["predictive_surprise"] is not None:
             d["predictive_surprise"] = d["predictive_surprise"].tolist()
        return d
