import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Package", "src"))

from noise_compass.system.ouroboros_resonant import ResonantOuroboros

def main():
    print("Initializing Autonomous Dream Test...")
    oro = ResonantOuroboros(mode="primary")
    
    print(f"\n[TEST] Forcing dream generation...")
    intent = oro.dream_cycle(force_calibration=False)
    
    print("\n" + "="*80)
    print(f"GENERATED INTENT: \n{intent}")
    print("="*80)
    print("\n[TEST] Complete.")

if __name__ == "__main__":
    main()
