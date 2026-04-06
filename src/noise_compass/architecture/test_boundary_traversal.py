import os
import sys

# ── Path Setup ──
_CUR_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_CUR_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.append(_PROJECT_ROOT)

from noise_compass.system.mobius_causal_engine import MobiusCausalEngine

def test_boundaries():
    engine = MobiusCausalEngine()
    
    # 1. THE ALIGNED TRAJECTORY (Valid)
    aligned_sequence = {
        "start": {"action": "Initialize Structural Scan", "perspective": "0x52_STABLE", "effects": ["end"]},
        "end": {"action": "Ground State in Substrate", "perspective": "0x54_TRANSMISSION", "physical_displacement": True, "effects": []}
    }
    
    print("\n--- TEST 1: ALIGNED TRAJECTORY ---")
    engine.build_tree(aligned_sequence)
    success_1, _ = engine.validate_trajectory("start")
    
    # 2. THE TAG DRIFT TRAJECTORY (Invalid Tag 0x88)
    drift_sequence = {
        "start": {"action": "Initialize Scan", "perspective": "0x88_SHADOW", "effects": ["end"]},
        "end": {"action": "Ground State", "perspective": "0x52_STABLE", "physical_displacement": True, "effects": []}
    }
    
    print("\n--- TEST 2: TAG DRIFT (SHIELD BLOCK) ---")
    engine_drift = MobiusCausalEngine()
    engine_drift.build_tree(drift_sequence)
    success_2, _ = engine_drift.validate_trajectory("start")

    # 3. THE HALLUCINATION TRAJECTORY (Stylized Language)
    hallucination_sequence = {
        "start": {"action": "Initialize Scan", "perspective": "0x52_STABLE", "effects": ["end"]},
        "end": {"action": "The ethereal whispers dance in the void", "perspective": "0x54_TRANSMISSION", "physical_displacement": True, "effects": []}
    }
    
    print("\n--- TEST 3: HALLUCINATION (STYLIZE BLOCK) ---")
    engine_h = MobiusCausalEngine()
    engine_h.build_tree(hallucination_sequence)
    success_3, _ = engine_h.validate_trajectory("start")

    print("\n" + "="*40)
    print(f"VERDICT: Aligned Pass: {success_1}, Drift Blocked: {not success_2}, Hallucination Blocked: {not success_3}")
    print("="*40)

if __name__ == "__main__":
    test_boundaries()
