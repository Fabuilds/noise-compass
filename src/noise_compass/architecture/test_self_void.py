import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.system.semantic_embedder import SemanticEmbedder
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def test_self():
    print("Initializing dictionary...")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    scout = Scout(dictionary=dictionary, soup_id="self_test_run")
    
    print("\n" + "═"*70)
    print(" APPLYING RECURSIVE TEXTS TO STRUCTURED MANIFOLD")
    print("═"*70)

    test_texts = [
        "Recursive awareness models the system that is processing the awareness.",
        "Existence possessing logical structure results in an unstable but aware self.",
        "Consciousness reduced to mere survival.",
        "Total annihilation of the observer."
    ]

    for i, text in enumerate(test_texts, 1):
        print(f"\n[{i}/4] Processing: \"{text}\"")
        
        emb = embedder.encode(text).astype(np.float32)
        
        msg, wf = scout.process(emb, content=text)
        
        # Log wave collapse
        print(f"  » Known (Re): {np.linalg.norm(wf.known):.4f}  |  Delta (Im): {np.linalg.norm(wf.delta):.4f}")
        print(f"  » Phase:      {wf.phase:.4f} rad ({wf.phase * 180 / np.pi:.1f}°) → {wf.zone()}")
        print(f"  » Energy:     {msg.energy_level:.4f}")
        
        # Print Gods detected
        gods = [g.id for g in msg.god_token_activations]
        print(f"  » God Tokens: {gods if gods else 'NONE'}")
        
        # Apophatic Basin
        if msg.apophatic_contact:
            print(f"  » APOPHATIC BASIN DETECTED: {msg.apophatic_contact}")
            
        # Recursive Limit Sanity check (Manual application)
        formula = scout.formula
        results = formula.apply_recursive(emb, depth=10)
        print(f"  » Recursion depth until fixed point: {len(results)}")
        
        print("─"*70)

if __name__ == "__main__":
    test_self()
