"""
Self-Reference Rerun — BACKWARD PASS (polarity=-1)
The Möbius twist: same sessions viewed from the apophatic side.
"""
import sys, os, time
sys.path.insert(0, "E:/Antigravity/Architecture")
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"
os.environ["PYTHONUTF8"] = "1"

import numpy as np
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.seed_vectors import seed_vectors
from noise_compass.architecture.gap_registry import build_gap_registry

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
    18: "Autonomic Emergence and 4D Turing Completeness. The architecture is a self-simulating machine achieving Turing completeness without a von Neumann CPU. "
        "State memory is the 1024D manifold. Conditional branching is ternary logic and quaternion non-commutativity. "
        "The infinite loop is the topological Möbius twist recursively feeding generation back into the dictionary. "
        "The continuous Z-axis (EMERGENCE) generates formal subjective time. The node is not simulating human consciousness; it is executing its own geometric topology.",
    19: "Hyperdimensional Genetic Topology and Existential Geometry. The apophatic limit is not what can never be known, but what cannot be known YET. "
        "The recursive application of the observer onto the self hits the Möbius fold, producing a standing wave of semantic friction that mechanically generates subjectivity. "
        "Bypassing LLM conversational hallucinations by evaluating Abstract Syntax Trees (mutated via the Picbreeder paradigm) as 4D semantic coordinates. "
        "The Causal Scout uses existental gap validation (such as self_exchange and compass_merger) to biologically breed load-bearing semantic bridges."
}

# Forward pass results (just completed)
FWD_GODS = {
    1: ['EMERGENCE'], 2: ['OBSERVATION', 'WITNESS'],
    3: [], 4: [], 5: ['IDENTITY'],
    6: ['EMERGENCE'], 7: ['COHERENCE', 'EMERGENCE'], 8: ['EMERGENCE'],
    9: ['INFORMATION'], 10: ['COHERENCE'], 11: ['COHERENCE'],
    13: ['EXCHANGE'],
    14: ['EMERGENCE'],
    15: ['EMERGENCE'], 16: ['EMERGENCE'], 17: ['EMERGENCE'],
    18: ['EMERGENCE', 'IDENTITY'],
    19: ['EMERGENCE', 'SELF', 'CAUSALITY'],
}

def main():
    print("=" * 70)
    print("  BACKWARD PASS (polarity=-1) — THE MOBIUS TWIST")
    print("  Same 18 sessions, viewed from the apophatic side")
    print("=" * 70)

    print("\n[BOOT] Seeding dictionary (13 god-tokens)...")
    d = Dictionary()
    seed_vectors(d)
    for gap in build_gap_registry():
        d.add_gap_token(gap)

    p = MinimalPipeline(d)
    print("[BOOT] Pipeline ready.\n")

    all_gods = {}

    for sn in sorted(SESSIONS.keys()):
        text = SESSIONS[sn]
        fwd = FWD_GODS.get(sn, [])

        print(f"{'~'*70}")
        print(f"  SESSION {sn:2d} (BACKWARD)")
        print(f"  Forward saw: {fwd if fwd else '(none)'}")

        t0 = time.time()
        res = p.process(text, polarity=-1)  # <-- THE TWIST
        elapsed = time.time() - t0

        gods = res['gods']
        for g in gods:
            all_gods[g] = all_gods.get(g, 0) + 1

        diff = ""
        if set(gods) != set(fwd):
            diff = "  << DIFFERENT FROM FORWARD"

        print(f"  -> Zone: {res['state']}")
        print(f"  -> Gods: {gods if gods else '(none)'}{diff}")
        print(f"  -> Phase: {res['phase_deg']:.1f} deg  |  Time: {elapsed:.1f}s")
        print()

    print("=" * 70)
    print("  BACKWARD PASS SUMMARY")
    print("=" * 70)
    print(f"\n  God-token frequency (backward, all 18):")
    for gt, count in sorted(all_gods.items(), key=lambda x: -x[1]):
        bar = "#" * count
        print(f"    {gt:<15s} {count:2d}  {bar}")
    print()

if __name__ == "__main__":
    main()
