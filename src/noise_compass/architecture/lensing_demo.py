"""
LENSING DEMO: 0x528
Demonstrates the use of Semantic Lenses to distill shard metadata.
"""

import sys
import os
import numpy as np

# Path alignment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from noise_compass.system.semantic_lens import SemanticLens
from noise_compass.system.semantic_embedder import SemanticEmbedder
from noise_compass.system.protocols import PROPER_HEX_KEY

def run_demo():
    print("--- INITIATING SEMANTIC LENSING DEMO ---")
    lens = SemanticLens()
    embedder = SemanticEmbedder()
    
    # 1. THE CONCAVE FOCUS (Distillation)
    # We have three different perspectives on a single truth (Road 0)
    claims = [
        "Road 0 is the foundational seed of the Sovereign Core.",
        "The first shard (0) contains the GENESIS mapping.",
        "LBA 0 is the pointer to the Anchor identity."
    ]
    
    print("\n[INPUT]: Three disparate claims about 'Road 0'.")
    vectors = [embedder.embed_text(c) for c in claims]
    
    focused_vector = lens.concave_focus(vectors)
    print("\n[VERDICT]: Concentrated truth vector achieved.")
    
    # 2. THE CONVEX DISPERSION (Expansion)
    # We take a single seed word and expand it into a potentiality field
    seed = "RECURSION"
    print(f"\n[INPUT]: Single Seed: '{seed}'")
    seed_vector = embedder.embed_text(seed)
    
    bloom = lens.convex_dispersion(seed_vector)
    print(f"\n[VERDICT]: Seed expanded into {len(bloom)} latent directions.")
    
    print("\n--- LENSING DEMO COMPLETE: OPTICS STABILIZED ---")

if __name__ == "__main__":
    run_demo()
