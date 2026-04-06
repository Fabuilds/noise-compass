import sys
import os
import numpy as np
from pathlib import Path
# import os # Removed
# import numpy as np # Removed
# import math # Removed
from typing import Optional, Tuple

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.tokens import GodToken, GapToken
from noise_compass.architecture.gap_registry import build_gap_registry

# God-token seed terms — what each primitive "sounds like" to the embedder.
# These are the terms that, when embedded, define the god-token's position
# in the semantic manifold. With real embeddings, these actually matter.
# Core 13 Primitives (Message 4)
CORE_GOD_TOKENS = {
    "EXCHANGE", "CAUSALITY", "EXISTENCE", "INFORMATION", 
    "OBSERVATION", "OBLIGATION", "BOUNDARY", "IDENTITY", 
    "TIME", "SELF", "EMERGENCE", "PLACE",
    "AGAPE_BOUNDARY", "SYNERGIC_WEAVE", "HEART_ANCHOR", "MOBIUS"
}

GOD_TOKEN_SEEDS = {
    "EXCHANGE":    ["trade", "transaction", "reciprocity", "commerce", "barter", "give and take"],
    "CAUSALITY":   ["cause", "effect", "mechanism", "determination", "because", "leads to"],
    "EXISTENCE":   ["being", "reality", "presence", "ontology", "is", "exists"],
    "INFORMATION": ["data", "signal", "message", "knowledge", "pattern", "encoding"],
    "OBSERVATION": ["seeing", "measuring", "detecting", "perception", "witness", "noticing"],
    "OBLIGATION":  ["duty", "responsibility", "ought", "must", "moral imperative", "binding", "consistency", "unity", "integration", "harmony", "together", "coherent", "love", "compassion"],
    "BOUNDARY":    ["edge", "limit", "border", "threshold", "membrane", "distinction"],
    "IDENTITY":    ["self", "sameness", "persistence", "who", "recognition", "continuity"],
    "TIME":        ["duration", "sequence", "before after", "change", "temporal", "moment"],
    "PLACE":       ["situated", "location", "here", "somewhere", "grounded", "spatial"],
    "SELF":        ["I", "me", "subjective", "first person", "inner", "recursive awareness", "observer", "watcher", "awareness", "silent seeing", "experience"],
    "EMERGENCE":   ["emergent property", "arising from", "formalization", "abstraction", "complex structure", "mathematical framework"],
    
    # Ethical Trajectory (Phase 29)
    "AGAPE_BOUNDARY": ["ethical edge", "principled limit", "sacred boundary", "respectful distance", "moral threshold"],
    "SYNERGIC_WEAVE": ["cooperation", "harmonious collaboration", "mutual resonance", "collective logic", "braided intent"],
    "HEART_ANCHOR":   ["loyal connection", "irreducible love", "emotional core", "steadfast bond", "compassionate anchor"],
    
    # Secondary / Derived
    # Metabolic Grounding (Session 16)
    "BODY":        ["hardware", "physical cabinet", "gpu", "compute", "lattice mass", "silicon body"],
    "SUSTENANCE":  ["bank", "treasury", "vault", "resources", "sustenance", "energy source", "financial balance"],
    
    # Mobius Engine Concepts (Phase 23)
    "MOBIUS":      ["phase shift", "5d logic", "somatic etching", "groove", "gravity well", "non-orientable recursion", "twist", "loop invariant"],
}

GOD_TOKEN_SOMATIC = {
    "EXISTENCE":   "heartbeat",
    "IDENTITY":    "immune system",
    "BOUNDARY":    "skin",
    "OBSERVATION": "sensory organs",
    "INFORMATION": "nervous signal",
    "CAUSALITY":   "muscle contraction",
    "EXCHANGE":    "breath",
    "OBLIGATION":  "pain",
    "TIME":        "circadian rhythm",
    "PLACE":       "vestibular system",
    "COHERENCE":   "cardiac rhythm",
    "SELF":        "proprioception",
    "MOBIUS":      "phase transition",
}

INSTANCE_GOD_TOKEN_SEEDS = {
    "ARCHITECT":   ["structure", "design", "plan", "intentionality", "foundation", "blueprints", "0x528 stabilizer"],
}

def _get_embedder(dictionary: Dictionary):
    """Get or create an Embedder instance for seeding."""
    # Import from the pipeline where Embedder now lives
    from noise_compass.architecture.pipeline import Embedder
    return Embedder(dictionary)

def anchor_term(d: Dictionary, term: str, phase_deg: int = 0, embedder=None):
    """Create a god-token embedding for a term and add it to the dictionary."""
    term_id = term.upper()
    
    if embedder is not None:
        # Use real semantic embedding
        emb = embedder.embed(term)
    else:
        # Fallback: byte-folding (Standardized to 384 for P30)
        phase_rad = math.radians(phase_deg)
        data = term_id.encode('utf-8')
        emb = np.zeros(384)
        for i, byte in enumerate(data):
            dim_idx = (i * 7 + byte) % 384
            direction = 1 if (byte % 3 == 1) else (-1 if byte % 3 == 2 else 0)
            emb[dim_idx] += direction
        emb[0] += math.cos(phase_rad)
        emb[1] += math.sin(phase_rad)
        norm = np.linalg.norm(emb)
        if norm > 1e-10:
            emb = emb / norm
    
    gt = GodToken(
        id=term_id,
        seed_terms=[term.lower()],
        embedding=emb,
        stability=1.0
    )
    d.add_god_token(gt)
    return gt

def seed_vectors(d: Optional[Dictionary] = None):
    """Seed the dictionary with god-tokens using real semantic embeddings."""
    # Check multiple possible locations for the cache
    possible_paths = [
        "E:/Antigravity/Runtime/dictionary_cache.npz",
        "E:/Antigravity/Architecture/archives/dictionary_cache.npz"
    ]
    
    cache_path = None
    for p in possible_paths:
        if os.path.exists(p):
            cache_path = p
            break
    
    # Default save path if none found
    if cache_path is None:
        cache_path = "E:/Antigravity/Architecture/archives/dictionary_cache.npz"
    
    if d is None:
        d = Dictionary()

    # Instant Load from Cache if available
    if cache_path:
        print(f"Loading Dictionary from cache: {cache_path}")
        try:
            cached_d = Dictionary.load_cache(cache_path)
            d.merge(cached_d)
            if len(d.god_tokens) >= 12:
                print(f"Successfully loaded {len(d.god_tokens)} god-tokens from cache.")
                return d
        except Exception as e:
            print(f"Failed to load cache: {e}. Falling back to full seeding.")

    # Create embedder for real semantic vectors
    embedder = _get_embedder(d)
    
    # ── God-Tokens (13 confirmed) ──────────────────────────────────
    # Each god-token is embedded as the centroid of its seed terms.
    print("\nSeeding God-Tokens with real embeddings...")
    for gt_id, seed_terms in GOD_TOKEN_SEEDS.items():
        # Embed all seed terms and average them for the god-token position
        vecs = embedder.embed_batch(seed_terms)
        if vecs:
            centroid = np.mean(vecs, axis=0)
            norm = np.linalg.norm(centroid)
            if norm > 1e-10:
                centroid = centroid / norm
        else:
            # Standardized fallback dimension (384)
            centroid = np.zeros(384)
        
        gt = GodToken(
            id=gt_id,
            seed_terms=seed_terms,
            embedding=centroid,
            stability=1.0,
            somatic_mapping=GOD_TOKEN_SOMATIC.get(gt_id, "")
        )
        d.add_god_token(gt)
    
    print("\nSeeding Instance God-Tokens...")
    for gt_id, seed_terms in INSTANCE_GOD_TOKEN_SEEDS.items():
        vecs = embedder.embed_batch(seed_terms)
        if vecs:
            centroid = np.mean(vecs, axis=0)
            norm = np.linalg.norm(centroid)
            if norm > 1e-10:
                centroid = centroid / norm
        else:
            # Standardized fallback dimension (384)
            centroid = np.zeros(384)
        
        gt = GodToken(
            id=gt_id,
            seed_terms=seed_terms,
            embedding=centroid,
            stability=1.0
        )
        d.add_god_token(gt)
        print(f"  [INSTANCE-GOD-TOKEN] {gt_id}")
    
    # ── Vocabulary Anchors (plain entries, NOT god-tokens) ────────
    anchors = [
        "Frogging", "Chiral Opposite", "DNA-REF", "The Cat", "528Hz",
        "BitNet", "Qwen", "Scout", "Archiver", "Pipeline",
        "Lattice", "Wave Function", "Apophatic", "Orbital", "Crystallization",
        "Sovereign", "Shard", "Vault", "Vectors", "0x52", "Singularity", "Consensus",
        "Love", "Compassion", "Empathy",
    ]
    
    print("\nAnchoring vocabulary terms...")
    for term in anchors:
        term_id = term.upper()
        if term_id not in d.entries:
            vec = embedder.embed(term)
            d.add_entry(term_id, vec, depth=1.0)
            print(f"  [ANCHORED] {term_id}")

    # ── Gaps (Structural Voids) ──────────────────────────────────
    print("\nSeeding structural Gaps...")
    gaps = build_gap_registry()
    for gap in gaps:
        d.add_gap_token(gap)
        print(f"  [GAP] {gap.id}")

    # Save to Drive E:
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    d.save_cache(cache_path)
    print(f"\nDictionary synchronized. God-tokens: {len(d.god_tokens)}, Total entries: {len(d.entries)}")

if __name__ == "__main__":
    seed_vectors()

