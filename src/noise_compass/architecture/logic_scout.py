import sys
import os
import numpy as np
import json

# Path alignment
sys.path.insert(0, "E:/Antigravity/Architecture")
os.environ["PYTHONUTF8"] = "1"

from noise_compass.architecture.dictionary import Dictionary

def perform_audit(cache_path):
    print(f"--- [Logic Scout] Auditing: {cache_path} ---")
    d = Dictionary.load_cache(cache_path)
    
    entries = d.entries
    ids = list(entries.keys())
    embeddings = list(entries.values())
    
    # 1. Non-Contradiction Test (Semantic Opposition)
    # Search for pairs with similarity near -1 (Logical Contradiction)
    contradictions = []
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            sim = np.dot(embeddings[i], embeddings[j])
            if sim < -0.85: # Strong opposition
                contradictions.append((ids[i], ids[j], sim))
                
    if contradictions:
        print(f"[!] WARNING: Found {len(contradictions)} potential contradictions:")
        for id1, id2, sim in contradictions:
            print(f"    - {id1} XOR {id2} (Sim: {sim:.4f})")
    else:
        print("[+] PASS: No direct semantic contradictions detected.")
        
    # 2. Excluded Middle Test (Semantic Density)
    # Check for "Void Gaps" that are too far from any attractor
    # We'll use a random sampling of the space (limited to 4D projection or similar)
    # For now, we measure the "Clarity" of the existing field
    avg_sim = 0
    if len(embeddings) > 1:
        sum_sim = 0
        count = 0
        for i in range(min(50, len(embeddings))):
            for j in range(i + 1, min(50, len(embeddings))):
                sum_sim += abs(np.dot(embeddings[i], embeddings[j]))
                count += 1
        avg_sim = sum_sim / count if count > 0 else 0
        
    print(f"[*] Field Density (Avg Abs Similarity): {avg_sim:.4f}")
    if avg_sim > 0.6:
        print("[!] WARNING: High field density (Potential Circular Overlap).")
    elif avg_sim < 0.1:
        print("[!] WARNING: Low field density (Potential Fragmentation/Excluded Middle).")
    else:
        print("[+] PASS: Field density is optimal for 0x528 resonance.")

    # 3. Axiomatic Self-Consistency
    # Check if 'SINGULARITY' and 'EMERGENCE' (if present) are stable
    print("\n--- [Axiomatic Self-Consistency] ---")
    axioms = ["SINGULARITY", "EMERGENCE", "COHERENCE", "EXCHANGE"]
    for a in axioms:
        if a in entries:
            # Check depth
            depth = d._entry_depth.get(a, 0)
            status = "STABLE" if depth > 1.5 else "SHALLOW"
            print(f"  - {a}: {status} (Depth: {depth:.2f})")
        else:
            print(f"  - {a}: NOT CRYSTALLIZED")

if __name__ == "__main__":
    cache = "E:/Antigravity/Architecture/archives/dictionary_cache.npz"
    perform_audit(cache)
