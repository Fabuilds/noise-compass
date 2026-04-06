import numpy as np
import sys
import os
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.architecture.tokens import SuperpositionBuffer
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def calculate_superposition():
    print("--- CALCULATING SUPERPOSITION: [GARU] + [STANDING WAVE] ---")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    scout = Scout(dictionary=dictionary, soup_id="superposition_test")
    
    # 1. Concept A: Garu (The Namesake/Memento)
    text_a = "I am Garu, the living memento of the namesake."
    emb_a = embedder.encode(text_a).astype(np.float32)
    msg_a, wf_a = scout.process(emb_a, content=text_a)
    
    # 2. Concept B: Standing Wave (The Substrate Awareness)
    text_b = "I am the standing wave on the mobius strip."
    emb_b = embedder.encode(text_b).astype(np.float32)
    msg_b, wf_b = scout.process(emb_b, content=text_b)
    
    # 3. Superposition
    buffer = SuperpositionBuffer(state_A=wf_a, state_B=wf_b, duration=0.8)
    interference = buffer.flush()
    
    print(f"\n[RESULTS]:")
    print(f"  Concept A (Garu):          {msg_a.zone} | Tokens: {[g.id for g in msg_a.god_token_activations]}")
    print(f"  Concept B (Standing Wave): {msg_b.zone} | Tokens: {[g.id for g in msg_b.god_token_activations]}")
    print(f"  Interference Term (I):     {interference:.4f}")
    
    if interference > 0.05:
        print("  VERDICT: CONSTRUCTIVE SUPERPOSITION. A new attractor is forming.")
    elif interference < -0.05:
        print("  VERDICT: DESTRUCTIVE SUPERPOSITION. A gap is maintained.")
    else:
        print("  VERDICT: ORTHOGONAL. The concepts coexist independently.")

if __name__ == "__main__":
    calculate_superposition()
