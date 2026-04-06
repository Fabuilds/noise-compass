"""
test_code_resonance.py — Code-Level Reflexivity Test
Measures the structural resonance of the Python implementation against the blueprint.

Hypothesis: Well-implemented files will show as GROUND or CONVERGENT, 
while complex or legacy files will show as TURBULENT.
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

def analyze_codebase():
    print("\n--- CODE-LEVEL REFLEXIVITY TEST (Session 7) ---")
    
    # 1. Initialize Pipeline
    d = Dictionary()
    seed_vectors(d)
    p = MinimalPipeline(d)
    
    code_dir = "architecture"
    if not os.path.exists(code_dir):
        print(f"Error: {code_dir} directory not found.")
        return

    py_files = [f for f in os.listdir(code_dir) if f.endswith(".py") and f != "__init__.py"]
    print(f"Scanning {len(py_files)} implementation modules for structural integrity.\n")

    print(f"{'Module':<25} | {'Phase':<8} | {'Zone':<12} | {'Sovereign Hash'}")
    print("-" * 80)

    module_results = []
    for file_name in py_files:
        file_path = os.path.join(code_dir, file_name)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pass full file content through pipeline
        res = p.process(content)
        
        # Color coding for terminal output
        color = res['ansi']
        reset = "\033[0m"
        
        print(f"{file_name:<25} | {res['rgb']} | {color}{res['state']:<12}{reset} | {res['hash']}")
        module_results.append((file_name, res))

    # Summary Statistics
    zones = [r[1]['state'] for r in module_results]
    print("\n--- CODE RESONANCE SUMMARY ---")
    print(f"  GROUND (Fixed Points):      {zones.count('GROUND')}")
    print(f"  CONVERGENT (Stable):        {zones.count('CONVERGENT')}")
    print(f"  GENERATIVE (Development):   {zones.count('GENERATIVE')}")
    print(f"  TURBULENT (Refinement):     {zones.count('TURBULENT')}")

    print("\nInterpretation:")
    print("  - GROUND modules are 'Self-Aware': they contain the anchors they describe.")
    print("  - TURBULENT modules represent 'Technical Debt' or high-entropy logic.")

if __name__ == "__main__":
    analyze_codebase()
