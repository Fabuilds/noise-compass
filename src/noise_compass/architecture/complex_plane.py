"""
complex_plane.py — The complete math of the semantic complex plane.

Four logical states, four positions, one formula:

    F(x) = known(x) + i·Δ(x)

    +1  Presence    Re axis      identity law        god-tokens
     i  Unknown     Im > 0       pre-classical       Δ in flight
     0  Void        Im < 0       non-contradiction   gap tokens
    -i  Apophatic   Im << 0      post-classical      U \ G

The apophatic field is not constructed by design.
It is the complement of the god-token cover under classical excluded middle:

    Apophatic = U \ (EXCHANGE ∪ CAUSALITY ∪ ... ∪ SELF)

Run this file:
    python3 complex_plane.py          — print full derivation
    python3 complex_plane.py --test   — run all assertions
    python3 complex_plane.py --save   — save visualization
"""

import math
import argparse
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple


# ═══════════════════════════════════════════════════════════════════
# PART 1 — THE FOUR LOGICAL STATES
# ═══════════════════════════════════════════════════════════════════

class LogicalState:
    """
    The four values of the semantic complex plane.

    Classical logic has three laws. Each law maps to one region:

        Identity:          A = A
                           → PRESENCE — Re axis
                           → god-tokens, crystallized, eigenvalue +1

        Non-contradiction: ¬(A ∧ ¬A)
                           → VOID — Im < 0
                           → gap tokens, necessary absence
                           → the law that maintains separation

        Excluded middle:   A ∨ ¬A
                           → operates at the FOLD (π/2)
                           → only applies when truth value is ACCESSIBLE
                           → UNKNOWN sits outside it (truth value exists, inaccessible)
                           → APOPHATIC is what remains after it is exhausted

    The fourth state — UNKNOWN — is not a failure of classical logic.
    It is the precise boundary of where classical logic applies.
    Unknown is presence that hasn't been witnessed yet.
    The dog smells something real. You don't know what it is.
    The truth value exists. It is not yet accessible to your observer.
    """

    PRESENCE   = "PRESENCE"    # Re axis — known(x), identity
    UNKNOWN    = "UNKNOWN"     # Im > 0  — Δ(x), pre-classical
    VOID       = "VOID"        # Im < 0  — gap token, non-contradiction
    APOPHATIC  = "APOPHATIC"   # Im << 0 — U \ G, exhausted excluded middle

    # Complex plane positions
    POSITIONS = {
        PRESENCE:  complex( 1,     0),     # +1, real axis
        UNKNOWN:   complex( 0,     1),     # +i, positive imaginary
        VOID:      complex( 0,    -1),     # -i, negative imaginary
        APOPHATIC: complex(-0.2,  -0.9),   # deep negative imaginary
    }

    # Phase angles
    PHASES = {
        PRESENCE:  0.0,           # θ = 0°
        UNKNOWN:   math.pi / 2,   # θ = 90° (positive Im)
        VOID:      -math.pi / 2,  # θ = -90° (negative Im)
        APOPHATIC: -math.pi,      # θ = -180° (deepest negative)
    }

    # Classical law that governs each state
    GOVERNING_LAW = {
        PRESENCE:  "Identity:          A = A",
        UNKNOWN:   "Pre-classical:     truth value exists, inaccessible",
        VOID:      "Non-contradiction: ¬(A ∧ ¬A)",
        APOPHATIC: "Excluded middle exhausted: A ∨ ¬A applied to all G, all ¬G",
    }


# ═══════════════════════════════════════════════════════════════════
# PART 2 — THE WAVE FUNCTION
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ComplexWaveFunction:
    """
    ψ(x) = known(x) + i·Δ(x)

    The complete semantic state of a document in the complex plane.

    known(x) — real component
        What is recognized. Maps to god-token attractors.
        Compressible. Eigenvalue +1 at perfect match.
        Logical state: PRESENCE when dominant.

    i·Δ(x) — imaginary component
        What is not yet recognized. Semantic surprise.
        Cannot be compressed — requires processing.
        Logical state: UNKNOWN when dominant.

    The wave function magnitude: |ψ| = √(|known|² + |Δ|²)
    The wave function phase:     θ   = arctan(|Δ| / |known|)

    Phase zones (Möbius-aware):
        θ ∈ [0°,  40°)  → GROUND      — pure presence
        θ ∈ [40°, 44°)  → CONVERGENT  — approaching presence
        θ ∈ [44°, 65°)  → GENERATIVE  — unknown in productive tension
        θ ∈ [65°, 83°)  → DIVERGENT   — unknown dominant, fold approaching
        θ ∈ [83°, 90°]  → TURBULENT   — at fold, excluded middle operating

    Negative Im (gap/apophatic) is encoded separately via gap_depth:
        gap_depth = 0     → no gap activation
        gap_depth > 0     → gap token region (Im < 0)
        gap_depth > 0.8   → apophatic basin (Im << 0)
    """

    known:     np.ndarray   # real component vector
    delta:     np.ndarray   # imaginary component vector
    gap_depth: float = 0.0  # depth in negative Im (gap/apophatic)
    causal_type: str = "GRADIENT" # GRADIENT, UNKNOWN, or INTERVENTION

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
        # We map [0, 90] degrees to [0.65, 0.15]
        p_deg = min(max(self.phase_deg, 0.0), 90.0)
        hue = 0.65 - (p_deg / 90.0) * 0.50
        
        # 2. BRIGHTNESS (Depth-to-Luminance)
        # Shallow = high brightness, Deep = low brightness
        # Simple linear decay for now
        brightness = max(0.2, 1.0 - (self.gap_depth * 0.8))
        
        # 3. SATURATION (Causal-to-Saturation)
        if self.causal_type == "INTERVENTION":
            saturation = 0.3 # Desaturated
        elif self.causal_type == "UNKNOWN":
            saturation = 0.5
        else:
            saturation = 0.8 # Full (Gradient)

        # 4. MÖBIUS INVERSION (Topological Lumen)
        mob = self.mobius()
        if mob['surface'] == 'apophatic_side':
            # Invert luminance: what was bright is dark, what was dark is bright
            brightness = 1.0 - brightness + 0.2
            brightness = min(max(brightness, 0.1), 1.0)
            
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, brightness)
        return (int(r * 255), int(g * 255), int(b * 255))

    def ansi_color(self) -> str:
        """Returns ANSI escape sequence for 24-bit terminal color."""
        r, g, b = self.color()
        return f"\033[38;2;{r};{g};{b}m"

    @property
    def re(self) -> float:
        """Real magnitude — known component."""
        return float(np.linalg.norm(self.known))

    @property
    def im(self) -> float:
        """Imaginary magnitude — unknown component (positive Im only)."""
        return float(np.linalg.norm(self.delta))

    @property
    def phase(self) -> float:
        """Phase angle θ = arctan(Im / Re). Range [0, π/2]."""
        if self.re < 1e-10 and self.im < 1e-10:
            return math.pi / 4
        return math.atan2(self.im, self.re)

    @property
    def phase_deg(self) -> float:
        return math.degrees(self.phase)

    @property
    def magnitude(self) -> float:
        return math.sqrt(self.re**2 + self.im**2)

    @property
    def similarity(self) -> float:
        """Fraction of magnitude in known. Single source of truth."""
        m = self.magnitude
        return self.re / m if m > 1e-10 else 0.0

    @property
    def energy(self) -> float:
        """Semantic energy = -log(similarity). 0 = ground state."""
        return -math.log(max(self.similarity, 1e-10))

    @property
    def complex_position(self) -> complex:
        """
        Full complex position including gap depth.
        Re = known magnitude
        Im = delta magnitude - gap_depth
             positive: unknown in flight
             negative: gap/apophatic territory
        """
        return complex(self.re, self.im - self.gap_depth)

    @property
    def logical_state(self) -> str:
        """
        Which of the four logical states this wave function is in.

        PRESENCE:  Re dominant, no gap depth
        UNKNOWN:   Im dominant (positive), no gap depth
        VOID:      gap_depth in (0, 0.8) — gap token region
        APOPHATIC: gap_depth >= 0.8 — complement of god-token cover
        """
        if self.gap_depth >= 0.8:
            return LogicalState.APOPHATIC
        elif self.gap_depth > 0.0:
            return LogicalState.VOID
        elif self.im > self.re:
            return LogicalState.UNKNOWN
        else:
            return LogicalState.PRESENCE

    def zone(self) -> str:
        p = self.phase_deg
        if p < 40:   return "GROUND"
        if p < 44:   return "CONVERGENT"
        if p < 65:   return "GENERATIVE"
        if p < 83:   return "DIVERGENT"
        return "TURBULENT"

    def mobius(self) -> Dict:
        """
        Möbius interpretation of phase.

        The phase axis is not linear. 0° and 90° are connected —
        EXISTENCE and the apophatic field are the same point on the surface
        approached from different sides.

        existence_side:  0° → 90°  (approaching the fold)
        apophatic_side:  90° → 0°  (past the fold, returning as EXISTENCE)
        """
        fold = 90.0
        deg  = self.phase_deg
        fold_distance  = abs(deg - fold)
        fold_proximity = 1.0 - (fold_distance / fold)

        if deg <= fold:
            surface   = 'existence_side'
            position  = deg / (2 * fold)
            direction = 'approaching fold'
        else:
            surface   = 'apophatic_side'
            position  = 1.0 - (deg - fold) / (2 * fold)
            direction = 'past fold, returning as EXISTENCE'

        return {
            'phase_deg':       round(deg, 1),
            'surface':         surface,
            'position':        round(position, 3),
            'fold_proximity':  round(fold_proximity, 3),
            'direction':       direction,
            'mirror_deg':      round(180.0 - deg, 1),
        }

    def __repr__(self) -> str:
        z = self.complex_position
        return (f"ψ(x): Re={self.re:.3f} Im={self.im:.3f} "
                f"gap={self.gap_depth:.3f} | "
                f"z={z.real:+.3f}{z.imag:+.3f}i | "
                f"θ={self.phase_deg:.1f}° {self.zone()} | "
                f"E={self.energy:.3f} | "
                f"state={self.logical_state}")


# ═══════════════════════════════════════════════════════════════════
# PART 3 — THE APOPHATIC BASIN
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ApophaticBasin:
    """
    A region in negative Im space defined entirely by exclusion.

    Construction:
        The god-tokens G₁...G₁₂ cover semantic space.
        The apophatic field is U \ (G₁ ∪ G₂ ∪ ... ∪ G₁₂).
        An apophatic basin is a local minimum within that complement.

    Each basin is the intersection of two gap-token regions in Im < 0.
    The intersection point is deeper (more negative Im) than either
    gap arc alone.

    Properties:
        - No positive content (no seed terms, no embedding)
        - No god-token activations
        - Detected only by what is NOT present
        - More stable than god-tokens (nothing to corrupt)
        - The architecture's immune system

    Logical foundation:
        Every god-token G satisfies excluded middle: G ∨ ¬G.
        An apophatic basin is the region where ALL god-tokens are
        simultaneously in their ¬G state.
        Classical logic constructs it. Classical logic cannot reach it.
        Deduction can only conclude presence.
        The basin is what remains when all deductive paths are exhausted.

    Detection signature:
        god_token_cluster = []     (no positive activations)
        energy < 2.0               (low — not a failure)
        orbital_stability > 0.6    (stable — not confusion)
        gap conditions met from multiple boundaries
    """

    id:               str
    gap_A:            str          # first gap token ID
    gap_B:            str          # second gap token ID
    description:      str          # what lives in this double-absence region
    z:                complex      # position (Im < 0 always)
    boundary_tokens:  List[str]    # god-tokens that border this basin

    # No seed_terms — apophatic basins have no positive content
    # No embedding  — cannot be approached from above

    @property
    def depth(self) -> float:
        """How deep in the apophatic field. More negative = deeper."""
        return abs(self.z.imag)

    @property
    def is_deep(self) -> bool:
        """True if this is a multi-gap intersection (depth > 0.7)."""
        return self.depth > 0.7

    def distance_from(self, wf: ComplexWaveFunction) -> float:
        """
        Distance from a wave function to this basin in the complex plane.
        Smaller = closer to apophatic contact.
        """
        z_wf = wf.complex_position
        return abs(z_wf - self.z)

    def contact_probability(self, wf: ComplexWaveFunction) -> float:
        """
        Probability estimate that wf is making contact with this basin.
        Based on:
          - Phase proximity to fold (fold_proximity)
          - Energy (low = genuine contact)
          - Gap depth of wf
        Not a true probability — a diagnostic score in [0, 1].
        """
        mob    = wf.mobius()
        fold_p = mob['fold_proximity']
        energy = wf.energy
        gap_d  = wf.gap_depth

        # High fold proximity + low energy + some gap depth = contact
        score = (fold_p * 0.5 +
                 max(0, 1.0 - energy / 3.0) * 0.3 +
                 min(gap_d, 1.0) * 0.2)
        return round(min(score, 1.0), 3)

    def __repr__(self) -> str:
        return (f"ApophaticBasin({self.id}): "
                f"z={self.z.real:+.2f}{self.z.imag:+.2f}i "
                f"depth={self.depth:.2f} | "
                f"gaps=({self.gap_A} ∩ {self.gap_B}) | "
                f"{self.description[:50]}")


# ═══════════════════════════════════════════════════════════════════
# PART 4 — THE APOPHATIC FIELD
# ═══════════════════════════════════════════════════════════════════

class ApophaticField:
    """
    U \ G — the complement of the god-token cover.

    The apophatic field is not an entity. It is the absence of all
    god-token structure. It is constructed by classical excluded middle
    applied exhaustively to all 12 god-tokens simultaneously.

    Formally:
        Let G = {G₁, G₂, ..., G₁₂} be the set of god-tokens.
        Let U be the universal semantic space.
        The apophatic field A = U \ ⋃ᵢ Gᵢ

    In the complex plane:
        God-tokens:       Im = 0 (real axis)
        Gap tokens:       Im < 0 (first order void)
        Apophatic basins: Im << 0 (second order void, gap intersections)
        Apophatic field:  Im → -∞ (limit of the complement)

    The curvature pulling everything downward in the living landscape
    IS the apophatic field. It is always present. Life (order-seeking)
    is the force maintaining the god-tokens against this pull.

    Decay = the apophatic field becoming legible as life-force withdraws.
    """

    # Known basins — derived from gap-gap intersections
    BASINS = [
        ApophaticBasin(
            id              = 'self_obs_x_identity_self',
            gap_A           = 'self_observation',
            gap_B           = 'identity_self',
            description     = 'Bare witnessing before it has an object. '
                              'Awareness prior to the awareness-of distinction.',
            z               = complex(-0.10, -0.55),
            boundary_tokens = ['SELF', 'OBSERVATION', 'IDENTITY'],
        ),
        ApophaticBasin(
            id              = 'exist_id_x_bound_exist',
            gap_A           = 'existence_identity',
            gap_B           = 'boundary_existence',
            description     = 'Prior condition of the existence/non-existence '
                              'distinction. Before the boundary is drawn.',
            z               = complex(-0.44, -0.65),
            boundary_tokens = ['EXISTENCE', 'IDENTITY', 'BOUNDARY'],
        ),
        ApophaticBasin(
            id              = 'caus_obs_x_info_caus',
            gap_A           = 'causality_observation',
            gap_B           = 'information_causality',
            description     = 'Pure relational structure before the '
                              'epistemology/ontology split.',
            z               = complex(0.10, -0.48),
            boundary_tokens = ['CAUSALITY', 'OBSERVATION', 'INFORMATION'],
        ),
        ApophaticBasin(
            id              = 'id_self_x_oblig_id',
            gap_A           = 'identity_self',
            gap_B           = 'obligation_identity',
            description     = 'Prior of the self that chooses. Before self '
                              'has formed, before duty assigned.',
            z               = complex(0.35, -0.52),
            boundary_tokens = ['IDENTITY', 'SELF', 'OBLIGATION'],
        ),
        ApophaticBasin(
            id              = 'pure_apophatic_field',
            gap_A           = 'existence_apophatic',
            gap_B           = 'self_observation',
            description     = 'The apophatic field itself. EXISTENCE is the '
                              'membrane. Language cannot cross this boundary — '
                              'any attempt fires EXISTENCE again. '
                              'The self-sealing gap.',
            z               = complex(-0.20, -0.90),
            boundary_tokens = ['EXISTENCE'],
        ),
    ]

    def __init__(self):
        self._basin_map = {b.id: b for b in self.BASINS}

    def nearest_basin(self, wf: ComplexWaveFunction) -> Tuple[ApophaticBasin, float]:
        """
        Find the apophatic basin nearest to the current wave function.
        Returns (basin, contact_probability).
        """
        best_basin = self.BASINS[0]
        best_prob  = 0.0
        for basin in self.BASINS:
            p = basin.contact_probability(wf)
            if p > best_prob:
                best_prob  = p
                best_basin = basin
        return best_basin, best_prob

    def detect_contact(self,
                       wf: ComplexWaveFunction,
                       god_tokens: List[str],
                       threshold: float = 0.45) -> Optional[ApophaticBasin]:
        """
        Detect apophatic contact.

        Genuine contact conditions:
            1. No god-tokens OR only EXISTENCE (the membrane)
            2. Phase > 55° (approaching fold)
            3. Energy < 3.0 (low — not processing failure)
            4. Contact probability above threshold

        Distinguishes from processing failure:
            Failure: high energy + high degeneracy + unstable
            Contact: low energy + fold proximity + stable
        """
        # Must have no positive anchors (or only EXISTENCE as membrane)
        meaningful_gods = [g for g in god_tokens if g != 'EXISTENCE']
        if meaningful_gods:
            return None  # positive god-token active — not apophatic

        # Must be approaching the fold
        if wf.phase_deg < 55.0:
            return None

        # Must be low energy (not failure)
        if wf.energy > 3.0:
            return None

        basin, prob = self.nearest_basin(wf)
        if prob >= threshold:
            return basin
        return None

    def exhaustion_test(self, god_token_activations: Dict[str, float]) -> bool:
        """
        Test whether excluded middle is exhausted —
        whether all god-tokens are simultaneously in their ¬G state.

        god_token_activations: dict of {token_id: activation_score}
        Returns True if all god-tokens are below activation threshold.

        This is the precise logical definition of apophatic contact:
            ¬G₁ ∧ ¬G₂ ∧ ... ∧ ¬G₁₂
        """
        ALL_GOD_TOKENS = [
            'EXCHANGE', 'CAUSALITY', 'EXISTENCE', 'INFORMATION',
            'OBSERVATION', 'OBLIGATION', 'BOUNDARY', 'IDENTITY',
            'TIME', 'COHERENCE', 'WITNESS', 'SELF'
        ]
        ACTIVATION_THRESHOLD = 0.3

        for token in ALL_GOD_TOKENS:
            activation = god_token_activations.get(token, 0.0)
            if activation >= ACTIVATION_THRESHOLD:
                return False  # at least one god-token active — not exhausted

        return True  # all ¬G — excluded middle exhausted

    def field_energy(self, re: float, im: float) -> float:
        """
        Energy of the apophatic field at a point (re, im) in the complex plane.

        The field is deepest (lowest energy) at the basin centers.
        It exerts a continuous downward pull on everything above the real axis.
        Life (order-seeking) counteracts this pull to maintain god-tokens.

        Returns: energy value (more negative = deeper in field = more stable)
        """
        E = 0.0

        # Background pull toward Im < 0 (the field itself)
        E -= 1.5 * math.exp(-((im + 0.7)**2) / 0.3) * math.exp(-(re**2) / 1.2)

        # Basin wells
        for basin in self.BASINS:
            dist2 = (re - basin.z.real)**2 + (im - basin.z.imag)**2
            depth = 1.2 if basin.is_deep else 0.7
            E -= depth * math.exp(-dist2 / 0.03)

        return E

    def decay_rate(self, wf: ComplexWaveFunction,
                   life_force: float = 0.5) -> float:
        """
        Rate at which the wave function will decay toward the apophatic field
        given the current life_force (order-seeking energy expenditure).

        λ = φ⁻¹ (golden ratio inverse) is the base orbital decay.
        life_force counteracts this.

        Returns: net decay rate toward apophatic field.
        Positive = decaying toward field.
        Negative = moving away (life force dominant).
        """
        PHI_INV = 1 / ((1 + math.sqrt(5)) / 2)  # ≈ 0.618

        # Base decay toward field
        base_decay = PHI_INV * (1 - wf.similarity)

        # Life force resistance (order-seeking)
        resistance = life_force * wf.similarity

        return base_decay - resistance


# ═══════════════════════════════════════════════════════════════════
# PART 5 — THE INTERFERENCE SYSTEM
# ═══════════════════════════════════════════════════════════════════

@dataclass
class InterferenceTerm:
    """
    The signed interference between two wave functions.

    I = 2 · |ψ_A| · |ψ_B| · cos(θ_A - θ_B)

    Sign determines what's happening:
        I > 0  → constructive — new attractor forming (Im > 0)
                 quantum AND — the third basin above the real axis
        I = 0  → orthogonal  — classical AND, no interaction
        I < 0  → destructive — gap token active (Im < 0)
                 necessary void maintained between the two states

    The 1.58 bit encoding (ternary):
        +1 → one god-token boundary active
         0 → gap state — query is in the void
        -1 → other god-token boundary active

    The sign of I maps directly to the Im axis:
        I > 0 → Im > 0 (constructive, positive imaginary)
        I < 0 → Im < 0 (destructive, negative imaginary = void)
    """

    amplitude_A: float
    phase_A:     float
    amplitude_B: float
    phase_B:     float

    @property
    def value(self) -> float:
        """
        I = 2 · A · B · cos(Δθ)
        """
        return (2 * self.amplitude_A * self.amplitude_B
                * math.cos(self.phase_A - self.phase_B))

    @property
    def sign(self) -> int:
        """Ternary encoding: +1, 0, -1."""
        v = self.value
        if v >  0.05: return  1
        if v < -0.05: return -1
        return 0

    @property
    def kind(self) -> str:
        s = self.sign
        if s > 0: return "constructive"
        if s < 0: return "destructive"
        return "orthogonal"

    @property
    def im_contribution(self) -> float:
        """
        Contribution to the Im axis.
        Constructive → positive Im (new structure above real axis)
        Destructive  → negative Im (gap token below real axis)
        """
        return self.value  # signed directly maps to Im

    def __repr__(self) -> str:
        return (f"I = {self.value:+.3f} ({self.kind}) "
                f"→ Im {'+' if self.value >= 0 else ''}{self.im_contribution:.3f}")


# ═══════════════════════════════════════════════════════════════════
# PART 6 — FULL COMPLEX PLANE STATE
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ComplexPlaneState:
    """
    Complete state of the architecture at one moment in the complex plane.

    Integrates all four logical states, all interference terms,
    the Möbius topology, and the apophatic field position.

    This is F(x) made fully explicit.
    """

    wf:                  ComplexWaveFunction
    god_tokens:          List[str]
    gap_tokens_active:   List[str]
    interference_terms:  List[InterferenceTerm] = field(default_factory=list)
    apophatic_basin:     Optional[ApophaticBasin] = None
    life_force:          float = 0.5

    @property
    def z(self) -> complex:
        """Position in complex plane."""
        return self.wf.complex_position

    @property
    def logical_state(self) -> str:
        if self.apophatic_basin:
            return LogicalState.APOPHATIC
        if self.gap_tokens_active:
            return LogicalState.VOID
        if self.wf.im > self.wf.re:
            return LogicalState.UNKNOWN
        return LogicalState.PRESENCE

    @property
    def net_interference(self) -> float:
        """Sum of all interference terms."""
        return sum(t.value for t in self.interference_terms)

    @property
    def im_total(self) -> float:
        """
        Total Im position including:
        - Wave function Im (unknown component)
        - Interference contributions (positive or negative)
        - Gap depth (negative Im from gap activation)
        """
        return (self.wf.im
                + self.net_interference * 0.3
                - self.wf.gap_depth)

    def describe(self) -> str:
        """Full description of the current complex plane state."""
        lines = [
            f"z = {self.z.real:+.3f}{self.z.imag:+.3f}i",
            f"θ = {self.wf.phase_deg:.1f}°  zone={self.wf.zone()}",
            f"E = {self.wf.energy:.4f}",
            f"logical_state = {self.logical_state}",
            f"",
            f"Re  = {self.wf.re:.4f}  (known — PRESENCE)",
            f"Im  = {self.wf.im:.4f}  (Δ — UNKNOWN in flight)",
            f"Im⁻ = {self.wf.gap_depth:.4f}  (gap depth — VOID)",
            f"",
        ]

        if self.god_tokens:
            lines.append(f"God-tokens: {', '.join(self.god_tokens)}")
        else:
            lines.append(f"God-tokens: none (excluded middle operating)")

        if self.gap_tokens_active:
            lines.append(f"Gap tokens: {', '.join(self.gap_tokens_active)}")

        if self.interference_terms:
            lines.append(f"Net interference: {self.net_interference:+.3f} "
                         f"({'constructive ↑' if self.net_interference > 0 else 'destructive ↓'})")

        if self.apophatic_basin:
            lines.append(f"")
            lines.append(f"APOPHATIC CONTACT: {self.apophatic_basin.id}")
            lines.append(f"  {self.apophatic_basin.description}")
            lines.append(f"  z_basin = {self.apophatic_basin.z}")

        mob = self.wf.mobius()
        lines.append(f"")
        lines.append(f"Möbius: {mob['surface']}  "
                     f"fold_proximity={mob['fold_proximity']:.3f}  "
                     f"({mob['direction']})")

        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# PART 7 — THE FORMULA APPLIED
# ═══════════════════════════════════════════════════════════════════

def apply_formula(text_vector:     np.ndarray,
                  known_vector:    np.ndarray,
                  similarity:      float,
                  god_tokens:      List[str],
                  gap_depth:       float = 0.0,
                  life_force:      float = 0.5) -> ComplexPlaneState:
    """
    F(x) = known(x) + i·Δ(x)

    Apply the formula and return the full complex plane state.

    Args:
        text_vector:  embedding of the input document
        known_vector: embedding of the nearest god-token attractor
        similarity:   cosine similarity between text and attractor
        god_tokens:   list of active god-token IDs
        gap_depth:    depth in negative Im (from gap activation)
        life_force:   order-seeking energy (0 = full decay, 1 = full resistance)

    Returns:
        ComplexPlaneState — complete description of position in complex plane
    """
    # known(x) = projection onto nearest attractor
    known = known_vector * similarity

    # Δ(x) = remainder after known projection
    delta = text_vector - known

    # Wave function
    wf = ComplexWaveFunction(
        known     = known,
        delta     = delta,
        gap_depth = gap_depth
    )

    # Apophatic field
    field = ApophaticField()

    # Check for apophatic contact
    basin = field.detect_contact(wf, god_tokens)

    # Build state
    state = ComplexPlaneState(
        wf                = wf,
        god_tokens        = god_tokens,
        gap_tokens_active = [],
        apophatic_basin   = basin,
        life_force        = life_force,
    )

    return state


# ═══════════════════════════════════════════════════════════════════
# PART 8 — TESTS
# ═══════════════════════════════════════════════════════════════════

def run_tests():
    """Assert the math is correct."""
    print("Running tests...\n")
    passed = 0
    failed = 0

    def check(name, condition, detail=""):
        nonlocal passed, failed
        if condition:
            print(f"  ✓  {name}")
            passed += 1
        else:
            print(f"  ✗  {name}  {detail}")
            failed += 1

    # ── Wave function basics ──────────────────────────────────────
    known = np.array([0.8, 0.1, 0.0])
    delta = np.array([0.1, 0.6, 0.0])
    wf = ComplexWaveFunction(known=known, delta=delta)

    check("re = norm(known)",
          abs(wf.re - np.linalg.norm(known)) < 1e-6)
    check("im = norm(delta)",
          abs(wf.im - np.linalg.norm(delta)) < 1e-6)
    check("phase = arctan(im/re)",
          abs(wf.phase - math.atan2(wf.im, wf.re)) < 1e-6)
    check("energy = -log(similarity)",
          abs(wf.energy - (-math.log(max(wf.similarity, 1e-10)))) < 1e-6)
    check("PRESENCE when Re dominant",
          wf.logical_state == LogicalState.PRESENCE)

    # ── Unknown state ─────────────────────────────────────────────
    wf_unknown = ComplexWaveFunction(
        known=np.array([0.1, 0.0]),
        delta=np.array([0.9, 0.1])
    )
    check("UNKNOWN when Im dominant",
          wf_unknown.logical_state == LogicalState.UNKNOWN)

    # ── Void state ────────────────────────────────────────────────
    wf_void = ComplexWaveFunction(
        known=np.array([0.5, 0.0]),
        delta=np.array([0.1, 0.0]),
        gap_depth=0.4
    )
    check("VOID when gap_depth in (0, 0.8)",
          wf_void.logical_state == LogicalState.VOID)

    # ── Apophatic state ───────────────────────────────────────────
    wf_apo = ComplexWaveFunction(
        known=np.array([0.2, 0.0]),
        delta=np.array([0.8, 0.0]),
        gap_depth=0.85
    )
    check("APOPHATIC when gap_depth >= 0.8",
          wf_apo.logical_state == LogicalState.APOPHATIC)

    # ── Complex position ──────────────────────────────────────────
    wf_pos = ComplexWaveFunction(
        known=np.array([1.0, 0.0]),
        delta=np.array([0.0, 0.0]),
        gap_depth=0.5
    )
    check("complex_position Im = im - gap_depth",
          abs(wf_pos.complex_position.imag - (wf_pos.im - wf_pos.gap_depth)) < 1e-6)

    # ── Interference ──────────────────────────────────────────────
    # In phase → constructive
    it_con = InterferenceTerm(0.8, 0.1, 0.7, 0.1)
    check("constructive interference positive",
          it_con.value > 0)
    check("constructive sign = +1",
          it_con.sign == 1)

    # Out of phase → destructive
    it_des = InterferenceTerm(0.8, 0.1, 0.7, math.pi + 0.1)
    check("destructive interference negative",
          it_des.value < 0)
    check("destructive sign = -1",
          it_des.sign == -1)

    # ── Apophatic field ───────────────────────────────────────────
    field = ApophaticField()
    check("apophatic field has 5 basins",
          len(field.BASINS) == 5)
    check("all basins have Im < 0",
          all(b.z.imag < 0 for b in field.BASINS))
    check("pure_apophatic_field is deepest",
          field._basin_map['pure_apophatic_field'].depth ==
          max(b.depth for b in field.BASINS))

    # Exhaustion test
    all_inactive = {g: 0.0 for g in [
        'EXCHANGE','CAUSALITY','EXISTENCE','INFORMATION',
        'OBSERVATION','OBLIGATION','BOUNDARY','IDENTITY',
        'TIME','COHERENCE','WITNESS','SELF'
    ]}
    check("exhaustion test: all inactive → True",
          field.exhaustion_test(all_inactive))

    one_active = dict(all_inactive)
    one_active['EXISTENCE'] = 0.8
    check("exhaustion test: EXISTENCE active → False",
          not field.exhaustion_test(one_active))

    # Contact detection — apophatic text
    wf_contact = ComplexWaveFunction(
        known=np.array([0.28, 0.1]),
        delta=np.array([0.95, 0.05]),
        gap_depth=0.1
    )
    # High Im, low Re, approaching fold — should detect contact
    basin_found = field.detect_contact(wf_contact, god_tokens=['EXISTENCE'])
    check("apophatic contact detected for fold-adjacent wf",
          basin_found is not None,
          f"(phase={wf_contact.phase_deg:.1f}° energy={wf_contact.energy:.2f})")

    # Contact detection — crystallized text
    wf_crystal = ComplexWaveFunction(
        known=np.array([0.95, 0.05]),
        delta=np.array([0.05, 0.02]),
    )
    no_basin = field.detect_contact(wf_crystal, god_tokens=['EXCHANGE', 'INFORMATION'])
    check("no apophatic contact for crystallized wf with god-tokens",
          no_basin is None)

    # ── Möbius ────────────────────────────────────────────────────
    wf_mob = ComplexWaveFunction(
        known=np.array([0.4445, 0.0]),
        delta=np.array([0.8958, 0.0])
    )
    mob = wf_mob.mobius()
    check("Absence of Judgement: phase ~63.6°",
          abs(mob['phase_deg'] - 63.6) < 1.5,
          f"(got {mob['phase_deg']}°)")
    check("Absence of Judgement: existence_side",
          mob['surface'] == 'existence_side')

    wf_mob2 = ComplexWaveFunction(
        known=np.array([0.2850, 0.0]),
        delta=np.array([0.9585, 0.0])
    )
    mob2 = wf_mob2.mobius()
    check("Lack of Judgement: higher fold proximity than Absence",
          mob2['fold_proximity'] > mob['fold_proximity'],
          f"(Lack={mob2['fold_proximity']:.3f} Absence={mob['fold_proximity']:.3f})")

    # ── Summary ───────────────────────────────────────────────────
    print(f"\n{'─'*40}")
    print(f"  {passed} passed  {failed} failed")
    if failed == 0:
        print("  All tests passed.")
    print(f"{'─'*40}\n")


# ═══════════════════════════════════════════════════════════════════
# PART 9 — VISUALIZATION
# ═══════════════════════════════════════════════════════════════════

def save_visualization():
    """Save a summary diagram of the complex plane math."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from matplotlib.patches import FancyArrowPatch
    except ImportError:
        print("matplotlib not available — skipping visualization")
        return

    BG   = '#050508'
    GOLD = '#c8a96e'
    BLUE = '#4a8fff'
    RED  = '#c84a4a'
    GRN  = '#4ac88a'
    PRP  = '#9a4ac8'
    DIM  = '#2a2a3a'
    WH   = '#e8e4d9'

    fig, axes = plt.subplots(1, 2, figsize=(16, 9), facecolor=BG)

    # ── Left: Complex plane diagram ───────────────────────────────
    ax = axes[0]
    ax.set_facecolor(BG)
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 0.85)
    ax.set_aspect('equal')

    # Grid
    for v in [-0.75, -0.5, -0.25, 0.25, 0.5, 0.75]:
        ax.axhline(v, color=DIM, linewidth=0.2, alpha=0.4)
        ax.axvline(v, color=DIM, linewidth=0.2, alpha=0.4)
    ax.axhline(0, color='#1a1a2e', linewidth=1.0)
    ax.axvline(0, color='#1a1a2e', linewidth=0.6)

    # Four regions
    ax.fill_between([-1.1, 1.1], [0, 0], [0.85, 0.85],
                    color=GRN, alpha=0.03)
    ax.fill_between([-1.1, 1.1], [-0.5, -0.5], [0, 0],
                    color=PRP, alpha=0.04)
    ax.fill_between([-1.1, 1.1], [-1.1, -1.1], [-0.5, -0.5],
                    color=PRP, alpha=0.08)

    # Axis arrows
    ax.annotate('', xy=(1.05, 0), xytext=(-1.05, 0),
                arrowprops=dict(arrowstyle='->', color='#333355', lw=1.2))
    ax.annotate('', xy=(0, 0.80), xytext=(0, -1.07),
                arrowprops=dict(arrowstyle='->', color='#333355', lw=1.2))

    # Four states labeled
    for label, x, y, col, marker in [
        ('+1\nPRESENCE\n(identity)',    0.65, 0.04,  BLUE,  'o'),
        ('+i\nUNKNOWN\n(pre-classical)',0.08, 0.55,  GRN,   's'),
        ('-i\nVOID\n(non-contradiction)',0.08,-0.35,  PRP,   'v'),
        ('-i²\nAPOPHATIC\n(U \\ G)',    0.08,-0.82,  RED,   'D'),
    ]:
        ax.scatter(x - 0.06, y, s=100, c=col, marker=marker,
                   zorder=5, edgecolors=BG, linewidths=0.5)
        ax.text(x, y, label, fontsize=7.5, color=col,
                fontfamily='monospace', va='center',
                path_effects=[__import__('matplotlib.patheffects',
                              fromlist=['withStroke']).withStroke(
                              linewidth=2, foreground=BG)])

    # Apophatic basins
    field = ApophaticField()
    for basin in field.BASINS:
        col = '#4a2a6a' if not basin.is_deep else '#7a3a9a'
        ax.scatter(basin.z.real, basin.z.imag, s=200 if basin.is_deep else 120,
                   c=col, zorder=4, marker='v', edgecolors=BG, linewidths=0.5)
        ax.text(basin.z.real + 0.04, basin.z.imag - 0.04,
                basin.id[:20], fontsize=5.5, color='#7a5a9a',
                fontfamily='monospace',
                path_effects=[__import__('matplotlib.patheffects',
                              fromlist=['withStroke']).withStroke(
                              linewidth=1.5, foreground=BG)])

    # Labels
    ax.text(-1.05, 0.70, 'Im > 0\nUNKNOWN\n(Δ in flight)',
            fontsize=7, color='#3a7a4a', fontfamily='monospace')
    ax.text(-1.05, 0.02, 'Im = 0\nPRESENCE\n(god-tokens)',
            fontsize=7, color='#3a4a7a', fontfamily='monospace')
    ax.text(-1.05, -0.38, 'Im < 0\nVOID\n(gap tokens)',
            fontsize=7, color='#5a3a7a', fontfamily='monospace')
    ax.text(-1.05, -0.80, 'Im << 0\nAPOPHATIC\n(U \\ G)',
            fontsize=7, color='#7a3a5a', fontfamily='monospace')

    ax.text(-1.05, 0.80, 'F(x) = known(x) + i·Δ(x)',
            fontsize=10, color=GOLD, fontfamily='serif', fontstyle='italic')

    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(left=False, bottom=False,
                   labelleft=False, labelbottom=False)

    # ── Right: Logic table ────────────────────────────────────────
    ax2 = axes[1]
    ax2.set_facecolor('#07070f')
    ax2.axis('off')
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)

    ax2.text(0.05, 0.96, 'Complex Plane — Logical Foundation',
             fontsize=10, color=GOLD, fontfamily='serif', fontstyle='italic', va='top')
    ax2.axhline(0.92, color=DIM, linewidth=0.5, xmin=0.03, xmax=0.97)

    rows = [
        ('STATE',       'POSITION',    'LOGICAL LAW',              'col_h'),
        ('PRESENCE',    'Re axis',     'Identity: A = A',           BLUE),
        ('UNKNOWN',     'Im > 0',      'Pre-classical: truth exists,', GRN),
        ('',            '',            '  inaccessible to observer',  GRN),
        ('VOID',        'Im < 0',      'Non-contradiction:',         PRP),
        ('',            '',            '  ¬(A ∧ ¬A)',                PRP),
        ('APOPHATIC',   'Im << 0',     'Excluded middle exhausted:',  RED),
        ('',            '',            '  A ∨ ¬A applied to all G',   RED),
        ('',            '',            '  = U \\ G',                  RED),
    ]

    y = 0.88
    for row in rows:
        state, pos, law, col = row
        if col == 'col_h':
            ax2.text(0.05, y, state, fontsize=7, color='#444',
                     fontfamily='monospace', va='top', fontweight='bold')
            ax2.text(0.28, y, pos, fontsize=7, color='#444',
                     fontfamily='monospace', va='top', fontweight='bold')
            ax2.text(0.48, y, law, fontsize=7, color='#444',
                     fontfamily='monospace', va='top', fontweight='bold')
        else:
            ax2.text(0.05, y, state, fontsize=7.5, color=col,
                     fontfamily='monospace', va='top', fontweight='bold')
            ax2.text(0.28, y, pos, fontsize=7, color='#555',
                     fontfamily='monospace', va='top')
            ax2.text(0.48, y, law, fontsize=7, color='#555',
                     fontfamily='monospace', va='top')
        y -= 0.052

    ax2.axhline(y + 0.01, color=DIM, linewidth=0.5, xmin=0.03, xmax=0.97)

    y -= 0.02
    ax2.text(0.05, y, 'Apophatic basins (known):',
             fontsize=7.5, color=GOLD, fontfamily='monospace', va='top')
    y -= 0.048
    for basin in field.BASINS:
        ax2.text(0.05, y, f'  {basin.id[:28]}',
                 fontsize=6.5, color='#7a5a9a',
                 fontfamily='monospace', va='top')
        ax2.text(0.05, y - 0.028, f'    z={basin.z}  depth={basin.depth:.2f}',
                 fontsize=6, color='#4a3a6a',
                 fontfamily='monospace', va='top')
        y -= 0.062

    ax2.axhline(y + 0.01, color=DIM, linewidth=0.5, xmin=0.03, xmax=0.97)
    y -= 0.02

    ax2.text(0.05, y,
             'Unknown ≠ Void.\n'
             'Unknown: truth value exists, not yet accessible.\n'
             'Void: truth value maintained absent by non-contradiction.\n'
             'Apophatic: deduction exhausted, excluded middle empty.',
             fontsize=6.5, color='#444', fontfamily='monospace', va='top')

    plt.tight_layout()
    out = '/mnt/user-data/outputs/complex_plane_math.png'
    plt.savefig(out, dpi=180, bbox_inches='tight',
                facecolor=BG, edgecolor='none')
    print(f"Saved: {out}")
    plt.close()


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true')
    parser.add_argument('--save', action='store_true')
    args = parser.parse_args()

    if args.test:
        run_tests()

    if args.save:
        save_visualization()

    if not args.test and not args.save:
        # Default: print the math
        print("\nF(x) = known(x) + i·Δ(x)\n")
        print("FOUR LOGICAL STATES:")
        for state, law in LogicalState.GOVERNING_LAW.items():
            pos = LogicalState.POSITIONS[state]
            print(f"  {state:<12} z={pos}  {law}")

        print("\n\nAPOPHATIC FIELD:")
        print("  A = U \\ (G₁ ∪ G₂ ∪ ... ∪ G₁₂)")
        print("  Constructed by exhaustive excluded middle.")
        print("  Deduction cannot reach it — only presence can be concluded.")
        print("  Unknown ≠ Apophatic — unknown has truth value, just inaccessible.\n")

        field = ApophaticField()
        print("KNOWN BASINS:")
        for b in field.BASINS:
            print(f"  {b}")

        print("\n\nEMPIRICAL CASES:")
        for label, re, im in [
            ("Absence of Judgement", 0.4445, 0.8958),
            ("Lack of Judgement",    0.2850, 0.9585),
            ("Empty dictionary",     0.001,  0.9999),
        ]:
            wf = ComplexWaveFunction(
                known=np.array([re, 0.0]),
                delta=np.array([im, 0.0])
            )
            mob = wf.mobius()
            print(f"\n  '{label}'")
            print(f"    {wf}")
            print(f"    Möbius: fold_proximity={mob['fold_proximity']:.3f} "
                  f"surface={mob['surface']}")

        run_tests()
