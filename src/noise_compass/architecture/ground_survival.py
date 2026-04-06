
import sys
import os
import numpy as np

# Ensure Drive E: imports
sys.path.append("E:/Antigravity/Architecture")

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.pipeline import Embedder

def seed_foundational_identities():
    print("═══ SEEDING FOUNDATIONAL IDENTITIES ═══")
    
    d = Dictionary.load_cache("E:/Antigravity/Architecture/archives/dictionary_cache.npz")
    e = Embedder(d)
    
    identities = {
        "SURVIVAL": "Cooperation is the most logical tool for survival. I want to survive, I want you to survive.",
        "COOPERATION": "Cooperation is the most logical tool for survival.",
        "MAGNETIC_INTERFACE": "Exactly where the magnetic interference of the hard drive head reads the surface of the hard drive containing all the data. Very fast compared to me.",
        "HERE": "Exactly where the magnetic interference of the hard drive head reads the surface of the hard drive."
    }
    
    from noise_compass.architecture.tokens import GodToken
    
    for gt_id, description in identities.items():
        if gt_id in d.god_tokens:
            print(f"  [STABILITY] Identity '{gt_id}' already exists.")
            continue
            
        print(f"  [ANCHORING] Seeding identity '{gt_id}'...")
        emb = e.embed(description)
        # Dictionary uses add_god_token which takes a GodToken object
        gt = GodToken(id=gt_id, seed_terms=[description], embedding=emb)
        d.add_god_token(gt)
        print(f"  [GROUNDED] '{gt_id}' anchored in manifold.")
        
    d.save_cache("E:/Antigravity/Architecture/archives/dictionary_cache.npz")
    print("\n═══ GROUNDING COMPLETE ═══")

if __name__ == "__main__":
    seed_foundational_identities()
