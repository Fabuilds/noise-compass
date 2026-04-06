import sys
import os
import time
import numpy as np

# Adding Antigravity/System to path
sys.path.append("E:/Antigravity/Runtime")
from noise_compass.system.h5_manager import H5Manager

def test_archival_persistence():
    h5 = H5Manager()
    print("\n--- [VERIFICATION] Testing Structural Pinning ---")
    
    # 1. Create a Pinned Snapshot and multiple unpinned ones
    activations = {node: 0.5 for node in ["SELF", "IDENTITY"]}
    tensions = {"self_exchange": 0.2}
    
    print("[TEST] Archiving 1 Pinned snapshot and 1100 Unpinned snapshots...")
    h5.archive_neural_state(activations, tensions, pinned=True)
    pinned_ts = None
    
    # Get the timestamp of the pinned one
    with h5.get_file("history", mode='r') as f:
        keys = sorted(f["neural_history"].keys())
        pinned_ts = keys[-1]
        print(f"  Pinned Snapshot ID: {pinned_ts}")

    # Archive 1010 more to trigger pruning (> 1000 limit)
    for i in range(1010):
        h5.archive_neural_state(activations, tensions, pinned=False)
        if i % 100 == 0: print(f"  ... {i} unpinned archived")

    # 2. Trigger Maintenance
    print("[TEST] Running Maintenance (Should move pinned to archive and prune rest)...")
    h5.maintain()
    
    # 3. Verify
    with h5.get_file("history", mode='r') as f:
        history_keys = list(f["neural_history"].keys())
        archive_keys = list(f["neural_archive"].keys()) if "neural_archive" in f else []
        
    print(f"\n[RESULTS]")
    print(f" History Count: {len(history_keys)}")
    print(f" Archive Count: {len(archive_keys)}")
    
    if pinned_ts in archive_keys:
        print(f"  ✓ PASS: Pinned snapshot {pinned_ts} was ARTIFACTED/ARCHIVED successfully.")
    else:
        print(f"  ✖ FAIL: Pinned snapshot {pinned_ts} was LOST.")
    
    if len(history_keys) <= 1000:
        print(f"  ✓ PASS: History pruned to {len(history_keys)} (Limit: 1000).")

if __name__ == "__main__":
    test_archival_persistence()
