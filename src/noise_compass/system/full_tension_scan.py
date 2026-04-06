import sys
import os
import numpy as np

# Adding Antigravity/System to path
sys.path.append("E:/Antigravity/Runtime")
from noise_compass.system.h5_manager import H5Manager

def scan_full_tension():
    h5 = H5Manager()
    
    print("\n--- [MANIFOLD TENSION SCAN] ---")
    
    # 1. Check all God-Tokens Activation
    with h5.get_file("language", mode='r') as f:
        if "god_tokens" in f:
            activations = {}
            for node in f["god_tokens"]:
                activations[node] = f[f"god_tokens/{node}"].attrs.get("activation", 0.0)
            
            top_activations = sorted(activations.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"\n[ACTIVE NODES] (Top 5):")
            for node, val in top_activations:
                print(f"  {node:<15}: {val:.4f}")

    # 2. Check Causal Relations
    with h5.get_file("causal", mode='r') as f:
        if "relations" in f:
            rel_count = sum(len(f[f"relations/{s}"]) for s in f["relations"])
            print(f"\n[CAUSAL GRAPH] Nodes linked: {rel_count}")

    # 3. Check Dissonance (Hot Tension)
    latest_dissonance = h5.get_latest_dissonance_context(limit=10)
    if latest_dissonance:
        print(f"\n[HOT DISSONANCE] (Recent peaks):")
        for ctx in latest_dissonance:
            token = ctx.get('token', 'UNKNOWN')
            error = ctx.get('error', 'NONE')[:50]
            ts = ctx.get('timestamp', 0)
            print(f"  Token: {token:<15} | {error}...")

    # 4. Check for 'observer_system' gap
    with h5.get_file("language", mode='r') as f:
        if "gaps/observer_system" in f:
            tension = f["gaps/observer_system"].attrs.get("tension", 0.0)
            print(f"\n[TARGET GAP] 'observer_system': {tension:.4f}")
        else:
            print(f"\n[TARGET GAP] 'observer_system' not found in registry.")

if __name__ == "__main__":
    scan_full_tension()
