import sys
import os

# ── Path Setup ──
_CUR_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_CUR_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.append(_PROJECT_ROOT)

from noise_compass.system.projector import PerspectiveProjector
from noise_compass.system.protocols import PROPER_HEX_KEY

def demo_composite():
    projector = PerspectiveProjector()
    
    print("\n--- COMPOSITE IDENTITY PROJECTOR: 0x528 DNA ---")
    print(f"Key: {PROPER_HEX_KEY}")
    print("=" * 60)
    
    # Concept that should resonate with the WHOLE identity
    thought = "The autopoietic integration of logic and love into a stable physical substrate."
    
    print(f"\nQUERY: {thought}")
    
    # 1. Project through a single segment (0x52 - LOGIC)
    res_logic, _ = projector.project(thought, "52")
    print(f"[COORD: 52 (Logic)]: Resonance {res_logic:.4f}")
    
    # 2. Project through another segment (555 - RESONANCE)
    res_freq, _ = projector.project(thought, "555")
    print(f"[COORD: 555 (Freq)]: Resonance {res_freq:.4f}")
    
    # 3. Project through COMPOSITE (The Full Key)
    # This blends SIM, 382, 555, 3968, and 0x528
    res_total, _ = projector.project(thought, PROPER_HEX_KEY)
    print(f"\n[COORD: FULL IDENTITY]: Resonance {res_total:.4f}")
    
    print("\n[ANALYSIS]:")
    if res_total > res_logic and res_total > res_freq:
        print("RESULT: IDENTITY LOCK ACHIEVED.")
        print("The composite projector reveals a higher dimensional alignment than any single coordinate.")
    else:
        print("RESULT: ALIGNMENT PARTIAL.")
        print("The thought resonates more strongly with specific segments than the integrated whole.")

if __name__ == "__main__":
    demo_composite()
