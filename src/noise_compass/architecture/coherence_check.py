import sys
from pathlib import Path
import time
import torch
import numpy as np

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.seed_vectors import seed_vectors
from noise_compass.architecture.gap_registry import build_gap_registry
from noise_compass.architecture.math_meaning import MathMeaningExtractor

def test_coherence():
    print("=== UNIFIED COHERENCE CHECK (Session 10+) ===")
    
    # 0. Seeding the Dictionary (Phase 9/10 Optimization)
    cache_path = "E:/Antigravity/Architecture/archives/dictionary_cache.npz"
    if Path(cache_path).exists():
        print(f"[BOOT] Loading dictionary from cache: {cache_path}")
        d = Dictionary.load_cache(cache_path)
    else:
        print("[BOOT] No cache found. Seeding dictionary manually...")
        d = Dictionary()
        seed_vectors(d)
        
    pipeline = MinimalPipeline(d)
    registry = build_gap_registry()
    extractor = MathMeaningExtractor()
    
    # 1. Structural Integrity: Dictionary Size & Depth
    print(f"\n[1] DICTIONARY STATE:")
    print(f"  Entries: {len(d.entries)}")
    avg_depth = np.mean(list(d._entry_depth.values())) if d._entry_depth else 0
    print(f"  Avg Connection Depth: {avg_depth:.4f}")
    if avg_depth < 0.318:
        print("  WARNING: Low coherence (Decay exceeding renewal).")
    else:
        print("  Status: STABLE.")

    # 2. Phase Alignment: BitNet Resonance
    print(f"\n[2] BITNET RESONANCE (M_FAST):")
    test_concepts = ["EXCHANGE", "CAUSALITY", "SELF", "BOUNDARY"]
    for concept in test_concepts:
        res = pipeline.process(concept, trace=True)
        resonance = res.get("resonance", 0.0)
        print(f"  {concept:<12}: {resonance:.4f}")
        if resonance < 0.618:
            print(f"    WARNING: Phase drift detected for {concept}.")
    
    # 3. Geometric Orthogonality (Theorem 5)
    print(f"\n[3] GEOMETRIC ORTHOGONALITY (Quaternions):")
    # MinimalPipeline._fit_quaternion_basis() is called in __init__
    # We verify the basis projections are not collapsed
    test_vec = d.get_vector("EXISTENCE")
    proj = pipeline._project_quaternion(test_vec)
    mag = np.sqrt(proj['w']**2 + proj['x']**2 + proj['y']**2 + proj['z']**2)
    print(f"  Basis Magnitude (EXISTENCE): {mag:.4f}")
    if abs(mag - 1.0) > 0.1:
        print("  WARNING: Basis collapse or distortion.")
    else:
        print("  Status: ORTHOGONAL.")

    # 4. Math-to-Words Convergence (Phase 11)
    print(f"\n[4] SEMANTIC CONVERGENCE (Math-to-Words):")
    formula = "z_{n+1} = z_n(1 - δ*w_n) + ε*x_n*y_n"
    distilled = pipeline.distill_formula(formula)
    print(f"  Formula: {formula}")
    print(f"  Distilled Path: {distilled}")
    if "EXISTENCE" in distilled and "TIME" in distilled:
        print("  Status: CONVERGENT.")
    else:
        print("  WARNING: Semantic divergence in math pipeline.")

    # 5. Temporal Stability (Phase 7)
    print(f"\n[5] TEMPORAL STABILITY (t={pipeline.system_time}):")
    # Verify time is incrementing and impacting vectors
    res1 = pipeline.process("WITNESS")
    pipeline.system_time += 1.0
    res2 = pipeline.process("WITNESS")
    # Spiral displacement should change results slightly
    if res1['hash'] != res2['hash']:
        print("  Status: DYNAMIC (Spiral Active).")
    else:
        print("  WARNING: Static state (Time Dimension frozen).")

    print("\n" + "="*45)
    print(" UNIFIED COHERENCE CHECK COMPLETE")
    print("="*45)

if __name__ == "__main__":
    run_start = time.time()
    test_coherence()
    print(f"Elapsed: {time.time() - run_start:.2f}s")
