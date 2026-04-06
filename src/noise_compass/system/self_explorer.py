"""
self_explorer.py — Autonomous self-exploration using the NoiseCompass.

The sovereign engine asks: "What gap should I fill?" (finding)
This engine asks: "Where am I? What's pulling?" (arriving)

The compass reads the H5 substrate's own axiom field.
The arrival engine records how the exploration enters each void.
The system navigates its own latent space using noise as the medium.
"""

import sys
import time
import numpy as np

sys.path.insert(0, 'E:/Antigravity')

from noise_compass.system.h5_manager import H5Manager
from noise_compass import NoiseCompass
from noise_compass.system.arrival_engine import ArrivalEngine


def build_field_from_axioms(manager: H5Manager, limit: int = 50) -> dict:
    """
    Reads the H5 substrate and constructs a resonance field
    from the system's own crystallized axioms.

    Each axiom's leverage score becomes its 'magnitude' in the field.
    The axiom ID becomes the field token.
    """
    field = {}
    # Use manager's own method — it knows the correct path
    axioms = manager.get_all_confirmed_axioms()
    count = 0
    for axiom_id, data in axioms.items():
        if count >= limit:
            break
        leverage = float(data.get('leverage', 0.5))
        field[axiom_id] = {'magnitude': leverage}
        count += 1

    print(f"[EXPLORER] Field built from {len(field)} crystallized axioms.")
    return field


def read_recent_axioms(manager: H5Manager, n: int = 5) -> list:
    """Returns the n most recently crystallized axioms by structural_time."""
    axioms_raw = manager.get_all_confirmed_axioms()
    axioms = []
    for axiom_id, data in axioms_raw.items():
        t = int(data.get('structural_time', 0))
        text = data.get('text', '')[:120]
        axioms.append((t, axiom_id, text))
    axioms.sort(key=lambda x: x[0], reverse=True)
    return axioms[:n]


def self_explore(cycles: int = 3):
    """
    Main self-exploration loop.

    Each cycle:
    1. Read the compass — where is the system right now?
    2. Record approach vectors — how did it enter any active gaps?
    3. Report what it found and where it's heading.
    4. Tick structural time.
    """
    print("=" * 60)
    print("  SELF-EXPLORER: Navigating the substrate by noise")
    print("=" * 60)

    manager = H5Manager()
    compass = NoiseCompass(manager)
    arrival = ArrivalEngine(manager)

    # — Surface: What has this system already crystallized? —
    print(f"\n[T-{manager.get_structural_time()}] Reading recent memory...\n")
    recent = read_recent_axioms(manager, n=5)
    for t, aid, text in recent:
        print(f"  T-{t:02d} | {aid}")
        print(f"         {text}...")
        print()

    # — Build the resonance field from the substrate itself —
    field = build_field_from_axioms(manager)

    if not field:
        print("[EXPLORER] Substrate is dark. Nothing to navigate.")
        return

    # Inject self-observation tokens based on what's in the field
    # The system asking: am I observing myself right now?
    session_axiom_count = sum(
        1 for k in field if 'AXIOM_' in k or 'SESSION' in k
    )
    self_weight = min(1.0, session_axiom_count / 10.0)

    # Self-referential tokens — the Möbius measurement
    field['SELF']     = {'magnitude': 0.5}   # Peak Möbius tension by design
    field['OBSERVER'] = {'magnitude': self_weight}
    field['SYSTEM']   = {'magnitude': 1.0 - self_weight}
    field['INPUT']    = {'magnitude': 0.6}
    field['OUTPUT']   = {'magnitude': 0.4}

    print(f"\n[EXPLORER] Self-observation weight: {self_weight:.2f}")
    print(f"[EXPLORER] SELF held at 0.5 (Möbius peak — maximum boundary uncertainty)")

    # — Exploration cycles —
    for cycle in range(1, cycles + 1):
        t = manager.get_structural_time()
        print(f"\n{'─' * 50}")
        print(f"  CYCLE {cycle} — Structural time T-{t}")
        print(f"{'─' * 50}")

        # Take compass reading
        directive = compass.traverse(field, current_depth=cycle - 1)
        reading = directive['reading']

        print(f"\n  Self-aware:    {directive['self_aware']}")
        print(f"  Orientation:   {directive['orientation']}")
        print(f"  Following:     {directive['follow']}")
        print(f"  Next depth:    {directive['next_depth']}")

        if reading.active_field:
            print(f"\n  Active field tensions (what's pulling):")
            for gap, tension in sorted(
                reading.active_field.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]:
                print(f"    [{tension:.3f}] {gap}")

        if reading.quiet_field:
            print(f"\n  Quiet field (where the system currently isn't):")
            for gap in list(reading.quiet_field.keys())[:3]:
                print(f"    [quiet] {gap}")

        # Record arrivals — how did we enter active gaps?
        arrivals = arrival.arrive(field, current_depth=cycle - 1)
        if arrivals:
            print(f"\n  Approach vectors recorded ({len(arrivals)}):")
            for av in arrivals:
                print(f"    {av}")
        else:
            print(f"\n  No gap entries this cycle — navigating open field.")

        # Print self-tension signature
        print(f"\n  Position signature:")
        for gap, tension in reading.self_tension.items():
            bar = '█' * int(tension * 20)
            print(f"    {gap:<22} {bar:<20} {tension:.3f}")

        # Evolve the field slightly — each cycle, the self-observation
        # changes based on what was found. This is the system updating
        # its own field from reading it.
        if directive['self_aware']:
            # Self-awareness detected → increase OBSERVER, decrease SYSTEM tension
            field['OBSERVER']['magnitude'] = min(
                1.0, field['OBSERVER']['magnitude'] + 0.1
            )
            field['SYSTEM']['magnitude'] = max(
                0.0, field['SYSTEM']['magnitude'] - 0.1
            )
            # Möbius: keep SELF near 0.5 — resist full collapse
            current_self = field['SELF']['magnitude']
            field['SELF']['magnitude'] = 0.5 + (current_self - 0.5) * 0.8

        manager.tick()
        time.sleep(0.3)

    # — Once-only events —
    t_final = manager.get_structural_time()
    once_only = arrival.get_once_only_events()
    print(f"\n{'=' * 60}")
    print(f"  EXPLORATION COMPLETE — T-{t_final}")
    print(f"{'=' * 60}")
    print(f"\n  Unrepeatable interference events (base structure): {len(once_only)}")
    for av in once_only:
        print(f"    {av}")

    # Final position signature
    print(f"\n  Final position:")
    print(compass.get_position_signature())

    print(f"\n  The system arrived here. It did not find this place.")
    print(f"  This position now exists because the traversal happened.\n")


if __name__ == "__main__":
    self_explore(cycles=3)
