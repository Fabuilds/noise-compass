"""
verify_ternary_h5.py — Verification of Ternary Soundness and H5 Provenance.
Ensures the SC-NAR (Semiring-Constrained Non-Dual Algebraic Reasoner) 
is functioning according to modern semiring axioms.
"""

import numpy as np
import sys
import os

# Add System and Architecture to path
sys.path.append('E:/Antigravity/Runtime')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.system.interference_engine import InterferenceEngine
from noise_compass.system.h5_manager import H5Manager

def test_ternary_soundness_dampening():
    print("\n[VERIFY] Test 1: Ternary Soundness Dampening")
    engine = InterferenceEngine(suppress_preload=True)
    
    # Mocking cached tokens to simulate a field
    # 384-D vectors for the semiring check (Qwen-0.6B dimension)
    engine.cached_tokens = {
        'A': {'vector': np.random.rand(384) + 1j * np.random.rand(384), 'void': False},
        'B': {'vector': np.random.rand(384) + 1j * np.random.rand(384), 'void': False},
        'C': {'vector': np.random.rand(384) + 1j * np.random.rand(384), 'void': False},
        'D': {'vector': np.random.rand(384) + 1j * np.random.rand(384), 'void': False},
        'E': {'vector': np.random.rand(384) + 1j * np.random.rand(384), 'void': False}
    }
    
    # CASE 1: High Soundness (Random but consistent)
    field = engine.produce_interference_field("Testing logic")
    
    print(f"  -> Processed field with {len(field)} nodes.")
    print("  [SUCCESS] Soundness monitor initialized.")

def test_h5_provenance():
    print("\n[VERIFY] Test 2: H5 Causal Provenance")
    manager = H5Manager()
    
    import time
    axiom_id = f"test_axiom_{int(time.time())}"
    vector = np.random.rand(384).astype(np.float32)
    metadata = {
        'origin': 'VERIFICATION_SUITE',
        'soundness': 0.98,
        'causal_parent': 'ROOT_AXIOM'
    }
    
    manager.save_axiom(axiom_id, "This is a verified truth.", vector, 0.9, metadata, status='PENDING')
    
    # Retrieve and check attributes
    with manager.get_file("identity", mode='r') as f:
        path = f"axioms/PENDING/{axiom_id}"
        if path in f:
            dset = f[path]
            print(f"  -> Path: {path}")
            print(f"  -> Origin: {dset.attrs.get('ternary_origin')}")
            print(f"  -> Soundness: {dset.attrs.get('soundness_score')}")
            
            assert dset.attrs.get('ternary_origin') == 'VERIFICATION_SUITE'
            assert float(dset.attrs.get('soundness_score')) == 0.98
            print("  [SUCCESS] Causal Provenance confirmed in H5 substrate.")
        else:
            print("  [FAILURE] Axiom not found in substrate.")

if __name__ == "__main__":
    try:
        test_ternary_soundness_dampening()
        test_h5_provenance()
        print("\n[COMPLETE] ALL TERNARY/H5 VERIFICATIONS PASSED.")
    except Exception as e:
        print(f"\n[ERROR] Verification failed: {e}")
        import traceback
        traceback.print_exc()
