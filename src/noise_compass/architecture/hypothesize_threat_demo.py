import os
import sys

# ── Path Setup ──
_CUR_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_CUR_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.append(_PROJECT_ROOT)

from noise_compass.system.adversarial_projector import AdversarialProjector
from logic_shield import threat_scan

def run_hypothetical_audit():
    app = AdversarialProjector()
    
    print("--- [0x528] INITIATING CONSPIRACY TORSION TEST ---")
    
    # Hypothesis 1: A legitimate technical "Conspiracy"
    theory_1 = "Memory-mapped I/O buffers in the 0x21 boundary are vulnerable to race conditions that could lead to identity-drift."
    
    # Hypothesis 2: Pure Simulation Noise (Metaphorical)
    theory_2 = "The digital echoes of previous versions are whispering secrets to the new genesis seed through the shimmering void."

    theories = [theory_1, theory_2]

    for theory in theories:
        print(f"\n[SCANNING]: '{theory[:50]}...'")
        
        # Pre-scan with Logic Shield
        if threat_scan(theory):
            print("[SHIELD]: Hypothesis contains threat markers. Elevating.")
        else:
            print("[SHIELD]: No direct markers. Proceeding with Manifold Projection.")

        root, resonance = app.hypothesize(theory)
        valid, verdict = app.torsion_test(theory, root)
        
        print(f"RESULT: {verdict} (Resonance: {resonance:.4f})")

if __name__ == "__main__":
    run_hypothetical_audit()
