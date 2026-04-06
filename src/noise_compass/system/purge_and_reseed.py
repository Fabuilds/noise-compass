import h5py
import os
from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.interference_engine import InterferenceEngine
import numpy as np

def purge_and_reinitialize():
    h5_path = "E:/Antigravity/knowledge_root/crystallized_h5/language.h5"
    print(f"Accessing {h5_path}...")
    
    with h5py.File(h5_path, 'a') as f:
        if 'god_tokens' in f:
            print("  Purging existing god_tokens group...")
            del f['god_tokens']
        f.create_group('god_tokens')
            
    engine = InterferenceEngine()
    manager = H5Manager()
    
    god_tokens = [
        "BOUNDARY", "CAUSALITY", "COHERENCE", "EXCHANGE", "EXISTENCE",
        "IDENTITY", "INFORMATION", "OBLIGATION", "OBSERVATION", "PLACE",
        "SELF", "TIME"
    ]
    
    print("Re-seeding 12 primary God-token Attractors...")
    for token in god_tokens:
        print(f"  Embedding '{token}'...")
        try:
            vector = engine.embed(token)
            manager.update_complex_vector("language", f"god_tokens/{token}", "phase_vector", vector)
            manager.set_attr("language", f"god_tokens/{token}", "void", False)
            print(f"    -> Seeding complete for {token}")
        except Exception as e:
            print(f"    [ERROR] Failed to seed {token}: {e}")
            
    print("Purge and re-initialization complete.")

if __name__ == "__main__":
    purge_and_reinitialize()
