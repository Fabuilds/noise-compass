"""
core.py — Formula, Scout, Witness.
Incorporates HiPPO-LegS for temporal context ψ(x,t).
"""

import math
import time
import hashlib
import numpy as np
from scipy.linalg import expm
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from noise_compass.system.tokens import WaveFunction, ArchiverMessage, CausalType
from noise_compass.system.dictionary import Dictionary


# ═══════════════════════════════════════════════════════════════
# HiPPO-LegS — Temporal Context Layer
# ═══════════════════════════════════════════════════════════════

def build_hippo_legs(N: int):
    """
    Construct the HiPPO-LegS (Legendre Scaled) A matrix and B vector.
    """
    A = np.zeros((N, N))
    for n in range(N):
        for k in range(N):
            if n > k:
                A[n, k] = -((2*n + 1)**0.5) * ((2*k + 1)**0.5)
            elif n == k:
                A[n, k] = -(n + 1)

    B = np.array([(2*n + 1)**0.5 for n in range(N)], dtype=np.float64)

    # Zero-order hold (ZOH) discretization, unit step
    A_bar = expm(A)
    B_bar = np.linalg.solve(A, (A_bar - np.eye(N)) @ B)

    return A_bar.astype(np.float32), B_bar.astype(np.float32)


class HiPPOLayer:
    """
    D independent HiPPO-LegS channels — one per embedding dimension.
    """

    def __init__(self, D: int, N: int = 8):
        self.D = D
        self.N = N
        self.A_bar, self.B_bar = build_hippo_legs(N)
        self.state = np.zeros((D, N), dtype=np.float32)
        self.t = 0

    def step(self, emb: np.ndarray) -> np.ndarray:
        """Update orbital state. Returns pre-step prediction."""
        prediction = self.state[:, 0].copy()
        self.state = (self.state @ self.A_bar.T) + np.outer(emb, self.B_bar)
        self.t += 1
        return prediction

    def predictive_surprise(self, emb: np.ndarray, unit: np.ndarray) -> np.ndarray:
        """Per-dimension surprise relative to trajectory prediction."""
        prediction = self.state[:, 0]
        pred_norm = np.linalg.norm(prediction)
        if pred_norm > 1e-10:
            prediction_unit = prediction / pred_norm
        else:
            prediction_unit = np.zeros(self.D, dtype=np.float32)
        return unit - prediction_unit

    def orbital_state_snapshot(self) -> np.ndarray:
        return self.state.copy()


# ═══════════════════════════════════════════════════════════════
# FORMULA
# ═══════════════════════════════════════════════════════════════

class Formula:
    """
    F(x) = known(x) + i·Δ(x)
    """
    SANITY_DEPTH = 7

    def __init__(self, dictionary: Dictionary):
        self.dictionary = dictionary
        self._depth     = 0

    def apply(self, emb: np.ndarray) -> WaveFunction:
        """Apply F once. Returns ψ(x)."""
        self._depth += 1
        try:
            if self._depth > self.SANITY_DEPTH:
                return WaveFunction(emb.copy(), np.zeros_like(emb))

            fid, sim, unit = self.dictionary.query(emb)

            if fid is None or sim < 1e-6:
                return WaveFunction(np.zeros_like(emb), emb.copy())

            known_vec = self.dictionary.entries[fid]
            known     = known_vec * sim
            delta     = emb - known
            return WaveFunction(known, delta)
        finally:
            self._depth -= 1


# ═══════════════════════════════════════════════════════════════
# SCOUT
# ═══════════════════════════════════════════════════════════════

class Scout:
    """
    Orbiting agent. Applies F, maintains SSM orbital state.
    """

    LAMBDA_DECAY = 0.618

    def __init__(self, dictionary: Dictionary, soup_id: str = "default",
                 encoder=None):
        self.dictionary     = dictionary
        self.soup_id        = soup_id
        self.formula        = Formula(dictionary)
        
        if encoder is None:
            from sentence_transformers import SentenceTransformer
            self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        else:
            self.encoder = encoder
            
        self.orbital_state: Optional[np.ndarray] = None
        self.sheet_index    = 0
        self._prev_phase: Optional[float] = None
        self.crystallized:  List[str] = []
        self.hippo: Optional[HiPPOLayer] = None
        self._first_encounter: dict = {}

    def process(self, emb: np.ndarray,
                content: str = "",
                timestamp: Optional[float] = None) -> Tuple[ArchiverMessage, WaveFunction]:
        if timestamp is None:
            timestamp = time.time()

        fid, sim, unit = self.dictionary.query(emb)
        sim = max(sim, 0.0)

        # Wave function
        wf = self.formula.apply(emb)

        # SSM state update
        if self.orbital_state is None:
            self.orbital_state = wf.known.copy()
        else:
            self.orbital_state = (
                self.LAMBDA_DECAY * self.orbital_state +
                (1 - self.LAMBDA_DECAY) * wf.known
            )

        # Sheet index
        if self._prev_phase is not None:
            crossed = (
                (self._prev_phase < math.pi/4 <= wf.phase) or
                (self._prev_phase > math.pi/4 >= wf.phase)
            )
            if crossed:
                self.sheet_index += 1
        self._prev_phase = wf.phase

        # Metrics
        s_iters = self.dictionary.sinkhorn_iterations(sim)
        energy = -math.log(max(sim, 1e-10))
        active_gods = self.dictionary.active_god_tokens(unit)
        gap_structure = self.dictionary.check_gaps(active_gods)

        # Causal type
        if sim > 0.75:
            causal_type = CausalType.GRADIENT
        elif sim < 0.25:
            causal_type = CausalType.INTERVENTION
        else:
            causal_type = CausalType.UNKNOWN

        fisher = max(0.0, 1.0 - abs(wf.phase - math.pi/4) / (math.pi/4))
        degeneracy = self.dictionary.causal_degeneracy(unit)

        # Routing
        if s_iters <= 10:
            routing = "COMPRESS  → dictionary pointer"
        elif s_iters >= 35:
            routing = "ROUTE     → Qwen processing"
        else:
            routing = "ORBIT     → continue processing"

        # Crystallize
        new_id = self.dictionary.maybe_crystallize(emb, sim)
        if new_id:
            self.crystallized.append(new_id)
            self.dictionary.record_activation(active_gods)

        # Archiver message
        msg = ArchiverMessage(
            god_token_cluster   = [{"id": gt[0], "magnitude": gt[1]} for gt in active_gods],
            energy_level        = energy,
            sheet_index         = self.sheet_index,
            causal_type         = causal_type.value,
            soup_provenance     = self.soup_id,
            gap_structure       = gap_structure,
            fisher_alignment    = fisher,
            sinkhorn_iterations = s_iters,
            orbital_state       = self.orbital_state.copy(),
            timestamp           = timestamp,
            degeneracy          = degeneracy,
            content_preview     = content[:80],
            zone                = wf.zone(),
            routing             = routing,
        )

        # Temporal layer
        if self.hippo is None:
            self.hippo = HiPPOLayer(D=len(emb), N=8)

        norm = float(np.linalg.norm(emb))
        prediction = self.hippo.step(emb)

        pred_norm = float(np.linalg.norm(prediction))
        if pred_norm > 1e-10 and norm > 1e-10:
            traj_alignment = float(np.dot(emb / norm, prediction / pred_norm))
        else:
            traj_alignment = 0.0

        ps = self.hippo.predictive_surprise(emb, unit)
        msg.predictive_surprise  = ps
        msg.trajectory_alignment = traj_alignment

        return msg, wf


# ═══════════════════════════════════════════════════════════════
# WITNESS
# ═══════════════════════════════════════════════════════════════

class Witness:
    """
    External reference for orbital stability.
    """

    ENERGY_THRESHOLD    = 1.2
    FISHER_THRESHOLD    = 0.35
    DEGENERACY_WARNING  = 0.6
    PRECESSION_LIMIT    = 0.4

    def __init__(self):
        self.history:        List[ArchiverMessage] = []
        self.orbital_lock:   bool  = False
        self._phase_history: List[float] = []

    def observe(self, msg: ArchiverMessage, wf: WaveFunction) -> Dict:
        self.history.append(msg)
        self._phase_history.append(wf.phase)

        temporal_stable  = msg.energy_level   < self.ENERGY_THRESHOLD
        causally_aligned = msg.fisher_alignment > self.FISHER_THRESHOLD
        gaps_intact      = len(msg.gap_structure["violated"]) == 0

        self.orbital_lock = temporal_stable and causally_aligned and gaps_intact

        # Precession
        precession = 0.0
        if len(self.history) >= 2:
            prev = self.history[-2].orbital_state
            curr = msg.orbital_state
            n_p  = float(np.linalg.norm(prev))
            n_c  = float(np.linalg.norm(curr))
            if n_p > 1e-10 and n_c > 1e-10:
                cos_sim    = float(np.dot(prev / n_p, curr / n_c))
                precession = 1.0 - max(-1.0, min(1.0, cos_sim))

        return {
            "orbital_lock":       self.orbital_lock,
            "temporal_stable":    temporal_stable,
            "causally_aligned":   causally_aligned,
            "gaps_intact":        gaps_intact,
            "precession":         f"{precession:.3f}",
            "zone":               wf.zone(),
            "routing":            msg.routing,
            "documents_seen":     len(self.history),
        }
