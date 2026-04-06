import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import numpy as np

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Runtime')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.system.gap_registry import GapRegistry
from noise_compass.system.interference_engine import InterferenceEngine
from noise_compass.architecture.dream import Dreamer

class TestAlgebraicLambda(unittest.TestCase):
    def setUp(self):
        self.mock_manager = MagicMock()
        self.gap_reg = GapRegistry(manager=self.mock_manager)
        
    def test_positive_semiring_clipping(self):
        """Verify that magnitudes are clipped to [0, 1] (Positive Semiring)."""
        engine = InterferenceEngine(suppress_preload=True)
        engine.manager = self.mock_manager
        engine.gap_registry = self.gap_reg
        engine.causal_dag = MagicMock()
        engine.causal_dag.apply_causal_flow.side_effect = lambda x: x # Identity
        engine.failure_cache = MagicMock()
        engine.failure_cache.calculate_repulsion.return_value = 2.0
        engine.manager.get_hot_failures.return_value = []
        
        # Mock wave_match to return values outside [0, 1]
        # wave_match(emb, attractor) -> (mag, phase)
        engine.wave_match = MagicMock(side_effect=[(1.5, 0.0), (-0.5, 0.0)])
        
        engine.cached_tokens = {
            'TOKEN_1': {'vector': np.zeros(1024), 'void': False},
            'TOKEN_2': {'vector': np.zeros(1024), 'void': False}
        }
        
        field = engine.produce_interference_field("clip test")
        
        # mag_1 should be clipped to 1.0 (from 1.5 * damping)
        # mag_2 should be clipped to 0.0 (from -0.5 * damping)
        mag_1 = field['TOKEN_1']['magnitude']
        mag_2 = field['TOKEN_2']['magnitude']
        
        self.assertIsInstance(mag_1, float)
        self.assertLessEqual(mag_1, 1.0)
        self.assertGreaterEqual(mag_1, 0.0)
        self.assertGreaterEqual(mag_2, 0.0)
        print(f"[SUCCESS] Positive Semiring clipping verified: {mag_1}, {mag_2}")

    def test_debruijn_depth_isolation(self):
        """Verify that GapRegistry isolates violations by binder_depth."""
        # 1. Register two gaps: one at depth 0, one at depth 1
        self.gap_reg.cached_gaps = {
            'surface_gap': {'left': 'A', 'right': 'B', 'void_depth': 0.8, 'binder_depth': 0},
            'deep_gap': {'left': 'A', 'right': 'C', 'void_depth': 0.9, 'binder_depth': 1}
        }
        
        # 2. Setup field with violation for BOTH
        # A=1.0, B=0.0 (Surface violation), C=0.0 (Deep violation)
        field = {
            'A': {'magnitude': 1.0},
            'B': {'magnitude': 0.0},
            'C': {'magnitude': 0.0}
        }
        
        # 3. Detect at depth 0
        violations_0 = self.gap_reg.detect_violations(field, current_depth=0)
        self.assertIn('surface_gap', violations_0)
        self.assertNotIn('deep_gap', violations_0)
        
        # 4. Detect at depth 1
        violations_1 = self.gap_reg.detect_violations(field, current_depth=1)
        self.assertNotIn('surface_gap', violations_1)
        self.assertIn('deep_gap', violations_1)
        print("[SUCCESS] De Bruijn Depth isolation verified.")

    def test_alpha_equivalence_merging(self):
        """Verify that similar axioms are merged (alpha-equivalent) instead of duplicated."""
        mock_pipeline = MagicMock()
        dreamer = Dreamer(mock_pipeline)
        
        # 1. Setup mock dictionary to find an existing concept
        mock_pipeline.dictionary.nearest_attractor.return_value = ('EXISTING_CONCEPT', 0.99)
        mock_pipeline.embedder.embed.return_value = np.zeros(1024)
        
        # 2. Setup double confirmation to pass
        # Initial, Zoom, Confirmation
        mock_pipeline.process.side_effect = [
            {'leverage': 0.8, 'hash': 'abc'}, 
            {'leverage': 0.82},
            {'leverage': 0.85}
        ]
        mock_pipeline.speak.return_value = "Riemann manifold bridge"
        
        # 3. Run dream to trigger assimilation
        dreamer.dream(steps=1, math_focused=True)
        
        # 4. Assertions
        # save_axiom should NOT be called
        self.assertFalse(mock_pipeline.dictionary.manager.save_axiom.called)
        # increment_bubble_mass SHOULD be called
        mock_pipeline.dictionary.manager.increment_bubble_mass.assert_called_with('EXISTING_CONCEPT')
        print("[SUCCESS] α-equivalence concept merging verified.")

if __name__ == "__main__":
    unittest.main()
