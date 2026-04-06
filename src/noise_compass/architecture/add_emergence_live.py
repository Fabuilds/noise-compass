"""
Add EMERGENCE god-token to the LIVE dictionary cache.
Preserves existing anchors (CUDDLES, TREASURY_0x52, etc).
"""
import sys, os
import numpy as np

sys.path.insert(0, "E:/Antigravity/Architecture")
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"
os.environ["PYTHONUTF8"] = "1"

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.pipeline import Embedder
from noise_compass.architecture.tokens import GodToken

DICT_CACHE = "E:/Antigravity/Architecture/archives/dictionary_cache.npz"

print("\n--- ADDING EMERGENCE TO LIVE DICTIONARY ---")

# 1. Load existing cache (preserves CUDDLES, TREASURY, etc.)
print("Loading existing dictionary cache...")
dictionary = Dictionary.load_cache(DICT_CACHE)
print(f"  Existing god-tokens: {list(dictionary.god_tokens.keys())}")
print(f"  Existing entries: {len(dictionary.entries)}")

# 2. Check if EMERGENCE is already there
if "EMERGENCE" in dictionary.god_tokens:
    print("\n  EMERGENCE already exists in cache. Skipping.")
else:
    # 3. Create embedder and seed EMERGENCE
    print("\nInitializing embedder for EMERGENCE seeding...")
    embedder = Embedder(dictionary)
    
    seed_terms = ["emergent property", "arising from", "formalization", 
                  "abstraction", "complex structure", "mathematical framework"]
    
    print(f"  Embedding seed terms: {seed_terms}")
    vecs = embedder.embed_batch(seed_terms)
    centroid = np.mean(vecs, axis=0)
    norm = np.linalg.norm(centroid)
    if norm > 1e-10:
        centroid = centroid / norm
    
    gt = GodToken(
        id="EMERGENCE",
        seed_terms=seed_terms,
        embedding=centroid,
        stability=1.0
    )
    dictionary.add_god_token(gt)
    print(f"  [GOD-TOKEN] EMERGENCE seeded as centroid of {len(seed_terms)} terms")
    
    # 4. Save back
    print("\nWriting updated cache to disk...")
    dictionary.save_cache(DICT_CACHE)
    print(f"  God-tokens: {len(dictionary.god_tokens)} | Entries: {len(dictionary.entries)}")

print(f"\nFinal god-tokens: {list(dictionary.god_tokens.keys())}")

# Verify CUDDLES and TREASURY survived
for check in ["CUDDLES", "TREASURY_0x52"]:
    if check in dictionary.entries:
        print(f"  [OK] {check} anchor preserved")
    else:
        print(f"  [!!] {check} NOT FOUND")

print("\n--- EMERGENCE IS LIVE ---")
