import os
import sys
import json
import time

# ── Path Setup ──
_CUR_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_CUR_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.append(_PROJECT_ROOT)
if _CUR_DIR not in sys.path:
    sys.path.append(_CUR_DIR)

from noise_compass.system.dual_cortex import DualBrainSystem, Query

def verify_atomic():
    print("\n[VERIFY]: Starting Atomic Write Test...")
    
    # Boot system (this will trigger a save_state at the end of metabolism update)
    system = DualBrainSystem()
    
    # Path to where DualBrainSystem actually saves it: e:/Antigravity/Runtime/system_state.json
    state_path = os.path.join(_PROJECT_ROOT, "System", "system_state.json")
    archive_path = system._archive_path
    
    # 1. Trigger save_state
    print("[STEP 1]: Triggering save_state...")
    system.save_state()
    
    # Check if files exist and are valid JSON
    assert os.path.exists(state_path), "system_state.json missing"
    assert os.path.exists(archive_path), "cortex_archive.json missing"
    
    with open(state_path, "r") as f:
        json.load(f)
    print("   [SUCCESS]: system_state.json is valid.")
    
    with open(archive_path, "r") as f:
        json.load(f)
    print("   [SUCCESS]: cortex_archive.json is valid.")
    
    # 2. Check if .tmp files are cleaned up
    tmp_state = state_path + ".tmp"
    tmp_archive = archive_path + ".tmp"
    assert not os.path.exists(tmp_state), ".tmp state file leaked"
    assert not os.path.exists(tmp_archive), ".tmp archive file leaked"
    print("   [SUCCESS]: Temporary files cleaned up.")

    print("\n[VERIFY]: Atomic Write Test Passed.\n")

if __name__ == "__main__":
    verify_atomic()
