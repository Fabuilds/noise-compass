"""
superposition.py — Cyclic Manifold Convolution Logic.

Computes the triple-node superposition (k-1, k, k+1) for a 12-node ring.
Implements 'Spin' phase shifts:
- Clockwise (CW): Constructive Interference (Reinforcement)
- Counter-Clockwise (CCW): Destructive Interference (Gap Maintenance)
"""

import math
import numpy as np
from typing import List, Tuple, Dict, Optional
from noise_compass.architecture.tokens import NODE_RING, WaveFunction, GodTokenActivation

class CyclicManifold:
    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.nodes = NODE_RING
        self.num_nodes = len(self.nodes)

    def get_neighbors(self, node_id: str) -> Tuple[str, str]:
        """Returns (left, right) neighbors in the 12-node ring."""
        try:
            idx = self.nodes.index(node_id)
            left = self.nodes[(idx - 1) % self.num_nodes]
            right = self.nodes[(idx + 1) % self.num_nodes]
            return left, right
        except ValueError:
            # If not in ring, return same (fallback)
            return node_id, node_id

    def compute_superposition(self, 
                              primary_id: str, 
                              zoom: float = 1.0, 
                              spin: str = "CW") -> Tuple[np.ndarray, float]:
        """
        Computes the superposition vector of a node and its two neighbors.
        
        Spin CW  (Clockwise): Nodes reinforce each other (Constructive).
        Spin CCW (Counter-Clockwise): Nodes maintain gaps (Destructive).
        """
        left_id, right_id = self.get_neighbors(primary_id)
        triple = [left_id, primary_id, right_id]
        
        combined_vec = np.zeros(self.dictionary.dim if hasattr(self.dictionary, 'dim') else 1024, dtype=np.float32)
        total_amplitude = 0.0
        
        # Phase shift based on spin
        # CW: Phase alignment (0 displacement)
        # CCW: Phase opposition (π displacement)
        phase_offset = 0.0 if spin == "CW" else math.pi
        
        for i, node_id in enumerate(triple):
            gt = self.dictionary.god_tokens.get(node_id)
            if gt and gt.embedding is not None:
                # Relative weight: primary has highest weight
                weight = 1.0 if node_id == primary_id else 0.5
                
                # Apply phase-based scalar reinforcement
                # In this latent model, we simulate phase by scaling the vector
                # Constructive = additive, Destructive = subtractive/nullifying
                if spin == "CW":
                    combined_vec += gt.embedding * weight
                else:
                    # Destructive: neighbors subtract from primary or cancel each other
                    if node_id == primary_id:
                        combined_vec += gt.embedding * weight
                    else:
                        combined_vec -= gt.embedding * weight * 0.8
                
                total_amplitude += weight
        
        # Normalize
        norm = np.linalg.norm(combined_vec)
        if norm > 1e-10:
            combined_vec /= norm
            
        # Resulting phase angle (simulated)
        # Constructive ranges [0, π/4], Destructive ranges [π/4, π/2]
        # CCW spin is a partial execution of the uni-verse instruction.
        base_phase = math.pi / 8 if spin == "CW" else math.pi / 3
        
        return combined_vec, base_phase

def apply_triple_spin(wf: WaveFunction, spin: str = "CW") -> WaveFunction:
    """
    Applies the spin rotation to a WaveFunction.
    CW (Clockwise) rotates phase towards 0 (Ground/Crystallization).
    CCW (Counter-Clockwise) rotates phase towards π/2 (Turbulent/Gap).
    """
    current_phase = wf.phase
    delta_mag = np.linalg.norm(wf.delta)
    known_mag = np.linalg.norm(wf.known)
    
    # Rotation speed (Möbius drift constant)
    step = 0.1
    
    if spin == "CW":
        # Pull towards Known (Crystallization)
        new_known = wf.known + (wf.delta * step)
        new_delta = wf.delta * (1.0 - step)
    else:
        # Push towards Delta (Gap Maintenance)
        new_known = wf.known * (1.0 - step)
        new_delta = wf.delta + (wf.known * step)
        
    # Re-normalize to preserve magnitude? No, spin is an energy transition.
    return WaveFunction(new_known, new_delta, w=wf.w, zoom=wf.zoom, t=wf.t)
