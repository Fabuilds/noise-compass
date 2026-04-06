
import numpy as np
import math
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.tokens import GodToken, WaveFunction
from noise_compass.architecture.core import Scout

def test_zoom_logic():
    print("--- Testing Multi-Scale Zoom (Renormalization) ---")
    
    d = Dictionary()
    # Add a dummy God token
    v = np.zeros(768)
    v[0] = 1.0
    gt = GodToken(id="EXISTENCE", seed_terms=["existence"], embedding=v)
    d.add_god_token(gt)
    
    scout = Scout(d)
    
    # Input embedding: somewhat similar but with a delta
    # 0.8 on EXISTENCE axis, 0.6 on orthogonal axis
    emb = np.zeros(768)
    emb[0] = 0.8
    emb[1] = 0.6
    # norm = 1.0
    
    print("\n[SCALING TEST]")
    # Use fresh scouts to avoid crystallization side-effects
    d05 = Dictionary()
    d05.add_god_token(GodToken(id="EXISTENCE", seed_terms=["existence"], embedding=v))
    scout05 = Scout(d05)
    msg_macro, wf_macro = scout05.process(emb.copy(), zoom=0.5)
    sim_macro = wf_macro.similarity
    phase_macro = wf_macro.phase_deg
    print(f"Zoom 0.5 (Macro): Sim={sim_macro:.4f}, Phase={phase_macro:.2f} deg")
    
    d1 = Dictionary()
    d1.add_god_token(GodToken(id="EXISTENCE", seed_terms=["existence"], embedding=v))
    scout1 = Scout(d1)
    msg_def, wf_def = scout1.process(emb.copy(), zoom=1.0)
    sim_def = wf_def.similarity
    phase_def = wf_def.phase_deg
    print(f"Zoom 1.0 (Default): Sim={sim_def:.4f}, Phase={phase_def:.2f} deg")
    
    d2 = Dictionary()
    d2.add_god_token(GodToken(id="EXISTENCE", seed_terms=["existence"], embedding=v))
    scout2 = Scout(d2)
    msg_micro, wf_micro = scout2.process(emb.copy(), zoom=2.0)
    sim_micro = wf_micro.similarity
    phase_micro = wf_micro.phase_deg
    print(f"Zoom 2.0 (Micro): Sim={sim_micro:.4f}, Phase={phase_micro:.2f} deg")
    
    # Assertions
    assert sim_macro > sim_def > sim_micro, "Similarity scaling failed"
    assert phase_macro < phase_def < phase_micro, "Phase renormalization scaling failed"
    print("✅ Similarity and Phase scaling verified.")
    
    print("\n[TEMPORAL TEST]")
    # HiPPO t should increment by 1/zoom
    # t was at 1.0 + 1.0 + 0.5 = 2.5 after above steps
    # Wait, the above steps:
    # 1. step(0.5) -> t = 2.0 (because initial t=0, step(1/0.5)=2.0)
    # 2. step(1.0) -> t = 2.0 + 1.0 = 3.0
    # 3. step(2.0) -> t = 3.0 + 0.5 = 3.5
    
    # Testing temporal on a fresh scout
    d_temp = Dictionary()
    scout_temp = Scout(d_temp)
    scout_temp.process(emb.copy(), zoom=0.5) # t += 2.0
    scout_temp.process(emb.copy(), zoom=1.0) # t += 1.0
    scout_temp.process(emb.copy(), zoom=2.0) # t += 0.5
    
    print(f"HiPPO clock (t): {scout_temp.hippo.t:.2f}")
    assert abs(scout_temp.hippo.t - 3.5) < 1e-6, f"HiPPO temporal scaling failed: {scout_temp.hippo.t}"
    print("✅ HiPPO temporal integration (delta_t) verified.")

if __name__ == "__main__":
    try:
        test_zoom_logic()
        print("\n--- ALL ZOOM TESTS PASSED ---")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n❌ TEST FAILED: {e}")
