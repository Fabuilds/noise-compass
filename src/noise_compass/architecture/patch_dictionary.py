
import sys
import os
import numpy as np

# Path setup
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.gap_registry import build_gap_registry

def patch_dictionary():
    cache_path = "E:/Antigravity/Architecture/archives/dictionary_cache.npz"
    print(f"Loading dictionary from {cache_path}...")
    
    d = Dictionary()
    if os.path.exists(cache_path):
        d.load_cache(cache_path)
    else:
        print("Error: No dictionary cache found to patch.")
        return

    # 1. Reclassify LOVE
    if "LOVE" in d.god_tokens:
        print("Reclassifying LOVE as a semantic anchor...")
        # Keep the embedding but remove from god_tokens
        gt = d.god_tokens.pop("LOVE")
        d.add_entry("LOVE", gt.embedding, depth=1.0)
        d.add_entry("COMPASSION", gt.embedding, depth=1.0) # Derivative
        d.add_entry("EMPATHY", gt.embedding, depth=1.0)    # Derivative

    # 2. Reclassify ARCHITECT
    # ARCHITECT is instance-specific. In this system it stays, 
    # but we mark it in the registry (handled by gap_registry changes).
    # No action needed in dictionary mapping besides ensuring it exists.
    if "ARCHITECT" not in d.god_tokens:
        print("Warning: ARCHITECT not in god_tokens. Ensure it's seeded as Instance-Specific.")

    # 3. Re-sync Gaps
    print("Re-syncing Gaps from registry...")
    d.gap_tokens = {} # Clear old gaps
    gaps = build_gap_registry()
    for gap in gaps:
        d.add_gap_token(gap)
        print(f"  [GAP] {gap.id} (depth={gap.void_depth})")

    # 4. Save
    d.save_cache(cache_path)
    print("\nPatch applied. Dictionary saved.")

if __name__ == "__main__":
    patch_dictionary()
