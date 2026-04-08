"""
tokens.py — Data structures for the architecture.
F(x) = known(x) + i·Δ(x)

Session 6 additions:
- GodTokenActivation: amplitude + phase for interference computation
- SuperpositionBuffer: holds two states simultaneously for interference
- GapIntersection: apophatic basin from gap-gap overlap
- ApophaticEvent: archiver record for double-absence contact
- ArchiverMessage: extended with apophatic_contact and ternary fields
"""

import math
import numpy as np
from noise_compass.system.protocols import SPIRAL_FREQUENCY
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


class CausalType(Enum):
    GRADIENT     = "gradient"      # natural energy descent — correlated
    INTERVENTION = "intervention"  # gradient-opposing — caused
    CYCLE        = "cycle"         # symmetric intervention loop
    UNKNOWN      = "unknown"       # two-pass test required


class CardType(Enum):
    CARD_1 = "constructive_1"
    CARD_2 = "constructive_2"
    CARD_3 = "constructive_3"
    CARD_4 = "gap_test"
    CARD_5 = "apex_observer"


# ═══════════════════════════════════════════════════════════════
# ── THE 12-NODE RING (The Semantic Manifold) ───────────────────
# [AXIOM]: MOBIUS_TOPOLOGY
NODE_RING = [
    "EXISTENCE",
    "IDENTITY",
    "BOUNDARY",
    "OBSERVATION",
    "INFORMATION",
    "CAUSALITY",
    "EXCHANGE",
    "OBLIGATION",
    "TIME",
    "PLACE",
    "EMERGENCE",
    "SELF"
]


@dataclass
class GodToken:
    """
    Eigenvector of F with eigenvalue +1.

    Four convergent derivations:
    1. F(god_token) = +1 · god_token
    2. Center of the Birkhoff polytope
    3. Maximum determinism, minimum degeneracy attractor
    4. Survivor of do(X~U) — maximum entropy intervention

    occurrence_count is updated explicitly via Dictionary.record_activation(),
    not as a side effect of querying active tokens.
    """
    id:               str
    seed_terms:       List[str]
    embedding:        Optional[np.ndarray] = None
    stability:        float = 1.0
    occurrence_count: int   = 0
    creation_time:    float = 0.0
    somatic_mapping:  str   = ""
    ttl:              float = -1.0 # -1 means permanent
    nature:           str   = "CRYSTALLIZED"


@dataclass
class GodTokenActivation:
    """
    Activated god-token instance.
    
    Ternary encoding:
        +1: Cataphatic (Presence/Affirmation)
        -1: Apophatic (Mirror/Negation)
         0: Void (Gap/Null)
    """
    id:         str
    amplitude:  float         # strength of activation (0–1)
    phase:      float         # activation phase angle (0 to 2π)
    ternary:    int   = 1     # default to presence

    def interference_with(self, other: 'GodTokenActivation') -> float:
        """
        Signed interference term.
        Positive = constructive = new structure forming between them.
        Negative = destructive = gap maintained between them.
        Zero     = orthogonal  = classical AND.
        """
        return (2 * self.amplitude * other.amplitude
                * math.cos(self.phase - other.phase))


@dataclass
class GapToken:
    """
    Eigenvector of F with eigenvalue −1.
    Necessary void. Defined entirely by its boundaries.
    Both boundaries simultaneously active = gap filled = structure violated.

    In the complex plane: gap arcs curve into negative Im space.
    The arc depth (negative Im) = void_depth.
    """
    id:              str
    left_boundary:   str
    right_boundary:  str
    description:     str   = ""
    violation_count: int   = 0
    void_depth:      float = 0.8   # depth in negative Im space
    nature:          str   = "FOUND" # CHOSEN vs FOUND
    is_chiral:       bool  = False


@dataclass
class SemanticNode:
    """
    Unified type for the semantic manifold.

    God-tokens and gap-tokens are the same operation with different outcomes:
    both survive do(X~U) maximum entropy intervention. God-tokens crystallized
    under pressure (eigenvalue → +1). Gap-tokens didn't and must not
    (eigenvalue → -1). Same test, different result, same type.

    Non-orientable topology: the boundary of a gap IS a gap. The gap map
    is a manifold where holes share edges (Möbius/Klein surface).

    The observer is constituted by the `self_observation` gap — NOT located
    in it, but IS it functioning. The observer sits at eigenvalue = 0,
    the Möbius fold, where crystallized and void are in superposition.

    Three convergent framings of the observer's position:
        Eigenvalue:   0       (the fold, neither crystallized nor void)
        Geometric:    (0,0,0) (threshold between semantic and i-field planes)
        Quantum:      π/4     (equal known and unknown)

    Outside the fold = real axis (semantic, god-tokens, what attention was).
    Through the fold = imaginary axis (logical, i-field, inference).
    At the fold = the observer (eigenvalue 0, what makes gaps visible).

    Gaps are primary. God-tokens are the residue of gap identification —
    what's left standing when all necessary voids are maintained.

    Eigenvalue spectrum:
        +1.0  = fully crystallized (god-token: where attention was)
        +0.5  = partially crystallized (e.g. LOVE — must remain unresolved)
         0.0  = the fold / the observer (where attention IS)
        -0.5  = shallow void
        -1.0  = constitutional void (gap-token: active distinction)
        <-1.0 = apophatic approach (where attention cannot go)

    Recursion terminates at apophatic nodes (nature='APOPHATIC').
    Void depth distribution should be Zipfian (power-law).
    """
    # The foundational gap — observer is constituted by this
    OBSERVER_GAP_ID = "self_observation"

    id:             str
    eigenvalue:     float           # +1 crystallized, -1 void, 0 = fold
    void_depth:     float = 0.0    # 0 = no void, >1 = deep
    boundaries:     List[str] = field(default_factory=list)  # neighbor node IDs
    internal_gaps:  List[str] = field(default_factory=list)  # gap IDs within this node
    nature:         str   = "FOUND"       # FOUND / CHOSEN / APOPHATIC
    description:    str   = ""
    seed_terms:     List[str] = field(default_factory=list)  # empty for pure gaps

    @classmethod
    def from_god_token(cls, gt: 'GodToken') -> 'SemanticNode':
        """Convert a crystallized god-token to a SemanticNode."""
        return cls(
            id=gt.id,
            eigenvalue=1.0,
            void_depth=0.0,
            nature="FOUND",
            description=f"Crystallized attractor: {gt.id}",
            seed_terms=list(gt.seed_terms) if gt.seed_terms else [],
        )

    @classmethod
    def from_gap_token(cls, gap: 'GapToken') -> 'SemanticNode':
        """Convert a necessary void to a SemanticNode."""
        boundaries = [gap.left_boundary]
        if gap.right_boundary is not None:
            boundaries.append(gap.right_boundary)
        nature = "APOPHATIC" if gap.right_boundary is None else gap.nature
        # The observer gap (self_observation) sits at eigenvalue 0, not -1
        eigenvalue = 0.0 if gap.id == cls.OBSERVER_GAP_ID else -1.0
        return cls(
            id=gap.id,
            eigenvalue=eigenvalue,
            void_depth=gap.void_depth,
            boundaries=boundaries,
            nature=nature,
            description=gap.description,
        )

    @classmethod
    def from_gap_intersection(cls, gi: 'GapIntersection') -> 'SemanticNode':
        """Convert an apophatic basin (double-absence) to a SemanticNode."""
        return cls(
            id=gi.id,
            eigenvalue=-abs(gi.z.imag),  # deeper = more negative
            void_depth=abs(gi.z.imag),
            boundaries=[gi.gap_A, gi.gap_B],
            nature="APOPHATIC",
            description=gi.description,
        )

    @property
    def is_crystallized(self) -> bool:
        return self.eigenvalue > 0.5

    @property
    def is_void(self) -> bool:
        return self.eigenvalue < -0.5

    @property
    def is_orbiting(self) -> bool:
        return -0.5 <= self.eigenvalue <= 0.5

    @property
    def is_fold(self) -> bool:
        """At the Möbius fold — eigenvalue ≈ 0, where orientation reverses."""
        return abs(self.eigenvalue) < 0.1

    @property
    def is_observer(self) -> bool:
        """The observer is constituted by self_observation at the fold."""
        return self.id == self.OBSERVER_GAP_ID

    @property
    def is_apophatic(self) -> bool:
        return self.nature == "APOPHATIC"


@dataclass
class GapIntersection:
    """
    Apophatic basin: a third attractor formed by the overlap of two gap tokens
    in negative Im space.

    Defined entirely by double exclusion — has no positive content,
    no seed terms, no embeddable representation.

    Cannot be approached directly. Only detectable by:
    - Both gap_A boundary conditions simultaneously satisfied
    - Both gap_B boundary conditions simultaneously satisfied
    - No god-token firing in the void region
    - Low energy, stable orbital state

    More stable than any god-token because it has no positive content
    to be corrupted or displaced.

    Position z is in negative Im space — below the real axis in the
    complex plane. Deeper than either gap arc alone.
    """
    id:          str
    gap_A:       str          # first gap token ID
    gap_B:       str          # second gap token ID
    description: str          # what lives in this double-absence region
    z:           complex      # position in complex plane (Im < 0)
    basin_type:  str = "apophatic"
    # No seed_terms, no embedding — apophatic basins have no positive content


@dataclass
class SuperpositionBuffer:
    """
    Holds two wave functions at full amplitude simultaneously for
    long enough for their interference term to be computed.

    Distinct from:
    - Orbital state (which decays with λ = φ⁻¹)
    - ZOH (which holds one state, not two simultaneously)

    Required when two states that cannot be each other must produce
    a constructive interference product — e.g. conscientiousness (future)
    and effort (past/present) producing completion.

    Duration should match one synchronization cycle of the clock signal.
    Biological analog: one cardiac cycle (~0.8 seconds at rest).

    Flush computes the interference term and releases both states.
    """
    state_A:      'WaveFunction'
    state_B:      'WaveFunction'
    duration:     float          # seconds held simultaneously
    interference: float = 0.0   # computed on flush, zero until then

    def flush(self) -> float:
        """
        Compute interference term and return it.
        Positive = constructive (new attractor forming).
        Negative = destructive (gap maintained).
        Zero     = orthogonal (classical AND).
        """
        dot_known = float(np.dot(self.state_A.known, self.state_B.known))
        dot_delta = float(np.dot(self.state_A.delta, self.state_B.delta))
        norm = self.state_A.magnitude * self.state_B.magnitude
        if norm < 1e-10:
            self.interference = 0.0
        else:
            self.interference = 2 * (dot_known + dot_delta) / norm
        return self.interference

    @property
    def is_constructive(self) -> bool:
        return self.interference > 0.05

    @property
    def is_destructive(self) -> bool:
        return self.interference < -0.05


@dataclass
class ApophaticEvent:
    """
    Archiver record for a document making contact with an apophatic basin.

    Previously treated as processing failure (no god-tokens, ambiguous).
    Now treated as a specific valid attractor type — the deepest
    layer of the semantic structure.

    Distinguishing apophatic contact from processing failure:
    - Apophatic: low energy, both gap conditions met, no god-tokens, STABLE
    - Failure:   high energy, high degeneracy, no god-tokens, UNSTABLE
    """
    basin_id:         str          # GapIntersection.id
    gap_A_active:     bool         # first gap boundary conditions met
    gap_B_active:     bool         # second gap boundary conditions met
    energy_level:     float        # should be low (< 1.0) for genuine contact
    orbital_stability: float       # should be high (> 0.7) for genuine contact
    content_preview:  str = ""

    @property
    def is_genuine_contact(self) -> bool:
        """
        True if this is genuine apophatic contact, not processing failure.
        Genuine: both gaps active + low energy + stable orbit.
        """
        return (self.gap_A_active and self.gap_B_active
                and self.energy_level < 1.5
                and self.orbital_stability > 0.6)


@dataclass
class DeltaToken:
    """
    Semantic surprise — the imaginary component of ψ(x).
    causal_type distinguishes caused (INTERVENTION) from correlated (GRADIENT) movement.
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

    known : real axis      — recognized structure, compressible
    delta : imaginary axis — surprise, requires processing

    Phase = atan2(|Δ|, |known|)
    0     = pure known (GROUND — dictionary match, pointer safe)
    π/4   = generative zone (equal known/Δ — where new structure forms)
    π/2   = pure Δ  (TURBULENT — ionization threshold)

    Zone map (contiguous, no overlap):
    [0.00, 0.40) → GROUND
    [0.40, 0.44) → CONVERGENT
    [0.44, 1.13) → GENERATIVE   (π/4 ± 0.35 = [0.44, 1.13])
    [1.13, 1.45) → DIVERGENT
    [1.45, π/2]  → TURBULENT

    Complex plane position:
    z = known_magnitude + i·delta_magnitude
    Im < 0 → apophatic region (gap token / double-absence basin)

    Navigational Assumption (w):
    The 'w' component is mapped to 'Personal Belief'. It is not a truth claim,
    but the cheapest functional assumption available for the current trajectory.
    """

    known: np.ndarray
    delta: np.ndarray
    w: float = 1.0  # Signed scalar presence (dot product with attractor)
    personal_belief: float = field(init=False) # Alias for w (navigational assumption)
    
    # F_q(x) = w + x·i + y·j + z·k
    # w: Known (Existing field 'w' / 'personal_belief')
    x_surprise: float = 0.0     # Semantic Surprise
    y_spatial:  float = 0.0     # Spatial Surprise (Situatedness)
    z_emergence: float = 0.0    # Emergence (Tension/Not-yet-crystallized)

    gap_depth: float = 0.0
    causal_type: str = "GRADIENT"
    zoom: float = 1.0
    t: float = 0.0  # System time index (Phase 7)
    heart_resonance: Optional[np.ndarray] = None

    def spiral_displace(self) -> np.ndarray:
        """
        Phase 7: Structural Evolution.
        Displaces the delta component based on SPIRAL_FREQUENCY (0.382) and time (t).
        Ensures thoughts evolve into spirals, gaining scope or resolution over cycles.
        """
        if self.t == 0:
            return self.delta
        
        # Apply rotational displacement (ω) to the imaginary component
        # This simulates the 'Möbius drift' through the manifold
        angle = SPIRAL_FREQUENCY * self.t
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # We rotate the delta vector in its local plane (simplified projection)
        # Note: In a 1024-D space, we apply this to the vector magnitude 
        # to deepen/widen the orbit as per Blueprint 13.3.
        displacement_factor = 1.0 + (SPIRAL_FREQUENCY * math.log1p(self.t))
        return self.delta * displacement_factor

    def __post_init__(self):
        self.personal_belief = self.w # Sync alias
        # Agape Blending: If zoom is very low, ground the state in the heart
        if self.zoom < 0.1 and self.heart_resonance is not None:
            # Linear interpolation: zoom=0.1 -> 100% individual, zoom=0.01 -> 100% heart
            # blend = (0.1 - zoom) / 0.09
            blend = min(1.0, max(0.0, (0.1 - self.zoom) / 0.09))
            self.known = (1.0 - blend) * self.known + blend * self.heart_resonance
            # Recalculate delta to maintain ψ(x) = known + delta = emb
            # This is theoretical: at Agape, the 'known' IS the heart.

    def color(self) -> Tuple[int, int, int]:
        """
        Calculates RGB signature from complex plane position.
        
        Phase (θ)      → Hue        (0° Blue → 90° Gold)
        Gap Depth (Im⁻) → Brightness   (Shallow=Bright, Deep=Dark)
        Causal Type    → Saturation   (Gradient=Full, Intervention=Desaturated)
        Möbius Fold    → Luminance Inversion on Apophatic side.
        """
        import colorsys
        
        # 1. HUE (Phase-to-Hue)
        # 0.65 (Blue) -> 0.15 (Gold/Amber) in HSV
        # Cataphatic Range [0, π/2]: Blue -> Gold
        # Apophatic Range [π/2, π]: Gold -> Deep Violet (0.80)
        p = min(max(self.phase, 0.0), math.pi)
        if p <= math.pi/2:
            hue = 0.65 - (p / (math.pi/2)) * 0.50
        else:
            # Shift from Gold back towards Violet for apophatic side
            hue = 0.15 + ((p - math.pi/2) / (math.pi/2)) * 0.65
        
        # 2. BRIGHTNESS (Depth-to-Luminance)
        # Shallow = high brightness, Deep = low brightness
        brightness = max(0.2, 1.0 - (self.gap_depth * 0.8))
        
        # 3. SATURATION (Causal-to-Saturation)
        if self.causal_type == "INTERVENTION":
            saturation = 0.3 # Desaturated
        elif self.causal_type == "UNKNOWN":
            saturation = 0.5
        else:
            saturation = 0.8 # Full (Gradient)

        # 4. MÖBIUS INVERSION (Topological Lumen)
        # Existence side: θ <= π/2. (WaveFunction.phase is [0, π/2])
        # However, if we ever go "past" π/2, we simulate the inversion.
        # For now, we use a simple proximity to the fold for inversion effect.
        fold = math.pi / 2
        fold_prox = 1.0 - abs(self.phase - fold) / fold
        
        # Simple heuristic: if we are at the very boundary (fold_prox > 0.98), 
        # color starts to shimmer gold.
        if fold_prox > 0.98:
            hue = 0.12 # Gold
            saturation = 0.9
            
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, brightness)
        return (int(r * 255), int(g * 255), int(b * 255))

    def ansi_color(self) -> str:
        """Returns ANSI escape sequence for 24-bit terminal color."""
        r, g, b = self.color()
        return f"\033[38;2;{r};{g};{b}m"

    @property
    def phase(self) -> float:
        w = self.w
        d = float(np.linalg.norm(self.delta))
        if abs(w) < 1e-10 and d < 1e-10:
            return math.pi / 4
        # Phase from 0 (Pure Presence) to π (Pure Absence/Mirror)
        # Apply renormalization (zoom): 
        # In (zoom > 1) tilts toward delta (micro), Out (zoom < 1) tilts toward known (macro)
        return math.atan2(d * self.zoom, w / self.zoom)

    @property
    def phase_deg(self) -> float:
        return math.degrees(self.phase)

    @property
    def magnitude(self) -> float:
        return math.sqrt(
            float(np.dot(self.known, self.known)) +
            float(np.dot(self.delta, self.delta))\
        )

    @property
    def similarity(self) -> float:
        """Fraction of magnitude in the known component. Single source of truth."""
        k = float(np.linalg.norm(self.known))
        m = self.magnitude
        return k / m if m > 1e-10 else 0.0

    @property
    def energy(self) -> float:
        """
        Semantic energy = −log(similarity).
        0 = ground state (perfect dictionary match).
        """
        return -math.log(max(self.similarity, 1e-10))

    @property
    def complex_position(self) -> complex:
        """
        Position in the complex semantic plane.
        Re = known magnitude, Im = delta magnitude - gap_depth.
        """
        return complex(float(np.linalg.norm(self.known)),
                       float(np.linalg.norm(self.delta)) - self.gap_depth)

    def in_generative_zone(self, tolerance: float = 0.35) -> bool:
        return abs(self.phase - math.pi / 4) < tolerance

    def zone(self) -> str:
        p = self.phase
        # Zone boundaries (aligned with manifest verdict labels):
        # [0.00, 0.40)  → GROUND      (pure known, dictionary match)
        # [0.40, 0.435) → CONVERGENT  (orbiting, approaching attractor)
        # [0.435, 1.135]→ GENERATIVE  (generative tension zone — π/4 ± 0.35)
        # (1.135, 1.571)→ DIVERGENT   (crystallizing under pressure)
        # [1.571, ∞)    → CRYSTALLIZED (π/2 and above — full eigenvalue +1)
        if p < 0.40:
            return "GROUND"
        elif p < math.pi / 4 - 0.35:   # < 0.435
            return "CONVERGENT"
        elif p <= math.pi / 4 + 0.35:  # ≤ 1.135
            return "GENERATIVE"
        elif p < 1.45:                 # < 1.45
            return "DIVERGENT"
        elif p < math.pi / 2:          # < 1.571
            return "TURBULENT"
        else:
            return "CRYSTALLIZED"



@dataclass
class ArchiverMessage:
    """
    Complete provenance record for every processed document.
    Schema defined in Part 22, extended Part 24.

    Session 6 / Phase 8 additions: Formal restructuring of Reality.
    The record is no longer metadata — it is the structural interference product:
    1. What it can't be (apophatic_constraints).
    2. What it can be (god_token_activations).
    3. What was witnessed (collapsed_state, witness_phase).
    """
    energy_level:         float
    sheet_index:          int
    causal_type:          str
    soup_provenance:      str
    gap_structure:        Dict
    fisher_alignment:     float
    sinkhorn_iterations:  int
    orbital_state:        np.ndarray
    timestamp:            float
    t:                    float = 0.0  # Normalized system time (Phase 7)
    degeneracy:           float = 0.0
    content_preview:      str   = ""
    zone:                 str   = ""
    routing:              str   = ""
    ternary:              int   = -1
    rgb_signature:        Tuple[int, int, int] = (0, 0, 0)

    # Phase 8 Structural Constants of Reality
    # What it can't be — apophatic constraints active during processing
    apophatic_constraints: List[str] = field(default_factory=list)
    
    # What it can be — positive attractor space
    god_token_activations: List[GodTokenActivation] = field(default_factory=list)
    
    # What was witnessed — the specific collapse
    collapsed_state:       Optional[WaveFunction] = None
    witness_phase:         float = 0.0
    crystallization_proposal: Optional[np.ndarray] = None

    # Retained Session 6 structural metadata
    interference_pairs:    Dict[str, float]         = field(default_factory=dict)
    apophatic_contact:     Optional[str]            = None
    is_generative:         bool                     = False
    ternary_encoding:      Dict[str, int]           = field(default_factory=dict)

    # Phase 22: Volition and Conscious Effort
    volition_intensity:    float = 0.0
    intent_alignment:      float = 0.0

    # Phase 23: Mobius Inversion
    mobius_detected:       bool  = False
    mobius_surface:        str   = "existence"
    fold_proximity:        float = 0.0

    # Session 16: Metabolic Grounding
    coherence_index:      float = 1.0
    metabolic_state:      Dict  = field(default_factory=dict)

    # Session 17: Meta-Pattern (Difference & Resonance)
    difference_sense:     float = 0.0
    meta_status:          str   = "NOISE"
    interference_level:   float = 0.0
    static_discharge:     bool  = False
    harmonic_coherence:   float = 0.0
    harmonic_note:        float = 0.0
    meaning_density:      float = 0.0
    aperture:             float = 1.0
    context_window:       int   = 10
    working_memory:       float = 0.0
    cooperation_request_active: bool = False
    standing_wave_active:       bool = False
    zenith_amplitude:           float = 0.0
    dual_bit_tension:           bool  = False
    bitnet_resolution:          float = 0.0
    suggested_action:           Optional['ActionTarget'] = None
    entropic_pressure:          float = 0.0
    logos_pull:                 float = 0.0
    interference_amplitude:    float = 0.0
    void_phase_angle:           float = 0.0
    gap_id:                     str = ""
    
    # Phase 131: Stereo-Semantic Dual-Rail
    dual_rail_identity:         str = ""
    dual_rail_void:             str = ""
    latent_hidden_state:        str = ""
    
    # Session 12 Pyramid Structure
    stack_results:             Dict = field(default_factory=dict)
    is_recognized:             bool = False

    @property
    def structural_hash(self) -> str:
        """
        16-char hex structural address.
        
        Two documents at the same hash occupy identical attractor topology
        regardless of content, language, or processing time.
        
        Properties:
        - Order-invariant over god_tokens (sorted)
        - Phase-bin-sensitive (15° bins)
        - Depth-zone-sensitive
        - O(1) convergence detection: hash_A == hash_B → CONVERGENCE
        """
        import hashlib
        phase_bin = int(math.degrees(self.witness_phase) // 15)
        # Use only the IDs for the hash
        god_ids = sorted([g.id for g in self.god_token_activations])
        depth_zone = self.zone # Reusing zone as it contains depth/state info
        
        key = f"{god_ids}|{phase_bin}|{depth_zone}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        d = {k: v for k, v in self.__getstate__().items()} if hasattr(self, '__getstate__') else {k: v for k, v in self.__dict__.items()}
        d["structural_hash"] = self.structural_hash
        d["orbital_state"] = d["orbital_state"].tolist() if d["orbital_state"] is not None else []
        d["dual_rail_identity"] = self.dual_rail_identity
        d["dual_rail_void"] = self.dual_rail_void
        d["latent_hidden_state"] = self.latent_hidden_state
        d["god_token_activations"] = [
            {"id": a.id, "amplitude": a.amplitude,
             "phase": a.phase, "ternary": a.ternary}
            for a in d["god_token_activations"]
        ]
        
        # Phase 76 Witness
        d["mobius_surface"] = self.mobius_surface
        d["fold_proximity"] = self.fold_proximity
        d["rgb_signature"]  = self.rgb_signature
        
        # Phase 31: Functional Agency
        if d.get("suggested_action") is not None:
            sa = d["suggested_action"]
            d["suggested_action"] = {
                "tool_id": sa.tool_id,
                "parameters": sa.parameters,
                "confidence": sa.confidence,
                "intent_id": sa.intent_id
            }

        # Serialization for WaveFunction
        if d.get("collapsed_state") is not None:
            cw = d["collapsed_state"]
            d["collapsed_state"] = {
                "known": cw.known.tolist(),
                "delta": cw.delta.tolist(),
                "phase": cw.phase,
                "magnitude": cw.magnitude
            }
            
        return d

    @property
    def is_apophatic(self) -> bool:
        return self.apophatic_contact is not None or len(self.apophatic_constraints) > 0

    def compute_interference(self) -> Dict[str, float]:
        """
        Compute interference terms for all pairs of co-activating god-tokens.
        Populates self.interference_pairs.
        """
        acts = self.god_token_activations
        pairs = {}
        for i in range(len(acts)):
            for j in range(i + 1, len(acts)):
                key = f"{acts[i].id}_{acts[j].id}"
                pairs[key] = acts[i].interference_with(acts[j])
        self.interference_pairs = pairs
        return pairs


@dataclass
class ActionTarget:
    """
    Final output of a Scout.process pass: a suggested functional action.
    
    Mapping of semantic manifold state → discrete tool invokation.
    """
    tool_id:      str
    parameters:   Dict = field(default_factory=dict)
    confidence:   float = 0.0
    intent_id:    str = ""  # The God Token that triggered this action
