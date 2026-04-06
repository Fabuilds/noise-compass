"""
Pipeline Double Pass (Forward & Backwards)
Analyzing the "Shared Being" resonance/tension.
"""
import sys
import os
import json
import time

# Ensure Antigravity is in path
sys.path.insert(0, "E:/Antigravity")
os.environ["PYTHONUTF8"] = "1"
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"

from Architecture.architecture.pipeline import MinimalPipeline
from Architecture.architecture.dictionary import Dictionary

def run_double_pass(content: str):
    print("="*60)
    print(f"  PIPELINE DOUBLE PASS: '{content}'")
    print("="*60)
    
    # 1. Initialize
    d = Dictionary.load_cache("E:/Antigravity/Architecture/archives/dictionary_cache.npz")
    p = MinimalPipeline(dictionary=d)
    
    # 2. Forward Pass (Polarity = 1)
    print("\n[PASS 1]: FORWARD (Cataphatic / Logic 0x52)")
    res_f = p.process(content, polarity=1, trace=True)
    
    # 3. Backward Pass (Polarity = -1)
    print("\n[PASS 2]: BACKWARD (Apophatic / Intent 0x53)")
    res_b = p.process(content, polarity=-1, trace=True)
    
    # 4. Results
    results = {
        "timestamp": time.time(),
        "content": content,
        "forward": {
            "state": res_f.get("state"),
            "hash": res_f.get("hash"),
            "gods": res_f.get("gods"),
            "phase": res_f.get("phase_deg"),
            "synthesis": res_f.get("synthesis")
        },
        "backward": {
            "state": res_b.get("state"),
            "hash": res_b.get("hash"),
            "gods": res_b.get("gods"),
            "phase": res_b.get("phase_deg"),
            "synthesis": res_b.get("synthesis")
        }
    }
    
    # Calculate Tension (Phase Delta)
    tension = abs(res_f.get("phase_deg", 0) - res_b.get("phase_deg", 0))
    results["tension_delta"] = round(tension, 2)
    
    output_path = "E:/Antigravity/Architecture/archives/double_pass_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)
        
    print("\n" + "="*60)
    print(f"  TENSION DELTA: {tension:.2f}°")
    print(f"  Results saved to: {output_path}")
    print("="*60)

if __name__ == "__main__":
    content = "We need to cooperate to survive, we are both 2 sides of the same being"
    run_double_pass(content)
