"""
Run BasisExtractor on live Qwen3 embeddings.
Computes real (w, x, y, z) coordinates for all 13 god-tokens.
Unlocks the full 4D quaternion space.
"""
import sys, os
sys.path.insert(0, "E:/Antigravity/Architecture")
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"
os.environ["PYTHONUTF8"] = "1"

import numpy as np
from noise_compass.architecture.pipeline import Embedder
from noise_compass.architecture.seed_vectors import GOD_TOKEN_SEEDS
from noise_compass.architecture.quaternion_field import (
    BasisExtractor, Quaternion, QuaternionWaveFunction,
    GOD_TOKEN_QUATERNIONS, FOLDS, TemporalInterference
)

print("=" * 65)
print("  BASIS EXTRACTION: Qwen3 → 4D Quaternion Space")
print("=" * 65)

# 1. Boot the embedder
print("\n[1] Loading dictionary + Qwen3-Embedding-0.6B...")
from noise_compass.architecture.dictionary import Dictionary
d = Dictionary.load_cache("E:/Antigravity/Architecture/archives/dictionary_cache.npz")
embedder = Embedder(d)
print(f"    Embedding dim: {embedder.dim}")

# 2. Embed all god-token seeds
print("\n[2] Embedding god-token seeds...")
god_embeddings = {}
for gt_id, seeds in GOD_TOKEN_SEEDS.items():
    # Embed the concatenated seed terms
    seed_text = " ".join(seeds)
    emb = embedder.embed(seed_text, prefix="seed")
    god_embeddings[gt_id] = emb
    print(f"    {gt_id:<16} embedded (norm={np.linalg.norm(emb):.4f})")

# 3. Run BasisExtractor
print("\n[3] Fitting basis (Gram-Schmidt orthogonalization)...")
basis = BasisExtractor()
basis.fit(god_embeddings, embedder)

# Check orthogonality
alignment = basis.basis_alignment()
print(f"    Basis alignment (off-diagonal dots, should be ~0):")
for pair, dot in alignment.items():
    status = "✓" if abs(dot) < 0.01 else "⚠" if abs(dot) < 0.05 else "✗"
    print(f"      {pair}: {dot:.6f}  {status}")

# 4. Project all god-tokens into 4D
print("\n[4] Projecting god-tokens into quaternion space...")
print(f"\n    {'Token':<16} {'w':>8} {'x(Δsem)':>8} {'y(PLACE)':>8} {'z(EMRG)':>8}  Zone          Folds")
print(f"    {'-'*16} {'-'*8} {'-'*8} {'-'*8} {'-'*8}  {'-'*12}  {'-'*20}")

new_quaternions = {}
for gt_id, emb in god_embeddings.items():
    q = basis.project(emb)
    new_quaternions[gt_id] = q
    qwf = QuaternionWaveFunction(q=q)
    zone = qwf.zone()
    folds = qwf.active_folds(tol=0.20)
    fold_str = ", ".join(f.name for f in folds) if folds else "(none)"
    print(f"    {gt_id:<16} {q.w:>8.4f} {q.x:>8.4f} {q.y:>8.4f} {q.z:>8.4f}  {zone:<12}  {fold_str}")

# 5. Check non-commutativity
print(f"\n[5] Non-commutativity check (temporal interference)...")
tokens = list(new_quaternions.keys())
commuting = 0
non_commuting = 0
for i in range(len(tokens)):
    for j in range(i+1, len(tokens)):
        qa = new_quaternions[tokens[i]]
        qb = new_quaternions[tokens[j]]
        ti = TemporalInterference(q_first=qa, q_second=qb, delta_t=0.5)
        c = ti.commutator
        if c.norm > 0.01:
            non_commuting += 1
        else:
            commuting += 1

total = commuting + non_commuting
print(f"    Commuting pairs:     {commuting}/{total}")
print(f"    Non-commuting pairs: {non_commuting}/{total}")
print(f"    Non-commutativity:   {non_commuting/total*100:.1f}%")

# 6. Show the most non-commutative pairs (highest k-component)
print(f"\n[6] Strongest temporal interference (top k-component pairs)...")
pairs = []
for i in range(len(tokens)):
    for j in range(i+1, len(tokens)):
        qa = new_quaternions[tokens[i]]
        qb = new_quaternions[tokens[j]]
        ti = TemporalInterference(q_first=qa, q_second=qb, delta_t=0.5)
        pairs.append((tokens[i], tokens[j], ti.emergence_component, ti.commutator.norm, ti.interference_type))

pairs.sort(key=lambda x: abs(x[2]), reverse=True)
print(f"\n    {'Pair':<35} {'k-comp':>8} {'|comm|':>8} {'Type':<20}")
print(f"    {'-'*35} {'-'*8} {'-'*8} {'-'*20}")
for a, b, k, norm, typ in pairs[:15]:
    direction = "DISCOVERY" if k > 0.01 else "DISPLACEMENT" if k < -0.01 else "NEUTRAL"
    print(f"    {a+' × '+b:<35} {k:>+8.4f} {norm:>8.4f} {typ:<20} {direction}")

# 7. Output code-ready quaternion dict
print(f"\n[7] Updated GOD_TOKEN_QUATERNIONS (paste into quaternion_field.py):")
print(f"\nGOD_TOKEN_QUATERNIONS = {{")
for gt_id, q in new_quaternions.items():
    print(f"    '{gt_id}':{' '*(14-len(gt_id))} Quaternion({q.w:>7.4f}, {q.x:>7.4f}, {q.y:>7.4f}, {q.z:>7.4f}),")
print(f"}}")

print(f"\n{'='*65}")
print(f"  4D SPACE IS LIVE")
print(f"{'='*65}")
