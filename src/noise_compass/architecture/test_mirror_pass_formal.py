import sys, os
import numpy as np
import math
sys.path.insert(0, "E:/Antigravity/Architecture")

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.tokens import WaveFunction
from noise_compass.architecture.core import Scout

def test_dictionary_signed_query():
    print("[TEST] Dictionary Signed Query...")
    d = Dictionary()
    vec = np.random.randn(1536).astype(np.float32)
    vec /= np.linalg.norm(vec)
    d.entries["test_node"] = vec
    
    # Forward query
    fid, sim, _ = d.query(vec)
    assert fid == "test_node"
    assert abs(sim - 1.0) < 1e-5
    
    # Mirror query (negated vector)
    fid_m, sim_m, _ = d.query(-vec)
    assert fid_m == "test_node"
    assert abs(sim_m + 1.0) < 1e-5
    print("  -> Passed.")

def test_wavefunction_phase_range():
    print("[TEST] WaveFunction Phase Range...")
    known = np.random.randn(1536).astype(np.float32)
    delta = np.random.randn(1536).astype(np.float32)
    # Ensure delta is not zero
    delta /= np.linalg.norm(delta)
    
    # Cataphatic (w > 0)
    wf_c = WaveFunction(known, delta, w=0.5)
    assert 0 < wf_c.phase < math.pi / 2
    
    # Apophatic (w < 0)
    wf_a = WaveFunction(known, delta, w=-0.5)
    assert math.pi / 2 < wf_a.phase < math.pi
    
    # Turbulent Wall (w = 0)
    wf_t = WaveFunction(known, delta, w=0.0)
    assert abs(wf_t.phase - math.pi / 2) < 1e-6
    
    # Pure Absence (w = -1, d = 0)
    wf_p = WaveFunction(known, np.zeros(1536, dtype=np.float32), w=-1.0)
    assert abs(wf_p.phase - math.pi) < 1e-6
    print("  -> Passed.")

def test_scout_no_clamping():
    print("[TEST] Scout No Clamping...")
    d = Dictionary()
    vec = np.random.randn(1536).astype(np.float32)
    vec /= np.linalg.norm(vec)
    d.entries["TARGET"] = vec
    
    scout = Scout(d)
    
    # Test negated input leads to negative w in WaveFunction
    msg, wf = scout.process(-vec)
    assert wf.w < -0.9, f"Expected negative w, got {wf.w}"
    assert wf.phase_deg > 170.0, f"Expected high phase, got {wf.phase_deg}"
    print("  -> Passed.")

if __name__ == "__main__":
    try:
        test_dictionary_signed_query()
        test_wavefunction_phase_range()
        test_scout_no_clamping()
        print("\n[SUCCESS] All Mirror Pass tests passed!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n[FAILURE] {e}")
        sys.exit(1)
