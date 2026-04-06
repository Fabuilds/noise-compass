import numpy as np
import sys
import os

# Add parent directory to sys.path for architecture imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout

def verify_zenith():
    print("--- ZENITH EVOLUTION VERIFICATION ---")
    d = Dictionary()
    
    # 1. Seed the dictionary with tokens to trigger y_spatial
    emb_dim = 1024
    vec_arch = np.random.randn(emb_dim).astype(np.float32)
    vec_arch /= np.linalg.norm(vec_arch)
    d.entries[1] = vec_arch
    d.god_tokens["ARCHITECT"] = type('GT', (), {'id': 'ARCHITECT', 'embedding': vec_arch})
    
    vec_place = np.random.randn(emb_dim).astype(np.float32)
    vec_place /= np.linalg.norm(vec_place)
    d.entries[2] = vec_place
    d.god_tokens["PLACE"] = type('GT', (), {'id': 'PLACE', 'embedding': vec_place})
    
    scout = Scout(d)
    
    # 2. Use a perturbed input near PLACE to trigger y_spatial
    input_emb = vec_place + 0.5 * np.random.randn(emb_dim).astype(np.float32)
    input_emb /= np.linalg.norm(input_emb)
    
    print(f"Initial z: {scout.z_persistence:.4f}")
    
    for i in range(10):
        msg, wf = scout.process(input_emb, content="Encountering PLACE on the manifold") 
        print(f"Pass {i+1}:")
        print(f"  w (known): {wf.w:.4f}")
        print(f"  x (semantic surprise): {wf.x_surprise:.4f}")
        print(f"  y (spatial surprise):  {wf.y_spatial:.4f}")
        print(f"  z (emergence):         {wf.z_emergence:.4f}")
        print("-" * 20)

if __name__ == "__main__":
    verify_zenith()
