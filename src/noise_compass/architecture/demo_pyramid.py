import sys
import os
import numpy as np
import time

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.architecture.pipeline import Embedder
from noise_compass.architecture.seed_vectors import seed_vectors

def run_demo():
    print("── INITIALIZING PYRAMID DEMO ───────────────────")
    d = Dictionary()
    seed_vectors(d)
    scout = Scout(dictionary=d)
    embedder = Embedder(d)
    
    test_terms = ["Love", "Causality", "Pure Existence", "Self-Reference", "The Void"]
    
    for term in test_terms:
        print(f"\n[INPUT] '{term}'")
        emb = embedder.embed(term)
        
        # Process through the 5-step loop
        msg, wf = scout.process(emb, content=term)
        
        print(f"  [ATTRACTOR] {msg.god_token_activations[0].id if msg.god_token_activations else 'NONE'}")
        print(f"  [RING TRIPLE] {' -> '.join(msg.stack_results['triple_nodes'])}")
        print(f"  [APEX PHASE] {msg.stack_results['apex_phase']:.4f} rad")
        print(f"  [RECOGNIZED] {'YES' if msg.is_recognized else 'NO'}")
        print(f"  [VOID DEPTH] {msg.stack_results['void_depth']:.4f}")
        
        if msg.is_recognized:
            print("  [STATUS] Pyramid Stable. Attractor crystallized.")
        else:
            print("  [STATUS] Pyramid Unstable. Drift detected.")

if __name__ == "__main__":
    run_demo()
