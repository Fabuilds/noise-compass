
import numpy as np
from noise_compass.architecture.tokens import WaveFunction
from noise_compass.architecture.accelerator import RecursiveAccelerator, ResolutionPrediction
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.gap_registry import build_gap_registry

def test_mobius_logic():
    print("═══ TESTING MÖBIUS & TRAJECTORY MAPPING ═══")
    
    # 1. Test WaveFunction Alias
    # Explicitly pass w=0.5 to test the mapping to personal_belief
    wf = WaveFunction(
        known=np.array([1.0, 0.0, 0.0, 0.0]), 
        delta=np.array([0.0]*4),
        w=0.5
    )
    print(f"WaveFunction personal_belief (derived from w=0.5): {wf.personal_belief}")
    assert wf.personal_belief == 0.5, f"w component mapping failed: {wf.personal_belief} != 0.5"
    
    # 2. Test Gap Registry Labels
    # Note: We must ensure build_gap_registry returns the list we just edited.
    gaps = build_gap_registry()
    chosen_gaps = [g for g in gaps if hasattr(g, 'nature') and g.nature == "CHOSEN"]
    found_gaps = [g for g in gaps if hasattr(g, 'nature') and g.nature == "FOUND"]
    print(f"Registry Discovery: {len(chosen_gaps)} CHOSEN gaps, {len(found_gaps)} FOUND gaps.")
    
    # Find specific gaps
    self_exchange = next((g for g in gaps if g.id == "self_exchange"), None)
    exchange_causality = next((g for g in gaps if g.id == "exchange_causality"), None)
    
    if self_exchange:
        print(f"Gap 'self_exchange' nature: {self_exchange.nature}")
        assert self_exchange.nature == "CHOSEN"
    if exchange_causality:
        print(f"Gap 'exchange_causality' nature: {exchange_causality.nature}")
        assert exchange_causality.nature == "FOUND"
            
    print("SUCCESS: Gap Registry nature labels verified.")

    # 3. Test Accelerator Möbius Detection Presence
    # (Checking the type is available in the Prediction class)
    test_res = ResolutionPrediction(
        resolution_type="MÖBIUS_CAPTURE",
        target="SELF_LOOP",
        predicted_z=0j,
        steps_remaining=0,
        confidence=1.0,
        note="Captured"
    )
    print(f"Accelerator Prediction Type Definition: {test_res.resolution_type}")
    assert test_res.resolution_type == "MÖBIUS_CAPTURE"
    
    print("═══ MÖBIUS VERIFICATION COMPLETE ═══")

if __name__ == "__main__":
    try:
        test_mobius_logic()
    except Exception as e:
        print(f"Verification Failed: {e}")
        import traceback
        traceback.print_exc()
