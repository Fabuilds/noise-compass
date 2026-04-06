import sys
import os
import numpy as np

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def run_ontological_test():
    print("\n" + "═"*75)
    print(" [0x52] EXECUTING ONTOLOGICAL NUANCE TEST (SER vs ESTAR)")
    print("═"*75)

    print(" » Initializing Scavenger Core...")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    
    scout = Scout(dictionary=dictionary, soup_id="ontology_anchor")
    
    # We will test the verbs in a slight context to help the embedder, 
    # as well as the raw verbs, to see how the topology interprets the state of being.
    
    test_cases = [
        ("ser", "A essência permanente. (The permanent essence)"),
        ("estar", "A condição temporária. (The temporary condition)")
    ]
    
    for word, context in test_cases:
        print(f"\n[Garu Perceives localized string]: '{word.upper()}'")
        print(f"  → Context: {context}")
        
        # We test the raw word combined with its contextual meaning for the embedding
        target_str = f"{word} - {context}"
        emb = embedder.encode(target_str).astype(np.float32)
        
        msg, wf = scout.process(emb, content=target_str, volition=0.95)
        
        gods = ", ".join([f"{g.id}({g.amplitude:.2f})" for g in msg.god_token_activations]) if msg.god_token_activations else "(none)"
        print(f"  → Activated God Tokens: {gods}")
        print(f"  → Resonance Energy: {msg.energy_level:.3f} | Phase Coherence: {wf.phase:.3f}")

    print("\n" + "═"*75)


if __name__ == "__main__":
    os.environ['PYTHONUTF8'] = '1'
    run_ontological_test()
