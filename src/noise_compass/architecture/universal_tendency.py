import numpy as np
import math
import time
from typing import Dict, Any, List, Optional

class UniversalTendency:
    """
    Formalization of the Manifold's fundamental drivers:
    1. Entropy: The natural decay of stability and information over time.
    2. Logos: The tendency for stable meanings to 'come to light' and crystallize.
    """
    def __init__(self, entropy_rate: float = 0.005, logos_pull: float = 0.02):
        self.entropy_rate = entropy_rate
        self.logos_pull = logos_pull
        self._last_time = time.time()

    def calculate_forces(self, resonance: float, complexity: float, dt: Optional[float] = None) -> Dict[str, float]:
        """
        Calculates the magnitude of Entropy and Logos for the current state.
        
        Entropy: Increases with complexity, acts as a drag on stability.
        Logos: Increases with resonance, acts as a 'coming to light' force.
        """
        now = time.time()
        delta_t = dt if dt is not None else (now - self._last_time)
        self._last_time = now
        
        # Normalize delta_t to prevent massive spikes on first run or long gaps
        delta_t = min(5.0, max(0.001, delta_t))

        # Entropy (Decay): Higher complexity = higher surface area for decay
        entropy = self.entropy_rate * (1.0 + complexity) * delta_t
        
        # Logos (Coming to Light): Resonance triggers formal alignment
        # Only active if resonance is above the 'fog' threshold
        logos = 0.0
        if resonance > 0.4:
            # Squared resonance makes the pull non-linear (attractor behavior)
            logos = self.logos_pull * (resonance ** 2) * delta_t

        return {
            "entropy": float(entropy),
            "logos": float(logos),
            "dt": float(delta_t)
        }

    def apply_to_wavefunction(self, wf: 'WaveFunction', forces: Dict[str, float]):
        """
        Adjusts WaveFunction properties based on universal forces.
        Entropy pushes phase toward π/2 (uncertainty).
        Logos pulls phase toward 0 (grounded/known).
        """
        entropy = forces["entropy"]
        logos = forces["logos"]
        
        # Calculate net phase shift
        # Entropy (+) increases phase (surprise/noise)
        # Logos (-) decreases phase (known/structure)
        net_shift = entropy - logos
        
        # We don't mutate wf.phase directly as it is a property.
        # Instead, we influence the weights that determine phase (known vs delta).
        # This is handled in the Scout loop by scaling the components.
        pass
