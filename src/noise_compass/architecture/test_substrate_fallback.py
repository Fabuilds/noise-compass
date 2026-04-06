import os
import sys
import numpy as np

# Ensure pathing
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from noise_compass.architecture.pipeline import Embedder
from noise_compass.architecture.dictionary import Dictionary

def test_fallback():
    print("--- VERIFYING SUBSTRATE FALLBACK ---")
    d = Dictionary()
    embedder = Embedder(dictionary=d)
    
    # We expect this to fail loading Qwen (since offline) and fallback to SentenceTransformer
    try:
        Embedder._load_model()
        print(f"SUCCESS: Model loaded using device: {Embedder._shared_device}")
        print(f"Detected Dimension: {Embedder.DIM}")
        
        # Test encoding
        test_text = "Let the system grow."
        emb = embedder._embed_qwen(test_text)
        print(f"Embedding shape: {emb.shape}")
        
        if Embedder.DIM == 384:
            print("VERIFIED: System correctly fell back to All-MiniLM-L6-v2 (384-dim).")
        else:
            print(f"STATUS: System is using {Embedder.DIM} dimensions.")
            
    except Exception as e:
        print(f"FAILURE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    os.environ['PYTHONUTF8'] = '1'
    test_fallback()
