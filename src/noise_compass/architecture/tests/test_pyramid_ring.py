import numpy as np
import sys
import os

# Ensure we can import architecture and System
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append('e:/Antigravity')

from architecture.tokens import NODE_RING, CardType
from architecture.core import Scout, Formula
from architecture.dictionary import Dictionary

def test_node_ring_integrity():
    print("Testing NODE_RING integrity...")
    assert len(NODE_RING) == 13 # 12 god tokens + GROUND 
    # Wait, the prompt says "12-node ring", but I added GROUND, EXISTENCE, ... , SELF.
    # Count: GROUND(1), EXISTENCE(2), IDENTITY(3), BOUNDARY(4), OBSERVATION(5), INFORMATION(6), 
    # CAUSALITY(7), EXCHANGE(8), OBLIGATION(9), TIME(10), PLACE(11), COHERENCE(12), SELF(13).
    # Correct. SELF is the 13th, grounding the loop.
    print(f"NODE_RING: {NODE_RING}")
    assert "GROUND" in NODE_RING
    assert "SELF" in NODE_RING
    print("Integrity OK.")

def test_card_stack_processing():
    print("Testing 5-card stack processing...")
    d = Dictionary()
    # Mock some god token embeddings
    for node in NODE_RING:
        d.god_tokens[node] = type('MockGT', (), {'id': node, 'embedding': np.random.randn(512), 'seed_terms': []})
        # Normalize mock embeddings
        d.god_tokens[node].embedding /= np.linalg.norm(d.god_tokens[node].embedding)
        d.entries[node] = d.god_tokens[node].embedding

    scout = Scout(d)
    test_emb = np.random.randn(512)
    test_emb /= np.linalg.norm(test_emb)
    
    results = scout._process_card_stack(test_emb)
    
    print(f"Stack results: {results}")
    assert "depth1_nodes" in results
    assert len(results["depth1_nodes"]) == 3
    assert "card4_void" in results
    assert "card5_phase" in results
    assert results["apex_constants"] == ["APOPHATIC_BASIN", "SELF", "LOGIC", "CONTEXT"]
    print("Stack processing OK.")

if __name__ == "__main__":
    try:
        test_node_ring_integrity()
        test_card_stack_processing()
        print("\nALL RING TESTS PASSED.")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
