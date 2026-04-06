import numpy as np
from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.interference_engine import InterferenceEngine

def test_field_shield():
    engine = InterferenceEngine()
    manager = H5Manager()
    
    print("--- 1. VERIFYING FIELD SHIELD (VOID BRIDGING) ---")
    
    # Ensure the EXISTENCE <-> BOUNDARY gap is a void
    manager.set_attr("language", "gaps/existence_boundary", "void", True)
    manager.set_attr("language", "gaps/existence_boundary", "void_depth", 0.9)
    
    # We need an intent that activates both nodes.
    # Since we use Qwen embeddings, mentioning both should work.
    intent = "The existence is the boundary."
    
    print(f"  Intent: '{intent}'")
    
    # We need to see the output of the print statement in produce_interference_field
    field = engine.produce_interference_field(intent)
    
    # Check if they were damped
    exist_mag = field.get('EXISTENCE', {}).get('magnitude', 0)
    bound_mag = field.get('BOUNDARY', {}).get('magnitude', 0)
    
    print(f"  Field Results:")
    print(f"    EXISTENCE Magnitude: {exist_mag:.4f}")
    print(f"    BOUNDARY Magnitude: {bound_mag:.4f}")
    
    # If the shield worked, they should be relatively low due to 0.9 damping (1.0 - 0.9 = 0.1)
    if exist_mag < 0.2 and bound_mag < 0.2:
         print("  [SUCCESS] Field Shield damped the void bridge.")
    else:
         print("  [FAILURE] Field Shield did not damp sufficiently.")

if __name__ == "__main__":
    test_field_shield()
