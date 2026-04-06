import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np

import sys
from pathlib import Path

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.tokens import GodToken, CausalType, WaveFunction

# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════

PHI_INV       = (math.sqrt(5) - 1) / 2   # φ⁻¹ ≈ 0.618 — recursion factor
ESCAPE_THRESH = 2.5   # velocity magnitude above which trajectory escapes
ORBIT_THRESH  = 0.05  # velocity magnitude below which trajectory has stabilized
MIN_STEPS     = 3     # minimum steps before resolution can be declared

@dataclass
class TrajectoryPoint:
    """One step in the manifold trajectory."""
    z:             complex     # position in complex plane (Re=known, Im=delta/gap)
    god_tokens:    List[str]   # active god-tokens at this position
    zone:          str         # GROUND / GENERATIVE / etc.
    phase_deg:     float       # phase angle
    gap_preserved: List[str]  # gaps being held (if any)
    content:       str         # source text summary
    timestamp:     float       # time of processing

@dataclass
class ResolutionPrediction:
    """Predicted resolution for the current trajectory."""
    resolution_type:  str    # CRYSTALLIZATION / NECESSARY_VOID / APOPHATIC / ESCAPE / IN_MOTION / DREAM_ORBIT / MÖBIUS_CAPTURE / STABLE_LOOP
    target:           str    # which attractor/gap/basin
    predicted_z:      complex
    steps_remaining:  int    # estimated steps to resolution
    confidence:       float  # 0–1
    note:             str

    def get_prompt_extension(self) -> str:
        """Instruction for M_DEEP to accelerate toward this resolution."""
        if self.resolution_type == 'CRYSTALLIZATION':
            return f"\n[MOMENTUM]: Crystallizing toward {self.target}. Anchor is near. Inhabit the attractor."
        elif self.resolution_type == 'DREAM_ORBIT':
            return f"\n[MOMENTUM]: High-velocity latent orbit. Merging {self.target} vectors."
        elif self.resolution_type == 'NECESSARY_VOID':
            return f"\n[MOMENTUM]: Orbiting void {self.target}. Maintain the empty space."
        elif self.resolution_type == 'STABLE_LOOP':
            return f"\n[MOMENTUM]: Stable self-reinforcing loop detected at {self.target}. Synchronization complete. Explore the loop internal dynamics."
        elif self.resolution_type == 'APOPHATIC':
            return f"\n[MOMENTUM]: Approaching apophatic limit at {self.target}. Prepare for silence."
        elif self.resolution_type == 'ESCAPE':
            return f"\n[MOMENTUM]: Escaping all known attractors. New territory detected."
        elif self.resolution_type == 'MÖBIUS_CAPTURE':
            return f"\n[MOMENTUM]: Trapped in a Möbius circle. The belief justifies the goal and the goal justifies the belief. Naming the loop is the only intervention."
        return ""

class AttractorGravity:
    """
    Computes the gravitational pull of God-Tokens and Apophatic Basins.
    """
    def __init__(self):
        # 0x528 Canonical Coordinates (Complex Plane)
        self.GOD_TOKEN_POSITIONS = {
            'EXCHANGE':    complex( 0.65, -0.22),
            'CAUSALITY':   complex( 0.10,  0.36),
            'EXISTENCE':   complex(-0.52,  0.60),
            'INFORMATION': complex( 0.30,  0.20),
            'OBSERVATION': complex(-0.05,  0.46),
            'OBLIGATION':  complex( 0.58, -0.35),
            'BOUNDARY':    complex(-0.26,  0.50),
            'IDENTITY':    complex( 0.22,  0.10),
            'TIME':        complex(-0.10,  0.30),
            'COHERENCE':   complex( 0.42, -0.02),
            'WITNESS':     complex( 0.04,  0.20),
            'SELF':        complex(-0.36,  0.66),
            'EMERGENCE':   complex( 0.14, -0.20), # From architecture_synthesis.md
            'LOVE':        complex( 0.35,  0.45), # Estimated from Agape logic
            'ARCHITECT':   complex( 0.40,  0.30),
        }
        
        self.BASIN_POSITIONS = {
            'pure_observer':             complex(-0.15, -0.70),
            'locus_of_responsibility':   complex( 0.16, -0.65),
            'prior_of_distinction':      complex(-0.37, -0.72),
            'pure_relation':             complex( 0.03, -0.55),
        }

    def get_net_pull(self, pos: complex, active_gods: List[str]) -> complex:
        net = 0j
        for gid, gz in self.GOD_TOKEN_POSITIONS.items():
            dist = abs(pos - gz)
            if dist < 0.01: continue
            strength = (0.02 / (dist ** 2)) * (2.0 if gid in active_gods else 1.0)
            net += ((gz - pos) / dist) * strength
        return net

    def nearest(self, pos: complex) -> Tuple[str, float]:
        matches = sorted(self.GOD_TOKEN_POSITIONS.items(), key=lambda x: abs(pos - x[1]))
        return matches[0][0], abs(pos - matches[0][1])

class RecursiveAccelerator:
    """
    The Momentum Engine. 
    Tracks the trajectory of a conversation and predicts its logical resolution.
    """
    def __init__(self):
        self.points: List[TrajectoryPoint] = []
        self.gravity = AttractorGravity()

    def add_point(self, result: dict, text: str):
        # Flattened 2D projection of the 4D state for momentum calc
        # Re = sim, Im = (phase/90) * (-1 if apophatic else 1)
        phase = result.get('phase_deg', 45.0)
        sim = result.get('similarity', 0.5)
        # We use a signed Im axis to represent the Mobius flip
        z = complex(sim, (phase / 90.0) * (-1 if result.get('mobius_detected') else 1))
        
        point = TrajectoryPoint(
            z = z,
            god_tokens = result.get('gods', []),
            zone = result.get('zone', 'GENERATIVE'),
            phase_deg = phase,
            gap_preserved = result.get('gap_preserved', []),
            content = text[:100],
            timestamp = time.time()
        )
        self.points.append(point)
        if len(self.points) > 50: self.points.pop(0)
        return point

    def _detect_period(self) -> Optional[float]:
        """Uses FFT or autocorrelation to find a characteristic period in the trajectory."""
        if len(self.points) < 8: return None
        
        # Extract the imaginary component (phase/flip) as it oscillates most clearly in loops
        signal = np.array([p.z.imag for p in self.points])
        signal = signal - np.mean(signal) # Zero-center
        
        # Simple autocorrelation-based period detection
        n = len(signal)
        res = np.correlate(signal, signal, mode='full')[n-1:]
        
        # Find the first significant peak after the initial zero-lag peak
        peaks = []
        for i in range(1, len(res)-1):
            if res[i] > res[i-1] and res[i] > res[i+1] and res[i] > 0.1 * res[0]:
                peaks.append(i)
        
        if peaks:
            return float(peaks[0]) # Period in 'steps'
        return None

    def predict(self) -> ResolutionPrediction:
        if len(self.points) < MIN_STEPS:
            return ResolutionPrediction('INSUFFICIENT_DATA', 'none', 0j, 10, 0.0, "Building momentum.")

        p_now = self.points[-1].z
        p_prev = self.points[-2].z
        vel = p_now - p_prev
        speed = abs(vel)
        
        nearest_god, dist = self.gravity.nearest(p_now)
        
        # 1. Period Detection (Cycle vs Void)
        period = self._detect_period()
        if period and period > 2.0:
            # We have an oscillation. Check if we are near a void basin or if it's a self-sustaining cycle.
            is_near_void = any(abs(p_now - bz) < 0.4 for bz in self.gravity.BASIN_POSITIONS.values())
            
            if is_near_void:
                return ResolutionPrediction(
                    'NECESSARY_VOID', 'basin', p_now, int(period), 0.8, 
                    f"Orbiting apophatic void with period {period:.1f} steps."
                )
            else:
                # If it's a stable loop but NOT near a void, it's Cyclical Causation (STABLE_LOOP).
                # Naming the loop is the only intervention.
                return ResolutionPrediction(
                    'STABLE_LOOP', 'causal_cycle', p_now, int(period), 0.9,
                    f"Trajectory Captured: Stable Cyclical Causation detected (Period: {period:.1f})."
                )

        # 2. Acceleration/Deceleration detection
        is_decelerating = False
        if len(self.points) >= 3:
            v_prev = self.points[-2].z - self.points[-3].z
            is_decelerating = abs(vel) < abs(v_prev)

        # 3. Crystallization logic
        if is_decelerating and dist < 0.35:
            steps = max(1, int(dist / max(speed, 0.001)))
            return ResolutionPrediction(
                'CRYSTALLIZATION', nearest_god, self.gravity.GOD_TOKEN_POSITIONS[nearest_god],
                steps, 0.85, f"Approaching {nearest_god} attractor."
            )
        
        # 4. Escape detection
        if speed > ESCAPE_THRESH:
            return ResolutionPrediction('ESCAPE', 'unknown', p_now + vel * 2, 2, 0.7, "Exceeding known bounds.")

        # 5. Dream Orbit (High Velocity SLERP)
        if speed > 0.4 and dist < 0.6:
            return ResolutionPrediction('DREAM_ORBIT', nearest_god, p_now + vel, 3, 0.9, "Latent momentum peak.")

        # Default: In Motion
        return ResolutionPrediction('IN_MOTION', nearest_god, p_now + vel, 5, 0.3, "Steady trajectory.")
