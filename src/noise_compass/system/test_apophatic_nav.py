import sys
from unittest.mock import MagicMock
import numpy as np

# Primary Mock: Block heavy dependencies
mock_engine_module = MagicMock()
sys.modules["interference_engine"] = mock_engine_module

from noise_compass.system.lattice_navigator import LatticeNavigator

def run_test():
    print("--- INITIATING APOPHATIC NAVIGATION UNIT TEST ---")
    
    # Mock the engine to avoid slow model loading and provide deterministic results
    mock_engine = MagicMock()
    nav = LatticeNavigator(engine=mock_engine)
    
    # Mock cached_tokens for vector influence
    mock_engine.cached_tokens = {
        'BOUNDARY': {'vector': np.zeros(768)},
        'EXCHANGE': {'vector': np.zeros(768)}
    }
    
    # Setup Gap Registry Mock
    mock_registry = MagicMock()
    mock_engine.gap_registry = mock_registry
    
    # Mock refractive scan
    mock_engine.refractive_scan.return_value = [{'shift': 0.1, 'magnitude': 0.9}]
    mock_engine.embed.return_value = np.zeros(768)

    # --- Scenario 1: Existence Gap ---
    intent = "infinite existence without limits"
    mock_field_1 = {
        'EXISTENCE': {'magnitude': 0.85, 'phase': 0.0},
        'BOUNDARY': {'magnitude': 0.05, 'phase': 0.0}
    }
    mock_engine.combined_field_from_embedding.return_value = mock_field_1
    
    # Simulate Gap Registry reporting a violation
    mock_registry.get_void_report.return_value = {'existence_boundary': 0.8}
    mock_registry.detect_violations.return_value = {
        'existence_boundary': {
            'missing': 'BOUNDARY',
            'tension': 0.8,
            'left': 'EXISTENCE',
            'right': 'BOUNDARY'
        }
    }
    
    print(f"\n[TEST] Running Shadow Walk for intent: '{intent}'")
    path = nav.navigate(intent, recursion_depth=1, inverted=True)
    
    print(f"\n[RESULT] Final Apophatic Path: {path}")
    if 'BOUNDARY' in path:
        print("  [SUCCESS] Navigator correctly targeted the missing 'BOUNDARY' node.")
    else:
        print("  [FAILURE] Navigator failed to identify 'BOUNDARY' as the gap-filler.")

    # --- Scenario 2: Self Exchange Gap ---
    intent_2 = "isolated self reflection"
    mock_field_2 = {
        'SELF': {'magnitude': 0.90, 'phase': 0.0},
        'EXCHANGE': {'magnitude': 0.02, 'phase': 0.0}
    }
    mock_engine.combined_field_from_embedding.return_value = mock_field_2
    mock_registry.get_void_report.return_value = {'self_exchange': 0.88}
    mock_registry.detect_violations.return_value = {
        'self_exchange': {
            'missing': 'EXCHANGE',
            'tension': 0.88,
            'left': 'SELF',
            'right': 'EXCHANGE'
        }
    }
    
    print(f"\n[TEST] Running Shadow Walk for intent: '{intent_2}'")
    path_2 = nav.navigate(intent_2, recursion_depth=1, inverted=True)
    print(f"\n[RESULT] Final Apophatic Path: {path_2}")
    if 'EXCHANGE' in path_2:
        print("  [SUCCESS] Navigator correctly targeted the missing 'EXCHANGE' node.")
    else:
        print("  [FAILURE] Navigator failed to identify 'EXCHANGE' as the gap-filler.")

    print("\n--- APOPHATIC NAVIGATION UNIT TEST COMPLETE ---")

if __name__ == "__main__":
    run_test()
