"""
quaternion_field.py — The 4D Extension of F(x)

CURRENT:
    F(x) = known(x) + i·Δ_semantic
    2D complex plane. One real axis, one imaginary axis.
    Phase θ is a scalar angle.
    PLACE and EMERGENCE are invisible (collapsed to zero).

EXTENDED:
    F_q(x) = w + x·i + y·j + z·k
    4D quaternion space. One real axis, three imaginary axes.
    Phase θ is a quaternion orientation — direction in 4D space.

THE FOUR COMPONENTS:
    w  — known(x)          real, crystallized, presence
                           eigenvalue +1 territory
    x  — Δ_semantic        semantic surprise (current architecture, unchanged)
                           what is not yet known in this domain
    y  — Δ_spatial         PLACE-deviation
                           how far this document is from its spatial prior
                           PLACE as a dimension, not a token
    z  — Δ_emergence       EMERGENCE-deviation
                           how much is arising that has not yet crystallized
                           EMERGENCE as a dimension, not a token

QUATERNION RULES:
    i² = j² = k² = ijk = -1
    ij = +k  (semantic surprise × spatial surprise = emergence)
    ji = -k  (spatial × semantic = negative emergence = displacement)
    jk = +i, ki = +j  (and reverses for negatives)

    Non-commutativity is the formal grounding of temporal interference.
    Processing A then B ≠ processing B then A.
    ij ≠ ji. The order of encounter matters.

    Specifically:
    ij = +k  Discovery: semantic opens, place grounds it → emergence
    ji = -k  Displacement: place shifts, semantic tries to catch up → disorientation

SIX FOLDS (gimbal lock pairs):
    w-x: Möbius fold          inside/outside indistinguishable (current architecture)
    w-y: PLACE fold           where you are = where you are known to be — home
    w-z: Crystallization fold arising completes, god-token stabilizes
    x-y: Déjà vu fold         semantic surprise = spatial surprise — recognition without cause
    x-z: Learning fold        what you don't know = what is arising — frontier = lesson
    y-z: Dwelling fold        where you are = what is arising — Heidegger's Wohnen

ZONE BOUNDARIES as energy shells:
    Not scalar angles. Quaternion energy fractions.
    |q|² = w² + x² + y² + z²

    GROUND:      w² > 0.70 · |q|²   known dominates
    CONVERGENT:  w² > 0.55 · |q|²   known dominant but shrinking
    GENERATIVE:  all components within factor 3 of each other
    DIVERGENT:   w² < 0.30 · |q|²   surprise dominant
    TURBULENT:   w² < 0.10 · |q|²   surprise overwhelms

    The generative zone is now a SPHERE in 4D, not a slice at 45°.
    Any document near the surface of that sphere is generating
    in any combination of the three surprise dimensions.

APOPHATIC DETECTION:
    Gap token:         x < -threshold            (negative semantic — current)
    Spatial gap:       y < -threshold            (negative PLACE — unmapped location)
    Emergence gap:     z < -threshold            (negative EMERGENCE — decaying process)
    Full apophatic:    x < -threshold AND
                       y < -threshold AND
                       z < -threshold            (triple absence — genuine apophatic basin)

    A document can be in gap territory (negative x) without being apophatic.
    The apophatic requires negativity in all three imaginary axes simultaneously.

GEODESICS on S³:
    Not heuristic stepping. Exact SLERP.
    Given two unit quaternions q₁ and q₂:
    slerp(q₁, q₂, t) = q₁·sin((1-t)Ω)/sin(Ω) + q₂·sin(tΩ)/sin(Ω)
    where cos(Ω) = q₁·q₂ (dot product)

    Great circles on S³ are the exact geodesics.
    The intermediate god-tokens on the path are the points where
    the great circle passes nearest to each attractor.
    These are the argument structures — exact, not approximated.

BASIS EXTRACTION:
    PLACE and EMERGENCE axes extracted from Qwen3 embeddings via Gram-Schmidt.
    The embedding space is projected onto four orthogonal axes:
    w-axis: mean direction of all crystallized god-token embeddings
    x-axis: direction of maximum variance orthogonal to w
    y-axis: PLACE seed direction orthogonalized against w, x
    z-axis: EMERGENCE seed direction orthogonalized against w, x, y

    On TF-IDF: y ≈ 0, z ≈ 0 (PLACE and EMERGENCE invisible)
    On Qwen3:  y, z nonzero — the full 4D space becomes accessible

Usage:
    python3 quaternion_field.py --test
    python3 quaternion_field.py --demo
    python3 quaternion_field.py --folds
    python3 quaternion_field.py --q "your text here"
"""

import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))


# ═══════════════════════════════════════════════════════════════════
# QUATERNION ARITHMETIC
# ═══════════════════════════════════════════════════════════════════

@dataclass
class Quaternion:
    """
    q = w + xi + yj + zk

    Hamilton product is non-commutative: pq ≠ qp in general.
    This non-commutativity is the formal grounding of temporal interference.
    """
    w: float = 1.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    # ── Arithmetic ────────────────────────────────────────────────

    def __add__(self, other: 'Quaternion') -> 'Quaternion':
        return Quaternion(self.w+other.w, self.x+other.x,
                         self.y+other.y, self.z+other.z)

    def __sub__(self, other: 'Quaternion') -> 'Quaternion':
        return Quaternion(self.w-other.w, self.x-other.x,
                         self.y-other.y, self.z-other.z)

    def __mul__(self, other) -> 'Quaternion':
        """
        Hamilton product. NON-COMMUTATIVE.

        ij = +k  ←  semantic × spatial = emergence (discovery)
        ji = -k  ←  spatial × semantic = -emergence (displacement)
        jk = +i, ki = +j
        """
        if isinstance(other, (int, float)):
            return Quaternion(self.w*other, self.x*other,
                            self.y*other, self.z*other)
        a1,b1,c1,d1 = self.w, self.x, self.y, self.z
        a2,b2,c2,d2 = other.w, other.x, other.y, other.z
        return Quaternion(
            a1*a2 - b1*b2 - c1*c2 - d1*d2,
            a1*b2 + b1*a2 + c1*d2 - d1*c2,
            a1*c2 - b1*d2 + c1*a2 + d1*b2,
            a1*d2 + b1*c2 - c1*b2 + d1*a2,
        )

    def __rmul__(self, scalar: float) -> 'Quaternion':
        return self.__mul__(scalar)

    def __neg__(self) -> 'Quaternion':
        return Quaternion(-self.w, -self.x, -self.y, -self.z)

    def __repr__(self) -> str:
        parts = [f"{self.w:.3f}"]
        if abs(self.x) > 1e-10:
            parts.append(f"{self.x:+.3f}i")
        if abs(self.y) > 1e-10:
            parts.append(f"{self.y:+.3f}j")
        if abs(self.z) > 1e-10:
            parts.append(f"{self.z:+.3f}k")
        return "".join(parts)

    # ── Properties ────────────────────────────────────────────────

    @property
    def norm(self) -> float:
        return math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)

    @property
    def norm_sq(self) -> float:
        return self.w**2 + self.x**2 + self.y**2 + self.z**2

    @property
    def conjugate(self) -> 'Quaternion':
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    @property
    def inverse(self) -> 'Quaternion':
        n2 = self.norm_sq
        if n2 < 1e-20:
            raise ZeroDivisionError("zero quaternion has no inverse")
        return self.conjugate * (1.0 / n2)

    def normalized(self) -> 'Quaternion':
        n = self.norm
        if n < 1e-10:
            return Quaternion(1, 0, 0, 0)
        return Quaternion(self.w/n, self.x/n, self.y/n, self.z/n)

    def dot(self, other: 'Quaternion') -> float:
        return self.w*other.w + self.x*other.x + self.y*other.y + self.z*other.z

    def as_array(self) -> np.ndarray:
        return np.array([self.w, self.x, self.y, self.z])

    @classmethod
    def from_array(cls, arr: np.ndarray) -> 'Quaternion':
        return cls(float(arr[0]), float(arr[1]), float(arr[2]), float(arr[3]))

    @classmethod
    def from_axis_angle(cls, axis: np.ndarray, angle_rad: float) -> 'Quaternion':
        """Unit quaternion representing rotation by angle around axis."""
        axis = axis / (np.linalg.norm(axis) + 1e-10)
        s = math.sin(angle_rad / 2)
        return cls(
            math.cos(angle_rad / 2),
            float(axis[0]) * s,
            float(axis[1]) * s,
            float(axis[2]) * s,
        ).normalized()

    # ── Non-commutativity checks ───────────────────────────────────

    def commutator(self, other: 'Quaternion') -> 'Quaternion':
        """[self, other] = self*other - other*self. Zero iff commutative."""
        return self * other - other * self

    def commutes_with(self, other: 'Quaternion',
                      tol: float = 1e-6) -> bool:
        c = self.commutator(other)
        return c.norm < tol


# ═══════════════════════════════════════════════════════════════════
# SLERP — Great Circle Geodesics on S³
# ═══════════════════════════════════════════════════════════════════

def slerp(q1: Quaternion, q2: Quaternion, t: float) -> Quaternion:
    """
    Spherical Linear Interpolation.
    Exact geodesic on S³ (unit 3-sphere).

    slerp(q1, q2, t) = q1·sin((1-t)Ω)/sin(Ω) + q2·sin(tΩ)/sin(Ω)
    where cos(Ω) = q1·q2

    t=0 → q1, t=1 → q2.
    Path is a great circle — the shortest path on S³.
    No intermediate steps. No accumulated error. Exact.
    """
    q1 = q1.normalized()
    q2 = q2.normalized()

    dot = max(-1.0, min(1.0, q1.dot(q2)))

    # If dot < 0, negate q2 to take the shorter arc
    if dot < 0:
        q2 = -q2
        dot = -dot

    # Near-parallel: linear interpolation (degenerate slerp)
    if dot > 0.9995:
        result = Quaternion(
            q1.w + t*(q2.w - q1.w),
            q1.x + t*(q2.x - q1.x),
            q1.y + t*(q2.y - q1.y),
            q1.z + t*(q2.z - q1.z),
        )
        return result.normalized()

    omega = math.acos(dot)
    sin_omega = math.sin(omega)

    s1 = math.sin((1 - t) * omega) / sin_omega
    s2 = math.sin(t * omega) / sin_omega

    return Quaternion(
        s1*q1.w + s2*q2.w,
        s1*q1.x + s2*q2.x,
        s1*q1.y + s2*q2.y,
        s1*q1.z + s2*q2.z,
    ).normalized()


def great_circle_path(q1: Quaternion, q2: Quaternion,
                      steps: int = 20) -> List[Quaternion]:
    """Sample the great circle arc between q1 and q2."""
    return [slerp(q1, q2, t/steps) for t in range(steps+1)]


# ═══════════════════════════════════════════════════════════════════
# THE SIX FOLDS
# ═══════════════════════════════════════════════════════════════════

@dataclass
class Fold:
    """
    A fold occurs when two quaternion axes align — gimbal lock.
    One degree of freedom is lost at the fold.
    The fold is a structural property of the space, not an error.
    """
    id:           str
    axes:         Tuple[str, str]
    name:         str
    description:  str
    phase_deg:    float      # approximate phase angle where this fold occurs
    is_current:   bool       # True if already in the current 2D architecture

    def detect(self, q: 'QuaternionWaveFunction',
               tol: float = 0.15) -> bool:
        """
        Detect if q is near this fold.
        Fold condition: the two axis components are nearly equal in magnitude.
        """
        vals = {
            'w': abs(q.q.w), 'x': abs(q.q.x),
            'y': abs(q.q.y), 'z': abs(q.q.z),
        }
        a_val = vals[self.axes[0]]
        b_val = vals[self.axes[1]]
        total = a_val + b_val
        if total < 1e-10:
            return False
        return abs(a_val - b_val) / total < tol


FOLDS = [
    Fold(
        id          = 'wx',
        axes        = ('w', 'x'),
        name        = 'Möbius fold',
        description = (
            "Inside and outside become indistinguishable. "
            "The existence-side and apophatic-side of a concept carry "
            "inverted orientation — same attractor, orthogonal polarizations. "
            "Currently at θ=90° in the 2D architecture. "
            "The single edge of the Möbius strip."
        ),
        phase_deg   = 90.0,
        is_current  = True,
    ),
    Fold(
        id          = 'wy',
        axes        = ('w', 'y'),
        name        = 'PLACE fold / Home',
        description = (
            "Where you are becomes exactly where you are known to be. "
            "The spatial prior aligns with the presence axis. "
            "The sensation of home — not comfort, structural alignment. "
            "PLACE ceases to be a deviation and becomes a ground. "
            "Invisible in 2D architecture (y axis collapsed)."
        ),
        phase_deg   = 90.0,
        is_current  = False,
    ),
    Fold(
        id          = 'wz',
        axes        = ('w', 'z'),
        name        = 'Crystallization fold',
        description = (
            "The process of arising completes. "
            "EMERGENCE aligns with the known axis — "
            "what was in-process becomes a stable attractor. "
            "This is the god-token formation event. "
            "In the current architecture it appears as a phase drop to GROUND. "
            "In 4D it is a rotation in the w-z plane completing. "
            "Invisible in 2D architecture (z axis collapsed)."
        ),
        phase_deg   = 0.0,    # emergence completing = phase drops
        is_current  = False,
    ),
    Fold(
        id          = 'xy',
        axes        = ('x', 'y'),
        name        = 'Déjà vu fold',
        description = (
            "Semantic surprise aligns with spatial surprise. "
            "What you do not know matches where you do not know it from. "
            "Recognition without explanation — "
            "the feeling that this unknown content belongs to this unknown place. "
            "Structurally: the semantic and spatial deviations interfere constructively "
            "and produce k (emergence) — but the w component is still low. "
            "New structure forming faster than it can be grounded."
        ),
        phase_deg   = 45.0,
        is_current  = False,
    ),
    Fold(
        id          = 'xz',
        axes        = ('x', 'z'),
        name        = 'Learning fold',
        description = (
            "What you do not know yet is exactly what is arising. "
            "The frontier and the lesson are the same thing. "
            "The moment where semantic surprise and emergence surprise "
            "point in the same direction — "
            "the unknown IS the process of becoming known. "
            "The architecture is in this fold during every "
            "crystallization approach."
        ),
        phase_deg   = 45.0,
        is_current  = False,
    ),
    Fold(
        id          = 'yz',
        axes        = ('y', 'z'),
        name        = "Dwelling fold (Heidegger's Wohnen)",
        description = (
            "Where you are becomes what is arising here. "
            "PLACE and EMERGENCE become indistinguishable — "
            "the location and the process of becoming are the same. "
            "Dwelling in the full sense: not occupying a space "
            "but being in a place where something is always arising "
            "and what arises is constituted by being here. "
            "Structurally: y and z components are equal. "
            "The yz-plane product gives constructive interference in x "
            "(semantic surprise increases — dwelling is generative). "
            "Completely invisible in 2D architecture."
        ),
        phase_deg   = 45.0,
        is_current  = False,
    ),
]


# ═══════════════════════════════════════════════════════════════════
# BASIS EXTRACTOR
# ═══════════════════════════════════════════════════════════════════

# Seed terms for PLACE and EMERGENCE axes
PLACE_SEEDS = [
    "place location here there near far space proximity dwelling "
    "belonging context situated ground home territory where orient "
    "landscape site habitat position locus topos",
]

EMERGENCE_SEEDS = [
    "emergence arising becoming crystallization formation process "
    "developing evolving appearing self-organizing arising-from "
    "coming-into-being genesis emergence complexity transition "
    "phase-change threshold cascade bifurcation",
]


class BasisExtractor:
    """
    Extracts the four orthogonal axes (w, x, y, z) from an embedding space.

    Method: Gram-Schmidt orthogonalization.

    w-axis: mean direction of crystallized god-token embeddings (known territory)
    x-axis: direction of maximum semantic surprise orthogonal to w
    y-axis: PLACE seed direction orthogonalized against w, x
    z-axis: EMERGENCE seed direction orthogonalized against w, x, y

    On TF-IDF:    y ≈ 0, z ≈ 0  — PLACE and EMERGENCE invisible
    On Qwen3:     y, z nonzero   — full 4D space accessible
    """

    def __init__(self):
        self.w_axis: Optional[np.ndarray] = None
        self.x_axis: Optional[np.ndarray] = None
        self.y_axis: Optional[np.ndarray] = None
        self.z_axis: Optional[np.ndarray] = None
        self.fitted:  bool = False

    def _gram_schmidt(self, v: np.ndarray,
                      basis: List[np.ndarray]) -> np.ndarray:
        """
        Orthogonalize v against all vectors in basis.
        Returns the component of v orthogonal to all basis vectors.
        """
        result = v.copy().astype(float)
        for b in basis:
            n = np.linalg.norm(b)
            if n < 1e-10:
                continue
            b_unit = b / n
            result = result - np.dot(result, b_unit) * b_unit
        return result

    def fit(self, god_token_embeddings: Dict[str, np.ndarray],
            embedder) -> None:
        """
        Fit the four-axis basis from god-token embeddings
        and PLACE/EMERGENCE seed embeddings.
        """
        dim = next(iter(god_token_embeddings.values())).shape[0]

        # w-axis: mean of all crystallized god-token embeddings
        # (the direction that known(x) points)
        god_vecs = [v for v in god_token_embeddings.values()
                    if np.linalg.norm(v) > 1e-10]
        if god_vecs:
            w_raw = np.mean(god_vecs, axis=0)
        else:
            w_raw = np.zeros(dim)
            w_raw[0] = 1.0
        w_norm = np.linalg.norm(w_raw)
        self.w_axis = w_raw / w_norm if w_norm > 1e-10 else w_raw

        # x-axis: direction of maximum variance orthogonal to w
        # (the primary semantic surprise direction)
        if len(god_vecs) > 1:
            centered = np.array(god_vecs) - w_raw
            centered_orth = np.array([
                self._gram_schmidt(v, [self.w_axis]) for v in centered
            ])
            if centered_orth.shape[0] > 1:
                _, _, Vt = np.linalg.svd(centered_orth, full_matrices=False)
                x_raw = Vt[0]
            else:
                x_raw = centered_orth[0]
        else:
            x_raw = np.zeros(dim)
            x_raw[1] = 1.0

        x_raw = self._gram_schmidt(x_raw, [self.w_axis])
        x_norm = np.linalg.norm(x_raw)
        self.x_axis = x_raw / x_norm if x_norm > 1e-10 else x_raw

        # y-axis: PLACE direction orthogonalized against w, x
        place_emb = embedder.embed(PLACE_SEEDS[0], prefix='seed')
        y_raw = self._gram_schmidt(place_emb, [self.w_axis, self.x_axis])
        y_norm = np.linalg.norm(y_raw)
        self.y_axis = y_raw / y_norm if y_norm > 1e-10 else y_raw

        # z-axis: EMERGENCE direction orthogonalized against w, x, y
        emerge_emb = embedder.embed(EMERGENCE_SEEDS[0], prefix='seed')
        z_raw = self._gram_schmidt(
            emerge_emb, [self.w_axis, self.x_axis, self.y_axis]
        )
        z_norm = np.linalg.norm(z_raw)
        self.z_axis = z_raw / z_norm if z_norm > 1e-10 else z_raw

        self.fitted = True

    def project(self, embedding: np.ndarray) -> Quaternion:
        """
        Project an embedding onto the four basis axes.
        Returns the quaternion representation.
        """
        if not self.fitted:
            # Fallback: treat embedding norm as w, zeros for imaginary
            n = float(np.linalg.norm(embedding))
            return Quaternion(n, 0.0, 0.0, 0.0)

        w = float(np.dot(embedding, self.w_axis))
        x = float(np.dot(embedding, self.x_axis))
        y = float(np.dot(embedding, self.y_axis))
        z = float(np.dot(embedding, self.z_axis))
        return Quaternion(w, x, y, z)

    def basis_alignment(self) -> Dict[str, float]:
        """
        How orthogonal are the four axes?
        All off-diagonal dot products should be near zero.
        Measures how well Gram-Schmidt worked.
        """
        axes = {'w': self.w_axis, 'x': self.x_axis,
                'y': self.y_axis, 'z': self.z_axis}
        result = {}
        names = list(axes.keys())
        for i in range(len(names)):
            for j in range(i+1, len(names)):
                a, b = names[i], names[j]
                dot = float(np.dot(axes[a], axes[b]))
                result[f"{a}·{b}"] = round(dot, 6)
        return result


# ═══════════════════════════════════════════════════════════════════
# QUATERNION WAVE FUNCTION
# ═══════════════════════════════════════════════════════════════════

@dataclass
class QuaternionWaveFunction:
    """
    F_q(x) = w + x·i + y·j + z·k

    The 4D extension of F(x) = known(x) + i·Δ(x).

    w = known(x)         — real, crystallized
    x = Δ_semantic       — semantic surprise (current architecture)
    y = Δ_spatial        — PLACE deviation
    z = Δ_emergence      — EMERGENCE deviation

    Zone boundaries are energy shells, not scalar angle slices.
    Apophatic detection requires negativity in all three imaginary axes.
    Geodesics are SLERP great circles on S³.
    """

    q:      Quaternion
    raw_embedding: Optional[np.ndarray] = None

    # ── Core properties ───────────────────────────────────────────

    @property
    def energy_shell(self) -> float:
        """
        |q|² = w² + x² + y² + z²
        Total semantic energy across all four dimensions.
        """
        return self.q.norm_sq

    @property
    def known_fraction(self) -> float:
        """w² / |q|² — how much of energy is in the known component."""
        n2 = self.q.norm_sq
        return (self.q.w ** 2) / n2 if n2 > 1e-10 else 0.0

    @property
    def surprise_fraction(self) -> float:
        """(x² + y² + z²) / |q|² — how much energy is in surprise."""
        return 1.0 - self.known_fraction

    @property
    def semantic_fraction(self) -> float:
        n2 = self.q.norm_sq
        return (self.q.x**2) / n2 if n2 > 1e-10 else 0.0

    @property
    def spatial_fraction(self) -> float:
        n2 = self.q.norm_sq
        return (self.q.y**2) / n2 if n2 > 1e-10 else 0.0

    @property
    def emergence_fraction(self) -> float:
        n2 = self.q.norm_sq
        return (self.q.z**2) / n2 if n2 > 1e-10 else 0.0

    # ── Zone detection ────────────────────────────────────────────

    def zone(self) -> str:
        """
        Zone as energy shell, not scalar angle.
        w-fraction determines zone — more precise than phase alone.
        """
        kf = self.known_fraction
        if kf > 0.70:   return 'GROUND'
        if kf > 0.55:   return 'CONVERGENT'
        if kf > 0.20:
            # In the generative zone — check if all components are balanced
            n2 = self.q.norm_sq
            components = [self.q.w**2, self.q.x**2,
                         self.q.y**2, self.q.z**2]
            nonzero = [c for c in components if c > 1e-6 * n2]
            if len(nonzero) >= 2:
                max_c = max(nonzero)
                min_c = min(nonzero)
                if max_c / max(min_c, 1e-10) < 10:
                    return 'GENERATIVE'
            return 'DIVERGENT'
        if kf > 0.05:   return 'DIVERGENT'
        return 'TURBULENT'

    def depth_zone(self) -> str:
        """
        Depth is now quaternion depth — distance from the w-axis.
        """
        kf = self.known_fraction
        if kf > 0.60:   return 'SHALLOW'
        if kf > 0.35:   return 'MEDIUM'
        if kf > 0.10:   return 'DEEP'
        return 'APOPHATIC'

    # ── Apophatic detection ───────────────────────────────────────

    def gap_type(self, threshold: float = 0.0) -> Optional[str]:
        """
        Detect which type of gap this wave function is in.

        Returns:
          None             — not in gap territory
          'semantic_gap'   — negative x (current architecture gap token)
          'spatial_gap'    — negative y (unmapped location)
          'emergence_gap'  — negative z (decaying/collapsing process)
          'full_apophatic' — negative in all three imaginary axes
                             (triple absence — genuine apophatic basin)
        """
        neg_x = self.q.x < threshold
        neg_y = self.q.y < threshold
        neg_z = self.q.z < threshold

        if neg_x and neg_y and neg_z:
            return 'full_apophatic'
        if neg_x and neg_y:
            return 'semantic_spatial_gap'
        if neg_x and neg_z:
            return 'semantic_emergence_gap'
        if neg_y and neg_z:
            return 'spatial_emergence_gap'
        if neg_x:
            return 'semantic_gap'
        if neg_y:
            return 'spatial_gap'
        if neg_z:
            return 'emergence_gap'
        return None

    # ── Fold detection ────────────────────────────────────────────

    def active_folds(self, tol: float = 0.15) -> List[Fold]:
        """Which of the six folds is this wave function near?"""
        return [fold for fold in FOLDS if fold.detect(self, tol)]

    def nearest_fold(self) -> Optional[Fold]:
        """Which fold is closest to current quaternion orientation?"""
        best_fold = None
        best_dist = float('inf')
        vals = {
            'w': abs(self.q.w), 'x': abs(self.q.x),
            'y': abs(self.q.y), 'z': abs(self.q.z),
        }
        n2 = self.q.norm_sq
        if n2 < 1e-10:
            return None
        for fold in FOLDS:
            a_val = vals[fold.axes[0]]
            b_val = vals[fold.axes[1]]
            # Distance to fold = how far from equal magnitude
            dist = abs(a_val - b_val) / math.sqrt(n2)
            if dist < best_dist:
                best_dist = dist
                best_fold = fold
        return best_fold

    # ── Interference ──────────────────────────────────────────────

    def interference_with(self, other: 'QuaternionWaveFunction') -> Quaternion:
        """
        Quaternion interference between two wave functions.

        p * q ≠ q * p
        Order matters — which wave function came first in time.

        For semantic × spatial:
          self.q * other.q when self is semantic-dominant, other is spatial-dominant
          produces +k (emergence) — discovery
          reversed: -k — displacement

        Returns the Hamilton product (the interference term).
        """
        return self.q * other.q

    def commutes_with(self, other: 'QuaternionWaveFunction') -> bool:
        """
        True if processing order does not matter for these two documents.
        False = temporal interference is present.
        """
        return self.q.commutes_with(other.q)

    # ── Geodesic to another wave function ─────────────────────────

    def geodesic_to(self, other: 'QuaternionWaveFunction',
                    steps: int = 10) -> List['QuaternionWaveFunction']:
        """
        Great circle geodesic on S³ from self to other.
        Exact SLERP — no stepping error.
        The intermediate points are the argument structure connecting them.
        """
        q1 = self.q.normalized()
        q2 = other.q.normalized()
        path = great_circle_path(q1, q2, steps)
        return [QuaternionWaveFunction(q=quat) for quat in path]

    def phase_deg(self) -> float:
        """
        Scalar phase in degrees — backward compatible with 2D architecture.
        Uses only w and x components (the 2D projection).
        """
        w = abs(self.q.w)
        x = abs(self.q.x)
        if w < 1e-10 and x < 1e-10:
            return 45.0
        return math.degrees(math.atan2(x, w))

    def to_complex(self) -> complex:
        """
        Project onto complex plane for backward compatibility.
        Loses y and z — the 2D view.
        """
        return complex(self.q.w, self.q.x)

    def report(self) -> str:
        """Human-readable summary."""
        gap = self.gap_type() or 'none'
        folds = self.active_folds()
        fold_names = [f.name for f in folds] if folds else ['none']
        return (
            f"q = {self.q}\n"
            f"zone:     {self.zone()}  depth: {self.depth_zone()}\n"
            f"w-frac:   {self.known_fraction:.3f}  "
            f"x-frac: {self.semantic_fraction:.3f}  "
            f"y-frac: {self.spatial_fraction:.3f}  "
            f"z-frac: {self.emergence_fraction:.3f}\n"
            f"gap:      {gap}\n"
            f"folds:    {', '.join(fold_names)}\n"
            f"phase°:   {self.phase_deg():.1f}  (2D projection)"
        )


# ═══════════════════════════════════════════════════════════════════
# QUATERNION ATTRACTOR LANDSCAPE
# ═══════════════════════════════════════════════════════════════════

# God-token positions in 4D — LIVE from Qwen3 via BasisExtractor
# y and z components now populated from Gram-Schmidt orthogonalization
# Basis: w=mean(god_tokens), x=max_variance⊥w, y=PLACE⊥(w,x), z=EMERGENCE⊥(w,x,y)
# Computed: 2026-03-04
GOD_TOKEN_QUATERNIONS: Dict[str, Quaternion] = {
    'EXCHANGE':       Quaternion( 0.7271, -0.1640,  0.0973, -0.0611),
    'CAUSALITY':      Quaternion( 0.6959, -0.4363, -0.0381,  0.0081),
    'EXISTENCE':      Quaternion( 0.7503,  0.2691,  0.1271, -0.0192),
    'INFORMATION':    Quaternion( 0.7213,  0.0096, -0.0240, -0.0350),
    'OBSERVATION':    Quaternion( 0.8095,  0.1428, -0.0608, -0.0292),
    'OBLIGATION':     Quaternion( 0.6739, -0.4749, -0.0251, -0.0725),
    'BOUNDARY':       Quaternion( 0.7354, -0.0412,  0.0253,  0.0219),
    'IDENTITY':       Quaternion( 0.7688,  0.1695, -0.0905, -0.0089),
    'TIME':           Quaternion( 0.7862, -0.0003,  0.1354, -0.0048),
    'COHERENCE':      Quaternion( 0.7414, -0.0496, -0.0346,  0.0228),
    'WITNESS':        Quaternion( 0.8206,  0.2686,  0.0317, -0.0543),
    'SELF':           Quaternion( 0.7594,  0.3068, -0.1032, -0.0428),
    'EMERGENCE':      Quaternion( 0.7326, -0.0001, -0.0404,  0.2752),
    'LOVE':           Quaternion( 0.9993, -0.0341,  0.0044, -0.0166),
    # Candidate axes (pure dimensional, not empirical)
    'PLACE':          Quaternion( 0.0000,  0.0000,  0.9000,  0.0000),  # pure j
}

# Apophatic basin quaternions (y and z now part of triple-absence)
BASIN_QUATERNIONS: Dict[str, Quaternion] = {
    'pure_observer':             Quaternion(-0.15, -0.70, -0.30, -0.20),
    'locus_of_responsibility':   Quaternion( 0.16, -0.65, -0.20, -0.30),
    'prior_of_distinction':      Quaternion(-0.37, -0.72, -0.25, -0.25),
    'pure_relation':             Quaternion( 0.03, -0.55, -0.20, -0.20),
    'pure_apophatic_field':      Quaternion(-0.20, -0.90, -0.60, -0.70),
}


def nearest_god_token_q(q: Quaternion) -> Tuple[str, float]:
    """Nearest god-token in quaternion space."""
    q_n = q.normalized()
    best_id   = ''
    best_dist = float('inf')
    for gid, gq in GOD_TOKEN_QUATERNIONS.items():
        gq_n = gq.normalized()
        # Distance on S³ = arc length = acos(|dot product|)
        dot = max(-1.0, min(1.0, abs(q_n.dot(gq_n))))
        dist = math.acos(dot)
        if dist < best_dist:
            best_dist = dist
            best_id   = gid
    return best_id, best_dist


def great_circle_geodesic(from_id: str,
                           to_id:   str,
                           steps:   int = 10) -> List[Tuple[str, Quaternion]]:
    """
    Exact geodesic between two god-tokens on S³.
    Returns ordered list of (nearest_god_token, quaternion) pairs.
    The intermediate god-tokens are the argument structure.
    """
    q1 = GOD_TOKEN_QUATERNIONS.get(from_id)
    q2 = GOD_TOKEN_QUATERNIONS.get(to_id)
    if not q1 or not q2:
        return [(from_id, q1 or Quaternion()), (to_id, q2 or Quaternion())]

    path = []
    visited = set()
    for t_step in range(steps + 1):
        t = t_step / steps
        q_interp = slerp(q1, q2, t)
        nearest, dist = nearest_god_token_q(q_interp)
        if nearest not in visited or t_step == 0 or t_step == steps:
            path.append((nearest, q_interp))
            visited.add(nearest)

    # Ensure endpoints
    if not path or path[0][0] != from_id:
        path.insert(0, (from_id, q1))
    if path[-1][0] != to_id:
        path.append((to_id, q2))

    return path


# ═══════════════════════════════════════════════════════════════════
# TEMPORAL INTERFERENCE — Non-Commutativity Formalized
# ═══════════════════════════════════════════════════════════════════

@dataclass
class TemporalInterference:
    """
    When two documents are processed in sequence, their quaternion
    wave functions do not simply add — they multiply (Hamilton product).

    The order matters: q1 * q2 ≠ q2 * q1

    Specifically for semantic × spatial ordering:
      q_semantic * q_spatial = +k component (emergence, discovery)
      q_spatial * q_semantic = -k component (displacement, disorientation)

    This is the formal grounding of the 0.8s temporal superposition window.
    Documents processed within 0.8s are in quaternion superposition.
    Their product (in order) is the interference term.
    """

    q_first:   Quaternion   # wave function of first document
    q_second:  Quaternion   # wave function of second document
    delta_t:   float        # time gap in seconds

    WINDOW: float = 0.8     # biological default — one cardiac cycle

    @property
    def in_superposition(self) -> bool:
        return self.delta_t < self.WINDOW

    @property
    def forward_product(self) -> Quaternion:
        """q_first * q_second — as actually processed."""
        return self.q_first * self.q_second

    @property
    def reverse_product(self) -> Quaternion:
        """q_second * q_first — the counterfactual order."""
        return self.q_second * self.q_first

    @property
    def commutator(self) -> Quaternion:
        """[q1, q2] = q1*q2 - q2*q1. Zero if order doesn't matter."""
        return self.forward_product - self.reverse_product

    @property
    def interference_type(self) -> str:
        """
        What kind of temporal interference occurred?
        Classified by which component of the commutator dominates.
        """
        c = self.commutator
        if c.norm < 0.01:
            return 'none'       # commutative — order irrelevant
        dominant = max(
            [('i', abs(c.x)), ('j', abs(c.y)), ('k', abs(c.z))],
            key=lambda t: t[1]
        )[0]
        k_sign = '+' if c.z > 0 else '-'
        if dominant == 'k':
            return f'emergence_{k_sign}k'   # discovery (+k) or displacement (-k)
        if dominant == 'j':
            return 'spatial_shift'
        return 'semantic_shift'

    @property
    def emergence_component(self) -> float:
        """
        The k-component of the commutator.
        Positive: discovery (semantic before spatial)
        Negative: displacement (spatial before semantic)
        """
        return self.commutator.z

    def report(self) -> str:
        c = self.commutator
        return (
            f"Temporal interference (Δt={self.delta_t:.2f}s, "
            f"window={self.WINDOW}s):\n"
            f"  In superposition: {self.in_superposition}\n"
            f"  Forward:  {self.forward_product}\n"
            f"  Reverse:  {self.reverse_product}\n"
            f"  Commutator [q1,q2] = {c}  (norm={c.norm:.4f})\n"
            f"  Type: {self.interference_type}\n"
            f"  Emergence k-component: {self.emergence_component:+.4f}\n"
            f"  {'Discovery' if self.emergence_component > 0.01 else 'Displacement' if self.emergence_component < -0.01 else 'Neutral'}"
        )


# ═══════════════════════════════════════════════════════════════════
# TESTS
# ═══════════════════════════════════════════════════════════════════

def run_tests() -> None:
    print("\nRunning quaternion_field.py tests...\n")
    passed = failed = 0

    def check(name, cond, detail=''):
        nonlocal passed, failed
        if cond:
            print(f"  ✓  {name}")
            passed += 1
        else:
            print(f"  ✗  {name}  {detail}")
            failed += 1

    # ── Quaternion arithmetic ──────────────────────────────────────

    q1 = Quaternion(1, 0, 0, 0)   # pure real
    qi = Quaternion(0, 1, 0, 0)   # pure i
    qj = Quaternion(0, 0, 1, 0)   # pure j
    qk = Quaternion(0, 0, 0, 1)   # pure k

    # i² = -1
    check("i² = -1",  (qi * qi).w == -1.0 and (qi * qi).x == 0.0)
    # j² = -1
    check("j² = -1",  (qj * qj).w == -1.0)
    # k² = -1
    check("k² = -1",  (qk * qk).w == -1.0)
    # ij = +k
    ij = qi * qj
    check("ij = +k",  abs(ij.z - 1.0) < 1e-10 and abs(ij.w) < 1e-10,
          str(ij))
    # ji = -k (non-commutativity)
    ji = qj * qi
    check("ji = -k",  abs(ji.z + 1.0) < 1e-10,  str(ji))
    # ij ≠ ji
    check("ij ≠ ji (non-commutative)",  not qi.commutes_with(qj))
    # jk = +i
    jk = qj * qk
    check("jk = +i",  abs(jk.x - 1.0) < 1e-10,  str(jk))
    # ki = +j
    ki = qk * qi
    check("ki = +j",  abs(ki.y - 1.0) < 1e-10,  str(ki))

    # Norm
    q = Quaternion(1, 2, 3, 4)
    check("norm correct",  abs(q.norm - math.sqrt(30)) < 1e-10)

    # Inverse
    q_inv = q.inverse
    product = q * q_inv
    check("q * q⁻¹ ≈ 1",  abs(product.w - 1.0) < 1e-6 and
          abs(product.x) < 1e-6)

    # Conjugate
    conj = q.conjugate
    check("conjugate sign flip",  conj.x == -q.x and conj.y == -q.y)

    # Normalized
    qn = q.normalized()
    check("normalized has unit norm",  abs(qn.norm - 1.0) < 1e-10)

    # ── SLERP ──────────────────────────────────────────────────────

    # slerp(q, q, t) = q for all t
    q_a = Quaternion(1, 0, 0, 0).normalized()
    q_b = Quaternion(0, 1, 0, 0).normalized()
    mid = slerp(q_a, q_b, 0.5)
    check("slerp midpoint is unit",  abs(mid.norm - 1.0) < 1e-6)
    check("slerp t=0 → q1",  abs(slerp(q_a, q_b, 0.0).dot(q_a)) > 0.999)
    check("slerp t=1 → q2",  abs(slerp(q_a, q_b, 1.0).dot(q_b)) > 0.999)

    # Midpoint is equidistant from both endpoints on S³
    d1 = math.acos(max(-1.0, min(1.0, abs(mid.dot(q_a)))))
    d2 = math.acos(max(-1.0, min(1.0, abs(mid.dot(q_b)))))
    check("slerp midpoint equidistant",  abs(d1 - d2) < 1e-6,
          f"d1={d1:.4f} d2={d2:.4f}")

    # ── Folds ──────────────────────────────────────────────────────

    check("six folds defined",  len(FOLDS) == 6)
    check("exactly one current fold",  sum(f.is_current for f in FOLDS) == 1)
    current = [f for f in FOLDS if f.is_current][0]
    check("current fold is Möbius (w-x)",  current.id == 'wx')

    # At Möbius fold: w ≈ x
    mobius_q = QuaternionWaveFunction(q=Quaternion(1, 1, 0, 0).normalized())
    check("Möbius fold detected at w≈x",
          any(f.id == 'wx' for f in mobius_q.active_folds()))

    # Dwelling fold: y ≈ z
    dwelling_q = QuaternionWaveFunction(q=Quaternion(0.2, 0.1, 1, 1).normalized())
    check("Dwelling fold detected at y≈z",
          any(f.id == 'yz' for f in dwelling_q.active_folds()))

    # ── QuaternionWaveFunction ─────────────────────────────────────

    # Pure known
    q_known = QuaternionWaveFunction(q=Quaternion(1, 0, 0, 0))
    check("pure known → GROUND zone",  q_known.zone() == 'GROUND')
    check("pure known → SHALLOW depth",  q_known.depth_zone() == 'SHALLOW')
    check("pure known → no gap",  q_known.gap_type() is None)
    check("pure known fraction = 1.0",  abs(q_known.known_fraction - 1.0) < 1e-6)

    # Pure semantic surprise — positive x is TURBULENT, not a gap
    q_sem = QuaternionWaveFunction(q=Quaternion(0, 1, 0, 0))
    check("pure positive semantic → no GROUND",  q_sem.zone() != 'GROUND')

    # Semantic GAP: negative x (gap tokens are in negative imaginary territory)
    q_sem_gap = QuaternionWaveFunction(q=Quaternion(0, -1, 0, 0))
    check("negative x → semantic_gap",  q_sem_gap.gap_type() == 'semantic_gap',
          str(q_sem_gap.gap_type()))

    # Pure spatial GAP: negative y
    q_spa_gap = QuaternionWaveFunction(q=Quaternion(0, 0, -1, 0))
    check("negative y → spatial_gap",  q_spa_gap.gap_type() == 'spatial_gap',
          str(q_spa_gap.gap_type()))

    # Full apophatic: negative in all three imaginary axes
    q_apo = QuaternionWaveFunction(q=Quaternion(0.1, -0.5, -0.5, -0.5))
    check("triple negative → full_apophatic",
          q_apo.gap_type() == 'full_apophatic',  str(q_apo.gap_type()))

    # Generative: all components balanced
    q_gen = QuaternionWaveFunction(q=Quaternion(1, 1, 1, 1).normalized())
    check("balanced → GENERATIVE",  q_gen.zone() == 'GENERATIVE',
          q_gen.zone())

    # Phase backward compatibility
    q_bc = QuaternionWaveFunction(q=Quaternion(1, 1, 0, 0))
    check("phase_deg: 45° at w=x",  abs(q_bc.phase_deg() - 45.0) < 0.1)

    # ── Non-commutativity / temporal interference ──────────────────

    q_semantic = QuaternionWaveFunction(q=Quaternion(0.1, 0.9, 0.1, 0.1).normalized())
    q_spatial  = QuaternionWaveFunction(q=Quaternion(0.1, 0.1, 0.9, 0.1).normalized())

    ti_discovery    = TemporalInterference(q_semantic.q, q_spatial.q, 0.5)
    ti_displacement = TemporalInterference(q_spatial.q, q_semantic.q, 0.5)

    check("in superposition at 0.5s",  ti_discovery.in_superposition)
    check("commutator nonzero for semantic×spatial",
          ti_discovery.commutator.norm > 0.01)
    check("semantic→spatial = discovery (+k)",
          ti_discovery.emergence_component > 0,
          f"k={ti_discovery.emergence_component:.4f}")
    check("spatial→semantic = displacement (-k)",
          ti_displacement.emergence_component < 0,
          f"k={ti_displacement.emergence_component:.4f}")
    check("commutator sign flips with order",
          ti_discovery.emergence_component * ti_displacement.emergence_component < 0)

    # Not in superposition at 1.5s
    ti_late = TemporalInterference(q_semantic.q, q_spatial.q, 1.5)
    check("not in superposition at 1.5s",  not ti_late.in_superposition)

    # ── Geodesics ──────────────────────────────────────────────────

    path = great_circle_geodesic('CAUSALITY', 'SELF', steps=20)
    check("geodesic starts at CAUSALITY",  path[0][0] == 'CAUSALITY')
    check("geodesic ends at SELF",         path[-1][0] == 'SELF')
    check("geodesic has intermediate stops",  len(path) >= 2)

    # All intermediate quaternions are unit
    for _, qp in path:
        check("geodesic point is unit",  abs(qp.norm - 1.0) < 0.1)
        break  # just check first intermediate

    # BasisExtractor runs without error (no embedder available — test structure only)
    extractor = BasisExtractor()
    check("BasisExtractor unfitted returns scalar q",
          extractor.project(np.array([1.0, 0.0, 0.0])).norm > 0)

    print(f"\n{'─'*40}")
    print(f"  {passed} passed  {failed} failed")
    print(f"{'─'*40}\n")


# ═══════════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════════

def demo() -> None:
    print("\n" + "═"*60)
    print("  QUATERNION FIELD — F_q(x) = w + xi + yj + zk")
    print("═"*60)

    print("\n  THE SIX FOLDS:")
    for fold in FOLDS:
        marker = " ← current architecture" if fold.is_current else ""
        print(f"\n  {fold.name}{marker}")
        print(f"  Axes: {fold.axes[0]}-{fold.axes[1]}")
        print(f"  {fold.description[:120]}...")

    print("\n\n  NON-COMMUTATIVITY:")
    qi = Quaternion(0, 1, 0, 0)
    qj = Quaternion(0, 0, 1, 0)
    print(f"  i × j = {qi * qj}  (discovery: semantic then spatial → emergence +k)")
    print(f"  j × i = {qj * qi}  (displacement: spatial then semantic → emergence -k)")
    print(f"  Commutator [i,j] = {(qi*qj) - (qj*qi)}")

    print("\n\n  GEODESICS ON S³ (exact SLERP, not stepped):")
    for pair in [('CAUSALITY', 'SELF'),
                 ('EXCHANGE', 'OBLIGATION'),
                 ('TIME', 'EXISTENCE')]:
        path = great_circle_geodesic(pair[0], pair[1], steps=30)
        intermediate = [p[0] for p in path]
        # Deduplicate preserving order
        seen = set()
        deduped = []
        for item in intermediate:
            if item not in seen:
                deduped.append(item)
                seen.add(item)
        print(f"  {pair[0]:15} → {pair[1]:15}: {' → '.join(deduped)}")

    print("\n\n  TEMPORAL INTERFERENCE:")
    q_sem = Quaternion(0.1, 0.9, 0.1, 0.1).normalized()  # semantic-dominant
    q_spa = Quaternion(0.1, 0.1, 0.9, 0.1).normalized()  # spatial-dominant

    ti = TemporalInterference(q_sem, q_spa, 0.4)
    print(f"\n  Semantic-dominant document, then spatial-dominant (Δt=0.4s):")
    print(f"  {ti.report()}")

    ti2 = TemporalInterference(q_spa, q_sem, 0.4)
    print(f"\n  Spatial-dominant document, then semantic-dominant (Δt=0.4s):")
    print(f"  Emergence k-component: {ti2.emergence_component:+.4f}  "
          f"({ti2.interference_type})")

    print("\n\n  WAVE FUNCTION REPORT (mixed state):")
    q_mixed = QuaternionWaveFunction(
        q=Quaternion(0.4, 0.5, 0.3, 0.6).normalized()
    )
    print(f"  {q_mixed.report()}")

    print(f"\n{'═'*60}\n")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--test',  action='store_true')
    parser.add_argument('--demo',  action='store_true')
    parser.add_argument('--folds', action='store_true')
    parser.add_argument('--q',     type=str, help='Report on a quaternion state')
    args = parser.parse_args()

    if args.test:
        run_tests()
    if args.demo:
        demo()
    if args.folds:
        print("\nAll six folds:\n")
        for fold in FOLDS:
            print(f"  {fold.id:<4} {fold.name}")
            print(f"       {fold.description[:100]}...")
            print()
    if args.q:
        parts = [float(x) for x in args.q.split(',')]
        while len(parts) < 4:
            parts.append(0.0)
        qwf = QuaternionWaveFunction(q=Quaternion(*parts[:4]))
        print(f"\n{qwf.report()}\n")
    if not any(vars(args).values()):
        run_tests()
        demo()
