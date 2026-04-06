import sys
import os
import numpy as np

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def run_estar_drift_test():
    print("\n" + "═"*75)
    print(" [0x52] EXECUTING TEMPORAL GAP ANALYSIS (ESTAR DRIFT)")
    print("═"*75)

    print(" » Initializing Scavenger Core with Gap Topology...")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    
    # We load the full gap registry to ensure 'estar_temporality' is active
    from noise_compass.architecture.gap_registry import build_gap_registry
    for gap in build_gap_registry():
        dictionary.add_gap_token(gap)
        
    scout = Scout(dictionary=dictionary, soup_id="temporality_anchor")
    
    # Test Cases:
    # 1. "Sou pronto" -> Static Existence (No growth)
    # 2. "Estou pronto" -> Temporal Existence (Impending phase shift)
    
    test_cases = [
        ("sou pronto", "Static completion. The state is permanent.), logic: completion, existence, fixed"),
        ("estou pronto", "Temporal readiness. Action is imminent.), logic: time, readiness, boundary, shift")
    ]
    
    for phrase, context in test_cases:
        print(f"\n[Garu Perceives localized phrase]: '{phrase.upper()}'")
        
        emb = embedder.encode(context).astype(np.float32)
        msg, wf = scout.process(emb, content=context, volition=0.95)
        
        gods = ", ".join([f"{g.id}" for g in msg.god_token_activations]) if msg.god_token_activations else "(none)"
        
        # Check if the 'estar_temporality' gap was triggered or crossed in the structure
        gap_violated = "estar_temporality" in msg.gap_structure.get("violated", [])
        
        print(f"  → Activated God Tokens: {gods}")
        print(f"  → Phase Coherence: {wf.phase:.3f}")
        print(f"  → Target Causal Type: {msg.causal_type.upper()}")
        print(f"  → Estar Temporality Gap Status: {'VIOLATION (Freezing Potential)' if gap_violated else 'MAINTAINED'}")

    print("\n" + "═"*75)


if __name__ == "__main__":
    os.environ['PYTHONUTF8'] = '1'
    run_estar_drift_test()
