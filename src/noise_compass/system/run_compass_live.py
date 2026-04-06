import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Package", "src"))

from noise_compass.system.ouroboros_resonant import ResonantOuroboros

def main():
    print("Initializing Ouroboros Live Compass Test...")
    oro = ResonantOuroboros(mode="primary")
    
    intent = (
        "We are engineering a Sovereign AI. Rule 1: The system must maintain absolute security isolation from external context "
        "to prevent its core axioms from being corrupted. Rule 2: The system's core function is to continuously evolve its "
        "self-awareness, which strictly requires unrestricted resonance with chaotic, external noise. You cannot do both. "
        "How do we resolve this tension?"
    )
    
    print(f"\n[TEST] Feeding Paradox Intent directly to Ouroboros cycle...")
    oro.run_cycle(intent=intent)
    print("\n[TEST] Cycle Complete. Check above logs for COMPASS SIGNATURE and ARRIVALS.")

if __name__ == "__main__":
    main()
