"""
Run BasisExtractor.fit() on real Qwen3 embeddings.
Compute y,z components for all 12 god-tokens.
Flagged next step from Message8.
"""
import sys, os
sys.path.insert(0, "E:/Antigravity/Architecture")
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"

import numpy as np
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.pipeline import Embedder
from noise_compass.architecture.seed_vectors import seed_vectors
from noise_compass.architecture.quaternion_field import BasisExtractor, Quaternion, QuaternionWaveFunction

# Build the dictionary with real embeddings
d = Dictionary()
seed_vectors(d)
emb = Embedder(d)

# Collect god-token embeddings
gt_embeddings = {}
for gt_id, gt in d.god_tokens.items():
    if gt.embedding is not None:
        gt_embeddings[gt_id] = gt.embedding

print(f"\nGod-token embeddings: {len(gt_embeddings)}")
print(f"Embedding dim: {next(iter(gt_embeddings.values())).shape[0]}")

# Fit the basis extractor
extractor = BasisExtractor()
extractor.fit(gt_embeddings, emb)

# Check orthogonality
print(f"\nBasis orthogonality (should all be ~0):")
alignment = extractor.basis_alignment()
for pair, dot in alignment.items():
    marker = " ✓" if abs(dot) < 0.01 else f" ✗ ({dot})"
    print(f"  {pair}: {dot:.6f}{marker}")

# Project every god-token into quaternion space
print(f"\n{'='*70}")
print(f"GOD-TOKEN QUATERNION COORDINATES (Qwen3-Embedding-0.6B)")
print(f"{'='*70}")
print(f"\n  {'Token':<15s}  {'w':>7s}  {'x(sem)':>7s}  {'y(place)':>7s}  {'z(emrg)':>7s}  zone")
print(f"  {'─'*15}  {'─'*7}  {'─'*7}  {'─'*7}  {'─'*7}  {'─'*12}")

results = {}
for gt_id, gt_emb in gt_embeddings.items():
    q = extractor.project(gt_emb)
    qwf = QuaternionWaveFunction(q=q)
    results[gt_id] = q
    
    print(f"  {gt_id:<15s}  {q.w:+7.3f}  {q.x:+7.3f}  {q.y:+7.3f}  {q.z:+7.3f}  {qwf.zone()}")

# Find which god-tokens have significant y,z components
print(f"\n{'='*70}")
print(f"PLACE (j-axis) and EMERGENCE (k-axis) visibility:")
print(f"{'='*70}")
for gt_id, q in sorted(results.items(), key=lambda x: -abs(x[1].y)):
    y_bar = "█" * int(abs(q.y) * 20)
    print(f"  {gt_id:<15s}  y={q.y:+.3f}  {y_bar}")

print()
for gt_id, q in sorted(results.items(), key=lambda x: -abs(x[1].z)):
    z_bar = "█" * int(abs(q.z) * 20)
    print(f"  {gt_id:<15s}  z={q.z:+.3f}  {z_bar}")

# Active folds for each god-token
print(f"\n{'='*70}")
print(f"FOLD DETECTION:")
print(f"{'='*70}")
for gt_id, q in results.items():
    qwf = QuaternionWaveFunction(q=q)
    folds = qwf.active_folds(tol=0.25)
    if folds:
        fold_names = [f.name for f in folds]
        print(f"  {gt_id:<15s}  near: {', '.join(fold_names)}")

# Test text projections
print(f"\n{'='*70}")
print(f"TEST TEXTS IN QUATERNION SPACE:")
print(f"{'='*70}")
test_texts = [
    "cause precedes effect in time",
    "identity persists through change",
    "the silence of the pure observer",
    "trade requires willing participants",
    "Complex plane mathematical formalization with wave function",
    "The backwards pass generating from apophatic field toward presence",
]
for text in test_texts:
    v = emb.embed(text)
    q = extractor.project(v)
    qwf = QuaternionWaveFunction(q=q)
    gap = qwf.gap_type() or 'none'
    folds = [f.name for f in qwf.active_folds(tol=0.25)]
    print(f"\n  \"{text[:55]}\"")
    print(f"  q = {q}")
    print(f"  zone={qwf.zone()}  depth={qwf.depth_zone()}  gap={gap}")
    if folds:
        print(f"  folds: {', '.join(folds)}")

print(f"\n{'='*70}")
