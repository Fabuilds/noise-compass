import numpy as np
import time
import sys
import os

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.tokens import GodToken
from noise_compass.system.protocols import LAMBDA_DECAY, SPIRAL_FREQUENCY

def run_simulation():
    print("=== PHASE 7: TIME DIMENSION SIMULATION ===")
    
    d = Dictionary()
    
    # 1. Setup - Create a knowledge entry
    emb = np.random.normal(0, 1, 1024)
    emb /= np.linalg.norm(emb)
    
    entry_id = "TX_DYNAMIC_THOUGHT"
    d.add_entry(entry_id, emb, depth=1.0)
    
    pipeline = MinimalPipeline(d)
    
    print(f"\n[INITIAL STATE]")
    print(f"Entry: {entry_id} | Depth: {d._entry_depth[entry_id]:.4f}")
    
    # 2. Test Decay (λ=0.618)
    print(f"\n[DECAY TEST (λ={LAMBDA_DECAY})]")
    for i in range(1, 4):
        d.apply_time_evolution(1.0) # Tick 1 second (delta_t = 1.0)
        depth = d._entry_depth.get(entry_id, 0.0)
        print(f"Tick {i} (t={d.system_time}) | Remaining Depth: {depth:.4f}")
    
    # 3. Test Spiral Displacement (ω=0.382)
    print(f"\n[SPIRAL TEST (ω={SPIRAL_FREQUENCY})]")
    
    # Re-add entry if it decayed too much
    d.add_entry("SPIRAL_CORE", emb, depth=2.0)
    
    results = []
    query_emb = emb + np.random.normal(0, 0.05, emb.shape)
    query_emb /= np.linalg.norm(query_emb)
    
    for i in range(5):
        # Update system time manually for simulation if using scout directly
        pipeline.system_time += 1.0
        
        # We use a static input to see if results change over time
        msg, wf = pipeline.scout.process(query_emb, content="Constant context for spiral test", t=pipeline.system_time, displacement=True)
        results.append((msg.t, np.linalg.norm(wf.delta), msg.structural_hash))
        print(f"Cycle {i} | t={msg.t} | |Δ|={np.linalg.norm(wf.delta):.4f} | Hash: {msg.structural_hash}")
        
    # Check if hashes/magnitudes change
    if results[0][1] != results[-1][1]:
        print("\n[VERIFIED] Spiral displacement active (Delta magnitude evolved).")
    else:
        print("\n[FAILED] Delta magnitude remained static.")

    if results[0][2] != results[-1][2]:
        print("[VERIFIED] Structural Hash displacement active.")
    else:
        print("[FAILED] Structural Hash remained static.")

if __name__ == "__main__":
    run_simulation()
