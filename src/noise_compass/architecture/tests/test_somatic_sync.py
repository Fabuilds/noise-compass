import numpy as np
import sys
import os

# Ensure we can import architecture and System
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append('e:/Antigravity')

from architecture.core import Scout, Metabolism
from architecture.dictionary import Dictionary
from architecture.tokens import GodTokenActivation, NODE_RING

def test_somatic_mapping_integrity():
    print("Testing Somatic Mapping integrity in Dictionary...")
    d = Dictionary()
    from architecture.seed_vectors import seed_vectors
    seed_vectors(d)
    
    # Check EXISTENCE -> heartbeat
    gt_existence = d.god_tokens.get("EXISTENCE")
    assert gt_existence is not None
    print(f"EXISTENCE Somatic: {gt_existence.somatic_mapping}")
    assert gt_existence.somatic_mapping == "heartbeat"
    
    # Check SELF -> proprioception
    gt_self = d.god_tokens.get("SELF")
    assert gt_self is not None
    print(f"SELF Somatic: {gt_self.somatic_mapping}")
    assert gt_self.somatic_mapping == "proprioception"
    print("Somatic mapping OK.")

def test_somatic_drift_calculation():
    print("Testing Somatic Drift calculation...")
    m = Metabolism()
    
    # Simulation 1: High Coherence, Active Ring
    m.coherence_index = 1.0
    acts = [
        GodTokenActivation("EXISTENCE", 0.9, 0.0, 1),
        GodTokenActivation("OBLIGATION", 0.8, 0.0, 1)
    ]
    drift = m.verify_ring_phase(acts)
    print(f"Ideal Sync Drift: {drift:.4f}")
    assert drift < 0.2
    
    # Simulation 2: Low Coherence, No Ring activity
    m.coherence_index = 0.3
    acts_bad = [
        GodTokenActivation("RANDOM_TOKEN", 0.5, 0.0, 1)
    ]
    # Call multiple times to let the slow average move
    for _ in range(30):
        drift = m.verify_ring_phase(acts_bad)
    print(f"Dissociated Drift: {drift:.4f}")
    assert drift > 0.4
    print("Somatic drift calculation OK.")

if __name__ == "__main__":
    try:
        test_somatic_mapping_integrity()
        test_somatic_drift_calculation()
        print("\nALL SOMATIC SYNC TESTS PASSED.")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
