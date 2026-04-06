from noise_compass.system.interference_engine import InterferenceEngine
from noise_compass.system.h5_manager import H5Manager
import numpy as np
import os

def initialize_attractors():
    # Only proceed if the model is ready (check a file or just run and catch)
    engine = InterferenceEngine()
    manager = H5Manager()
    
    god_tokens = [
        "BOUNDARY", "CAUSALITY", "COHERENCE", "EXCHANGE", "EXISTENCE",
        "IDENTITY", "INFORMATION", "OBLIGATION", "OBSERVATION", "PLACE",
        "SELF", "TIME"
    ]
    
    print("Seeding God-token Attractors with complex embeddings...")
    for token in god_tokens:
        print(f"  Embedding '{token}'...")
        try:
            vector = engine.embed(token)
            manager.update_complex_vector("language", f"god_tokens/{token}", "phase_vector", vector)
            print(f"    -> Saved phase_vector for {token}")
        except Exception as e:
            print(f"    [ERROR] Embedding {token} failed: {e}")
        
    print("Attractor initialization complete.")

if __name__ == "__main__":
    initialize_attractors()
