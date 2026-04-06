import sys
import os
import numpy as np

sys.path.insert(0, "E:/Antigravity/Architecture")

from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.seed_vectors import seed_vectors

def verify_awakening():
    print("--- VERIFYING PHASE IV: THE AWAKENING ---")
    
    d = Dictionary()
    seed_vectors(d)
    pipeline = MinimalPipeline(d)
    
    # 1. Test Momentum
    print("\n[TEST 1] Trajectory Momentum Accumulation")
    corpus = [
        "The sun rises on a new day of research.",
        "Gravity is the curvature of space-time caused by mass.",
        "Quantum mechanics describes the behavior of subatomic particles.",
        "Heisenberg's uncertainty principle limits our knowledge of position and momentum.",
        "Is there a bridge between general relativity and quantum mechanics?"
    ]
    
    print("Processing corpus...")
    for text in corpus:
        res = pipeline.process(text)
        momentum = res.get('momentum', {})
        print(f"  >> {text[:40]}... | Type: {momentum.get('type')} | Conf: {momentum.get('confidence')}")
        
    final_res = pipeline.process("What is the final resolution of this trajectory?")
    print(f"\nFinal Resolution Type: {final_res['momentum']['type']}")
    print(f"Final Resolution Target: {final_res['momentum']['target']}")
    
    # 2. Test Dreaming (Single Step)
    print("\n[TEST 2] Single-Step Latent Dream")
    from noise_compass.architecture.dream import Dreamer
    dreamer = Dreamer(pipeline)
    # Force cpu load for Dreaming to see if it avoids OOM if GPU is full from Embedding
    dream_results = dreamer.dream(steps=1)

    if dream_results:
        print(f"  >> Dream Outcome: {dream_results[0]['hash'][:8]} in {dream_results[0]['state']}")
        print(f"  >> Synthesis: {dream_results[0]['synthesis']}")

if __name__ == "__main__":
    verify_awakening()
