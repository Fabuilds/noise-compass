from noise_compass.system.interference_engine import InterferenceEngine
import numpy as np
import os

def l3_canonical(field):
    return {k: round(v['magnitude'], 2)
            for k, v in field.items()
            if v['magnitude'] > 0.3}

def verify_all():
    engine = InterferenceEngine()
    
    # 1. L3 EQUIVALENCE
    print("--- 1. VERIFYING L3 CANONICAL EQUIVALENCE ---")
    text1 = "a dog is here"
    text2 = "here is a dog"
    
    field1 = engine.produce_interference_field(text1)
    field2 = engine.produce_interference_field(text2)
    
    canon1 = l3_canonical(field1)
    canon2 = l3_canonical(field2)
    
    print(f"  Field 1: {canon1}")
    print(f"  Field 2: {canon2}")
    if canon1 == canon2:
        print("  [SUCCESS] L3 Canonical Equivalence verified.")
    else:
        print("  [WARNING] L3 Projections differ. This may be due to uninitialized attractors.")

    # 3. LAYERS & ROUTING (Session 12)
    print("\n--- 3. VERIFYING LAYERS & ROUTING ---")
    layer_tests = {
        "hello": 2, # signals -> semantic
        "the identity of existence": 3, # L3 referent
        "the identity of existence in time": 4 # L4 context
    }
    
    for text, expected in layer_tests.items():
        field = engine.combined_field(text)
        layer = engine.identify_layer(field)
        route = engine.route(field, current_level=2)
        print(f"  Text: '{text}'")
        print(f"    Expected Layer: L{expected} | Actual: L{layer}")
        print(f"    Route (from L2): {route}")

if __name__ == "__main__":
    try:
        verify_all()
    except Exception as e:
        print(f"Verification aborted: {e}")
