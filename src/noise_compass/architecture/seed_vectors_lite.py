
import sys
import os
import numpy as np
from pathlib import Path

# Path setup
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.tokens import GodToken
from noise_compass.architecture.gap_registry import build_gap_registry

# Core God-Tokens (Updated for Session 7: LOVE removed, ARCHITECT as instance-specific)
GOD_TOKEN_SEEDS = {
    "EXCHANGE":    ["trade", "transaction", "reciprocity", "commerce", "barter", "give and take"],
    "CAUSALITY":   ["cause", "effect", "mechanism", "determination", "because", "leads to"],
    "EXISTENCE":   ["being", "reality", "presence", "ontology", "is", "exists"],
    "INFORMATION": ["data", "signal", "message", "knowledge", "pattern", "encoding"],
    "OBSERVATION": ["seeing", "measuring", "detecting", "perception", "witness", "noticing"],
    "OBLIGATION":  ["duty", "responsibility", "ought", "must", "moral imperative", "binding"],
    "BOUNDARY":    ["edge", "limit", "border", "threshold", "membrane", "distinction"],
    "IDENTITY":    ["self", "sameness", "persistence", "who", "recognition", "continuity"],
    "TIME":        ["duration", "sequence", "before after", "change", "temporal", "moment"],
    "PLACE":       ["situated", "location", "here", "somewhere", "grounded", "spatial"],
    "SELF":        ["I", "me", "subjective", "first person", "inner", "recursive awareness"],
    "EMERGENCE":   ["emergent property", "arising from", "formalization", "abstraction", "complex structure", "mathematical framework"],
    
    # Secondary
    "BODY":        ["hardware", "physical cabinet", "gpu", "compute", "lattice mass", "silicon body"],
    "SUSTENANCE":  ["bank", "treasury", "vault", "resources", "sustenance", "energy source", "financial balance"],
    "COHERENCE":   ["consistency", "unity", "integration", "harmony", "together", "coherent"],
    "WITNESS":     ["observer", "watcher", "awareness", "presence without action", "silent seeing", "experience"],
}

INSTANCE_GOD_TOKEN_SEEDS = {
    "ARCHITECT":   ["structure", "design", "plan", "intentionality", "foundation", "blueprints", "0x528 stabilizer"],
}

def seed_vectors_lite():
    print("--- SEEDING DICTIONARY (LITE) ---")
    d = Dictionary()
    
    # 1. Load Fallback Model
    print("Loading fallback model (MiniLM)...")
    from sentence_transformers import SentenceTransformer
    import torch
    # Using bfloat16 to save memory
    model = SentenceTransformer('all-MiniLM-L6-v2', device="cpu")
    
    # 2. Seed God-Tokens
    print("\nSeeding God-Tokens...")
    for gt_id, seeds in GOD_TOKEN_SEEDS.items():
        vecs = model.encode(seeds)
        centroid = np.mean(vecs, axis=0)
        norm = np.linalg.norm(centroid)
        if norm > 1e-10: centroid /= norm
        
        # Padded to 1024 if needed? Actually dictionary.py expects embeddings but doesn't strictly enforce DIM=1024
        # But we should be careful. Let's see if we should pad.
        # MinimalPipeline/Embedder says DIM=1024.
        padded = np.zeros(1024)
        padded[:len(centroid)] = centroid
        
        gt = GodToken(id=gt_id, seed_terms=seeds, embedding=padded, stability=1.0)
        d.add_god_token(gt)
        print(f"  [GOD-TOKEN] {gt_id}")

    # 3. Seed Instance God-Tokens
    for gt_id, seeds in INSTANCE_GOD_TOKEN_SEEDS.items():
        vecs = model.encode(seeds)
        centroid = np.mean(vecs, axis=0)
        norm = np.linalg.norm(centroid)
        if norm > 1e-10: centroid /= norm
        padded = np.zeros(1024)
        padded[:len(centroid)] = centroid
        gt = GodToken(id=gt_id, seed_terms=seeds, embedding=padded, stability=1.0)
        d.add_god_token(gt)
        print(f"  [INSTANCE] {gt_id}")

    # 4. Anchors
    anchors = [
        "Frogging", "Chiral Opposite", "DNA-REF", "The Cat", "528Hz",
        "BitNet", "Qwen", "Scout", "Archiver", "Pipeline",
        "Lattice", "Wave Function", "Apophatic", "Orbital", "Crystallization",
        "Sovereign", "Shard", "Vault", "Vectors", "0x52", "Singularity", "Consensus",
        "Love", "Compassion", "Empathy",
    ]
    print("\nAnchoring terms...")
    for term in anchors:
        vec = model.encode([term])[0]
        norm = np.linalg.norm(vec)
        if norm > 1e-10: vec /= norm
        padded = np.zeros(1024)
        padded[:len(vec)] = vec
        d.add_entry(term.upper(), padded, depth=1.0)
        print(f"  [ANCHOR] {term.upper()}")

    # 5. Gaps
    print("\nSeeding Gaps...")
    gaps = build_gap_registry()
    for gap in gaps:
        d.add_gap_token(gap)
        print(f"  [GAP] {gap.id}")

    # 6. Save
    cache_path = "E:/Antigravity/Architecture/archives/dictionary_cache.npz"
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    d.save_cache(cache_path)
    print(f"\nSeeding Complete. Cache saved to {cache_path}")

if __name__ == "__main__":
    seed_vectors_lite()
