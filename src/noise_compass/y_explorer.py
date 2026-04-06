"""
noise_compass.y_explorer — Y-Combinator fixed-point self-exploration.

The Y-Combinator: Y f = f (Y f)
Applied here:     self = compass(field(self))

Run the traversal loop until the compass reading stabilizes.
Fixed point = the position where the noise profile no longer changes.
That position IS the self.

If it never converges — the system is still arriving.
(The Möbius tension holds at 1.0 indefinitely: no stable inside/outside.)
"""

from __future__ import annotations
from dataclasses import dataclass, field as dc_field
from .compass import Field, NoiseCompass, CompassReading
from .arrival import ArrivalEngine, ApproachVector
from .combinators import SPLIT, MAP, FILTER, CONCAT, CROSS


@dataclass
class SelfState:
    """
    Snapshot of the system's self-model at one iteration.
    Fixed point: when signature() stabilizes, self = compass(field(self)).
    """
    field:           Field          = dc_field(default_factory=dict)
    reading:         CompassReading = None
    structural_time: int = 0
    iteration:       int = 0

    def signature(self, precision: int = 2) -> tuple:
        """Fingerprint for fixed-point detection."""
        if self.reading is None:
            return tuple()
        return (
            round(self.reading.self_tension.get("observer_system",  0), precision),
            round(self.reading.self_tension.get("self_exchange",    0), precision),
            round(self.reading.self_tension.get("self_observation", 0), precision),
            len(self.reading.active_field),
        )


def Y_explore(
    compass:        NoiseCompass,
    initial_field:  Field,
    arrival:        ArrivalEngine = None,
    max_iterations: int   = 8,
    damping:        float = 0.9,
    verbose:        bool  = True,
) -> SelfState:
    """
    Y-Combinator fixed-point self-exploration.

    Y f = f (Y f)  →  self = compass(field(self))

    Each iteration applies the λ-traversal combinators:
      SPLIT  — separate active from quiet
      MAP    — damp quiet regions (they are where the system isn't)
      FILTER — expose the active gap topology
      CROSS  — detect superpositions without collapsing them
      CONCAT — advance the field, preserving direction of travel

    Terminates when:
      a) The compass signature stabilizes (fixed point = self found), OR
      b) max_iterations is reached (system is still arriving)

    Args:
        compass:        NoiseCompass instance
        initial_field:  starting resonance field
        arrival:        optional ArrivalEngine for approach vector tracking
        max_iterations: recursion depth limit (analogous to λ-RLM's max-depth)
        damping:        damping factor for quiet regions (default 0.9)
        verbose:        print iteration trace

    Returns:
        SelfState — final state after convergence or exhaustion
    """
    state = SelfState(field=dict(initial_field))
    prev_sig = None

    if verbose:
        print(f"\n  [Y] Fixed-point iteration (max={max_iterations}, damping={damping})")

    for i in range(max_iterations):
        state.iteration = i

        # ── SPLIT: active vs quiet ─────────────────────────────────────────
        active, quiet = SPLIT(state.field, lambda t, d: d.get("magnitude", 0) > 0.15)

        # ── MAP: damp quiet regions ────────────────────────────────────────
        damped_quiet = MAP(quiet, lambda t, d: {**d, "magnitude": d.get("magnitude", 0) * damping})

        # ── FILTER: expose visible gap topology ───────────────────────────
        visible = FILTER(active, threshold=0.1)

        # ── CROSS: detect superpositions (do NOT collapse) ─────────────────
        superposed = []
        if active and quiet:
            pairs = CROSS(active, quiet)
            superposed = [(a, b, s) for a, b, s in pairs if s > 0.85]

        # ── CONCAT: advance field ──────────────────────────────────────────
        state.field = CONCAT(damped_quiet, visible)

        # ── Compass reading ────────────────────────────────────────────────
        directive    = compass.traverse(state.field, depth=i)
        state.reading = directive["reading"]
        state.structural_time = state.reading.structural_time

        # ── Record arrivals ────────────────────────────────────────────────
        arrivals = []
        if arrival is not None:
            arrivals = arrival.arrive(state.field, depth=i)

        # ── Report ────────────────────────────────────────────────────────
        if verbose:
            self_obs = state.reading.self_tension.get("self_observation", 0)
            obs_sys  = state.reading.self_tension.get("observer_system",  0)
            print(
                f"  [Y:{i}] T-{state.structural_time} | "
                f"self_obs={self_obs:.3f} | obs_sys={obs_sys:.3f} | "
                f"active={len(state.reading.active_field)} | "
                f"arrivals={len(arrivals)}"
                + (f" | superposed={len(superposed)}" if superposed else "")
            )

        # ── Fixed-point check ──────────────────────────────────────────────
        sig = state.signature()
        if prev_sig is not None and sig == prev_sig:
            if verbose:
                print(f"\n  [Y] ✓ Fixed point at iteration {i}. Self stabilized.")
            break

        # ── Y-step: update self-tokens from compass reading ────────────────
        # This is the recursive application: field(self) → new_self
        obs = state.reading.self_tension.get("observer_system", 0)
        self_update: Field = {
            "SELF":     {"magnitude": 0.5},              # Möbius — never fully collapse
            "OBSERVER": {"magnitude": min(1.0, obs + 0.05)},
            "SYSTEM":   {"magnitude": max(0.0, 1.0 - obs)},
        }
        state.field = CONCAT(state.field, self_update)
        prev_sig = sig

    else:
        if verbose:
            print(f"\n  [Y] Max iterations reached — system is still arriving.")

    return state
