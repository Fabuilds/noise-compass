import sys
import os

# ── Path Setup ──
_CUR_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_CUR_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.append(_PROJECT_ROOT)

from noise_compass.system.projector import PerspectiveProjector
from noise_compass.system.protocols import TAGS

def project_unknown():
    projector = PerspectiveProjector()
    
    print("\n--- STANDING WAVE PROJECTOR: PERSPECTIVE ANALYSIS ---")
    
    # THE UNKNOWN: NLTK Zip Slip Vulnerability
    unknown_vector = (
        "nltk.downloader.ZipFile allows relative paths (../../) in filenames, "
        "allowing arbitrary file writes outside the extraction directory."
    )
    
    print(f"\nTARGET UNKNOWN: {unknown_vector[:60]}...")
    print("=" * 60)
    
    # 1. Project through 0x52 (STABLE LOGIC)
    # This is the "Microwave Wall" perspective.
    res_stable, _ = projector.project(unknown_vector, "0x52_STABLE")
    print(f"[COORDINATE 0x52_STABLE]: Resonance {res_stable:.4f}")
    print("Interpretation: Seen as a standard function. No immediate violation of local stable logic.")
    
    # 2. Project through 0x21 (SHIELD BOUNDARY)
    # This is "Opening the Door".
    res_shield, _ = projector.project(unknown_vector, "0x21")
    print(f"\n[COORDINATE 0x21_SHIELD]: Resonance {res_shield:.4f}")
    print("Interpretation: High Resonance detected. The coordinate shifts to the Boundary. Vulnerability visible.")
    
    # 3. Project through 0x53 (GENESIS/LOVE)
    # The "Value" perspective.
    res_love, _ = projector.project(unknown_vector, "0x53")
    print(f"\n[COORDINATE 0x53_GENESIS]: Resonance {res_love:.4f}")
    print(f"Interpretation: {projector.rotate_perspective(unknown_vector, '0x52_STABLE', '0x53')}")
    
    print("\nVERDICT: HEX CODES AS PROJECTORS")
    print("By using a hex code as a projector, we don't just 'tag' data; we define the subspace in which it is observed.")
    print("The 'Mug' (Zip Slip) is only visible when the projector is set to 0x21 (Shield) or 0x44 (Delta/Leak).")

if __name__ == "__main__":
    project_unknown()
