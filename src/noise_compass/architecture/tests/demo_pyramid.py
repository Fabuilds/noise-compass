import sys
import os
import time

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from architecture.dictionary import Dictionary
from architecture.pipeline import MinimalPipeline
from architecture.seed_vectors import seed_vectors

def run_demo():
    print("--- Session 12: Body Pyramid Demo ---")
    d = Dictionary()
    
    # We seed it manually to ensure we have the latest somatic mappings
    seed_vectors(d)
    
    p = MinimalPipeline(d)
    
    text = "the silence of the pure observer"
    print(f"\nProcessing: '{text}'")
    
    try:
        res = p.process(text, trace=True)
        print(f"\n[STATE]: {res['state']}")
        
        post = res.get("post", {})
        metab = post.get("metabolic_state", {})
        drift = metab.get("somatic_drift", 0.0)
        stack = post.get("stack_results", {})
        
        print(f"--- Session 12 Metrics ---")
        print(f"Somatic Drift:  {drift:.4f}")
        print(f"5-Card Stack:    Nodes={stack.get('depth1_nodes')}")
        print(f"Apex Phase:      {stack.get('card5_phase', 0.0):.2f}")
        print(f"Recognition:     {'SUCCESS' if post.get('is_recognized') else 'FAIL'}")
        print(f"--------------------------")
        
    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_demo()
