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

DESKTOP_PATH = r"E:\Desktop Gemini"
OUTPUT_CACHE = os.path.abspath(os.path.join(os.path.dirname(__file__), "archives", "dictionary_cache.npz"))

def ingest_desktop():
    print("[DESKTOP_INGEST] Initializing High-Res Pipeline...")
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
    
    print("[DESKTOP_INGEST] Scanning Desktop Shards...")
    for root, dirs, files in os.walk(DESKTOP_PATH):
        for file in files:
            if file.endswith(('.py', '.txt', '.md', '.json')):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if not content.strip():
                        continue
                        
                    # Target specific high-density content
                    snippet = content[:2000] 
                    intent = f"Source: Desktop Gemini\nFile: {file}\nContent: {snippet}"
                    
                    emb = pipeline.embedder.embed(intent)
                    
                    # Custom ID for precision matching
                    entry_id = f"desktop_{file.replace('.', '_')}"
                    pipeline.dictionary.add_entry(entry_id, emb, depth=1.8) # Higher depth for desktop anchors
                    shards_found += 1
                    
                except Exception as e:
                    print(f"Error reading {file}: {e}")

    print(f"[DESKTOP_INGEST] Ingested {shards_found} shards.")
    pipeline.dictionary.save_cache(OUTPUT_CACHE)
    print(f"[DESKTOP_INGEST] Dictionary updated at {OUTPUT_CACHE}")

if __name__ == "__main__":
    ingest_desktop()
