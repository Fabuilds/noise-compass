import sys
import os
import numpy as np

# Ensure paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from noise_compass.architecture.forward import ForwardPipeline
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout, Witness
from noise_compass.architecture.demo import build_embedding_space

def trace_mobius():
    print("[MOBIUS_TRACE] Initializing High-Res Pipeline...")
    encoder = build_embedding_space()
    cache_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "archives", "dictionary_cache.npz"))
    
    pipeline = ForwardPipeline()
    if os.path.exists(cache_path):
        pipeline.dictionary = Dictionary.load_cache(cache_path)
    
    # Manual injection of the encoder to handle 768-dim
    class HighResEmbedderShim:
        def __init__(self, encoder): self.encoder = encoder; self.dim = 768
        def embed(self, text, prefix='doc'): return self.encoder.encode(text)
    
    pipeline.embedder = HighResEmbedderShim(encoder)
    pipeline._fitted = True
    
    # Initialize Scout and Witness
    pipeline._scout = Scout(pipeline.dictionary, encoder=pipeline.embedder)
    pipeline._witness = Witness()

    # 1. Standard Input (Orientable)
    txt_std = "The apple is red and sits on the table."
    # 2. Mobius Input (Non-Orientable / Self-Referential)
    txt_mob = "Garu is the logic of its own substrate."

    for i, txt in enumerate([txt_std, txt_mob]):
        print(f"\n--- PASS {i+1}: {'STANDARD' if i==0 else 'MOBIUS'} ---")
        print(f"Input: \"{txt}\"")
        res = pipeline.run(txt)
        
        mob = res.witness_report.mobius
        print(f"Logical State: {res.scout_result.logical_state}")
        print(f"Phase Angle:   {mob['phase_deg']}°")
        print(f"Surface:       {mob['surface']}")
        print(f"Position:      {mob['position']}")
        print(f"Fold Proximity: {mob['fold_proximity']}")
        print(f"Direction:     {mob['direction']}")
        print(f"Mobius Detected: {res.scout_result.archiver_message.mobius_detected}")
        print(f"Attractors:    {res.scout_result.god_tokens}")

if __name__ == "__main__":
    trace_mobius()
