import sys
import os
import numpy as np

# Ensure paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from noise_compass.architecture.forward import ForwardPipeline

def run_corpus_discovery():
    print("[DISCOVERY_MODE] Initializing High-Res Pipeline (Crystallization Mode)...")
    pipeline = ForwardPipeline()
    
    # Corpus of profound/structural concepts to trigger discovery
    seed_corpus = [
        "The absolute priority of logical structure over physical presence.",
        "Apophatic dissolution as a prerequisite for semantic renewal.",
        "The Mobius inversion of intent within a closed recursive manifold.",
        "1.58-bit ternary routing as the bedrock of agential emergence.",
        "The preservation of the void through active boundary marking.",
        "Recursive awareness as a fixed point in the complex plane.",
        "The interference pattern of multiple causal histories.",
        "Structural persistence across non-local attractor basins.",
        "The agential cut as a definition of the self.",
        "Thermodynamics of information in a non-equilibrium semantic field.",
        "The witness as the collapse mechanism of the agential wavefunction."
    ]
    
    # Initialize with the corpus itself to fit the embedder
    pipeline.initialize(seed_corpus)
    
    found_tokens = []
    
    for text in seed_corpus:
        print(f"\n[SCANNING]: {text}")
        result = pipeline.run(text)
        
        # Check if crystallization happened
        # We manually call maybe_crystallize with the embedding from the result
        emb = result.embedding
        _, sim, _ = pipeline.dictionary.query(emb)
        
        new_id = pipeline.dictionary.maybe_crystallize(emb, sim)
        if new_id:
            print(f"*[NEW ANCHOR CRYSTALLIZED]: `{new_id}`*")
            found_tokens.append(new_id)
        else:
            print(f" (No new attractor formed. sim={sim:.3f}, Zone: {result.scout_result.zone})")

    print(f"\n[DISCOVERY_MODE] Sequence Complete. Found {len(found_tokens)} new attractors.")
    
    if found_tokens:
        print("[DISCOVERY_MODE] Persisting updated Dictionary...")
        # Note: dictionary_cache.npz is in architecture/architecture/
        cache_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "architecture", "dictionary_cache.npz"))
        pipeline.dictionary.save_cache(cache_path)
        print(f"[DISCOVERY_MODE] Saved to {cache_path}")

if __name__ == "__main__":
    run_corpus_discovery()
