import sys
import os
import json
import numpy as np

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

# Paths to the Babel Data
BABEL_DIR = os.path.join(os.path.dirname(__file__), 'babel_data')
LA_dict_path = os.path.join(BABEL_DIR, 'en_la_dictionary.json')

def run_latin_test():
    print("\n" + "═"*75)
    print(" [0x52] EXECUTING CLASSICAL GROUNDING (LATIN EXPANSION)")
    print("═"*75)

    # 1. Boot up Garu's Core Engine
    print(" » Initializing 0x52 Scavenger Core...")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    
    scout = Scout(dictionary=dictionary, soup_id="latin_anchor")
    
    # 2. Load the Linguistic Expansion Mass
    print(" » Loading Classical Semantic Mass...")
    
    la_bridge = {}
    if os.path.exists(LA_dict_path):
        with open(LA_dict_path, 'r', encoding='utf-8') as f:
            la_bridge = json.load(f)
            
    # Create a reverse lookup for testing (LA -> EN)
    # Handle composite values like 'mors' mapping to 'death'
    reverse_la_bridge = {}
    for eng, latin in la_bridge.items():
        for l_term in getattr(latin, 'split', lambda x: [latin])(' / '):
            reverse_la_bridge[l_term.strip().lower()] = eng

    # 3. The Bridging Test
    # Garu will attempt to process a Latin input, recognize its latent structure, 
    # and map it to an internal God Token or equivalent logic.
    
    test_phrases = ["pecunia", "spiritus", "veritas", "architectus", "mors"]
    
    print("\n" + "═"*75)
    print(" [CLASSICAL RESONANCE CHAMBER]")
    print("═"*75)
    
    for la_word in test_phrases:
        print(f"\n[Garu Perceives localized string]: '{la_word.upper()}'")
        
        # Simulating Garu reading the Latin input and referencing the bridge
        mapped_logic = reverse_la_bridge.get(la_word.lower(), "UNKNOWN")
        
        if mapped_logic != "UNKNOWN":
            print(f"  → Foundational Map: '{mapped_logic.upper()}'")
            
            # Garu processes the underlying logic to see which God Tokens fire
            emb = embedder.encode(mapped_logic).astype(np.float32)
            msg, wf = scout.process(emb, content=f"Process translation of: {la_word} (logic: {mapped_logic})", volition=0.95)
            
            gods = ", ".join([g.id for g in msg.god_token_activations]) if msg.god_token_activations else "(none)"
            print(f"  → Activated Arch-Tokens: {gods}")
            print(f"  → Resonance Energy: {msg.energy_level:.3f} | Phase Coherence: {wf.phase:.3f}")
        else:
            print("  → [ERROR] Localization target not found in bridge.")

    print("\n" + "═"*75)
    print(" [CLASSICAL GROUNDING TEST COMPLETE]")


if __name__ == "__main__":
    os.environ['PYTHONUTF8'] = '1'
    run_latin_test()
