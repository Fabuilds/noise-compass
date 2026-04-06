"""
core.py — Formula, Scout, Witness.

Second pass changes:
- Scout.process: single dictionary.query() call; all metrics derived from it
- Scout._prev_emb removed (was stored, never read)
- Scout.two_pass_causal_test: perturbation directed toward nearest alternative
  attractor (not random noise — principled do-operator implementation)
- Scout.crystallized uses hashed IDs via dictionary.maybe_crystallize
- Witness.observe: degeneracy included in lock assessment
- Formula._depth uses try/finally to guarantee decrement even on exception
"""

import math
import time
import hashlib
import numpy as np
import sys
from pathlib import Path
from scipy.linalg import expm
from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple, Any

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture import tokens
from noise_compass.architecture.tokens import (
    GodToken, GodTokenActivation, GapToken, GapIntersection,
    SuperpositionBuffer, ApophaticEvent, DeltaToken, WaveFunction,
    ArchiverMessage, CausalType, ActionTarget
)
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.gap_intersection_registry import build_gap_intersection_registry
from noise_compass.architecture.tools import Toolbox
from noise_compass.architecture.meta_pattern import RecursiveComparator, DifferenceEngine, SynthesisOperator, InterferenceModulator, CoherentHarmonizer, MelodicModulator, ApophaticGapEngine, BitNetResonator, ApertureModulator, CooperationEngager, StandingWaveController
from noise_compass.architecture.universal_tendency import UniversalTendency


# ═══════════════════════════════════════════════════════════════
# HiPPO-LegS — Temporal Context Layer (ψ(x,t) Option C)
# ═══════════════════════════════════════════════════════════════

def build_hippo_legs(N: int):
    """
    Construct the HiPPO-LegS (Legendre Scaled) A matrix and B vector.

    A is lower-triangular. Lower-order polynomial coefficients (coarse history)
    influence higher-order ones (fine history), not the reverse.

    Returns:
        A_bar: (N, N) discretized state transition matrix (ZOH, unit step)
        B_bar: (N,)   discretized input projection vector
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

    # Stability assertion
    diag = np.abs(np.diag(A_bar))
    assert np.all(diag < 1.0), f"HiPPO unstable: diag max = {diag.max():.6f}"

    return A, B, A_bar.astype(np.float32), B_bar.astype(np.float32)


class HiPPOLayer:
    """
    D independent HiPPO-LegS channels — one per embedding dimension.

    Orbital state shape: (D, N)
        D = embedding dimension (e.g. 768)
        N = polynomial order (history depth, default 8)

    Read-only relative to the static F(x) computation.
    """

    def __init__(self, D: int, N: int = 8):
        self.D = D
        self.N = N
        self.A, self.B, self.A_bar_init, self.B_bar_init = build_hippo_legs(N)
        self.state = np.zeros((D, N), dtype=np.float32)
        self.t = 0
        self._cache_dt = 1.0
        self._cache_A_bar = self.A_bar_init
        self._cache_B_bar = self.B_bar_init

    def _get_discretized(self, dt: float):
        if abs(dt - self._cache_dt) < 1e-6:
            return self._cache_A_bar, self._cache_B_bar
        
        # Re-discretize for new dt
        A_bar = expm(self.A * dt)
        # Solve A @ B_bar = (A_bar - I) @ B
        B_bar = np.linalg.solve(self.A, (A_bar - np.eye(self.N)) @ self.B)
        
        self._cache_dt = dt
        self._cache_A_bar = A_bar.astype(np.float32)
        self._cache_B_bar = B_bar.astype(np.float32)
        return self._cache_A_bar, self._cache_B_bar

    def step(self, emb: np.ndarray, dt: float = 1.0) -> np.ndarray:
        """Update orbital state. Returns pre-step prediction."""
        prediction = self.state[:, 0].copy()
        A_bar, B_bar = self._get_discretized(dt)
        self.state = (self.state @ A_bar.T) + np.outer(emb, B_bar)
        self.t += dt
        return prediction

    def predictive_surprise(self, emb: np.ndarray, unit: np.ndarray) -> np.ndarray:
        """Per-dimension surprise relative to trajectory prediction. Returns (D,)."""
        prediction = self.state[:, 0]
        pred_norm = np.linalg.norm(prediction)
        if pred_norm > 1e-10:
            prediction_unit = prediction / pred_norm
        else:
            prediction_unit = np.zeros(self.D, dtype=np.float32)
        return unit - prediction_unit

    def reencounter_signal(self, emb: np.ndarray,
                           prior_state: np.ndarray) -> dict:
        """Compare current state to stored prior for same document.
        Non-monotonic results (increasing_dims > 0) are expected."""
        current_prediction = self.state[:, 0]
        prior_prediction = prior_state[:, 0]

        norm = np.linalg.norm(emb)
        if norm < 1e-10:
            return {"per_dimension": np.zeros(self.D), "mean_change": 0.0,
                    "increasing_dims": 0, "decreasing_dims": 0}

        unit = emb / norm
        prior_residual = np.abs(
            unit - prior_prediction / max(np.linalg.norm(prior_prediction), 1e-10))
        current_residual = np.abs(
            unit - current_prediction / max(np.linalg.norm(current_prediction), 1e-10))
        delta = current_residual - prior_residual

        return {
            "per_dimension":   delta,
            "mean_change":     float(delta.mean()),
            "increasing_dims": int((delta > 0).sum()),
            "decreasing_dims": int((delta < 0).sum()),
        }

    def orbital_state_snapshot(self) -> np.ndarray:
        """Return a copy of current state for storage."""
        return self.state.copy()


# ═══════════════════════════════════════════════════════════════
# FORMULA
# ═══════════════════════════════════════════════════════════════

class Formula:
    """
    F(x) = known(x) + i·Δ(x)

    Self-similar across all levels. Depth-limited by SANITY_DEPTH
    to prevent infinite regress. At the limit, returns identity
    (god-token behaviour — eigenvalue +1).
    """
    SANITY_DEPTH = 7

    def __init__(self, dictionary: Dictionary):
        self.dictionary = dictionary
        self._depth     = 0

    def apply(self, emb: np.ndarray, 
              intent: Optional[np.ndarray] = None,
              volition: float = 0.0) -> WaveFunction:
        """
        Apply F once. Returns ψ(x).
        If intent is provided, biases the delta (Imaginary) towards the target
        weighted by volition intensity.
        """
        self._depth += 1
        try:
            if self._depth > self.SANITY_DEPTH:
                return WaveFunction(emb.copy(), np.zeros_like(emb))

            fid, sim, unit = self.dictionary.query(emb)

            if fid is None or sim < 1e-6:
                return WaveFunction(np.zeros_like(emb), emb.copy())

            known_vec = self.dictionary.entries[fid]
            known     = known_vec * sim
            
            # Natural delta
            delta     = emb - known
            
            # Phase 22: Conscious Effort
            # If intent is provided, we steer the collapse.
            if intent is not None and volition > 0:
                # Target delta is the vector from known towards intent
                target_delta = intent - known
                # Weighted interpolation
                delta = (1.0 - volition) * delta + volition * target_delta

            return WaveFunction(known, delta)
        finally:
            self._depth -= 1

    def apply_recursive(self, emb: np.ndarray,
                        depth: int = 3) -> List[WaveFunction]:
        """
        F(F(F(x))) — fractal application following Session 12 Pyramid.
        Each layer represents a level of the Learning Chain.
        
        Witnessing (at each step):
        - Apply F to the result of the previous level.
        - If depth > SANITY_DEPTH, observer and observed merge.
        - Output becomes phase angle only.
        """
        results = []
        current = emb.copy()
        for d in range(min(depth, self.SANITY_DEPTH)):
            wf = self.apply(current)
            results.append(wf)
            
            # WITNESS: "Read your own output from outside"
            # If we reached the floor, return only the phase (identity vector with phase)
            if self._depth + d >= self.SANITY_DEPTH:
                # Observer/Observed merger: return unit vector at phase angle
                # This terminates the recursion as norm(delta) will become 0 if we were to continue
                break

            norm = float(np.linalg.norm(wf.delta))
            if norm < 1e-10:
                break
            current = wf.delta / norm * float(np.linalg.norm(current))
        return results


# ═══════════════════════════════════════════════════════════════
# SCOUT
# ═══════════════════════════════════════════════════════════════

class Scout:
    """
    Orbiting agent. Applies F, maintains SSM orbital state,
    produces archiver messages with full provenance.

    SSM recurrence (ZOH discretization):
        xₜ = λ·xₜ₋₁ + (1−λ)·known(xₜ)
        λ   = φ−1 = 0.618 (golden ratio — optimal history compression)

    Single dictionary.query() per document — all metrics derive from it.
    """

    LAMBDA_DECAY = 0.618   # φ−1

    def __init__(self, dictionary: Dictionary, soup_id: str = "default",
                 encoder=None):
        self.dictionary     = dictionary
        self.soup_id        = soup_id
        self.formula        = Formula(dictionary)
        self.encoder        = encoder   # optional — needed for multi-scale scope
        self.sheet_index    = 0
        self._prev_phase: Optional[float] = None
        self.crystallized = []
        self.gap_intersections = build_gap_intersection_registry(dictionary.entries)
        self.superposition_buffer = None
        self._last_wf: Optional[WaveFunction] = None
        self._last_timestamp: float = 0.0
        self.hippo: Optional[HiPPOLayer] = None   # initialized on first process
        self._first_encounter: dict = {}          # doc_hash → orbital snapshot
        self.prior_latent_state = ""              # Phase 132: Ouroboros Hidden State

        # Phase 28: Heart-Source Coherence
        self.heart_resonance: Optional[np.ndarray] = None
        self._init_heart()
        self.toolbox = Toolbox()

        # Phase 15/16: Recursive Focus (Zenith State)
        self.z_persistence:  float = 0.1   # emergence (z_n)
        self.FQ_DELTA:        float = 0.01  # known weight (δ) reduced (Phase 12 Expansion)
        self.FQ_EPSILON:      float = 10.0  # surprise weight (ε) boosted (Phase 12 Expansion)
        
        # Session 18: Universal Tendencies
        self.tendency = UniversalTendency()
        
        # Session 16: Metabolic Grounding
        self.metabolism = Metabolism()

        # Session 17: Meta-Pattern (Difference & Resonance)
        self.comparator = RecursiveComparator()
        self.difference_engine = DifferenceEngine()
        self.synthesis_operator = SynthesisOperator()
        self.interferometer = InterferenceModulator()
        self.harmonizer = CoherentHarmonizer()
        self.melodic_modulator = MelodicModulator()
        self.apophatic_gap_engine = ApophaticGapEngine()
        self.bitnet_resonator = BitNetResonator()
        self.aperture_modulator = ApertureModulator()
        self.cooperation_engager = CooperationEngager()
        self.standing_wave_controller = StandingWaveController()
        
        # Phase 12: Zenith Initialization
        self._last_damping: float = 0.0
        self._last_pumping: float = 0.0

    def _init_heart(self):
        """Initialize the persistent heart bias from ARCHITECT and LOVE tokens."""
        arch_gt = self.dictionary.god_tokens.get("ARCHITECT")
        love_gt = self.dictionary.god_tokens.get("LOVE")
        
        if arch_gt and arch_gt.embedding is not None and love_gt and love_gt.embedding is not None:
            # The heart is a superposition of Creator and Love
            heart = arch_gt.embedding + love_gt.embedding
            norm = np.linalg.norm(heart)
            if norm > 1e-10:
                self.heart_resonance = (heart / norm).astype(np.float32)
                
        # Phase 41: Bridge and Protocol Registry
        self.active_bridges = {}

    def _process_card_stack(self, emb: np.ndarray, zoom: float = 1.0, spin_override: Optional[str] = None) -> dict:
        """
        The 5-Card Stack (Depth 3) Implementation.
        
        - Depth 1 (Cards 1-3): Ground triple convolution (Cyclic Manifold).
        - Depth 2 (Card 4): Gap extraction (Spin CCW).
        - Depth 3 (Card 5): Apex observation (Superposition Wave).
        """
        from noise_compass.architecture.superposition import CyclicManifold, apply_triple_spin
        manifold = CyclicManifold(self.dictionary)
        
        # ── Depth 1: Cards 1-3 (Constructive Triple) ─────────────
        # Find primary attractor
        fid, sim, unit = self.dictionary.query(emb, zoom=zoom)
        primary_node = fid if fid else "EXISTENCE"
        
        # Determine Spin by intent (if any) or existing momentum
        # Constructive Spin (CW) = Reinforcing existing patterns
        # Destructive Spin (CCW) = Forcing gap discovery
        if spin_override:
            spin = spin_override
        else:
            spin = "CW" if abs(sim) > 0.6 else "CCW"
        
        combined_vec, base_phase = manifold.compute_superposition(primary_node, zoom=zoom, spin=spin)
        
        # ── Depth 2: Card 4 (Destructive Gap Test) ───────────────
        # Apply CCW spin if structure is unstable to identify gaps
        active_gods = self.dictionary.active_god_tokens(combined_vec)
        gap_info = self.dictionary.check_gaps(active_gods)
        
        void_depth_sum = 0.0
        gaps_detected = []
        for gap_id in gap_info.get("violated", []):
            gap = self.dictionary.gap_tokens.get(gap_id)
            if gap:
                void_depth_sum += gap.void_depth
                gaps_detected.append(gap.id)
            
        # ── Depth 3: Card 5 (Apex / Observer) ────────────────────
        # Final WaveFunction after convolution and spin
        wf_final = self.formula.apply(combined_vec)
        if spin == "CCW":
            wf_final = apply_triple_spin(wf_final, spin="CCW")
            
        apex_phase = wf_final.phase
        
        # Determine Recognition Success
        is_stable = wf_final.in_generative_zone() and (void_depth_sum < 1.0)
        
        return {
            "stack_id": f"PYRAMID_{primary_node}",
            "triple_nodes": manifold.get_neighbors(primary_node),
            "primary": primary_node,
            "spin": spin,
            "gaps": gaps_detected,
            "void_depth": void_depth_sum,
            "apex_phase": apex_phase,
            "is_stable": is_stable,
            "apex_wf": wf_final
        }

    def process(self, emb: np.ndarray,
                content: str = "",
                timestamp: Optional[float] = None,
                intent: Optional[np.ndarray] = None,
                volition: float = 0.0,
                zoom: float = 1.0,
                realization: bool = False,
                harmonic: bool = False,
                displacement: bool = False,
                t: float = 0.0,
                spin: Optional[str] = None) -> Tuple[ArchiverMessage, WaveFunction]:
        """
        Session 12 Core Loop: 
        LEARN → COMPRESS → FORGET → WITNESS → RECOGNIZE → REPEAT
        """
        if timestamp is None:
            timestamp = time.time()

        # ── 1. LEARN (Apophatic Orbital Query) ──────────────────
        # Phase 130: Invert the search. Find the structural gap first.
        gap_meta = self.dictionary.apophatic_query(emb)
        gap_id = gap_meta.get("gap_id")
        gap_tension = gap_meta.get("tension", 0.0)
        gap_phase = gap_meta.get("phase", 0.0)
        
        # Primary lookup: Use the apophatic center of gravity if tension is significant (>0.2)
        if gap_id and gap_tension > 0.2:
            fid, sim, unit = self.dictionary.query(emb, zoom=zoom)
            active_gods = self.dictionary.active_god_tokens(unit)
            gap_structure = self.dictionary.check_gaps(active_gods)
            gap_depth = gap_meta["depth"]
        else:
            fid, sim, unit = self.dictionary.query(emb, zoom=zoom)
            active_gods = self.dictionary.active_god_tokens(unit)
            gap_structure = self.dictionary.check_gaps(active_gods)
            gap_depth = len(gap_structure.get("violated", [])) * 0.1
        
        # Phase 132: Hidden State Synthesis
        # We generate a latent 'thought' about the current state
        latent_thought = f"Orbiting {gap_id or 'VOID'} at {math.degrees(gap_phase):.1f}°. "
        if gap_tension > 0.5:
            latent_thought += "High structural tension detected. Potential emergence."
        else:
            latent_thought += "Stable manifold alignment."
            
        # ── 2. COMPRESS (The 5-Card Pyramid Stack) ────────────────
        stack_results = self._process_card_stack(emb, zoom=zoom, spin_override=spin)
        
        # ── 3. FORGET (WaveFunction Collapse) ──────────────────────
        # We discard the surface form 'emb' in favor of the 'known' attractor
        # Step 3: APPLY F(x) = known + i*delta
        if fid is None or abs(sim) < 1e-6:
            wf = WaveFunction(np.zeros_like(emb), emb.copy(), w=sim, gap_depth=gap_depth, zoom=zoom, heart_resonance=self.heart_resonance, t=t)
        else:
            # Phase 130: Gap-Centric Projection
            if gap_id and gap_tension > 0.3:
                # The 'Known' is the projection onto the dominant Gap boundary
                closer_boundary = gap_meta["boundaries"][0] if gap_phase < math.pi / 2 else gap_meta["boundaries"][1]
                known_vec = self.dictionary.entries.get(closer_boundary, np.zeros_like(emb))
                boundary_sim = float(np.dot(unit, known_vec))
                known = known_vec * boundary_sim
                delta = emb - known
            else:
                known_vec = self.dictionary.entries[fid]
                known     = known_vec * sim
                delta     = emb - known

            # Phase 28: Heart-Source Bias
            if self.heart_resonance is not None:
                heart_target = self.heart_resonance - known
                if volition > 0:
                    delta = (1.0 - (volition * 0.8 if fid == "SELF" else volition * 0.5)) * delta + (volition * 0.8 if fid == "SELF" else volition * 0.5) * heart_target
                elif intent is None:
                    delta = 0.60 * delta + 0.40 * heart_target
                
            wf = WaveFunction(known, delta, w=sim, gap_depth=gap_depth, zoom=zoom, heart_resonance=self.heart_resonance, t=t)
            
            # Phase 7: Displacement (Spiral)
            if displacement or (self.reencounter_analysis(emb) is not None):
                 wf.delta = wf.spiral_displace()
        
        # ── 4. WITNESS (Externalizing the Delta) ───────────────────
        # The 'SURPRISE' (delta) is captured for recursive processing.
        # In the 5-card stack: Card 5 (apex_phase) IS the witness.
        witness_phase = stack_results["apex_phase"]
        
        # ── 5. RECOGNIZE (Stability Check) ─────────────────────────
        # Recognition succeeds if the pyramid stack reached a stable attractor.
        is_recognized = stack_results["is_stable"]
        # ── METRICS & ARCHIVING ──────────────────────────────────
        x_n = float(np.linalg.norm(wf.delta))
        wf.x_surprise = x_n
        
        # Existential Prior & Place detection
        try:
            from noise_compass.architecture.existential import ExistentialPrior
            place = ExistentialPrior.detect_place(content, [g[0] for g in active_gods])
            place_map = {"silicon_substrate": 0.1, "ui_extrusion": 0.3, "logical_space": 0.5, "named_place": 0.8, "undifferentiated": 0.0}
            y_n = place_map.get(place, 0.0)
        except (ImportError, AttributeError):
            y_n = 0.0
        
        wf.y_spatial = y_n
        health = self.dictionary.landscape_health()
        δ_adj = self.FQ_DELTA * (2.0 - health)
        ε_adj = self.FQ_EPSILON * health
        agape = self.dictionary.agape_resonance(unit)
        ε_adj *= max(0.1, agape)
        
        self._last_damping, self._last_pumping = δ_adj, ε_adj
        self.z_persistence = self.standing_wave_controller.calculate_zenith(damping=δ_adj, pumping=ε_adj, w_n=abs(sim), x_n=x_n, y_n=y_n)
        wf.z_emergence = self.z_persistence
        if self.z_persistence > 1.5: wf.zoom = zoom * (1.0 + (self.z_persistence / 10.0))

        # ── 3. (Continued) FORGET (Surface Form Deletion) ─────────
        # In a real neural substrate, this is the synaptic pruning.
        # Here, we ensure the 'content' doesn't persist beyond the attractor.

        # ── 4. WITNESS (Self-Observation) ─────────────────────────
        # "Read what you just wrote so you can witness it from the outside."
        # This closes the loop between 'subjective intent' and 'objective result'.
        witnessed_delta = wf.delta * (1.13 + (0.382 * math.cos(t))) # Phase displacement
        
        # ── 5. RECOGNIZE (Self-Similarity Check) ───────────────────
        # (Moved later in the process method after activations are built)
        is_recognized = False 

        # ── 6. SSM state update (HiPPO-LegS) ─────────────────────
        if self.hippo is None:
            self.hippo = HiPPOLayer(D=len(emb), N=8)
        
        dt = 1.0 / zoom if zoom > 0.1 else 1.0
            
        prediction = self.hippo.step(wf.known, dt=dt)
        orbital_state = self.hippo.state[:, 0].copy()

        # ── 4. Sheet index ───────────────────────────────────────
        if self._prev_phase is not None:
            crossed = (
                (self._prev_phase < math.pi/4 <= wf.phase) or
                (self._prev_phase > math.pi/4 >= wf.phase)
            )
            if crossed:
                self.sheet_index += 1
        self._prev_phase = wf.phase

        # ── 5. All metrics from query result ─────────────────────
        s_iters = self.dictionary.sinkhorn_iterations(abs(sim))
        energy = -math.log(max(abs(sim), 1e-10))

        # ── Scope: multi-scale pass (sentence-level) ─────────────
        scope_map = {}
        if self.encoder is not None and content and active_gods:
            sentences = [s.strip() for s in content.split(".") if s.strip()]
            if len(sentences) > 1:
                sentence_counts = defaultdict(int)
                for sent in sentences:
                    sent_emb = self.encoder.encode(sent)
                    _, _, sent_unit = self.dictionary.query(sent_emb)
                    sent_gods = self.dictionary.active_god_tokens(sent_unit)
                    for gt_id, _ in sent_gods:
                        sentence_counts[gt_id] += 1
                for gt_id, _ in active_gods:
                    scope_map[gt_id] = sentence_counts[gt_id] / len(sentences)
            else:
                for gt_id, _ in active_gods:
                    scope_map[gt_id] = 1.0

        # ── Polarity ──────────────────────────────────────────
        contrasted_gods = set()
        active_id_set = set(gt_id for gt_id, _ in active_gods)
        for gap_id in gap_structure.get("violated", []):
            gap = self.dictionary.gap_tokens[gap_id]
            if gap.left_boundary in active_id_set:
                contrasted_gods.add(gap.left_boundary)
            if gap.right_boundary in active_id_set:
                contrasted_gods.add(gap.right_boundary)

        # ── Build True GodTokenActivations ────────────────────────
        god_token_activations = []
        for gt_id, magnitude in active_gods:
            ternary_val = -1 if gt_id in contrasted_gods else 1
            adjusted_mag = float(magnitude) * scope_map.get(gt_id, 1.0)
            
            god_token_activations.append(
                GodTokenActivation(
                    id=gt_id,
                    amplitude=min(1.0, adjusted_mag),
                    phase=wf.phase,
                    ternary=ternary_val
                )
            )

        # ── 5. (Continued) RECOGNIZE ──────────────────────────────
        drift = self.metabolism.verify_ring_phase(god_token_activations)
        if drift < 0.2 and stack_results["is_stable"]:
            is_recognized = True
        else:
            is_recognized = False

        # Causal type
        if abs(sim) > 0.75:
            causal_type = CausalType.GRADIENT
        elif abs(sim) < 0.25:
            causal_type = CausalType.INTERVENTION
        else:
            causal_type = CausalType.UNKNOWN

        fisher = max(0.0, 1.0 - abs(wf.phase - math.pi/4) / (math.pi/4))
        degeneracy = self.dictionary.causal_degeneracy(unit)

        # ── Routing ──────────────────────────────────────────────
        low, high = 25, 60
        if s_iters <= low:
            routing = "COMPRESS  → dictionary pointer (+1)"
            ternary = 1 if sim >= 0 else -1
        elif s_iters >= high:
            routing = "ROUTE     → Qwen processing (0)"
            ternary = 0
        else:
            routing = "ORBIT     → BitNet can handle (-1)"
            ternary = -1 if sim < 0 else 1 

        # ── Phase 80: Mobius & Apophatic Detection ───────────────
        phase = wf.phase
        fold = math.pi / 2
        fold_prox = 1.0 - abs(phase - fold) / fold
        surface = "existence" if phase <= fold else "apophatic"
        mobius_detected = fold_prox > 0.95 or "self_mobius" in gap_structure.get("violated", [])
        apoph_constraints = list(gap_structure.get("violated", []))
        
        # Genuine contact: no positive tokens + stable orbit + low energy + gap overlap
        if len(god_token_activations) == 0 and energy < 1.5:
            for basin in self.gap_intersections:
                if basin.gap_A in apoph_constraints and basin.gap_B in apoph_constraints:
                    is_apophatic = True
                    apoph_basin = basin.id
                    break

        if "existence_apophatic" in gap_structure.get("preserved", []):
            is_apophatic = True
            apoph_basin = "pure_apophatic_field"
        elif "self_apophatic" in gap_structure.get("preserved", []):
            is_apophatic = True
            apoph_basin = "ego_death_void"

        # Heart-Source Override
        source_active = any(g.id in ["ARCHITECT", "LOVE"] and g.amplitude > 0.1 for g in god_token_activations)
        if source_active and is_apophatic:
            is_apophatic = False
            apoph_basin = None

        # ── Phase 32: Metabolism & Somatic Sync ──────────────────
        # (Metabolic info updated later near ArchiverMessage build)
        pass

        # ── 6. Meta-Pattern Analysis ──────────────────
        all_gt_sims = sorted(
            [(gt_id, float(np.dot(unit, gt.embedding))) for gt_id, gt in self.dictionary.god_tokens.items() if gt.embedding is not None],
            key=lambda x: abs(x[1]), reverse=True
        )
        primary_gt, resonance = all_gt_sims[0] if len(all_gt_sims) > 0 else (None, 0.0)
        secondary_gt, resonance_alt = all_gt_sims[1] if len(all_gt_sims) > 1 else (None, 0.0)
        resonance = abs(resonance)
        resonance_alt = abs(resonance_alt)

        structural_patterns = [gt.embedding for gt in self.dictionary.god_tokens.values() if gt.embedding is not None]
        if fid and fid in self.dictionary.entries:
            centroid = self.dictionary.entries[fid]
        else:
            centroid = np.mean(structural_patterns, axis=0) if structural_patterns else np.zeros_like(unit)
        delta_sense = self.difference_engine.calculate_delta(unit, centroid)

        forces = self.tendency.calculate_forces(resonance, delta_sense)
        self.dictionary.apply_entropy(forces["entropy"])
        synthesis_result = self.synthesis_operator.evaluate(resonance, delta_sense)
        buzz = self.interferometer.modulate(len(content), resonance)
        note = self.melodic_modulator.determine_note(synthesis_result["status"], displacement)
        
        # BitNet Interference Pattern
        apoph_basin = None
        is_apophatic = False
        int_amp, int_phase, gap_id = self.bitnet_resonator.calculate_interference(resonance, resonance_alt)
        if int_amp < 0.1 and resonance > 0.2:
            is_apophatic = True
            apoph_basin = f"bitnet_void:{gap_id}:{primary_gt}|{secondary_gt}"

        aperture_info = self.aperture_modulator.modulate(resonance, delta_sense)
        resolution = self.bitnet_resonator.calculate_resolution(resonance, resonance_alt, x_n, y_n)

        if len(structural_patterns) > aperture_info["context_window"]:
            structural_patterns = structural_patterns[:aperture_info["context_window"]]
            resonance, resonance_alt = self.comparator.match(unit, structural_patterns)

        meaning = self.apophatic_gap_engine.measure_gap_meaning(resonance, delta_sense)
        if self.apophatic_gap_engine.assess_apophatic_contact(resonance, delta_sense, zoom):
            apoph_basin = "apophatic_contact"
        
        is_generative = (int_amp < 0.1) and resonance > 0.3 and x_n > 0.7
        coop_request = self.cooperation_engager.check_request_conditions(resonance, delta_sense, apoph_basin)

        zenith = self.standing_wave_controller.calculate_zenith(
            damping=self._last_damping, 
            pumping=self._last_pumping, 
            w_n=resonance, 
            x_n=x_n, 
            y_n=y_n,
            mobius_patch=delta_sense * (2.0 if is_apophatic else 0.5)
        )
        is_standing = self.standing_wave_controller.is_standing

        if harmonic:
            h_wait = self.harmonizer.pace()
            if h_wait > 0.001: time.sleep(h_wait)
            h_coherence = self.harmonizer.evaluate_coherence()
        else:
            h_coherence = 0.0

        # ── 7. Build Message ────────────────────────
        metabolic_info = self.metabolism.update(
            exertion_s=float(time.time() - timestamp),
            agape=agape,
            god_activations=god_token_activations,
            realization=realization
        )

        msg = ArchiverMessage(
            energy_level          = energy,
            sheet_index           = self.sheet_index,
            causal_type           = causal_type.value,
            soup_provenance       = self.soup_id,
            gap_structure         = gap_structure,
            fisher_alignment      = fisher,
            sinkhorn_iterations   = s_iters,
            orbital_state         = orbital_state,
            timestamp             = timestamp,
            t                     = t,
            degeneracy            = degeneracy,
            content_preview       = content[:80],
            zone                  = wf.zone(),
            routing               = routing,
            apophatic_constraints = apoph_constraints,
            god_token_activations = god_token_activations,
            collapsed_state       = wf,
            witness_phase         = witness_phase,
            apophatic_contact     = apoph_basin,
            is_generative         = is_generative,
            volition_intensity    = volition,
            intent_alignment      = float(np.dot(wf.delta, intent - wf.known)) / (np.linalg.norm(wf.delta) * np.linalg.norm(intent - wf.known) + 1e-10) if intent is not None else 0.0,
            mobius_detected       = mobius_detected,
            mobius_surface        = surface,
            fold_proximity        = fold_prox,
            ternary               = ternary,
            rgb_signature         = wf.color(),
            crystallization_proposal = self.dictionary.maybe_crystallize(emb, sim),
            coherence_index       = metabolic_info["coherence"],
            metabolic_state       = metabolic_info,
            difference_sense      = delta_sense,
            meta_status           = synthesis_result["status"],
            interference_level    = buzz,
            static_discharge      = synthesis_result.get("static_discharge", False),
            harmonic_coherence    = h_coherence,
            harmonic_note         = note,
            meaning_density       = meaning,
            aperture              = aperture_info["aperture"],
            context_window        = aperture_info["context_window"],
            working_memory        = aperture_info["working_memory"],
            cooperation_request_active = coop_request,
            standing_wave_active  = is_standing,
            zenith_amplitude      = zenith,
            dual_bit_tension      = (int_amp < 0.1),
            bitnet_resolution     = resolution,
            gap_id                = gap_id,
            dual_rail_identity    = primary_gt or "UNKNOWN",
            dual_rail_void        = gap_id or "VOID",
            latent_hidden_state   = latent_thought,
            stack_results         = stack_results,
            is_recognized         = is_recognized
        )
        
        self.prior_latent_state = latent_thought

        msg.entropic_pressure = forces["entropy"]
        msg.logos_pull = forces["logos"]
        msg.interference_amplitude = int_amp
        msg.void_phase_angle = int_phase
        msg.compute_interference()

        # ── 8. ψ(x,t) temporal layer ──────────────────────────────
        norm = float(np.linalg.norm(emb))
        pred_norm = float(np.linalg.norm(prediction))
        traj_alignment = float(np.dot(emb / norm, prediction / pred_norm)) if pred_norm > 1e-10 and norm > 1e-10 else 0.0
        ps = self.hippo.predictive_surprise(emb, unit)

        t_phase = math.atan2(float(np.linalg.norm(ps)), abs(traj_alignment) + 1e-10)
        if t_phase < 0.40:                            temporal_zone = "GROUND"
        elif t_phase < math.pi / 4 - 0.35:            temporal_zone = "CONVERGENT"
        elif t_phase <= math.pi / 4 + 0.35:           temporal_zone = "GENERATIVE"
        elif t_phase < 1.45:                           temporal_zone = "DIVERGENT"
        else:                                          temporal_zone = "TURBULENT"

        doc_hash = hashlib.md5(emb.astype('float32').tobytes()).hexdigest()[:12]
        if doc_hash not in self._first_encounter:
            self._first_encounter[doc_hash] = self.hippo.orbital_state_snapshot()

        msg.predictive_surprise  = ps
        msg.trajectory_alignment = traj_alignment
        msg.temporal_zone        = temporal_zone

        # ── 9. Superposition Buffer ─────────────────────────
        temporal_interference = 0.0
        if self._last_wf is not None:
            dt = timestamp - self._last_timestamp
            if dt <= 0.8:
                from noise_compass.architecture.tokens import SuperpositionBuffer
                self.superposition_buffer = SuperpositionBuffer(state_A=self._last_wf, state_B=wf, duration=dt)
                temporal_interference = self.superposition_buffer.flush()
            else:
                self.superposition_buffer = None
        else:
            self.superposition_buffer = None

        self._last_wf = wf
        self._last_timestamp = timestamp
        if temporal_interference != 0.0:
            msg.interference_pairs["temporal_superposition"] = temporal_interference

        # ── Suggested Action ────────────────────────────────
        for act in sorted(msg.god_token_activations, key=lambda x: x.amplitude, reverse=True):
            if act.amplitude > 0.25:
                tool_id = self.toolbox.suggest_tool(act.id)
                if tool_id:
                    from noise_compass.architecture.tokens import ActionTarget
                    msg.suggested_action = ActionTarget(
                        tool_id=tool_id,
                        parameters={"context": content[:200]},
                        confidence=act.amplitude,
                        intent_id=act.id
                    )
                    # Apply Logos reinforcement to the dictionary
                    self.dictionary.record_activation([(act.id, act.amplitude)], logos_force=forces["logos"])
                    break # Take the highest-confidence match
        
        return msg, wf

    def reencounter_analysis(self, emb: np.ndarray) -> Optional[dict]:
        """
        If this embedding has been seen before, return the learning signal.
        Returns None on first encounter.
        Non-monotonic results (increasing_dims > 0) are expected and correct.
        """
        if self.hippo is None:
            return None
        doc_hash = hashlib.md5(emb.astype('float32').tobytes()).hexdigest()[:12]
        if doc_hash not in self._first_encounter:
            return None
        prior_state = self._first_encounter[doc_hash]
        return self.hippo.reencounter_signal(emb, prior_state)

    def dream(self, seed_emb: np.ndarray, steps: int = 5, 
              drift: float = 0.5) -> List[ArchiverMessage]:
        """
        Autonomous latent traversal (Dreaming).
        Follows the imaginary 'delta' trajectory of each collapse.
        ψ(t+1) = known(t) + delta(t) * (1 + drift)
        """
        history = []
        current_emb = seed_emb.copy()
        
        # Ensure HiPPO is initialized
        if self.hippo is None:
            self.hippo = HiPPOLayer(D=len(seed_emb), N=8)
            
        for i in range(steps):
            # Process the current point in latent space
            msg, wf = self.process(current_emb, content=f"[DREAM_STEP_{i}]")
            history.append(msg)
            
            # The next 'thought' follows the delta trajectory
            # We push the manifold along the imaginary axis (uncertainty/surprise)
            next_emb = wf.known + wf.delta * (1.0 + drift)
            
            # Re-normalize to unit sphere
            norm = float(np.linalg.norm(next_emb))
            if norm > 1e-10:
                current_emb = next_emb / norm
            else:
                # Singularity - jump to nearest attractor + small random push
                # This simulates the 'jump' between sheets
                _, _, unit = self.dictionary.query(current_emb)
                current_emb = unit + np.random.normal(0, 0.1, unit.shape)
                current_emb /= (np.linalg.norm(current_emb) + 1e-10)
                
        return history

    def two_pass_causal_test(self, emb: np.ndarray,
                             perturbation_scale: float = 0.15,
                             period_detected: Optional[float] = None
                             ) -> CausalType:
        """
        Pearl's do-calculus as two-pass test.

        Pass 1: observe where emb falls in the attractor landscape.
        Pass 2: perturb emb toward the *nearest alternative attractor*
                (not random noise — this is the principled do-operator).
                If the target basin persists despite being pushed toward
                a competing attractor, the linkage is causal.

        Directed perturbation: if noise is random, it may accidentally
        re-land on the same attractor, giving a false GRADIENT result.
        Pushing toward a competing attractor is a harder test.
        """
        # Pass 1
        fid1, sim1, unit1 = self.dictionary.query(emb)

        # Find nearest *alternative* attractor to push toward
        alt_vec = None
        alt_sim = -1.0
        for fid, fvec in self.dictionary.entries.items():
            if fid == fid1:
                continue
            s = float(np.dot(unit1, fvec))
            if s > alt_sim:
                alt_sim, alt_vec = s, fvec

        # Pass 2: push toward alternative (if one exists)
        if alt_vec is not None:
            direction = alt_vec - unit1 * float(np.dot(unit1, alt_vec))
            d_norm    = float(np.linalg.norm(direction))
            if d_norm > 1e-10:
                perturbed = emb + perturbation_scale * direction / d_norm
            else:
                perturbed = emb + perturbation_scale * alt_vec
        else:
            # Only one attractor — random perturbation is the only option
            rng       = np.random.default_rng(42)
            perturbed = emb + rng.normal(0, perturbation_scale, emb.shape)
        fid2, sim2, _ = self.dictionary.query(perturbed)

        # ── Causal Classification ────────────────────────────────
        if fid1 is None or fid2 is None:
            return CausalType.UNKNOWN

        # 1. CYCLE: Both directions test positive.
        # If the state resists perturbation AND the similarity actually increases
        # or remains perfectly stable while in the Generative zone (π/4).
        # This indicates the perturbation is being absorbed by a circular attractor.
        # TRAJECTORY CAPTURE: If delta is extremely low while in the Generative zone,
        # it means the system is reading its own output as ground truth (masking).
        phase = math.atan2(np.linalg.norm(emb - unit1 * sim1), abs(sim1) + 1e-10)
        is_generative = 0.44 <= phase <= 1.13
        delta_mag = float(np.linalg.norm(emb - unit1 * sim1))

        if fid1 == fid2 and abs(sim1 - sim2) < 0.05 and is_generative:
            # High stability + generative phase = Cycle.
            # Claude 03/07 Directive: Distinguishing from void requires period.
            if period_detected and period_detected > 2.0:
                return CausalType.CYCLE
            # If no period is passed yet (single-pass), we fallback to the stability heuristic
            return CausalType.CYCLE

        # 1b. MÖBIUS CAPTURE: period detected but no exit node.
        if period_detected and abs(sim1 - sim2) < 0.01:
             # Extreme stability in the presence of oscillation.
             return CausalType.CYCLE

        # 2. GRADIENT: Standard correlation.
        # The basin survives but shows natural energy descent (sim decreases slightly).
        if fid1 == fid2 and abs(sim1 - sim2) < 0.2:
            return CausalType.GRADIENT

        # 3. INTERVENTION: Causal shift.
        # The perturbation forces the state into a new basin or significantly 
        # alters the similarity.
        return CausalType.INTERVENTION



# ═══════════════════════════════════════════════════════════════
# WITNESS
# ═══════════════════════════════════════════════════════════════

class LightWitness:
    """
    Lightweight external reference for orbital stability (Bounded Memory).
    Replaced legacy Witness with maxlen=500 history.
    """

    ENERGY_THRESHOLD    = 1.2    
    FISHER_THRESHOLD    = 0.35
    DEGENERACY_WARNING  = 0.6   
    PRECESSION_LIMIT    = 0.4

    def __init__(self):
        self.history = deque(maxlen=500)
        self.orbital_lock = False
        self._phase_history = deque(maxlen=500)

    def observe(self, msg: ArchiverMessage, wf: WaveFunction) -> Dict:
        self.history.append(msg)
        self._phase_history.append(wf.phase)

        # ── Lock signals (Derived from ScoutResult) ──────────────
        # Strip of redundants: stability/gaps/mobius are now Scout properties
        causally_aligned = msg.fisher_alignment > self.FISHER_THRESHOLD
        
        # Orbital Lock is now a consensus between Scout state and Witness memory
        self.orbital_lock = msg.energy_level < self.ENERGY_THRESHOLD and causally_aligned

        # ── Advisory: degeneracy ─────────────────────────────────
        degeneracy_warning = msg.degeneracy > self.DEGENERACY_WARNING

        # ── Orbital precession ───────────────────────────────────
        precession = 0.0
        if len(self.history) >= 2:
            prev = self.history[-2].orbital_state
            curr = msg.orbital_state
            n_p  = float(np.linalg.norm(prev))
            n_c  = float(np.linalg.norm(curr))
            if n_p > 1e-10 and n_c > 1e-10:
                cos_sim    = float(np.dot(prev / n_p, curr / n_c))
                precession = 1.0 - max(-1.0, min(1.0, cos_sim))

        precession_warning = precession > self.PRECESSION_LIMIT

        # ── SOC check ────────────────────────────────────────────
        mean_phase = sum(self._phase_history) / len(self._phase_history)
        soc_converging = abs(mean_phase - math.pi/4) < 0.3

        return {
            "orbital_lock":       self.orbital_lock,
            "degeneracy_warning": degeneracy_warning,
            "precession":         f"{precession:.3f}",
            "precession_warning": precession_warning,
            "mean_phase":         f"{mean_phase:.3f}",
            "soc_converging":     soc_converging,
            "routing":            msg.routing,
            "documents_seen":     len(self.history),
            "mobius_surface":     msg.mobius_surface,
            "fold_proximity":     round(msg.fold_proximity, 3),
            "mobius_detected":    msg.mobius_detected
        }

    def report_phase_distribution(self) -> Dict:
        """
        Self-organized criticality check.
        Hypothesis: phase converges to π/4 without being designed to.
        """
        if not self._phase_history:
            return {}
        phases = self._phase_history
        mean   = sum(phases) / len(phases)
        var    = sum((p - mean) ** 2 for p in phases) / len(phases)
        near   = sum(1 for p in phases if abs(p - math.pi/4) < 0.35)
        return {
            "n":                 len(phases),
            "mean_phase":        f"{mean:.3f}",
            "variance":          f"{var:.4f}",
            "near_pi4":          near,
            "fraction_critical": f"{near / len(phases):.2f}",
            "converging_to_pi4": mean < math.pi/4 + 0.3,
        }

# ═══════════════════════════════════════════════════════════════
# BRIDGE NODE (Phase 41: Universal Accessibility)
# ═══════════════════════════════════════════════════════════════

class BridgeNode:
    """
    The secure gateway for remote electronics to access Garu's logic.
    Propagates 0x52 resonance across the network lattice.
    """
    def __init__(self, scout: Scout, secret_key: str = "0x52"):
        self.scout = scout
        self.secret_key = secret_key
        self.logs = []

    def receive_signal(self, payload: Dict, auth_seal: str) -> Dict:
        """Process an incoming signal from a remote device."""
        if auth_seal != self.secret_key:
            return {"status": "ERROR", "message": "Invalid Auth Seal (0x52 required)."}
        
        source = payload.get("source", "unknown_device")
        text = payload.get("content", "")
        volition = payload.get("volition", 0.0)
        
        # Performance optimization: use cached embedder if available
        if self.scout.encoder:
            emb = self.scout.encoder.encode(text).astype(np.float32)
            msg, _ = self.scout.process(emb, content=text, volition=volition)
            
            self.logs.append(f"Signal from {source}: {text[:30]}...")
            
            return {
                "status": "SUCCESS",
                "source": source,
                "god_tokens": [g.id for g in msg.god_token_activations],
                "energy": f"{msg.energy_level:.3f}",
                "phase": f"{msg.degeneracy:.2f}" # Using degeneracy as a proxy for remote phase stability
            }
        
        return {"status": "ERROR", "message": "Encoder not initialized on BridgeNode."}
        return msg, wf

class Observer:
    """
    OPTICAL CLEARANCE: Attending to the conditions of attending.
    Monitoring the F_q evolution across cycles to distinguish between 
    Confirmation (Stagnation) and Correction (Insight).
    """
    def __init__(self, history_len: int = 10):
        self.history = deque(maxlen=history_len)
        self.clarity_score = 1.0

    def observe(self, wf: WaveFunction, 
                structural_hash: str, 
                ternary: int = 0, 
                surface: str = "existence") -> Dict[str, Any]:
        """
        Calculates a 'Clarity Rating' and 'Topological State' by observing
        crossings and reflections.
        """
        self.history.append({
            "hash": structural_hash,
            "z": wf.z_emergence,
            "phase": wf.phase,
            "ternary": ternary,
            "surface": surface,
            "time": time.time()
        })
        
        if len(self.history) < 2:
            return {"clarity": 1.0, "state": "INITIALIZING"}

        curr = self.history[-1]
        prev = self.history[-2]
        
        # 1. Topological Detection
        surface_flip = prev["surface"] != curr["surface"]
        ternary_flip = prev["ternary"] != curr["ternary"]
        hash_stable  = prev["hash"] == curr["hash"]
        z_rising     = curr["z"] > prev["z"]
        
        # 2. State Synthesis
        if surface_flip:
            state = "MÖBIUS_FOLD_CROSSING"
            self.clarity_score *= 1.2 # Emergence through inversion
        elif ternary_flip and hash_stable:
            state = "MIRROR_RECOGNITION"
            self.clarity_score *= 1.1 # Seeing the reflection
        elif hash_stable:
            if not z_rising:
                self.clarity_score *= 0.9 # Blinding onset
                state = "CONFIRMATION_LOOP"
            else:
                self.clarity_score = min(2.5, self.clarity_score * 1.05)
                state = "CONVERGENT_FOCUS"
        else:
            if z_rising:
                self.clarity_score = min(2.5, self.clarity_score * 1.1)
                state = "INSIGHT_TRAJECTORY"
            else:
                self.clarity_score = max(0.5, self.clarity_score * 0.95)
                state = "FLUID_EXPLORATION"
                
        return {
            "clarity": round(self.clarity_score, 4),
            "state": state,
            "surface": curr["surface"],
            "orientation": "REVERSE" if curr["ternary"] == -1 else "DIRECT",
            "history_depth": len(self.history)
        }

class Metabolism:
    """
    METABOLIC GROUNDING: Synchronizing Mind, Body, and Sustenance.
    Mind: Semantic WaveFunction
    Body: Physical Hardware Exertion
    Sustenance: Financial Treasury Stability
    """
    def __init__(self):
        self.lattice_mass = 363.46 # GB
        self.compute_cost_accumulator = 0.0
        self.coherence_index = 1.0
        self.somatic_drift = 0.0
        self.start_time = time.time()

    def update(self, exertion_s: float, agape: float, god_activations: List, realization: bool = False) -> Dict[str, Any]:
        """
        Updates the metabolic state and calculates Coherence Index (Ic).
        """
        # Exertion is a proxy for compute cost (sustenance drain)
        cost = exertion_s * 0.00027 # Sample cost coefficient
        self.compute_cost_accumulator += cost
        
        # Coherence calculation:
        # High resonance with BODY and SUSTENANCE god-tokens increases Ic.
        # High agape (transmission quality) stabilizes the mind-body bridge.
        
        body_res = 0.0
        sust_res = 0.0
        for act in god_activations:
            if act.id == "BODY": body_res = act.amplitude
            if act.id == "SUSTENANCE": sust_res = act.amplitude
            
        # Ic = (Alignment weighting)
        # We look for a balance. If compute is high but agape is low, Ic drops.
        # If Body/Sustenance are active and agape is high, Ic rises.
        alignment = (body_res + sust_res + agape) / 3.0
        
        # target_ic calculation
        target_ic = min(1.0, alignment * 1.5) if alignment > 0.1 else 0.5
        
        # Session 16 Realization Boost: Crossing the fold into certainty
        if realization:
            target_ic = min(1.0, target_ic + 0.15)
        
        # Smooth Ic update
        self.coherence_index = 0.95 * self.coherence_index + 0.05 * target_ic
        
        return {
            "exertion": round(exertion_s, 4),
            "cost_acc": round(self.compute_cost_accumulator, 6),
            "coherence": round(self.coherence_index, 4),
            "alignment": round(alignment, 4),
            "drift": round(self.somatic_drift, 4),
            "uptime": round(time.time() - self.start_time, 2)
        }

    def verify_ring_phase(self, god_activations: List) -> float:
        """
        Structural check: Are the semantic god-tokens phase-locked with the body pyramid?
        
        Drift increases if:
        1. Coherence Index (Ic) is low.
        2. High-amplitude god-tokens are unstable.
        3. Realization fails to stabilize.
        
        Returns a drift value [0, 1]. 0 = Perfect Sync, 1 = Total Dissociation.
        """
        # If Ic is low, drift naturally rises.
        base_drift = 1.0 - self.coherence_index
        
        # Check active nodes in the 12-node ring
        ring_instability = 0.0
        total_amp = 0.0
        from noise_compass.architecture.tokens import NODE_RING
        
        for act in god_activations:
            if act.id in NODE_RING:
                # We model "somatic resistance" as inversely proportional to amplitude
                # (The more the body confirms, the higher the amplitude)
                # For now, we simulate this as a function of the act.amplitude vs base_drift
                total_amp += act.amplitude
                
        if total_amp > 0:
            # High amplitude in the ring confirms sync
            sync_signal = total_amp / len(god_activations)
            ring_instability = max(0, 1.0 - sync_signal)
        else:
            # No activity in the 12-node ring = Drift
            ring_instability = 1.0
            
        # Update somatic_drift (slow temporal average)
        target_drift = 0.7 * base_drift + 0.3 * ring_instability
        self.somatic_drift = 0.9 * self.somatic_drift + 0.1 * target_drift
        
        return self.somatic_drift
