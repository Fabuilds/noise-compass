import sys
import os
import numpy as np
from pathlib import Path

# Ensure paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.forward import ForwardPipeline
from noise_compass.architecture.demo import build_embedding_space

def find_new_tokens():
    print("[DISCOVERY_MODE] Initializing High-Res Expansion (Nomic-Embed 768 Mode)...")
    
    # Locate the real dictionary cache
    cache_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "archives", "dictionary_cache.npz"))
    
    # Load the REAL encoder (whitened NomicEmbed)
    print("[DISCOVERY_MODE] Loading High-Resolution Encoder...")
    encoder = build_embedding_space()
    
    if os.path.exists(cache_path):
        print(f"[DISCOVERY_MODE] Loading settled dictionary from {cache_path}")
        dictionary = Dictionary.load_cache(cache_path)
    else:
        print("[DISCOVERY_MODE] No dictionary cache found. Creating fresh...")
        dictionary = Dictionary()

    # Broad, profound lexicon to probe for new attractors
    lexicon = [
        "PARADOX", "VOID", "ENTROPY", "VOLITION", "SYNERGY", "SOURCE",
        "DECAY", "AGENCY", "JUSTICE", "GRACE", "BEAUTY", "TRUTH",
        "EMPTINESS", "ABSOLUTE", "VIRTUE", "SACRIFICE", "PROVIDENCE",
        "SOVEREIGNTY", "TRANSCENDENCE", "IMMANENCE", "COSMOS", "CHAOS",
        "EQUILIBRIUM", "TURBULENCE", "RESONANCE", "DISSOLUTION", "SYNTHESIS",
        "TRANSUBSTANTIATION", "QUINTESSENCE", "SINGULARITY", "PRIMORDIAL",
        "ETHER", "AXIOM", "DYNAMIS", "ENERGEIA", "ENTELECHY", "MONAD",
        "DUALITY", "TRINITY", "QUATERNITY", "LIMIT", "INFINITE",
        "TEMPORALITY", "ETERNITY", "RECURSION", "SELF_REFERENCE"
    ]
    
    total_found = 0
    newly_crystallized = []

    print(f"\n[PHASE 1]: Probing Lexicon ({len(lexicon)} terms)")
    for term in lexicon:
        # Use the real encoder
        emb = encoder.encode(term)
        _, sim, _ = dictionary.query(emb)
        
        # Check for gaps/new attractors
        # Threshold 0.88 sim check is inside maybe_crystallize
        new_id = dictionary.maybe_crystallize(emb, sim)
        if new_id:
            print(f"  [+] CRYSTALLIZED: `{new_id}` (from '{term}', sim={sim:.3f})")
            newly_crystallized.append((new_id, term))
            total_found += 1
        else:
            if sim > 0.88:
                print(f"  [.] Already indexed: '{term}' (sim={sim:.3f})")

    print(f"\n[DISCOVERY_MODE] Sequence Complete.")
    print(f"TOTAL NEW ANCHORS FOUND: {total_found}")
    
    if total_found > 0:
        print(f"[DISCOVERY_MODE] Persisting {total_found} entries to {cache_path}")
        dictionary.save_cache(cache_path)
        
        # Log to the permanent record
        log_path = os.path.join(os.path.dirname(__file__), "discovery_log.txt")
        with open(log_path, "a") as f:
            for nid, src in newly_crystallized:
                f.write(f"{nid} | {src}\n")
        print(f"[DISCOVERY_MODE] Discovery log updated at {log_path}")

if __name__ == "__main__":
    find_new_tokens()
