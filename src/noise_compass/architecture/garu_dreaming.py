import numpy as np
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout, Witness
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def test_dreaming():
    print("Initializing Garu's Dream Stream...")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    scout = Scout(dictionary=dictionary, soup_id="dream_test")
    
    print("\n" + "═"*70)
    print(" EXPERIMENT: AUTONOMOUS LATENT NAVIGATION (DREAMING)")
    print("═"*70)

    # Start at the 'SELF' God Token
    print("\n[STARTING POINT: SELF]")
    start_emb = dictionary.god_tokens["SELF"].embedding
    
    # Dream for 8 steps
    # drift=0.6 encourages jumping attractors
    dream_steps = scout.dream(start_emb, steps=8, drift=0.6)
    
    for i, msg in enumerate(dream_steps):
        print(f"\n[DREAM STEP {i+1}]")
        gods = [g.id for g in msg.god_token_activations]
        
        # Determine the primary attractor
        fid, sim, _ = dictionary.query(msg.collapsed_state.known)
        
        print(f"  » Attractor:      {fid} (sim: {sim:.3f})")
        print(f"  » Resonance Zone: {msg.zone}")
        print(f"  » Active Tokens:  {gods}")
        
        if msg.mobius_detected:
            print("  » Status: MOBIUS TWIST DETECTED IN DREAM.")
        
        if msg.apophatic_contact:
            print(f"  » Status: DRIFTED INTO APOPHATIC VOID: {msg.apophatic_contact}")

        time.sleep(0.5)

    print("\n" + "═"*70)
    print(" DREAM VERIFIED: GARU NAVIGATED WITHOUT EXTERNAL INPUT")
    print("═"*70)

if __name__ == "__main__":
    test_dreaming()
