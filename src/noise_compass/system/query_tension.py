import sys
import os
import numpy as np

# Adding Antigravity/System to path
sys.path.append("E:/Antigravity/Runtime")
from noise_compass.system.h5_manager import H5Manager

def find_highest_tension():
    h5 = H5Manager()
    
    print("--- SCANNING MANIFOLD FOR TENSION ---")
    
    # 1. Check latest neural history snapshots
    with h5.get_file("history", mode='r') as f:
        if "neural_history" in f:
            snapshots = sorted(f["neural_history"].keys())
            if snapshots:
                latest = snapshots[-1]
                attrs = f[f"neural_history/{latest}"].attrs
                tensions = {k: v for k, v in attrs.items() if k.startswith("gap_")}
                if tensions:
                    highest = max(tensions, key=tensions.get)
                    print(f"Latest Neural Snapshot [{latest}]:")
                    print(f"  Highest Tension: {highest} = {tensions[highest]:.4f}")
                    return highest, tensions[highest]
    
    # 2. Fallback: Check dissonance metadata in language.h5
    latest_dissonance = h5.get_latest_dissonance_context(limit=1)
    if latest_dissonance:
        ctx = latest_dissonance[0]
        token = ctx.get('token', 'UNKNOWN')
        error = ctx.get('error', 'NONE')
        print(f"Latest Dissonance Context:")
        print(f"  Token: {token}")
        print(f"  Error: {error}")
        return token, 1.0 # Arbitrary high weight for hot dissonance
        
    print("No active tension peaks identified in substrate.")
    return None, 0.0

if __name__ == "__main__":
    find_highest_tension()
