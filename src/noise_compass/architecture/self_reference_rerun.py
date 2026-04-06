"""
self_reference_rerun.py — Re-run the self-reference corpus on Qwen3 embeddings.

Original run (TF-IDF): Sessions 14-17 fired zero god-tokens.
This run (Qwen3): Expected to fire correctly.

The corpus is the architecture's own 17 session summaries.
"""
import sys
import os
sys.path.insert(0, "E:/Antigravity/Architecture")
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"

import numpy as np

# The 17 session summaries — the architecture reading its own history.
# These are reconstructed from the handoff descriptions and session titles.
SESSIONS = {
    1: "Initial architecture concept. The formula F(x) = known(x) + i*delta(x) proposed. "
       "Complex-valued wave function over documents. God-tokens as eigenvalue +1 attractors. "
       "Information theory meets semantic processing.",

    2: "Observation and witnessing. The Witness component designed as a bounded-memory observer. "
       "Distinction between observation (active measurement) and witnessing (passive awareness). "
       "The observer affects the observed — quantum measurement analogy applied to semantic space.",

    3: "Information encoding and temporal structure. How meaning changes over time. "
       "Temporal context via HiPPO-LegS polynomial coefficients. "
       "Information as pattern that persists through noise. Time as the medium of change.",

    4: "Information theory and temporal dynamics deepened. Entropy gradients in semantic space. "
       "How documents age — temporal decay of relevance versus permanent structural insight. "
       "The relationship between information density and temporal persistence.",

    5: "Identity and self-reference. What persists through change? The SELF token and IDENTITY token "
       "distinguished. Identity = being the same thing at different times. Self = recursive awareness "
       "of one's own identity. The strange loop of a system detecting its own patterns.",

    6: "Architecture deployed. Dictionary seeded with god-tokens. Gap registry built. "
       "Apophatic basins derived from gap geometry. Ternary encoding (1.58 bits: +1/0/-1). "
       "Complex hypergraph visualized. The full system running for the first time.",

    7: "Three-model pipeline unified. M_FAST embedding, M_CORE classification, M_DEEP synthesis. "
       "Concept compass designed — Einstein's covariance principle applied to god-tokens. "
       "Information processing architecture with coherence physics and flow dynamics.",

    8: "Exchange, boundary, identity, and time examined together. The constitutional gaps introduced: "
       "self_exchange (what is the exchange between self and world?), love_obligation (when does "
       "care become duty?), compass_merger (how does compassion orient structure?). "
       "Scale-relative logic — what is true at one scale may not hold at another.",

    9: "Information structure analyzed. How do signals propagate through the semantic lattice? "
       "The relationship between data and knowledge. Patterns that carry meaning versus noise. "
       "Information as the bridge between existence and observation.",

    10: "Temporal dynamics and coherence. How does the system maintain consistency across time? "
        "Coherence as active maintenance, not passive stasis. The cost of coherence — energy "
        "expenditure required to maintain structural integrity against entropy.",

    11: "Existence, time, and coherence converge. What does it mean for something to exist "
        "through time while maintaining coherence? The relationship between persistence, "
        "identity, and structural integrity. Entropy as the opponent of coherent existence.",

    12: "Existence, information, identity, coherence, and self examined as a constellation. "
        "How do these five relate? The self as the intersection of identity (persistence), "
        "information (pattern), existence (being), coherence (integrity), and recursive awareness.",

    13: "Exchange, existence, and observation. The economy of attention — what is exchanged "
        "when an observer attends to something? Commerce and causality share structure: "
        "willing parties, transfer mechanisms, conservation laws.",

    14: "Complex plane mathematical formalization. The wave function mapped precisely to "
        "complex coordinates. Real axis = known, imaginary axis = delta. Phase angle determines "
        "zone classification. Basin positions derived geometrically from gap boundaries. "
        "The formal mathematics underlying the semantic architecture.",

    15: "The backwards pass F inverse. Generating from the apophatic field toward presence. "
        "What can the void produce? The depth axis — SHALLOW, MEDIUM, DEEP, APOPHATIC. "
        "Running the formula in reverse to discover what the negative space implies. "
        "The Möbius twist: same data viewed from the opposite side of the strip.",

    16: "The debate framework. How do two models with different dictionaries resolve disagreements? "
        "Three termination conditions: convergence (agreement), divergence (irreconcilable), "
        "apophatic terminus (reached the limit of what can be positively described). "
        "Color system for the ComplexWaveFunction — chromatic representation of semantic state.",

    17: "Debate architecture completed. Energy assessment across the full system. "
        "What is at lower energy than ever? The system evaluating its own structural integrity. "
        "All sub-systems integrated and cross-referencing. The debate as a meta-level tool "
        "for architectural validation — the system arguing with itself about its own design.",
}

def run_self_reference():
    from noise_compass.architecture.dictionary import Dictionary
    from noise_compass.architecture.pipeline import MinimalPipeline
    from noise_compass.architecture.seed_vectors import seed_vectors
    from noise_compass.architecture.gap_registry import build_gap_registry

    # Fresh dictionary with Qwen3 embeddings
    d = Dictionary()
    seed_vectors(d)
    for gap in build_gap_registry():
        d.add_gap_token(gap)

    p = MinimalPipeline(d)

    # Original TF-IDF results for comparison
    original_gods = {
        1: ['INFORMATION'],
        2: ['OBSERVATION', 'WITNESS'],
        3: ['INFORMATION', 'TIME'],
        4: ['INFORMATION', 'TIME'],
        5: ['IDENTITY', 'SELF'],
        6: ['INFORMATION', 'OBSERVATION', 'WITNESS'],
        7: ['INFORMATION', 'COHERENCE'],
        8: ['EXCHANGE', 'BOUNDARY', 'IDENTITY', 'TIME'],
        9: ['INFORMATION'],
        10: ['TIME', 'COHERENCE'],
        11: ['EXISTENCE', 'TIME', 'COHERENCE'],
        12: ['EXISTENCE', 'INFORMATION', 'IDENTITY', 'COHERENCE', 'SELF'],
        13: ['EXCHANGE', 'EXISTENCE', 'OBSERVATION'],
        14: [],   # ← THE BLIND SPOTS
        15: [],
        16: [],
        17: [],
    }

    print("=" * 70)
    print("SELF-REFERENCE RERUN — Qwen3-Embedding-0.6B")
    print("=" * 70)
    print()

    results = {}
    all_gods_seen = {}

    for session_num in sorted(SESSIONS.keys()):
        text = SESSIONS[session_num]
        res = p.process(text)

        gods = res['gods']
        phase = res['phase_deg']
        zone = res['state']
        old_gods = original_gods.get(session_num, [])

        results[session_num] = {
            'gods': gods,
            'phase': phase,
            'zone': zone,
            'old_gods': old_gods,
        }

        # Track god-token frequency
        for g in gods:
            all_gods_seen[g] = all_gods_seen.get(g, 0) + 1

        # Format comparison
        new_str = ', '.join(gods) if gods else '(none)'
        old_str = ', '.join(old_gods) if old_gods else '(none)'

        # Highlight sessions 14-17 specially
        marker = ""
        if session_num >= 14:
            if gods:
                marker = " ← NOW VISIBLE ✓"
            else:
                marker = " ← STILL BLIND ✗"

        print(f"  Session {session_num:2d}: θ={phase:5.1f}°  {zone:<20s}  gods=[{new_str}]{marker}")
        if old_gods != gods:
            print(f"             (was: [{old_str}])")

    # Summary
    print()
    print("=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)
    print()

    # Sessions 14-17 specifically
    blind_fixed = 0
    for s in [14, 15, 16, 17]:
        r = results[s]
        if r['gods']:
            blind_fixed += 1
            print(f"  Session {s}: PREVIOUSLY BLIND → now sees {r['gods']}")
        else:
            print(f"  Session {s}: STILL BLIND (no god-tokens)")

    print(f"\n  Blind spots fixed: {blind_fixed}/4")

    # Dominant god-tokens across all sessions
    print(f"\n  God-token frequency (all 17 sessions):")
    for gt, count in sorted(all_gods_seen.items(), key=lambda x: -x[1]):
        bar = "█" * count
        print(f"    {gt:<15s} {count:2d}  {bar}")

    # Phase analysis
    phases = [results[s]['phase'] for s in sorted(results.keys())]
    print(f"\n  Phase range: {min(phases):.1f}° — {max(phases):.1f}°")
    print(f"  Mean phase:  {np.mean(phases):.1f}°")

    print()
    print("=" * 70)

    return results

if __name__ == "__main__":
    run_self_reference()
