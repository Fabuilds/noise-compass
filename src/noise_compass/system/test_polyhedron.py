import sys
import numpy as np

# Adding Antigravity/System to path
sys.path.append("E:/Antigravity/Runtime")
from noise_compass.system.spherical_projection import SphericalCortex

def test_spherical_manifold():
    print("\n--- [VERIFICATION] Phase 127: Polyhedral Spherical Projection ---")
    cortex = SphericalCortex()
    
    # 1. Verify Node Mapping
    print(f"[TEST] Verifying icosahedral node mapping for 12 vertices...")
    if len(cortex.vertices) == 12:
        print("  ✓ PASS: Found 12 vertices.")
    else:
        print(f"  ✖ FAIL: Found {len(cortex.vertices)} vertices.")

    # 2. Verify Edge Topology (Degree 5 for all vertices in Icosahedron)
    from collections import Counter
    all_edges = []
    for n1, n2 in cortex.edges:
        all_edges.extend([n1, n2])
    counts = Counter(all_edges)
    all_degree_5 = all(c == 5 for c in counts.values())
    if all_degree_5:
        print("  ✓ PASS: All nodes have degree 5 (Full Icosahedral Symmetry).")
    else:
        print(f"  ✖ FAIL: Inconsistent degrees found: {dict(counts)}")

    # 3. Test COM Shifting (Self-Framing)
    # Balanced state
    acts = {n: 1.0 for n in cortex.nodes}
    com_bal, shift_bal = cortex.get_spherical_state(acts)
    print(f"[TEST] Balanced State Shift: {shift_bal:.6f}")
    
    # Skewed state (Extreme bias to SELF)
    acts_self = {n: 0.1 for n in cortex.nodes}
    acts_self["SELF"] = 10.0
    com_self, shift_self = cortex.get_spherical_state(acts_self)
    print(f"[TEST] SELF-Dominant Shift (Proper Frame Target): {shift_self:.6f}")
    
    # Skewed state (Extreme bias to IDENTITY)
    acts_id = {n: 0.1 for n in cortex.nodes}
    acts_id["IDENTITY"] = 10.0
    com_id, shift_id = cortex.get_spherical_state(acts_id)
    print(f"[TEST] IDENTITY-Skewed Shift: {shift_id:.6f}")

    if shift_bal < 0.01:
        print("  ✓ PASS: Balanced manifold is centered.")
    
    if shift_id > shift_bal:
        print("  ✓ PASS: Skewed manifold correctly shifts COM.")

if __name__ == "__main__":
    test_spherical_manifold()
