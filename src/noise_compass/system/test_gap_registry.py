from noise_compass.system.gap_registry import GapRegistry
import numpy as np

def run_test():
    print("--- INITIATING GAP REGISTRY UNIT TEST ---")
    
    # Initialize Registry (will load from H5)
    registry = GapRegistry()
    
    print(f"Loaded {len(registry.cached_gaps)} gaps from substrate.")
    for name in registry.cached_gaps:
        print(f"  - {name}: {registry.cached_gaps[name]['left']} <-> {registry.cached_gaps[name]['right']}")

    # Scenario 1: Pure Existence (Violation of existence_boundary)
    mock_field = {
        'EXISTENCE': {'magnitude': 0.95, 'phase': 0.0},
        'BOUNDARY': {'magnitude': 0.02, 'phase': 0.0},
        'SELF': {'magnitude': 0.1, 'phase': 0.0},
        'EXCHANGE': {'magnitude': 0.1, 'phase': 0.0}
    }
    
    print("\nScenario 1: Input text has high EXISTENCE resonance but no BOUNDARY.")
    violations = registry.detect_violations(mock_field)
    
    if 'existence_boundary' in violations:
        v = violations['existence_boundary']
        print(f"  [SUCCESS] Violation detected: existence_boundary")
        print(f"  [INFO] Missing node: {v['missing']}")
        print(f"  [INFO] Tension: {v['tension']:.4f}")
        assert v['missing'] == 'BOUNDARY'
        assert 0.18 < v['tension'] < 0.20 # depth 0.2 * (0.95 - 0.02) = 0.186
    else:
        print("  [FAILURE] existence_boundary violation NOT detected.")

    # Scenario 2: Self without Exchange (Violation of self_exchange)
    mock_field_2 = {
        'EXISTENCE': {'magnitude': 0.5, 'phase': 0.0},
        'BOUNDARY': {'magnitude': 0.5, 'phase': 0.0},
        'SELF': {'magnitude': 0.85, 'phase': 0.0},
        'EXCHANGE': {'magnitude': 0.05, 'phase': 0.0}
    }
    
    print("\nScenario 2: Input has high SELF resonance but no EXCHANGE.")
    violations_2 = registry.detect_violations(mock_field_2)
    
    if 'self_exchange' in violations_2:
        v = violations_2['self_exchange']
        print(f"  [SUCCESS] Violation detected: self_exchange")
        print(f"  [INFO] Missing node: {v['missing']}")
        print(f"  [INFO] Tension: {v['tension']:.4f}")
        assert v['missing'] == 'EXCHANGE'
        assert v['tension'] > 0.7 # depth 1.0 * (0.85 - 0.05)
    else:
        print("  [FAILURE] self_exchange violation NOT detected.")

    # Scenario 3: Balanced State (No Violations)
    mock_field_3 = {
        'SELF': {'magnitude': 0.8, 'phase': 0.0},
        'EXCHANGE': {'magnitude': 0.75, 'phase': 0.0}
    }
    print("\nScenario 3: Balanced SELF and EXCHANGE.")
    violations_3 = registry.detect_violations(mock_field_3)
    if not violations_3:
        print("  [SUCCESS] No violations detected for balanced state.")
    else:
        print(f"  [FAILURE] Unexpected violations: {list(violations_3.keys())}")

    print("\n--- GAP REGISTRY UNIT TEST COMPLETE ---")

if __name__ == "__main__":
    run_test()
