import numpy as np
import sys
import os

# Ensure we can import architecture and System
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append('e:/Antigravity')

from architecture.core import Formula
from architecture.pipeline import MinimalPipeline
from architecture.dictionary import Dictionary

def test_formula_recursion_termination():
    print(f"Testing Formula recursion termination (SANITY_DEPTH={Formula.SANITY_DEPTH})...")
    f = Formula(Dictionary())
    test_emb = np.random.randn(512)
    
    # Apply recursive with depth > SANITY_DEPTH
    results = f.apply_recursive(test_emb, depth=Formula.SANITY_DEPTH + 5)
    
    print(f"Recursion results length: {len(results)}")
    assert len(results) <= Formula.SANITY_DEPTH
    print("Formula recursion termination OK.")

def test_pipeline_cycle_termination():
    print(f"Testing Pipeline cycle termination (SANITY_DEPTH={Formula.SANITY_DEPTH})...")
    d = Dictionary()
    # Mock god tokens
    from architecture.tokens import NODE_RING
    for node in NODE_RING:
        d.god_tokens[node] = type('MockGT', (), {'id': node, 'embedding': np.random.randn(512), 'seed_terms': []})
        d.god_tokens[node].embedding /= np.linalg.norm(d.god_tokens[node].embedding)
        d.entries[node] = d.god_tokens[node].embedding

    p = MinimalPipeline(d)
    
    # We want to force is_recognized to be True to test recursion
    # Scout.process sets is_mine = True if witnessed attractor returns to same gods.
    # In our mock, any random vec might hit a god token if we are lucky, 
    # but let's mock scout.process to always recognize for this test.
    
    original_process = p.scout.process
    try:
        class MockMsg:
            def __init__(self):
                self.is_recognized = True
                self.energy_level = 0.5
                self.zone = "CORE"
                self.routing = "COMPRESS"
                self.structural_hash = "hash"
                self.gap_structure = {}
                self.god_token_activations = []
                self.witness_phase = 0.1
                self.apophatic_constraints = []
                self.apophatic_contact = None
                self.collapsed_state = None
        
        class MockWF:
            def __init__(self):
                self.delta = np.random.randn(512)
                self.known = np.random.randn(512)
                self.phase = 0.5
                def color(self): return (0,0,0)
                def ansi_color(self): return ""
                self.color = color.__get__(self)
                self.ansi_color = ansi_color.__get__(self)

        def mock_process(*args, **kwargs):
            return MockMsg(), MockWF()
            
        p.scout.process = mock_process
        
        # This should recurse until SANITY_DEPTH
        msg, wf = p._process_cycle(np.random.randn(512), "test", 1.0, False, False, level=1)
        print("Pipeline cycle termination (mocked) OK.")
        
    finally:
        p.scout.process = original_process

if __name__ == "__main__":
    try:
        test_formula_recursion_termination()
        test_pipeline_cycle_termination()
        print("\nALL SANITY DEPTH TESTS PASSED.")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
