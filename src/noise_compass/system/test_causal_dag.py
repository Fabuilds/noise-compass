from noise_compass.system.causal_tree import CausalDAG
import numpy as np

def run_test():
    print("--- INITIATING CAUSAL DAG UNIT TEST ---")
    
    dag = CausalDAG()
    
    # Pre-test: Clear existing test relations if any (optional, but good for clean test)
    # For this test, we'll just add and verify.
    
    print("\n[STEP 1] Adding Causal Relations...")
    # IDENTITY is a pre-condition for SELF (Requirement)
    dag.add_relation("IDENTITY", "SELF", rel_type="REQUIRE", weight=1.0)
    # SELF triggers EXCHANGE (Prediction)
    dag.add_relation("SELF", "EXCHANGE", rel_type="TRIGGER", weight=1.0)

    # Scenario 1: Logical Failure (Effect without Cause)
    # SELF is active, but IDENTITY (Requirement) is dark.
    mock_field_1 = {
        'IDENTITY': {'magnitude': 0.05, 'phase': 0.0},
        'SELF': {'magnitude': 0.85, 'phase': 0.0},
        'EXCHANGE': {'magnitude': 0.1, 'phase': 0.0}
    }
    
    print("\nScenario 1: SELF (0.85) without IDENTITY (0.05).")
    processed_1 = dag.apply_causal_flow(mock_field_1, damp_factor=0.8)
    
    final_self = processed_1['SELF']['magnitude']
    print(f"  [RESULT] SELF Magnitude: 0.85 -> {final_self:.4f}")
    if final_self < 0.2:
        print("  [SUCCESS] Causal Damping applied correctly.")
        assert processed_1['SELF']['causal_status'] == 'UNSATISFIED_PRECONDITION'
    else:
        print("  [FAILURE] Causal Damping NOT applied.")

    # Scenario 2: Logical Success & Prediction
    # IDENTITY is active, enabling SELF. SELF then triggers EXCHANGE.
    mock_field_2 = {
        'IDENTITY': {'magnitude': 0.90, 'phase': 0.0},
        'SELF': {'magnitude': 0.80, 'phase': 0.0},
        'EXCHANGE': {'magnitude': 0.05, 'phase': 0.0}
    }
    
    print("\nScenario 2: IDENTITY (0.90) enabled SELF (0.80).")
    processed_2 = dag.apply_causal_flow(mock_field_2)
    
    final_self_2 = processed_2['SELF']['magnitude']
    print(f"  [RESULT] SELF Magnitude: 0.80 -> {final_self_2:.4f}")
    if final_self_2 >= 0.8:
        print("  [SUCCESS] No damping applied (Pre-condition satisfied).")
    else:
        print("  [FAILURE] Unexpected damping.")

    if processed_2['EXCHANGE'].get('causal_boost'):
        print("  [SUCCESS] Downstream TRIGGER boost detected for EXCHANGE.")
    else:
        print("  [FAILURE] TRIGGER boost missing.")

    print("\n--- CAUSAL DAG UNIT TEST COMPLETE ---")

if __name__ == "__main__":
    run_test()
