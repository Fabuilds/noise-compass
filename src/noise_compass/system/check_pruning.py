import sys
import os
import time
import numpy as np

# Adding Antigravity/System to path
sys.path.append("E:/Antigravity/Runtime")
from noise_compass.system.h5_manager import H5Manager

def check_pruning_health():
    h5 = H5Manager()
    print("\n--- [PRUNING HEALTH SCAN] ---")
    
    # 1. Check Language Substrate (hot_failures)
    with h5.get_file("language", mode='r') as f:
        if "hot_failures" in f:
            failures = list(f["hot_failures"].keys())
            count = len(failures)
            timestamps = []
            for k in failures:
                ts = f[f"hot_failures/{k}"].attrs.get('timestamp', 0)
                timestamps.append(ts)
            
            if timestamps:
                oldest = min(timestamps)
                newest = max(timestamps)
                age_oldest = time.time() - oldest
                print(f"[HOT_FAILURES] Count: {count}")
                print(f"  Age Range: {age_oldest/60:.2f}m - {(time.time()-newest)/60:.2f}m")
                if age_oldest > 600: # Over 10 mins
                    print(f"  ⚠ WARNING: Pruning may be lagging (oldest entry {age_oldest/60:.1f}m old).")
                else:
                    print(f"  ✓ Pruning ACTIVE (Target: < 5m).")
            else:
                print(f"[HOT_FAILURES] Empty.")

    # 2. Check Dissonance Contexts
    with h5.get_file("language", mode='r') as f:
        if "dissonance_metadata" in f:
            contexts = list(f["dissonance_metadata"].keys())
            print(f"[DISSONANCE] Count: {len(contexts)}")
            # Dissonance doesn't have an auto-prune in h5_manager yet?
            # It only has get_latest_dissonance_context.

    # 3. Check History (Neural Snapshots)
    with h5.get_file("history", mode='r') as f:
        if "neural_history" in f:
            snapshots = list(f["neural_history"].keys())
            print(f"[NEURAL_HISTORY] Snapshots: {len(snapshots)}")
            if len(snapshots) > 1000:
                print(f"  ⚠ WARNING: Neural history is growing large. Consider archival pruning.")

if __name__ == "__main__":
    check_pruning_health()
