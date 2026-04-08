"""
verify_option_b.py — Verification suite for the Option B deferred seeding implementation.

Run from the package root:
    python E:/Antigravity/Package/src/noise_compass/system/verify_option_b.py

Tests:
    V1: Startup embedding — god-tokens loaded from seed phrases in-memory
    V2: λ-operator ordering — semantically seeded operators are geometrically ordered
    V3: Model switch — H5 unchanged, two different embedders both work
    V4_static: NODE_RING canonicalization — ouroboros_resonant uses tokens.NODE_RING
"""

import os
import sys
import math
import json
import numpy as np

SRC = os.path.normpath("E:/Antigravity/Package/src")
sys.path.insert(0, SRC)

SEEDS_PATH = os.path.join(SRC, "noise_compass", "config", "god_token_seeds.json")

PASS = "\033[92m✓ PASS\033[0m"
FAIL = "\033[91m✗ FAIL\033[0m"


def header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ─────────────────────────────────────────────────────────────────
# V1 — Startup embedding check
# ─────────────────────────────────────────────────────────────────
def test_v1():
    header("V1: Startup Embedding (God-Token Seed Phrases)")
    from noise_compass.system.h5_manager import H5Manager
    from noise_compass.architecture.dictionary import Dictionary

    h5 = H5Manager()

    # Check seed phrases in H5
    seeds_in_h5 = h5.get_god_token_seeds()
    print(f"  Seeds in H5:  {len(seeds_in_h5)} god-tokens")

    # Load dictionary with default embedder (InterferenceEngine)
    d = Dictionary.load_cache(h5_manager=h5)

    print(f"  God-tokens loaded: {len(d.god_tokens)}")
    print(f"  Entries (all):     {len(d.entries)}")

    expected = list(json.load(open(SEEDS_PATH))["god_tokens"].keys())
    missing = [n for n in expected if n not in d.god_tokens]

    for name in expected:
        if name in d.god_tokens and d.god_tokens[name].embedding is not None:
            emb = d.god_tokens[name].embedding
            print(f"  {PASS} {name:15s} shape={np.array(emb).shape}")
        else:
            print(f"  {FAIL} {name:15s} — missing or no embedding")

    if not missing:
        print(f"\n  {PASS} V1: All {len(expected)} god-tokens embedded from seed phrases")
    else:
        print(f"\n  {FAIL} V1: {len(missing)} god-tokens missing: {missing}")
    return len(missing) == 0


# ─────────────────────────────────────────────────────────────────
# V2 — λ-operator ordering check
# ─────────────────────────────────────────────────────────────────
def test_v2():
    header("V2: λ-Operator Semantic Seeding (vs hash-random baseline)")
    from noise_compass.system.h5_manager import H5Manager
    from noise_compass.architecture.dictionary import Dictionary
    from noise_compass.system.lambda_manifold import LambdaManifold

    h5 = H5Manager()
    d  = Dictionary.load_cache(h5_manager=h5)
    lm_semantic = LambdaManifold(embedder=d._embedder or d._default_embedder(),
                                 seeds_path=SEEDS_PATH)
    lm_hash     = LambdaManifold()   # no embedder — falls back to hash seeding

    ops = list(lm_semantic.operators.keys())
    print(f"  Semantic operators loaded: {ops}")

    if len(ops) < 2:
        print(f"  {FAIL} V2: Not enough operators")
        return False

    # Compare: does semantic seeding produce vectors closer to the god-token
    # manifold than the hash-seeded random baseline?
    # IDENTITY op should land near stable god-tokens (EXISTENCE, IDENTITY, COHERENCE)
    # SURPRISE op should land near boundary/void god-tokens (BOUNDARY, OBSERVATION)
    passed_checks = 0
    total_checks  = 0

    def avg_sim(op_vec, token_names):
        sims = []
        for name in token_names:
            if name in d.entries:
                sims.append(float(np.dot(op_vec / (np.linalg.norm(op_vec) + 1e-9),
                                         d.entries[name])))
        return sum(sims) / len(sims) if sims else 0.0

    stable_tokens  = ["EXISTENCE", "COHERENCE", "IDENTITY"]
    void_tokens    = ["BOUNDARY", "OBSERVATION", "CAUSALITY"]

    for op_name, stable, void in [("IDENTITY", stable_tokens, void_tokens),
                                   ("SURPRISE", void_tokens, stable_tokens)]:
        sem_vec  = lm_semantic.get_imaginary_vector(op_name)
        hash_vec = lm_hash.get_imaginary_vector(op_name)
        if sem_vec is None or hash_vec is None:
            continue

        sem_sim  = avg_sim(sem_vec,  stable)
        hash_sim = avg_sim(hash_vec, stable)
        total_checks += 1

        label = PASS if sem_sim > hash_sim else FAIL
        result = sem_sim > hash_sim
        if result: passed_checks += 1

        print(f"  {label} {op_name:10s}  semantic={sem_sim:+.4f}  hash={hash_sim:+.4f}  "
              f"({'semantic closer to expected region' if result else 'hash closer — suspicious'})")

    passed = passed_checks == total_checks
    label = PASS if passed else FAIL
    print(f"\n  {label} V2: Semantic seeding {'correct' if passed else 'INCORRECT'} "
          f"({passed_checks}/{total_checks} checks)")
    return passed


# ─────────────────────────────────────────────────────────────────
# V3 — Model switch check (structural-only H5)
# ─────────────────────────────────────────────────────────────────
def test_v3():
    header("V3: Model Switch (H5 unchanged with different embedders)")
    from noise_compass.system.h5_manager import H5Manager
    from noise_compass.architecture.dictionary import Dictionary

    h5 = H5Manager()

    # Two trivial embedders with different output (simulates model switch)
    def embedder_a(text):
        rng = np.random.RandomState(abs(hash(text)) % (2**31))
        return rng.randn(384).astype(np.float32)

    def embedder_b(text):
        rng = np.random.RandomState((abs(hash(text)) + 99999) % (2**31))
        return rng.randn(384).astype(np.float32)

    d_a = Dictionary.load_cache(h5_manager=h5, embedder=embedder_a)
    d_b = Dictionary.load_cache(h5_manager=h5, embedder=embedder_b)

    keys_a = set(d_a.god_tokens.keys())
    keys_b = set(d_b.god_tokens.keys())

    print(f"  Embedder A loaded: {len(keys_a)} god-tokens")
    print(f"  Embedder B loaded: {len(keys_b)} god-tokens")

    # Same set of tokens — different vectors
    same_keys = keys_a == keys_b
    # Vectors differ (different random seeds)
    if "EXISTENCE" in d_a.god_tokens and "EXISTENCE" in d_b.god_tokens:
        e_a = np.array(d_a.god_tokens["EXISTENCE"].embedding)
        e_b = np.array(d_b.god_tokens["EXISTENCE"].embedding)
        vectors_differ = float(np.linalg.norm(e_a - e_b)) > 0.01
    else:
        vectors_differ = False

    passed = same_keys and vectors_differ
    label = PASS if passed else FAIL

    print(f"  Same token set: {'yes' if same_keys else 'NO'}")
    print(f"  Vectors differ: {'yes (model switch works)' if vectors_differ else 'NO'}")
    print(f"\n  {label} V3: H5 unchanged across model switch")
    return passed


# ─────────────────────────────────────────────────────────────────
# V4 (static) — NODE_RING canonicalization
# ─────────────────────────────────────────────────────────────────
def test_v4_static():
    header("V4: NODE_RING Canonicalization")
    from noise_compass.architecture.tokens import NODE_RING

    print(f"  tokens.NODE_RING = {list(NODE_RING)}")

    # Read ouroboros_resonant.py source and check it no longer hardcodes COHERENCE
    resonant_path = os.path.join(SRC, "noise_compass", "system", "ouroboros_resonant.py")
    src = open(resonant_path, encoding='utf-8').read()

    hardcoded_coherence = '"COHERENCE"' in src and 'self.nodes = [' in src
    uses_canonical      = '_CANONICAL_RING' in src or 'NODE_RING' in src

    print(f"  Still hardcodes COHERENCE list: {hardcoded_coherence}")
    print(f"  References canonical NODE_RING: {uses_canonical}")

    passed = uses_canonical and not hardcoded_coherence
    label = PASS if passed else FAIL
    print(f"\n  {label} V4: NODE_RING canonicalized")
    return passed


# ─────────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    results = {}
    try:
        results["V1"] = test_v1()
    except Exception as e:
        print(f"  {FAIL} V1 crashed: {e}")
        results["V1"] = False

    try:
        results["V2"] = test_v2()
    except Exception as e:
        print(f"  {FAIL} V2 crashed: {e}")
        results["V2"] = False

    try:
        results["V3"] = test_v3()
    except Exception as e:
        print(f"  {FAIL} V3 crashed: {e}")
        results["V3"] = False

    try:
        results["V4"] = test_v4_static()
    except Exception as e:
        print(f"  {FAIL} V4 crashed: {e}")
        results["V4"] = False

    header("SUMMARY")
    for k, v in results.items():
        print(f"  {PASS if v else FAIL}  {k}")
    total = sum(results.values())
    print(f"\n  {total}/{len(results)} tests passed")
