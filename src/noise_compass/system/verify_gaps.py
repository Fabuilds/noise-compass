import time
import numpy as np
from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.lattice_neural_engine import LatticeNeuralEngine

def test_gap_enforcement():
    manager = H5Manager()
    engine = LatticeNeuralEngine()
    
    # Define a test gap between neighbors: SELF (11) and COHERENCE (10)
    gap_name = "self_coherence_test"
    print(f"--- 1. INITIALIZING VOID GAP: {gap_name} (SELF <-> COHERENCE) ---")
    
    # Ensure they are neighbors in the engine's node list
    # index 11: SELF, index 10: COHERENCE. confirmed.
    
    manager.set_attr("language", f"gaps/{gap_name}", "left_boundary", "SELF")
    manager.set_attr("language", f"gaps/{gap_name}", "right_boundary", "COHERENCE")
    manager.set_attr("language", f"gaps/{gap_name}", "void", True)
    manager.set_attr("language", f"gaps/{gap_name}", "void_depth", 1.0) # Absolute barrier
    
    # Clear activations
    for node in engine.nodes:
        manager.set_attr("language", f"god_tokens/{node}", "activation", 0.0)
    
    print("--- 2. INJECTING ACTIVATION INTO SELF ---")
    # We use engine.pulse with intensity. It should try to spread to COHERENCE.
    engine.h5.set_attr("language", "god_tokens/SELF", "activation", 5.0)
    
    print("--- 3. EXECUTING PULSE (VOID ACTIVE) ---")
    engine.pulse() # This should respect the void
    
    # Check activation of COHERENCE
    coherence_act = manager.get_attr("language", "god_tokens/COHERENCE", "activation")
    print(f"  COHERENCE Activation (Post-Pulse, Void Active): {coherence_act:.6f}")
    
    if coherence_act < 0.0001:
        print("  [SUCCESS] Void Gap blocked the spread.")
    else:
        print(f"  [FAILURE] Void Gap leaked {coherence_act:.6f} activation.")

    print("\n--- 4. REMOVING VOID GAP ---")
    manager.set_attr("language", f"gaps/{gap_name}", "void", False)
    
    # Reset SELF to 5.0 for a fair test
    manager.set_attr("language", "god_tokens/SELF", "activation", 5.0)
    manager.set_attr("language", "god_tokens/COHERENCE", "activation", 0.0)
    
    print("--- 5. EXECUTING PULSE (VOID INACTIVE) ---")
    engine.pulse()
    
    coherence_act_new = manager.get_attr("language", "god_tokens/COHERENCE", "activation")
    print(f"  COHERENCE Activation (Post-Pulse, Void Inactive): {coherence_act_new:.6f}")
    
    if coherence_act_new > 0.1:
        print("  [SUCCESS] Activation spread naturally.")
    else:
        print("  [FAILURE] Activation still blocked.")

if __name__ == "__main__":
    test_gap_enforcement()
