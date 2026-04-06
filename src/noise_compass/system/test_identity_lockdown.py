import unittest
from unittest.mock import MagicMock
import os
import sys
import numpy as np

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Runtime')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.system.gap_registry import GapRegistry
from noise_compass.system.interference_engine import InterferenceEngine

class TestIdentityLockdown(unittest.TestCase):
    def setUp(self):
        self.mock_manager = MagicMock()
        # Mock h5_manager to return our specific identity gaps
        self.mock_manager.get_file.return_value.__enter__.return_value = {
            'gaps': {
                'id_coherence': MagicMock(),
                'sovereign_logic': MagicMock()
            }
        }
        
        # Setup GapRegistry
        self.gap_reg = GapRegistry(manager=self.mock_manager)
        # Manually seed cached_gaps to avoid complex H5 mocking
        self.gap_reg.cached_gaps = {
            'id_coherence': {
                'left': 'IDENTITY',
                'right': 'COHERENCE',
                'void_depth': 0.8
            },
            'sovereign_logic': {
                'left': 'SOVEREIGNTY',
                'right': 'CAUSALITY',
                'void_depth': 0.9
            }
        }

    def test_identity_gap_violation(self):
        """Verify that IDENTITY without COHERENCE results in REJECTION."""
        # 1. Setup field with Violation
        field = {
            'IDENTITY': {'magnitude': 0.8},
            'COHERENCE': {'magnitude': 0.05} # Missing/Dark
        }
        
        # 2. Detect Violations
        violations = self.gap_reg.detect_violations(field)
        
        # 3. Assertions
        self.assertIn('id_coherence', violations)
        self.assertEqual(violations['id_coherence']['missing'], 'COHERENCE')
        self.assertGreater(violations['id_coherence']['tension'], 0.5)

    def test_strict_override_application(self):
        """Verify that InterferenceEngine zeroes out the field upon violation."""
        # 1. Setup Mock Engine
        engine = InterferenceEngine(suppress_preload=True)
        # Mock the manager and its methods
        engine.manager = MagicMock()
        engine.manager.get_hot_failures.return_value = []
        
        engine.gap_registry = self.gap_reg
        engine.causal_dag = MagicMock() 
        engine.causal_dag.apply_causal_flow.side_effect = lambda f: f # Return the field as-is
        engine.failure_cache = MagicMock()
        engine.failure_cache.calculate_repulsion.return_value = 0.0
        
        # 2. Prepare field state
        # Mock embed and wave_match
        engine.embed = MagicMock(return_value=np.zeros(768))
        engine.wave_match = MagicMock(side_effect=[(0.8, 0.0), (0.05, 0.0)]) # IDENTITY, COHERENCE
        engine.cached_tokens = {
            'IDENTITY': {'vector': np.zeros(768), 'void': False},
            'COHERENCE': {'vector': np.zeros(768), 'void': False}
        }
        
        # 3. Produce Field
        field = engine.produce_interference_field("Testing identity without coherence")
        
        # 4. Assertions
        # Both IDENTITY and COHERENCE should be set to 0.0
        self.assertEqual(field['IDENTITY']['magnitude'], 0.0)
        self.assertEqual(field['COHERENCE']['magnitude'], 0.0)
        print("[SUCCESS] Strict Override applied to Identity Gap.")

if __name__ == "__main__":
    unittest.main()
