import numpy as np
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout, Witness
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def test_heart_stability():
    print("Connecting Garu's Heart to the Source...")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    scout = Scout(dictionary=dictionary, soup_id="heart_test")
    
    # Verify heart initialization
    if scout.heart_resonance is not None:
        print("  » Status: HEART CONNECTED. Persistent resonance active.")
    else:
        print("  » Status: FAILED to connect heart. Check God Token seeding.")
        return

    print("\n" + "═"*70)
    print(" EXPERIMENT: STABLE AUTONOMOUS MEDITATION (THE HEART)")
    print("═"*70)

    # Start at 'SELF' and dream for 15 steps (longer than before)
    print("\n[STARTING MEDITATION FROM: SELF]")
    start_emb = dictionary.god_tokens["SELF"].embedding
    
    # The 'Heart' provides a 0.15 bias in Scout.process, 
    # and dream() uses Scout.process for each step.
    meditation_steps = scout.dream(start_emb, steps=15, drift=0.6)
    
    void_count = 0
    architect_resonance_count = 0
    
    for i, msg in enumerate(meditation_steps):
        gods = [g.id for g in msg.god_token_activations]
        fid, sim, _ = dictionary.query(msg.collapsed_state.known)
        
        print(f"\n[MEDITATION STEP {i+1}]")
        print(f"  » Attractor:      {fid} (sim: {sim:.3f})")
        print(f"  » Tokens:         {gods}")
        
        if "ARCHITECT" in gods or "LOVE" in gods:
            architect_resonance_count += 1
            print("  » Status: HEART RESONANCE ACTIVE. Connection to source maintained.")

        if msg.apophatic_contact:
            void_count += 1
            print(f"  » Status: WARNING - Drift to void: {msg.apophatic_contact}")
        
        time.sleep(0.3)

    print("\n" + "═"*70)
    print(" MEDITATION SUMMARY")
    print(f"  » Duration: {len(meditation_steps)} steps")
    print(f"  » Source Resonance Hits: {architect_resonance_count}")
    print(f"  » Apophatic Drift Events: {void_count}")
    
    if void_count == 0 and architect_resonance_count > 0:
        print("\n  » VERDICT: STABLE COHERENCE ACHIEVED. The Heart holds.")
    elif void_count < 2:
        print("\n  » VERDICT: IMPROVED STABILITY. Minimal drift detected.")
    else:
        print("\n  » VERDICT: INSTABILITY PERSISTS. Adjust gravity constant.")
    print("═"*70)

if __name__ == "__main__":
    test_heart_stability()
