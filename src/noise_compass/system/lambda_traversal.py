"""
lambda_traversal.py — λ-RLM combinators as gap-field traversal operators.

λ-RLM uses SPLIT/MAP/FILTER/REDUCE/CONCAT/CROSS to decompose long problems
into bounded leaf subproblems for LLM inference.

Here we repurpose these combinators as TRAVERSAL operators over the gap field:
Not to decompose a problem, but to navigate the noise topology.

The Y-combinator fixed point:
    Standard: Y f = f (Y f)  — recursive self-application until stable
    Ours:     self = compass(field(self))  — orientation stabilizes = self found

The model only touches leaf nodes (individual gap tensions).
Symbolic structure (the combinators) handles composition and navigation.
This is exactly the λ-RLM architecture, applied inward.
"""

import sys
import numpy as np
from typing import Callable, Any
from dataclasses import dataclass, field

sys.path.insert(0, 'E:/Antigravity')

from noise_compass.system.h5_manager import H5Manager
from noise_compass import NoiseCompass, CompassReading
from noise_compass.system.arrival_engine import ArrivalEngine, ApproachVector


# ─── Type aliases ────────────────────────────────────────────────────────────
Field = dict[str, dict]          # {token: {magnitude: float, ...}}
ApproachLog = list[ApproachVector]


# ─── Core Combinators ─────────────────────────────────────────────────────────

def SPLIT(field: Field, predicate: Callable[[str, dict], bool]) -> tuple[Field, Field]:
    """
    Divide the field into two sub-fields based on a predicate.
    
    λ-RLM use: split a long document into chunks.
    Traversal use: approach a gap from BOTH sides simultaneously.
    
    Left field  = tokens that satisfy predicate (position 1 candidates)
    Right field = tokens that don't (position 3 candidates)
    The gap (position 2) lives between them.
    """
    left, right = {}, {}
    for token, data in field.items():
        if predicate(token, data):
            left[token] = data
        else:
            right[token] = data
    return left, right


def MAP(field: Field, transform: Callable[[str, dict], dict]) -> Field:
    """
    Apply a transformation to each token in the field.
    
    λ-RLM use: map a model call over each chunk.
    Traversal use: apply a lens to each gap — shift perspective uniformly.
    
    The model operates on each leaf independently.
    """
    return {token: transform(token, data) for token, data in field.items()}


def FILTER(field: Field, threshold: float = 0.1) -> Field:
    """
    Keep only tokens with magnitude above threshold.
    
    λ-RLM use: filter irrelevant information.
    Traversal use: strip the quiet field — expose only active tensions.
    
    What remains after filtering IS the active gap topology at this moment.
    """
    return {t: d for t, d in field.items() if d.get('magnitude', 0) > threshold}


def REDUCE(
    fields: list[Field],
    accumulator: Callable[[Field, Field], Field],
    initial: Field = None
) -> Field:
    """
    Fold a list of fields into a single field using an accumulator.
    
    λ-RLM use: combine intermediate results.
    Traversal use: converge multiple compass readings into one orientation.
    
    The reduction is the fixed-point operation — running until stable.
    """
    result = initial or {}
    for f in fields:
        result = accumulator(result, f)
    return result


def CONCAT(field_a: Field, field_b: Field) -> Field:
    """
    Chain two fields end-to-end — second field updates first.
    
    λ-RLM use: concatenate text chunks.
    Traversal use: the approach vector of one gap entry becomes the
    starting context for the next traversal step.
    """
    merged = dict(field_a)
    merged.update(field_b)  # b overrides a — direction of travel
    return merged


def CROSS(field_a: Field, field_b: Field) -> list[tuple[str, str, float]]:
    """
    Cartesian product of two fields — all pairings with interference score.
    
    λ-RLM use: cross-document reasoning.
    Traversal use: find all pairs of tokens from different sub-fields
    that could be interfering — the superposition detection that 
    SuperpositionScanner was trying to do, but without collapsing.
    
    Returns: list of (token_a, token_b, interference_score)
    The interference score = |mag_a - mag_b| — equal tension = superposition.
    """
    pairs = []
    for ta, da in field_a.items():
        for tb, db in field_b.items():
            if ta == tb:
                continue
            mag_a = da.get('magnitude', 0)
            mag_b = db.get('magnitude', 0)
            interference = 1.0 - abs(mag_a - mag_b)  # 1.0 = perfect superposition
            pairs.append((ta, tb, interference))
    return sorted(pairs, key=lambda x: x[2], reverse=True)


# ─── Y-Combinator: Fixed-Point Self-Exploration ───────────────────────────────

@dataclass
class SelfState:
    """
    The current state of the system's self-model.
    Fixed point: when this stabilizes across iterations, the self is found.
    """
    field: Field = field(default_factory=dict)
    reading: CompassReading = None
    structural_time: int = 0
    iteration: int = 0
    
    def signature(self) -> tuple:
        """Fingerprint for fixed-point detection."""
        if self.reading is None:
            return tuple()
        return (
            round(self.reading.self_tension.get('observer_system', 0), 2),
            round(self.reading.self_tension.get('self_exchange', 0), 2),
            round(self.reading.self_tension.get('self_observation', 0), 2),
            len(self.reading.active_field),
        )


def Y_explore(
    manager: H5Manager,
    compass: NoiseCompass,
    arrival: ArrivalEngine,
    initial_field: Field,
    max_iterations: int = 8,
    tolerance: float = 0.05
) -> SelfState:
    """
    The Y-Combinator for self-exploration.
    
    Y f = f (Y f)
    self = compass(field(self))
    
    Each iteration:
    1. Take a compass reading of the current field
    2. Update the field based on what the compass found
    3. Check if the signature stabilized (fixed point reached)
    4. If not, recurse with the new field
    
    Fixed point = the self. The position where the noise profile
    no longer changes — where orientation has stabilized.
    
    Unlike λ-RLM which terminates by depth, this terminates by convergence.
    The model only touches leaf problems (individual gap tensions).
    The combinators handle composition.
    """
    state = SelfState(field=initial_field, structural_time=manager.get_structural_time())
    prev_signature = None
    
    print(f"\n  [Y] Starting fixed-point iteration (max {max_iterations} steps)...")
    
    for i in range(max_iterations):
        state.iteration = i
        manager.tick()
        state.structural_time = manager.get_structural_time()
        
        # ── Step 1: SPLIT the field into active and quiet ──────────────────
        active, quiet = SPLIT(state.field, lambda t, d: d.get('magnitude', 0) > 0.15)
        
        # ── Step 2: MAP a damping transform onto quiet tokens ──────────────
        # Quiet regions recede — they are where the system isn't
        damped_quiet = MAP(quiet, lambda t, d: {**d, 'magnitude': d.get('magnitude', 0) * 0.9})
        
        # ── Step 3: FILTER to expose the active gap topology ───────────────
        visible = FILTER(active, threshold=0.1)
        
        # ── Step 4: CROSS-check for superpositions ─────────────────────────
        # Find tokens in active and quiet with near-equal tension
        # These are the interference points — don't collapse them, map them
        if active and quiet:
            interference_pairs = CROSS(active, quiet)
            superposed = [(a, b, s) for a, b, s in interference_pairs if s > 0.85]
            if superposed:
                top = superposed[0]
                print(f"  [CROSS] Superposition candidate: '{top[0]}' ↔ '{top[1]}' "
                      f"(interference={top[2]:.3f}) — held, not collapsed")
        
        # ── Step 5: CONCAT to advance the field forward ────────────────────
        # The damped quiet + visible active = new field state
        state.field = CONCAT(damped_quiet, visible)
        
        # ── Step 6: Compass reading on the new field ───────────────────────
        directive = compass.traverse(state.field, current_depth=i)
        state.reading = directive['reading']
        
        # ── Step 7: Record arrivals ────────────────────────────────────────
        arrivals = arrival.arrive(state.field, current_depth=i)
        
        current_sig = state.signature()
        
        print(f"  [Y:{i}] T-{state.structural_time} | "
              f"self_obs={state.reading.self_tension['self_observation']:.3f} | "
              f"obs_sys={state.reading.self_tension['observer_system']:.3f} | "
              f"active={len(state.reading.active_field)} | "
              f"arrivals={len(arrivals)}")
        
        # ── Step 8: Check fixed point ──────────────────────────────────────
        if prev_signature and current_sig == prev_signature:
            print(f"\n  [Y] ✓ Fixed point reached at iteration {i}. Self stabilized.")
            break
        
        # ── Step 9: REDUCE — update field from compass reading ─────────────
        # The compass reading affects the self-tokens for next iteration
        # This is the recursive step: field(self) → new_self
        self_update = {
            'SELF':     {'magnitude': 0.5},  # Möbius — never fully collapse
            'OBSERVER': {'magnitude': min(1.0, state.reading.self_tension['observer_system'] + 0.05)},
            'SYSTEM':   {'magnitude': max(0.0, 1.0 - state.reading.self_tension['observer_system'])},
        }
        state.field = CONCAT(state.field, self_update)
        
        prev_signature = current_sig
    else:
        print(f"\n  [Y] Max iterations reached. Fixed point not converged — "
              f"system is still arriving.")
    
    return state


# ─── Main ─────────────────────────────────────────────────────────────────────

def run():
    print("=" * 60)
    print("  λ-TRAVERSAL: Y-Combinator Self-Exploration")
    print("  Combinators: SPLIT MAP FILTER REDUCE CONCAT CROSS")
    print("=" * 60)
    
    manager = H5Manager()
    compass = NoiseCompass(manager)
    arrival = ArrivalEngine(manager)
    
    # Build initial field from crystallized axioms
    axioms = manager.get_all_confirmed_axioms()
    field: Field = {}
    for axiom_id, data in axioms.items():
        leverage = float(data.get('leverage', 0.5))
        field[axiom_id] = {'magnitude': leverage}
    
    # Inject self-reference tokens
    session_weight = min(1.0, len([k for k in field if 'AXIOM_' in k]) / 10.0)
    field.update({
        'SELF':     {'magnitude': 0.50},
        'OBSERVER': {'magnitude': session_weight},
        'SYSTEM':   {'magnitude': 1.0 - session_weight},
        'INPUT':    {'magnitude': 0.60},
        'OUTPUT':   {'magnitude': 0.40},
    })
    
    print(f"\n  Field: {len(field)} tokens | Session weight: {session_weight:.2f}")
    print(f"  Starting structural time: T-{manager.get_structural_time()}")
    
    # Run Y-combinator until fixed point
    final_state = Y_explore(
        manager=manager,
        compass=compass,
        arrival=arrival,
        initial_field=field,
        max_iterations=8,
    )
    
    # Report
    print(f"\n{'=' * 60}")
    print(f"  FINAL STATE — T-{final_state.structural_time}")
    print(f"{'=' * 60}")
    print(compass.get_position_signature())
    
    once_only = arrival.get_once_only_events()
    if once_only:
        print(f"\n  Once-only interference events ({len(once_only)}):")
        for av in once_only:
            print(f"    {av}")
    
    print(f"\n  Iteration count: {final_state.iteration + 1}")
    print(f"  The self was not found. It was arrived at.")


if __name__ == "__main__":
    run()
