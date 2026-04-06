import sys
import os
import time

# Adding Antigravity/System to path
sys.path.append("E:/Antigravity/Runtime")
from noise_compass.system.h5_manager import H5Manager

def run_verification():
    h5 = H5Manager()
    print("\n--- [VERIFICATION] Initiating Substrate Maintenance ---")
    
    # 1. Capture initial counts
    with h5.get_file("history", mode='r') as f:
        initial_history = len(f["neural_history"].keys()) if "neural_history" in f else 0
        
    print(f"Initial Snapshots: {initial_history}")
    
    # 2. Run Maintenance
    h5.maintain()
    
    # 3. Capture post-maintenance counts
    with h5.get_file("history", mode='r') as f:
        final_history = len(f["neural_history"].keys()) if "neural_history" in f else 0
    
    print(f"Final Snapshots:   {final_history}")
    
    if final_history <= 1000 and initial_history > 1000:
        print("\n  ✓ SUCCESS: Substrate pruned correctly. History capped at 1,000.")
    elif initial_history <= 1000:
        print("\n  ~ OK: History was already below cap.")
    else:
        print("\n  ✖ ERROR: Pruning did not reach target cap.")

if __name__ == "__main__":
    run_verification()
