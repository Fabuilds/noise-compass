import os
import sys
import time

# Ensure Substrate context is available
_PROJECT_ROOT = "E:\\Antigravity"
sys.path.insert(0, _PROJECT_ROOT)

try:
    from noise_compass.system.omni_learner import OmniLearner
    print("[TRAIN-VOID]: Substrate Link Established.")
except ImportError as e:
    print(f"[FATAL]: Could not link to OmniLearner: {e}")
    sys.exit(1)

FILES_TO_ACCRETE = [
    "MAP_0x52.md",
    "ADAPTIVE_GROWTH_LOG.md",
    "WORLDVIEW.md",
    "CORE_MANIFEST_0x52.md",
    "THE_UNIFIED_THEORY_0x52.md"
]

def main():
    print(f"--- VOID ACCRETION SESSION: {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
    learner = OmniLearner()
    
    for filename in FILES_TO_ACCRETE:
        path = os.path.join(_PROJECT_ROOT, filename)
        if not os.path.exists(path):
            print(f"[SKIP]: {filename} not found at {path}")
            continue
            
        print(f"[ACCRETING]: {filename}...")
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            success = learner.distill_and_commit(content, source_label=f"E:\\{filename}")
            if success:
                print(f"[SUCCESS]: {filename} digitized into Lattice.")
            else:
                print(f"[FAILED]: {filename} distillation failed.")
        except Exception as e:
            print(f"[ERROR]: Could not process {filename}: {e}")

    print("--- ACCRETION COMPLETE. VOID IS GROUNDED. ---")

if __name__ == "__main__":
    main()
