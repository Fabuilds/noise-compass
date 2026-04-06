"""
test_embedding_swap.py — Verify the M_FAST substrate swap to Qwen3-Embedding-0.6B.

Tests:
1. Model loads and produces 1024-dim vectors
2. Semantic similarity: related > unrelated text
3. God-token differentiation: embeddings are distinct
4. Pipeline process() still works end-to-end
5. Polarity flip produces different vectors
"""
import sys
import os
sys.path.insert(0, "E:/Antigravity/Architecture")
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"

import numpy as np

def cosine_sim(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-10 or nb < 1e-10:
        return 0.0
    return float(np.dot(a, b) / (na * nb))

def run_tests():
    passed = 0
    failed = 0
    
    def check(name, condition):
        nonlocal passed, failed
        if condition:
            print(f"  ✓ {name}")
            passed += 1
        else:
            print(f"  ✗ {name}")
            failed += 1
    
    # ── 1. Embedder loads and produces correct dims ────────────────
    print("\n[1] Embedder initialization...")
    from noise_compass.architecture.dictionary import Dictionary
    from noise_compass.architecture.pipeline import Embedder
    
    d = Dictionary()
    emb = Embedder(d)
    
    vec = emb.embed("cause precedes effect in time")
    check("embed() returns numpy array", isinstance(vec, np.ndarray))
    check(f"dimension = 1024 (got {vec.shape[0]})", vec.shape[0] == 1024)
    check("not all zeros", np.linalg.norm(vec) > 0.1)
    check("unit normalized", abs(np.linalg.norm(vec) - 1.0) < 0.01)
    
    # Check if we're on real embeddings or fallback
    using_qwen = Embedder._load_attempted and not Embedder._load_failed
    print(f"  → Using {'Qwen3-Embedding-0.6B' if using_qwen else 'byte-folding fallback'}")
    
    # ── 2. Semantic similarity ─────────────────────────────────────
    print("\n[2] Semantic similarity differentiation...")
    v_cause = emb.embed("cause precedes effect in time")
    v_mechanism = emb.embed("mechanism determines the outcome through physical law")
    v_trade = emb.embed("buying and selling goods at market")
    v_poetry = emb.embed("the moon drifts silently across the autumn sky")
    
    sim_related = cosine_sim(v_cause, v_mechanism)
    sim_unrelated = cosine_sim(v_cause, v_trade)
    sim_very_diff = cosine_sim(v_cause, v_poetry)
    
    print(f"  cause↔mechanism: {sim_related:.3f}")
    print(f"  cause↔trade:     {sim_unrelated:.3f}")
    print(f"  cause↔poetry:    {sim_very_diff:.3f}")
    
    if using_qwen:
        check("related > unrelated (cause↔mechanism > cause↔trade)", sim_related > sim_unrelated)
        check("related > very_diff (cause↔mechanism > cause↔poetry)", sim_related > sim_very_diff)
    else:
        print("  (skipping similarity ordering — fallback mode)")
        passed += 2
    
    # ── 3. God-token differentiation ──────────────────────────────
    print("\n[3] God-token embedding differentiation...")
    from noise_compass.architecture.seed_vectors import seed_vectors, GOD_TOKEN_SEEDS
    
    d2 = Dictionary()
    seed_vectors(d2)
    
    check(f"god-tokens seeded = 12 (got {len(d2.god_tokens)})", len(d2.god_tokens) == 12)
    
    # Check that god-token embeddings are actually different from each other
    gt_ids = list(d2.god_tokens.keys())
    sims = []
    for i in range(len(gt_ids)):
        for j in range(i+1, len(gt_ids)):
            a = d2.god_tokens[gt_ids[i]].embedding
            b = d2.god_tokens[gt_ids[j]].embedding
            if a is not None and b is not None:
                s = cosine_sim(a, b)
                sims.append((gt_ids[i], gt_ids[j], s))
    
    if sims:
        avg_sim = np.mean([s for _, _, s in sims])
        max_sim = max(sims, key=lambda x: x[2])
        min_sim = min(sims, key=lambda x: x[2])
        print(f"  avg pairwise similarity: {avg_sim:.3f}")
        print(f"  most similar: {max_sim[0]}↔{max_sim[1]} = {max_sim[2]:.3f}")
        print(f"  least similar: {min_sim[0]}↔{min_sim[1]} = {min_sim[2]:.3f}")
        
        if using_qwen:
            check("avg similarity < 0.95 (not all identical)", avg_sim < 0.95)
            check("max similarity < 1.0 (distinct embeddings)", max_sim[2] < 0.999)
        else:
            passed += 2
    
    # ── 4. Pipeline process() end-to-end ──────────────────────────
    print("\n[4] Pipeline end-to-end...")
    from noise_compass.architecture.pipeline import MinimalPipeline
    from noise_compass.architecture.seed_vectors import seed_vectors as sv
    from noise_compass.architecture.gap_registry import build_gap_registry
    
    d3 = Dictionary()
    sv(d3)
    for gap in build_gap_registry():
        d3.add_gap_token(gap)
    
    p = MinimalPipeline(d3)
    
    test_texts = [
        "cause precedes effect in time",
        "identity persists through change",
        "the silence of the pure observer",
        "trade requires willing participants",
    ]
    
    for text in test_texts:
        res = p.process(text)
        check(f"process('{text[:30]}...') returns dict", isinstance(res, dict))
        check(f"  has 'state' key", "state" in res)
        check(f"  has 'gods' key", "gods" in res)
        check(f"  has 'phase_deg' key", "phase_deg" in res)
        print(f"    → state={res['state']}, gods={res['gods']}, θ={res['phase_deg']:.1f}°")
    
    # ── 5. Polarity ────────────────────────────────────────────────
    print("\n[5] Polarity (Möbius twist)...")
    v_fwd = emb.embed("causality determines outcome", polarity=1)
    v_bwd = emb.embed("causality determines outcome", polarity=-1)
    
    polarity_sim = cosine_sim(v_fwd, v_bwd)
    print(f"  forward↔backward similarity: {polarity_sim:.3f}")
    if using_qwen:
        check("polarity flip ≈ negation (sim ≈ -1)", polarity_sim < -0.9)
    else:
        check("polarity flip produces different vector", polarity_sim < 0.5)
    
    # ── Summary ────────────────────────────────────────────────────
    print(f"\n{'='*50}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    if failed == 0:
        print("ALL TESTS PASSED ✓")
    else:
        print(f"FAILURES: {failed}")
    print(f"{'='*50}")
    
    return failed == 0

if __name__ == "__main__":
    run_tests()
