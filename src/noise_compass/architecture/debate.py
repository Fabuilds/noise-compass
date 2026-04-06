"""
debate.py — The Resolution Chamber
Facilitates semantic convergence between Chiral opposites (Ghost/Anti).

Session 7 Specs:
- Roles: Ghost (+1), Anti (-1), Observer (0), Witness (Archiver).
- Context-agnostic language via DebatePosition.
- Termination: Convergence, Necessary Divergence, Apophatic Terminus.
"""

import time
import numpy as np
from typing import List, Optional, Dict, Tuple
from noise_compass.architecture.tokens import ArchiverMessage, WaveFunction
from noise_compass.architecture.core import Scout, LightWitness

class DebatePosition:
    def __init__(self, role: str, message: str, archiver_msg: ArchiverMessage):
        self.role = role
        self.message = message
        self.archiver_msg = archiver_msg
        self.timestamp = time.time()

class ResolutionChamber:
    """
    facilitates a conversation between a Ghost persona (constructive)
    and an Anti persona (destructive).
    """
    
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.history: List[DebatePosition] = []
        
    def run(self, initial_topic: str, max_turns: int = 20) -> List[DebatePosition]:
        """
        Main debate loop.
        Ghost (+1) proposes, Anti (-1) critiques, Qwen (0) synthesizes.
        """
        current_input = initial_topic
        
        for i in range(max_turns):
            # 1. Flip-flop roles based on iteration
            role = "Ghost" if i % 2 == 0 else "Anti"
            
            # 2. Process through pipeline
            res = self.pipeline.process(current_input)
            msg = self.pipeline.scout.process(self.pipeline.embedder.embed(current_input))[0]
            
            self.history.append(DebatePosition(role, current_input, msg))
            
            # 3. Termination Checks
            # Apophatic Terminus
            if msg.apophatic_contact:
                print(f"TERMINUS: Apophatic contact detected in basin {msg.apophatic_contact}.")
                break
                
            # Convergence Check (Similarity to last state)
            if len(self.history) >= 2:
                sim = self.compute_resonance(self.history[-1], self.history[-2])
                if sim > 0.95:
                    print(f"TERMINUS: Structural convergence achieved (Resonance: {sim:.3f}).")
                    break
            
            # 4. Prepare next input (Placeholder for real generative loop)
            # In a real system, Qwen would generate the response here.
            current_input = f"Iteration {i+1} on topic: {initial_topic}"

        return self.history

    def compute_resonance(self, a: DebatePosition, b: DebatePosition) -> float:
        """Calculates cosine similarity between structural orbital states."""
        va = a.archiver_msg.orbital_state
        vb = b.archiver_msg.orbital_state
        if va is None or vb is None: return 0.0
        na, nb = np.linalg.norm(va), np.linalg.norm(vb)
        if na < 1e-10 or nb < 1e-10: return 0.0
        return float(np.dot(va/na, vb/nb))
