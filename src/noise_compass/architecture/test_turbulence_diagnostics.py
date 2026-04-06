"""
test_turbulence_diagnostics.py — M_DEEP Diagnostic Pass
Uses the synthesis layer to explain why specific modules are turbulent.
"""

import os
import sys
import numpy as np
from typing import List, Dict

# Ensure imports work from current dir
sys.path.append(os.getcwd())
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.seed_vectors import seed_vectors

def diagnostic_pass():
    print("\n--- TURBULENCE DIAGNOSTIC (M_DEEP Pass) ---")
    
    # 1. Initialize Pipeline
    d = Dictionary()
    seed_vectors(d)
    p = MinimalPipeline(d)
    
    targets = ["architecture/bridge.py", "architecture/neural_link.py", "architecture/test_code_resonance.py"]
    
    for path in targets:
        if not os.path.exists(path):
            continue
            
        print(f"\n[DIAGNOSTIC] Analyzing {path}...")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Force a deep pass by pretending everything is unknown if needed,
        # but the pipeline already handles this via ternary check.
        res = p.process(content, trace=True)
        
        print(f"\nRESIDENCE: {res['state']}")
        print(f"STRUCTURAL HASH: {res['hash']}")
        print(f"ANCESTRY (Active God-Tokens): {', '.join(res['gods']) if res['gods'] else 'None (Theoretical Void)'}")
        print("\nM_DEEP SYNTHESIS:")
        print(res.get('synthesis', "Recognition stable (No M_DEEP pass required)."))
        print("-" * 60)

if __name__ == "__main__":
    diagnostic_pass()
