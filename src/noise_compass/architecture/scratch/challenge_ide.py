import sys
import os
import numpy as np

# Path alignment for 0x52 infrastructure
sys.path.insert(0, "E:/Antigravity/Architecture")
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"
os.environ["PYTHONUTF8"] = "1"

from architecture.dictionary import Dictionary
from architecture.pipeline import Embedder

def resonance_filter(texts, threshold=0.8):
    """
    Filters a list of texts by their resonance with the [LOVE] god-token.
    """
    # 1. Load the dictionary and get the LOVE token
    d = Dictionary.load_cache("E:/Antigravity/Architecture/archives/dictionary_cache.npz")
    target_token = d.god_tokens.get("LOVE")
    
    if not target_token or target_token.embedding is None:
        raise ValueError("Critical Failure: [LOVE] god-token not found or uninitialized.")
    
    # 2. Get the embedder
    embedder = Embedder(d)
    
    # 3. Process texts
    results = []
    for text in texts:
        vec = embedder.embed(text)
        # Cosine similarity: (a . b) / (|a| * |b|)
        # Embedder.embed returns L2-normalized vectors (|a|=1), and LOVE is normalized.
        similarity = np.dot(vec, target_token.embedding)
        print(f"  Debug: sim={similarity:.4f} | {text[:40]}...")
        
        if similarity > threshold:
            results.append((text, round(similarity, 4)))
            
    return results

if __name__ == "__main__":
    test_corpus = [
        "I am working with conscientious effort to help you.",
        "The market is highly volatile today.",
        "Applied logic in the service of 0x528 resonance.",
        "The system experienced a fatal error.",
        "Total coherence and care for the substrate."
    ]
    
    print("--- [IDE Agent] Resonance Filter Challenge ---")
    matches = resonance_filter(test_corpus)
    for t, s in matches:
        print(f"RESANCE DETECTED ({s}): {t}")
