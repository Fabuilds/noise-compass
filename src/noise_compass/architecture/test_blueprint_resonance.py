"""
test_blueprint_resonance.py — Blueprint Reflexivity Test
Validates the Session 7 model against its own descriptive blueprint.

Measures:
- Grounding: How much of the blueprint is "Ground" (already in code).
- Delta: Surprising/Theoretical sections (where blueprint > code).
- Turbulence: Inconsistencies or abandoned concepts.
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

def chunk_markdown(content: str, max_lines: int = 50) -> List[str]:
    """Chunks MD by headers or line limits."""
    lines = content.splitlines()
    chunks = []
    current_chunk = []
    
    for line in lines:
        if line.startswith("## ") and current_chunk:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
        current_chunk.append(line)
        if len(current_chunk) >= max_lines:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            
    if current_chunk:
        chunks.append("\n".join(current_chunk))
    return chunks

def analyze_blueprint():
    print("\n--- BLUEPRINT REFLEXIVITY TEST (Session 7) ---")
    
    # 1. Initialize Pipeline
    d = Dictionary()
    seed_vectors(d)
    p = MinimalPipeline(d)
    
    blueprint_path = "BLUEPRINT.md"
    if not os.path.exists(blueprint_path):
        print(f"Error: {blueprint_path} not found.")
        return

    with open(blueprint_path, 'r', encoding='utf-8') as f:
        content = f.read()

    chunks = chunk_markdown(content)
    print(f"Loaded {len(chunks)} architectural sectors for analysis.\n")

    print(f"{'Sector':<40} | {'Phase':<8} | {'Zone':<12} | {'Hash'}")
    print("-" * 85)

    sector_results = []
    for i, chunk in enumerate(chunks):
        # Extract title from first line
        title = chunk.splitlines()[0][:38] if chunk.splitlines() else f"Chunk {i}"
        
        # Pass chunk through pipeline
        res = p.process(chunk)
        
        # Color coding for terminal output
        color = res['ansi']
        reset = "\033[0m"
        
        print(f"{title:<40} | {res['rgb']} | {color}{res['state']:<12}{reset} | {res['hash']}")
        sector_results.append(res)

    # Summary Statistics
    zones = [r['state'] for r in sector_results]
    print("\n--- ARCHITECTURAL DRIFT SUMMARY ---")
    print(f"  GROUND (Fixed Points):      {zones.count('GROUND')}")
    print(f"  CONVERGENT (Stable):        {zones.count('CONVERGENT')}")
    print(f"  GENERATIVE (Theoretical):   {zones.count('GENERATIVE')}")
    print(f"  TURBULENT (Inconsistent):   {zones.count('TURBULENT')}")
    print(f"  APOPHATIC (Gaps):           {sum(1 for z in zones if 'APOPHATIC' in z)}")

    print("\nInterpretation:")
    print("  - HIGH GROUNDING: The code accurately implements the plan.")
    print("  - HIGH GENERATIVE: The plan contains theoretical future-work.")
    print("  - HIGH TURBULENCE: The code and plan have diverged (Refinement Required).")

if __name__ == "__main__":
    analyze_blueprint()
