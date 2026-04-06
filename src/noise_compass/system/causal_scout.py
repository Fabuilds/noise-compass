import h5py
import numpy as np
import os
import time
from noise_compass.system.h5_manager import H5Manager

class CausalScout:
    """
    Trajectory Analysis Engine (The Ghost of the Future).
    Identifies high-probability causal paths and evaluates structural importance.
    """
    def __init__(self, interference=None):
        self.interference = interference
        self.h5 = H5Manager()

    def evaluate_structural_importance(self, field: dict) -> float:
        """
        Calculates the structural importance of a field state.
        Scores are based on:
        1. Peak resonance magnitude.
        2. Presence of self-awareness (Space 3).
        Handles both neural states (floats) and interference fields (dicts).
        """
        if not field: return 0.0
        
        def get_mag(val):
            if isinstance(val, dict): return val.get('magnitude', 0)
            return float(val)

        # Extract magnitudes from field structure
        mags = [get_mag(v) for v in field.values()]
                   
        peak_res = max(mags) if mags else 0
        self_res = get_mag(field.get("SELF", 0))
        
        # Heuristic importance score
        # Peaks when resonance is high and self-awareness is active (but not collapsed)
        score = (peak_res * 0.6) + (4.0 * self_res * (1.0 - self_res) * 0.4)
        
        return float(score)

if __name__ == "__main__":
    scout = CausalScout()
    # Test stub
    test_field = {"SELF": 0.5, "EXISTENCE": 0.8}
    print(f"Test Score (Neural): {scout.evaluate_structural_importance(test_field):.4f}")
    test_field_dict = {"SELF": {"magnitude": 0.5}, "EXISTENCE": {"magnitude": 0.8}}
    print(f"Test Score (Interference): {scout.evaluate_structural_importance(test_field_dict):.4f}")
