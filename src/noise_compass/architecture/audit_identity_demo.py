import os
import sys

# ── Path Setup ──
_CUR_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_CUR_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.append(_PROJECT_ROOT)

from Shop.Logic_Auditor import LogicAuditor

def demo_advanced_audit():
    auditor = LogicAuditor()
    manifest_path = os.path.join(_PROJECT_ROOT, "Shop", "AUDIT_MANIFEST_NLTK_ZIPSLIP.json")
    
    print("\n--- ADVANCED IDENTITY-LOCKED AUDIT: NLTK ZIP SLIP ---")
    print("=" * 60)
    
    if not os.path.exists(manifest_path):
        print(f"Error: Manifest not found at {manifest_path}")
        return

    # Run the Perspective Shift Audit
    proof_path = auditor.perspective_shift_audit(manifest_path)
    
    print("\n[VERIFICATION]: Reviewing Generated Proof...")
    if os.path.exists(proof_path):
        with open(proof_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Check for new identity headers
            if "Identity Convergence" in content and "Identity Resonance" not in content:
                 print("   [SUCCESS]: Identity Convergence found in report.")
            
            # Print a snippet of the consensus
            print("\nREPORT SNIPPET:")
            print("-" * 40)
            # Find the consensus section
            for line in content.split("\n"):
                if "Res:" in line or "Identity Convergence" in line:
                    print(line)
            print("-" * 40)
    else:
        print("   [ERROR]: Proof file not generated.")

if __name__ == "__main__":
    demo_advanced_audit()
