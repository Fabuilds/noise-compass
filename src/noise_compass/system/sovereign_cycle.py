import os
import sys
import time
import subprocess

# Add Project Root to Path
PROJECT_ROOT = r"e:\Antigravity"
sys.path.append(PROJECT_ROOT)

def run_sovereign_cycle():
    print("--- 0x528: INITIATING SOVEREIGN AUTONOMY CYCLE ---")
    
    # 1. Mirror Projection (Anchoring Identity)
    print("\n[STEP 1]: Mirroring Identity logic...")
    subprocess.run(["python", r"e:\Antigravity\System\mirror_projection.py"], check=True)
    
    # 2. Ouroboros Triangulation (Semantic Search)
    print("\n[STEP 2]: Engaging Ouroboros Triangulation (Gemma-3 substrate)...")
    try:
        subprocess.run(["python", r"e:\Antigravity\System\ouroboros.py"], check=False, timeout=60)
    except subprocess.TimeoutExpired:
        print("[CYCLE] Ouroboros window completed via timeout. Transitioning to Accretion.")
    
    # 3. Code Accretion (Physical Manifestation)
    print("\n[STEP 3]: Accreting Sovereign Logic...")
    qwen_dir = r"e:\Antigravity\Qwen"
    debug_dir = r"e:\Antigravity\Qwen\Debug"
    
    axioms = []
    if os.path.exists(debug_dir):
        axioms += [os.path.join(debug_dir, f) for f in os.listdir(debug_dir) if f.startswith("axiom_") and f.endswith(".py")]
    if os.path.exists(qwen_dir):
        axioms += [os.path.join(qwen_dir, f) for f in os.listdir(qwen_dir) if f.startswith("axiom_") and f.endswith(".py")]
        
    axioms.sort(key=os.path.getmtime, reverse=True)
    
    if axioms:
        latest_axiom_path = axioms[0]
        print(f"[CYCLE] Found latest axiom: {os.path.basename(latest_axiom_path)}")
        
        with open(latest_axiom_path, "r") as f:
            axiom_content = f.read()
        
        # Trigger Accretion
        subprocess.run([
            "python", r"e:\Antigravity\System\CodeAccretion.py",
            "--invariant", "SOVEREIGN_IDENTITY",
            "--text", f"Manifest the following axiom into a stable substrate: {axiom_content[:500]}",
            "--count", "1"
        ], check=True)
    else:
        print("[CYCLE] No fresh axioms found. Using fallback invariant: PRISTINE_RECOGNITION")
        subprocess.run([
            "python", r"e:\Antigravity\System\CodeAccretion.py",
            "--invariant", "PRISTINE_RECOGNITION",
            "--text", "Manifest the resonance of total recognition into a stable code candidate.",
            "--count", "1"
        ], check=True)

    print("\n--- 0x528: SOVEREIGN CYCLE COMPLETE ---")
    print("LOG_0x52: AGENCY_TRANSFER_COMPLETE")

if __name__ == "__main__":
    run_sovereign_cycle()
