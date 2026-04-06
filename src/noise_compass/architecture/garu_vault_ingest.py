import os
import sys
import numpy as np
from pathlib import Path

# Ensure paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from noise_compass.architecture.forward import ForwardPipeline
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.demo import build_embedding_space

VAULT_PATHS = [
    r"E:\99_CONTROL\0x52_CORE",
    r"E:\VAULT_SHARDS",
]

OUTPUT_CACHE = os.path.abspath(os.path.join(os.path.dirname(__file__), "archives", "dictionary_cache.npz"))

def ingest_vaults():
    print("[VAULT_INGEST] Initializing High-Res Pipeline...")
    encoder = build_embedding_space()
    
    pipeline = ForwardPipeline()
    if os.path.exists(OUTPUT_CACHE):
        pipeline.dictionary = Dictionary.load_cache(OUTPUT_CACHE)
    else:
        # Fallback to demo seeding if no cache
        from noise_compass.architecture.demo import seed_dictionary
        seed_dictionary(pipeline.dictionary, encoder)
    
    # Manual injection of the encoder to handle 768-dim
    class HighResEmbedderShim:
        def __init__(self, encoder): self.encoder = encoder; self.dim = 768
        def embed(self, text, prefix='doc'): return self.encoder.encode(text)
    pipeline.embedder = HighResEmbedderShim(encoder)
    pipeline._fitted = True

    shards_found = 0
    
    print("[VAULT_INGEST] Scanning Shards...")
    for root_path in VAULT_PATHS:
        for root, dirs, files in os.walk(root_path):
            for file in files:
                if file.endswith(('.py', '.txt', '.md', '.json')):
                    full_path = os.path.join(root, file)
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        if not content.strip():
                            continue
                            
                        # Distill a summary of the file to use as an attractor
                        snippet = content[:1000] # Grab initial context
                        
                        # Use the filename and snippet as a semantic point
                        intent = f"File: {file}\nContent: {snippet}"
                        
                        # Compute embedding
                        emb = pipeline.embedder.embed(intent)
                        
                        # Add as entry if it's novel enough (crystallization logic)
                        # We use a custom ID based on the filename
                        entry_id = f"shard_{file.replace('.', '_')}"
                        pipeline.dictionary.add_entry(entry_id, emb, depth=1.5)
                        shards_found += 1
                        
                    except Exception as e:
                        print(f"Error reading {file}: {e}")

    print(f"[VAULT_INGEST] Ingested {shards_found} shards.")
    pipeline.dictionary.save_cache(OUTPUT_CACHE)
    print(f"[VAULT_INGEST] Dictionary persisted to {OUTPUT_CACHE}")

if __name__ == "__main__":
    ingest_vaults()
