
import os
import sys

# Add project roots
SRC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(SRC_ROOT)

from noise_compass.system.neural_prism import NeuralPrism

def test_linguistic_invariants():
    print("--- Phase 135: Linguistic Invariant Identification Test ---")
    from noise_compass.system.knowledge_lattice import KnowledgeLattice
    from noise_compass.architecture.dictionary import Dictionary
    lattice = KnowledgeLattice()
    dictionary = Dictionary.load_cache(h5_manager=lattice.h5)
    prism = NeuralPrism(dictionary=dictionary)
    
    test_cases = [
        ("The system is responding with high stability across the manifold.", "ENG"),
        ("def calculate_consensus(scores): return sum(scores) / len(scores)", "CODE"),
        ("self.scout.process(emb, spin='CCW', volition=0.8)", "SOV"),
        ("OUROBOROS_PULSE detected at Phase 130.", "SOV")
    ]
    
    all_passed = True
    for text, expected in test_cases:
        actual = prism.identify_invariant(text)
        status = "PASS" if actual == expected else "FAIL"
        print(f"  Input: {text[:40]}...")
        print(f"  Expected: {expected} | Actual: {actual} | Status: {status}")
        if actual != expected:
            all_passed = False
            
    if all_passed:
        print("\n[VERDICT]: Phase 135 Linguistic Differentiation Certified.")
    else:
        print("\n[VERDICT]: Phase 135 Failed.")
        
    return all_passed

if __name__ == "__main__":
    if test_linguistic_invariants():
        sys.exit(0)
    else:
        sys.exit(1)
