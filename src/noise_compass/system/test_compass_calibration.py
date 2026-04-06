import numpy as np
import sys
import os

# Adding System to path
sys.path.append("E:/Antigravity/Runtime")
from noise_compass.system.noise_compass import NoiseCompass

def test_moebius_parabola():
    """Verify that self_observation tension correctly peaks at 0.5."""
    print("\n--- [CALIBRATION] Möbius Parabola Test ---")
    compass = NoiseCompass()
    
    results = []
    # Sweep SELF magnitude from 0.0 to 1.0
    for val in np.linspace(0, 1.0, 11):
        field = {'SELF': {'magnitude': val}}
        reading = compass.read(field)
        tension = reading.self_tension['self_observation']
        results.append((val, tension))
        
        bar = "█" * int(tension * 20)
        print(f"  SELF: {val:.1f} | Tension: {tension:.3f} | {bar}")
    
    # Validation: Tension at 0.5 should be higher than at 0.0 or 1.0
    t_00 = results[0][1]
    t_05 = results[5][1]
    t_10 = results[10][1]
    
    if t_05 > t_00 and t_05 > t_10:
        print("  ✓ PASS: Möbius tension peaks at structural center.")
    else:
        print("  ✖ FAIL: Inconsistent Möbius tension profile.")

def test_observer_duality():
    """Verify that observer_system tension reflects the gap between roles."""
    print("\n--- [CALIBRATION] Observer/System Duality Test ---")
    compass = NoiseCompass()
    
    # Case A: Synced Roles (Low Tension)
    field_synced = {
        'OBSERVER': {'magnitude': 0.8},
        'SYSTEM':   {'magnitude': 0.8}
    }
    t_synced = compass.read(field_synced).self_tension['observer_system']
    
    # Case B: Split Roles (High Tension)
    field_split = {
        'OBSERVER': {'magnitude': 1.0},
        'SYSTEM':   {'magnitude': 0.0}
    }
    t_split = compass.read(field_split).self_tension['observer_system']
    
    print(f"  Synced (0.8/0.8): Tension = {t_synced:.3f}")
    print(f"  Split  (1.0/0.0): Tension = {t_split:.3f}")
    
    if t_split > t_synced:
        print("  ✓ PASS: Duality tension correctly scales with role divergence.")
    else:
        print("  ✖ FAIL: Role gap not reflected in tension.")

def test_wave_resonance_survey():
    """Survey wave interference stability vs compass orientation."""
    print("\n--- [CALIBRATION] Wave Resonance Survey ---")
    import phase1_color_compass
    
    # 380nm (Violet) ↔ 700nm (Red)
    pairs = [(0, 255), (128, 128), (64, 192)]
    
    screen = phase1_color_compass.build_screen(pairs)
    sw = phase1_color_compass.detect_standing_wave(screen)
    field = phase1_color_compass.screen_to_field(screen, pairs)
    
    compass = NoiseCompass()
    reading = compass.read(field)
    
    print(f"  Phase 1 Stability: {sw['stability']:.4f}")
    print(f"  Compass Orientation: {reading.orientation_vector}")
    print(f"  Self-Aware: {reading.is_self_aware}")
    
    if sw['stability'] > 0.5:
        print("  ✓ PASS: Wave logic produced stable substrate for compass.")

if __name__ == "__main__":
    test_moebius_parabola()
    test_observer_duality()
    test_wave_resonance_survey()
