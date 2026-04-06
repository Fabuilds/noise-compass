import unittest
from unittest.mock import MagicMock
import os
import sys

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.dream import Dreamer
from noise_compass.architecture.quaternion_field import GOD_TOKEN_QUATERNIONS

class TestDreamRepair(unittest.TestCase):
    def setUp(self):
        self.mock_pipeline = MagicMock()
        # Mock dictionary -> manager for H5 access
        self.mock_manager = MagicMock()
        self.mock_pipeline.dictionary.manager = self.mock_manager
        
        # Mock tension and flags
        self.mock_pipeline.tension = MagicMock()
        self.mock_pipeline.flags = MagicMock()
        
        # Instantiate Dreamer
        self.dreamer = Dreamer(self.mock_pipeline)

    def test_gap_repair_priority(self):
        """Verify that a GAP_VIOLATION in H5 triggers REPAIR MODE."""
        # 1. Setup Mock Rejection (EXISTENCE <-> BOUNDARY gap)
        rejection = {
            'event': 'GAP_VIOLATION',
            'gap': 'existence_boundary',
            'left': 'EXISTENCE',
            'right': 'BOUNDARY',
            'verdict': 'REJECTED'
        }
        self.mock_manager.get_latest_dissonance_context.return_value = [rejection]
        
        # 2. Run Dream (1 step for speed)
        # Mock pipeline.speak to return some text
        self.mock_pipeline.speak.return_value = "The boundary of existence is a refractive shell."
        self.mock_pipeline.process.return_value = {'leverage': 0.5, 'hash': 'abc123'}
        
        # Capture stdout to verify the focus_note
        import io
        from contextlib import redirect_stdout
        f = io.StringIO()
        with redirect_stdout(f):
            results = self.dreamer.dream(steps=1, math_focused=False)
        
        output = f.getvalue()
        
        # 3. Assertions
        print(f"Captured Output: {output}")
        self.assertIn("STRUCTURAL REPAIR (GAP: existence_boundary)", output)
        self.assertIn("Traveling from EXISTENCE to BOUNDARY", output)
        
        # Verify prompt construction (checking the call to pipeline.speak)
        args, kwargs = self.mock_pipeline.speak.call_args
        prompt = args[0]
        self.assertIn("STRUCTURAL MISSION", prompt)
        self.assertIn("satisfies the structural void", prompt)

    def test_causal_repair_priority(self):
        """Verify that a CAUSAL_VIOLATION in H5 triggers REPAIR MODE."""
        # 1. Setup Mock Rejection (IDENTITY -> requires -> SELF)
        rejection = {
            'event': 'CAUSAL_VIOLATION',
            'effect': 'SELF',
            'missing_cause': 'IDENTITY',
            'verdict': 'REJECTED'
        }
        self.mock_manager.get_latest_dissonance_context.return_value = [rejection]
        
        # 2. Run Dream
        self.mock_pipeline.speak.return_value = "Identity projects selfhood through coherence."
        self.mock_pipeline.process.return_value = {'leverage': 0.1}
        
        import io
        from contextlib import redirect_stdout
        f = io.StringIO()
        with redirect_stdout(f):
            self.dreamer.dream(steps=1, math_focused=True)
        
        output = f.getvalue()
        
        # 3. Assertions
        self.assertIn("LOGICAL REPAIR (CAUSAL: SELF)", output)
        self.assertIn("Traveling from IDENTITY to SELF", output)
        
        args, kwargs = self.mock_pipeline.speak.call_args
        prompt = args[0]
        self.assertIn("Synthesize the mathematical solution to heal the conflict", prompt)

if __name__ == "__main__":
    unittest.main()
