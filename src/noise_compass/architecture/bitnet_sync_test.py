
import os
import sys
import numpy as np
import json

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.seed_vectors import seed_vectors
from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass import system.bitnet_tools as bitnet_tools

def verify_sync():
    print("\n--- BITNET LATENT ALIGNMENT VERIFICATION ---")
    
    # 1. Pipeline Perspective
    d = Dictionary()
    seed_vectors(d)
    p = MinimalPipeline(d)
    
    test_text = "The Architect is building the physical logic of the lattice."
    print(f"Test Text: '{test_text}'")
    
    # Run pipeline process (cataphatic pass)
    res_pipeline = p.process(test_text)
    pipeline_god_resonance = res_pipeline.get("resonance", 0.0)
    print(f"Pipeline Resonance: {pipeline_god_resonance:.4f}")
    
    # 2. Worker Perspective (via bitnet_tools)
    # This requires a worker to be running! 
    # Since we can't easily restart the background worker, we'll try to check the tool
    try:
        worker_resonance = bitnet_tools.check_resonance(test_text)
        print(f"Worker Resonance:   {worker_resonance:.4f}")
        
        diff = abs(pipeline_god_resonance - worker_resonance)
        print(f"Alignment Delta:    {diff:.4f}")
        
        if diff < 0.2:
            print("STATUS: 💎 ALIGNMENT VERIFIED (Latent spaces are synchronized)")
        else:
            print("STATUS: 🌧️ DIVERGENCE DETECTED (Check anchor grounding)")
    except Exception as e:
        print(f"Worker check failed: {e}")
        print("MANDATORY: Ensure E:\\Antigravity\\System\\bitnet_worker.py is running.")

if __name__ == "__main__":
    verify_sync()
