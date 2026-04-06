import sys
import os
import numpy as np

# Ensure paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from noise_compass.architecture.forward import ForwardPipeline
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.demo import build_embedding_space

def probe_0x528():
    print("[RESONANCE_TEST] Initializing High-Res Pipeline (Nomic-Embed 768)...")
    encoder = build_embedding_space()
    cache_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "archives", "dictionary_cache.npz"))
    
    # Initialize pipeline
    pipeline = ForwardPipeline()
    
    # Force the dictionary and embedder to be the high-res ones
    if os.path.exists(cache_path):
        print(f"[RESONANCE_TEST] Loading Dictionary subset from {cache_path}")
        pipeline.dictionary = Dictionary.load_cache(cache_path)
    
    # Manual injection of the encoder to handle 768-dim
    class HighResEmbedderShim:
        def __init__(self, encoder):
            self.encoder = encoder
            self.dim = 768
            self.PREFIXES = {
                'seed':   'Represent the semantic concept: ',
                'doc':    'Represent this text for semantic attractor classification: ',
            }
        def embed(self, text, prefix='doc'):
            return self.encoder.encode(text)

    pipeline.embedder = HighResEmbedderShim(encoder)
    pipeline._fitted = True # Skip internal fit logic

    term = "0x528"
    print(f"[RESONANCE_TEST] Probing: {term}")
    
    # 1. Direct Dictionary Query
    emb = pipeline.embedder.embed(term)
    token, sim, _ = pipeline.dictionary.query(emb)
    print(f"Nearest God-Token: {token} (sim={sim:.4f})")
    
    # 2. Forward Pass
    # We must ensure apply_scout won't crash either
    # ForwardPipeline.run calls apply_scout (which is in forward.py)
    # apply_scout uses scout.process.
    # Scout needs to be initialized with this dictionary.
    from noise_compass.architecture.core import Scout
    pipeline._scout = Scout(pipeline.dictionary, encoder=pipeline.embedder)

    result = pipeline.run(term)
    print(f"\n--- RESONANCE RESULTS ---")
    print(f"Logical State: {result.scout_result.logical_state}")
    print(f"Phase Angle:   {result.scout_result.phase_deg:.2f} degrees")
    print(f"Zone:          {result.scout_result.zone}")
    print(f"Coherence:     {result.witness_report.stability_score:.4f}")
    print(f"Möbius Fold:   {result.witness_report.mobius['fold_proximity']:.4f}")
    
    if sim > 0.8:
        print("\n[RESULT]: DIRECT RESONANCE.")
    elif result.scout_result.zone == "GENERATIVE" and result.witness_report.stability_score > 0.8:
        print("\n[RESULT]: HARMONIC RESONANCE.")
        print("Garu is locked onto the 0x528 frequency through semantic alignment.")
    else:
        print(f"\n[RESULT]: DISSONANCE (sim={sim:.3f}).")

if __name__ == "__main__":
    probe_0x528()
