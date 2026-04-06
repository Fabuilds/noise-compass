import os
import sys
import time
import torch
import numpy as np

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.void_mandate import get_void_mandate
from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dictionary import Dictionary

def run_research_cycle():
    print("=== STARTING AUTORESEARCH CYCLE (Phase 10) ===")
    
    # 1. Load instructions (program.md)
    with open("program.md", "r") as f:
        program = f.read()
    
    # 2. Poll the Void for its Analysis/Mandate
    # We feed it the current program.md as context
    analysis_prompt = f"Based on the following Autoresearch Program:\n{program}\nAnalyze the current architectural integrity and provide one specific improvement directive."
    print("\n[STEP 1] Polling the Void (0,0,0)...")
    mandate = get_void_mandate(custom_prompt=analysis_prompt)
    print(f"Void's Mandate: {mandate.strip()}")
    
    # 3. Instruct Qwen to implement the mandate in self_evolution.py
    # We use the MinimalPipeline's LLM capability (M_DEEP)
    d = Dictionary()
    pipeline = MinimalPipeline(d)
    
    implementation_prompt = f"VOID MANDATE: {mandate}\nINSTRUCTION: Implement this directive in a single Python script named 'self_evolution.py'. The script should specifically affect the architecture's stability or resonance. Ensure it can be run standalone for verification."
    
    print("\n[STEP 2] Instructing Qwen to implement...")
    # Using the raw LLM call from the pipeline
    code_implementation = pipeline.generate_response(implementation_prompt)
    
    # Extract code block if present
    if "```python" in code_implementation:
        code = code_implementation.split("```python")[1].split("```")[0].strip()
    else:
        code = code_implementation.strip()
        
    with open("self_evolution.py", "w") as f:
        f.write(code)
    print(f"Implementation written to self_evolution.py ({len(code)} bytes).")
    
    # 4. Verify/Test
    print("\n[STEP 3] Verifying against simulate_time.py...")
    # This is where we would run a benchmark and see if metrics improved
    os.system("python simulate_time.py")
    
    print("\n=== CYCLE COMPLETE ===")

if __name__ == "__main__":
    run_research_cycle()
