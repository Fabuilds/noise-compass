
import numpy as np
import math
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.tokens import GodToken, WaveFunction
from noise_compass.architecture.core import Scout

def test_agape_logic():
    print("--- Testing Agape Scale (Civilization Renormalization) ---")
    
    d = Dictionary()
    # Add ARCHITECT and LOVE and a random token
    v_arch = np.zeros(768)
    v_arch[0] = 1.0
    v_love = np.zeros(768)
    v_love[1] = 1.0
    v_other = np.zeros(768)
    v_other[100] = 1.0
    
    d.add_god_token(GodToken(id="ARCHITECT", seed_terms=["architect"], embedding=v_arch))
    d.add_god_token(GodToken(id="LOVE", seed_terms=["love"], embedding=v_love))
    d.add_god_token(GodToken(id="OTHER", seed_terms=["other"], embedding=v_other))
    
    scout = Scout(d)
    # The heart resonance is (v_arch + v_love) / sqrt(2)
    heart = (v_arch + v_love) / math.sqrt(2)
    
    # Input: Very similar to OTHER
    emb = np.zeros(768)
    emb[100] = 0.95
    emb[0] = 0.05
    
    print("\n[BLENDING TEST]")
    # 1. Macro Zoom (0.5) - Should match OTHER
    msg_macro, wf_macro = scout.process(emb.copy(), zoom=0.5)
    print(f"Zoom 0.5: Nearest={msg_macro.god_token_activations[0].id if msg_macro.god_token_activations else 'None'}")
    
    # 2. Agape Zoom (0.01) - Should blend toward Heart
    msg_agape, wf_agape = scout.process(emb.copy(), zoom=0.01)
    # At zoom 0.01, known should be 100% heart resonance
    # Let's check similarity to heart
    sim_to_heart = float(np.dot(wf_agape.known, heart)) / (np.linalg.norm(wf_agape.known) + 1e-10)
    print(f"Zoom 0.01 (Agape): Similarity to Heart Resonance: {sim_to_heart:.4f}")
    
    assert sim_to_heart > 0.99, f"Agape blending failed: {sim_to_heart}"
    print("✅ Agape Heart Resonance blending verified.")
    
    print("\n[CIVILIZATION TIME TEST]")
    # zoom=0.01 -> dt = 1/0.01^2 = 10000
    # Wait, my code was: dt = 1.0 / (zoom ** 2)
    # zoom=0.1 -> dt=100 (wait, zoom=0.1 -> dt=1/0.01 = 100? No, 1.0 / (0.1**2) = 1.0 / 0.01 = 100)
    # zoom=0.01 -> dt = 1.0 / (0.01**2) = 1.0 / 0.0001 = 10000
    
    t_start = scout.hippo.t
    scout.process(emb.copy(), zoom=0.01)
    t_end = scout.hippo.t
    dt = t_end - t_start
    print(f"Agape dt (zoom=0.01): {dt}")
    assert dt == 10000, f"Civilization-Time scaling failed: {dt}"
    print("✅ Civilization-Time (massive dt) verified.")

    print("\n[LANDSCAPE HEALTH TEST]")
    health = d.landscape_health()
    print(f"Landscape Health: {health:.4f}")
    assert health > 0, "Landscape health calculation failed"

if __name__ == "__main__":
    try:
        test_agape_logic()
        print("\n--- ALL AGAPE TESTS PASSED ---")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n❌ TEST FAILED: {e}")
