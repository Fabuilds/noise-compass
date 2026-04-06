import unittest
from unittest.mock import MagicMock
import os
import sys
import numpy as np

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Runtime')
sys.path.append('E:/Antigravity/Architecture')

# Primary Mock: Block heavy dependencies
mock_engine_module = MagicMock()
sys.modules["interference_engine"] = mock_engine_module

from noise_compass.architecture.dream import Dreamer
from noise_compass.architecture.dictionary import Dictionary

class TestAxiomAssimilation(unittest.TestCase):
    def setUp(self):
        self.mock_pipeline = MagicMock()
        self.mock_manager = MagicMock()
        self.mock_pipeline.dictionary.manager = self.mock_manager
        self.mock_pipeline.dictionary.god_tokens = {}
        self.mock_pipeline.embedder.embed.return_value = np.zeros(768)
        self.mock_pipeline.tension = MagicMock()
        self.mock_pipeline.flags = MagicMock()
        
        self.dreamer = Dreamer(self.mock_pipeline)

    def test_auto_math_promotion(self):
        """Verify that high-leverage math dreams are promoted to CRYSTALLIZED automatically."""
        # 1. Setup mock rejection (math-based)
        rejection = {
            'event': 'GAP_VIOLATION',
            'gap': 'math_existence',
            'left': 'EXISTENCE',
            'right': 'BOUNDARY',
            'verdict': 'REJECTED'
        }
        self.mock_manager.get_latest_dissonance_context.return_value = [rejection]
        
        # 2. Setup mock dream result (High Leverage)
        self.mock_pipeline.speak.return_value = "Riemann manifold bridges exist at t=0.5."
        # 1. Initial process (dream loop)
        # 2. Deep Zoom (dream loop, if leverage > 0.4)
        # 3. Confirmation Pass (assimilate_axiom)
        self.mock_pipeline.process.side_effect = [
            {'leverage': 0.85, 'hash': 'abc123'}, 
            {'leverage': 0.88, 'hash': 'abc456'},  
            {'leverage': 0.90, 'hash': 'abc789'}   
        ]
        
        # 3. Run dream (math_focused=True)
        results = self.dreamer.dream(steps=1, math_focused=True)
        
        # 4. Assert save_axiom was called with CRYSTALLIZED status
        args, kwargs = self.mock_manager.save_axiom.call_args
        status = kwargs.get('status')
        self.assertEqual(status, "CRYSTALLIZED")
        # metadata is the 5th positional argument
        self.assertEqual(args[4].get('category'), 'MATH')

    def test_manual_identity_pending(self):
        """Verify that identity dreams are saved as PENDING even if high leverage."""
        # 1. Setup mock rejection (identity-based)
        rejection = {
            'event': 'CAUSAL_VIOLATION',
            'effect': 'IDENTITY',
            'missing_cause': 'COHERENCE',
            'verdict': 'REJECTED'
        }
        self.mock_manager.get_latest_dissonance_context.return_value = [rejection]
        
        # 2. Setup high leverage dream
        self.mock_pipeline.speak.return_value = "Identity is the echo of a resonant field."
        self.mock_pipeline.process.side_effect = [
            {'leverage': 0.95, 'hash': 'xyz'}, 
            {'leverage': 0.97},
            {'leverage': 0.98}
        ]
        
        # 3. Run dream (math_focused=False)
        self.dreamer.dream(steps=1, math_focused=False)
        
        # 4. Assert save_axiom was called with PENDING status
        args, kwargs = self.mock_manager.save_axiom.call_args
        status = kwargs.get('status')
        self.assertEqual(status, "PENDING")
        self.assertEqual(args[4].get('category'), 'IDENTITY_ETHICS')

if __name__ == "__main__":
    unittest.main()
