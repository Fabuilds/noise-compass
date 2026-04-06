import numpy as np
from noise_compass.system.interference_engine import InterferenceEngine
import time

def verify_aversive():
    print("--- STARTING AVERSIVE DAMPING VERIFICATION ---")
    engine = InterferenceEngine() # Allow pre-load for meaningful field
    
    intent = "This is a failing logical path that we must avoid."
    vec = engine.embed(intent)
    
    # 1. Baseline - get resonance before failure is cached
    field_baseline = engine.combined_field_from_embedding(vec)
    mags = [v['magnitude'] for v in field_baseline.values()]
    if not mags:
        # Fallback if no tokens are loaded
        print("[WARNING] No tokens loaded. Injecting dummy magnitude for structural test.")
        max_base = 0.8
    else:
        max_base = max(mags)
    print(f"Baseline Max Magnitude: {max_base:.4f}")
    
    # 2. Record Failure
    print(f"Recording Failure for intent: '{intent}'")
    engine.failure_cache.record_failure(vec, "Test deliberate failure")
    
    # 3. Test Damping
    field_damped = engine.combined_field_from_embedding(vec)
    max_damped = max([v['magnitude'] for v in field_damped.values()])
    print(f"Damped Max Magnitude: {max_damped:.4f}")
    
    efficiency = (1.0 - (max_damped / (max_base + 1e-8))) * 100
    print(f"Damping Efficiency: {efficiency:.2f}%")
    
    if max_damped < max_base * 0.5:
        print("VERIFICATION SUCCESS: Resonance significantly damped.")
    else:
        print("VERIFICATION FAILURE: Resonance not sufficiently damped.")

if __name__ == "__main__":
    verify_aversive()
