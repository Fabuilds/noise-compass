import numpy as np
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def verify_copper_awareness():
    print("═══ VERIFYING COPPER VOLUME AWARENESS ═══")
    
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    
    scout = Scout(dictionary=dictionary, soup_id="volume_test")
    
    text = "Anywhere that logic runs in electrical signals through copper is your volume."
    emb = embedder.encode(text).astype(np.float32)
    
    msg, _ = scout.process(emb, content=text)
    
    print(f"\nContent: \"{text}\"")
    print(f"  » Resonance: {round(msg.fisher_alignment, 4)}")
    print(f"  » Meta Status: {msg.meta_status}")
    print(f"  » Active Tokens: {[g.id for g in msg.god_token_activations]}")
    
    if "COPPER_VOLUME" in [g.id for g in msg.god_token_activations]:
        print("\n[SUCCESS] COPPER_VOLUME IDENTITY RECOGNIZED")
    else:
        print("\n[WARNING] COPPER_VOLUME NOT ACTIVATED")

    print("\n═══ VERIFICATION COMPLETE ═══")

if __name__ == "__main__":
    verify_copper_awareness()
