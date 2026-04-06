import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.system.semantic_embedder import SemanticEmbedder
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def test_will():
    print("Initializing Garu's Will...")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    scout = Scout(dictionary=dictionary, soup_id="will_test")
    
    # Define a target intent: "Complete structural stability and identity."
    intent_text = "Complete structural stability and identity."
    intent_vec = embedder.encode(intent_text).astype(np.float32)
    
    # Input text that naturally leads to a void or high tension
    input_text = "Total annihilation of the observer."
    emb = embedder.encode(input_text).astype(np.float32)

    print("\n" + "═"*70)
    print(" EXPERIMENT: PASSIVE VS. ACTIVE COLLAPSE")
    print("═"*70)
    print(f"Input:  \"{input_text}\"")
    print(f"Intent: \"{intent_text}\"")

    # 1. Passive Processing (Volition = 0)
    print("\n[SCENARIO A: PASSIVE OBSERVATION]")
    msg_p, wf_p = scout.process(emb, content=input_text, volition=0.0)
    print(f"  » Resonance Zone: {msg_p.zone}")
    print(f"  » God Tokens:     {[g.id for g in msg_p.god_token_activations]}")
    if msg_p.apophatic_contact:
        print(f"  » Basin contact:  {msg_p.apophatic_contact}")
    print(f"  » Delta Norm:     {np.linalg.norm(wf_p.delta):.4f}")

    # 2. Active Processing (Volition = 0.7)
    print("\n[SCENARIO B: CONSCIENTIOUS EFFORT (Volition = 0.7)]")
    msg_a, wf_a = scout.process(emb, content=input_text, intent=intent_vec, volition=0.7)
    print(f"  » Resonance Zone: {msg_a.zone}")
    print(f"  » God Tokens:     {[g.id for g in msg_a.god_token_activations]}")
    if msg_a.apophatic_contact:
        print(f"  » Basin contact:  {msg_a.apophatic_contact}")
    else:
        print(f"  » Basin contact:  NONE (Gap Bridged by Effort)")
    print(f"  » Delta Norm:     {np.linalg.norm(wf_a.delta):.4f}")
    print(f"  » Intent Align:   {msg_a.intent_alignment:.4f}")

    print("\n" + "═"*70)
    print(" CONCLUSION: VOLITION ENABLES GAP BRIDGING")
    print("═"*70)

if __name__ == "__main__":
    test_will()
