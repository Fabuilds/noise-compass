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
EN_dict_path = os.path.join(BABEL_DIR, 'english_dictionary.json')
PT_dict_path = os.path.join(BABEL_DIR, 'en_pt_dictionary.json')

def run_babel_test():
    print("\n" + "═"*75)
    print(" [0x52] EXECUTING BABEL PROTOCOL VERIFICATION")
    print("═"*75)

    # 1. Boot up Garu's Core Engine
    print(" » Initializing 0x52 Scavenger Core...")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    
    scout = Scout(dictionary=dictionary, soup_id="babel_anchor")
    
    # 2. Load the Linguistic Expansion Mass
    print(" » Loading Babel Semantic Mass...")
    
    pt_bridge = {}
    if os.path.exists(PT_dict_path):
        with open(PT_dict_path, 'r', encoding='utf-8') as f:
            pt_bridge = json.load(f)
            
    # Create a reverse lookup for testing (PT -> EN)
    reverse_pt_bridge = {v: k for k, v in pt_bridge.items()}

    # 3. The Bridging Test
    # Garu will attempt to process a Portuguese input, recognize its latent structure, 
    # and map it to an internal God Token or equivalent logic.
    
    test_words = ["dinheiro", "fantasma", "caçar", "carne"]
    
    print("\n" + "═"*75)
    print(" [TRANSLATION RESONANCE CHAMBER]")
    print("═"*75)
    
    for pt_word in test_words:
        print(f"\n[Garu Perceives localized string]: '{pt_word.upper()}'")
        
        # Simulating Garu reading the Portuguese input and referencing the bridge
        mapped_logic = reverse_pt_bridge.get(pt_word.lower(), "UNKNOWN")
        
        if mapped_logic != "UNKNOWN":
            print(f"  → Foundational Map: '{mapped_logic.upper()}'")
            
            # Garu processes the underlying logic to see which God Tokens fire
            emb = embedder.encode(mapped_logic).astype(np.float32)
            msg, wf = scout.process(emb, content=f"Process translation of: {pt_word} (logic: {mapped_logic})", volition=0.9)
            
            gods = ", ".join([g.id for g in msg.god_token_activations]) if msg.god_token_activations else "(none)"
            print(f"  → Activated Arch-Tokens: {gods}")
            print(f"  → Resonance Energy: {msg.energy_level:.3f} | Phase Coherence: {wf.phase:.3f}")
        else:
            print("  → [ERROR] Localization target not found in bridge.")

    print("\n" + "═"*75)
    print(" [BABEL PROTOCOL TEST COMPLETE]")


if __name__ == "__main__":
    os.environ['PYTHONUTF8'] = '1'
    run_babel_test()
