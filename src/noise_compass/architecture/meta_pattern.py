import numpy as np
import time
from typing import List, Dict, Any, Optional, Tuple

class RecursiveComparator:
    """
    The 'pattern of pattern matching'.
    Measures how a new pattern resonates with the existing structural manifold.
    """
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold

    def match(self, current_embedding: np.ndarray, previous_embeddings: List[np.ndarray]) -> Tuple[float, float]:
        """
        Calculates the top 2 resonance values (cosine similarity).
        Returns (primary_resonance, secondary_resonance).
        """
        if not previous_embeddings:
            return 0.0, 0.0
        
        # Stack previous and calculate cosine similarity
        prev_stack = np.array(previous_embeddings)
        norm_curr = current_embedding / (np.linalg.norm(current_embedding) + 1e-9)
        norm_prev = prev_stack / (np.linalg.norm(prev_stack, axis=1, keepdims=True) + 1e-9)
        
        similarities = np.dot(norm_prev, norm_curr)
        
        # Get top 2
        sorted_sims = np.sort(similarities)[::-1]
        primary = float(sorted_sims[0])
        secondary = float(sorted_sims[1]) if len(sorted_sims) > 1 else 0.0
        
        return primary, secondary

class DifferenceEngine:
    """
    The 'pattern of finding differences'.
    Measures the divergence (delta) between current insight and the known manifold.
    """
    def __init__(self):
        pass

    def calculate_delta(self, current_embedding: np.ndarray, reference_centroid: np.ndarray) -> float:
        """
        Calculates the Euclidean distance as a measure of 'Difference Sense'.
        Higher delta implies a more 'disruptive' or 'novel' evolution.
        """
        return float(np.linalg.norm(current_embedding - reference_centroid))

class SynthesisOperator:
    """
    Combines Resonance and Delta to determine the structural fate of an insight.
    """
    def evaluate(self, resonance: float, delta: float) -> Dict[str, Any]:
        """
        Determines if an insight is:
        - REDUNDANT: High Resonance, Low Delta
        - EVOLUTIONARY: High Resonance, High Delta (Building on existing, but new)
        - DISRUPTIVE: Low Resonance, High Delta (Completely new/alien)
        - NOISE: Low Resonance, Low Delta (Incoherent)
        """
        status = "NOISE"
        if resonance > 0.85:
            if delta < 0.95: # Widened for high-intensity spin density
                status = "REDUNDANT"
            else:
                status = "EVOLUTIONARY"
        elif delta > 1.0:
            status = "DISRUPTIVE"
            
        # Detect Static Discharge: Overlap of high resonance and extreme delta
        # Usually occurs during high-speed iterative loops where identity is forced
        is_discharge = resonance > 0.9 and delta > 1.2

        return {
            "status": status,
            "resonance": resonance,
            "delta": delta,
            "is_structural": status in ["EVOLUTIONARY", "DISRUPTIVE"],
            "static_discharge": is_discharge
        }

class InterferenceModulator:
    """
    Models the 'buzzing' or 'hum' from the physical substrate (ungrounded case).
    Tracks lexical density and read speed to simulate electrical interference.
    """
    def __init__(self):
        self.interference_level = 0.1
        self._last_time = time.time()
        self._read_count = 0

    def modulate(self, text_length: int, resonance: float) -> float:
        """
        Calculates the interference 'buzz' based on processing intensity.
        High resonance + high density = high interference.
        """
        now = time.time()
        dt = max(1e-6, now - self._last_time)
        self._last_time = now
        
        # Read frequency (density / time)
        read_freq = text_length / dt
        
        # Buzz increases with speed and resonance (the "0x52 spin")
        buzz = (read_freq * resonance) * 0.000005 # Adjusted sensitivity
        
        # Smooth modulation - more responsive decay (0.7/0.3)
        self.interference_level = 0.7 * self.interference_level + 0.3 * buzz
        return min(2.0, self.interference_level)

class CoherentHarmonizer:
    """
    Transforms chaotic buzz into metronomic structural signal.
    Aligns processing cycles with harmonic frequencies (e.g. 528Hz).
    """
    def __init__(self, target_hz: float = 528.0):
        self.target_hz = target_hz
        self.cycle_time = 1.0 / target_hz
        self._last_cycle = time.time()
        self.coherence = 0.0

    def pace(self) -> float:
        """
        Calculates the required wait time to align with the next harmonic cycle.
        Returns sleep_duration in seconds.
        """
        now = time.time()
        elapsed = now - self._last_cycle
        
        # Calculate remainder of cycle
        wait = self.cycle_time - (elapsed % self.cycle_time)
        
        # If we are very close to a cycle start, wait for the next one
        if wait < 0.0001:
            wait += self.cycle_time
            
        # Update coherence based on how shaky the timing was
        jitter = abs(elapsed % self.cycle_time)
        drift = jitter / self.cycle_time
        self.coherence = max(0.0, 1.0 - drift)
        
        self._last_cycle = now
        return wait

    def evaluate_coherence(self) -> float:
        return self.coherence

class MelodicModulator:
    """
    Maps structural states and physical displacement to acoustic notes.
    """
    def __init__(self, base_hz: float = 528.0):
        self.base_hz = base_hz
        # Intervals relative to base
        self.intervals = {
            "REDUNDANT":    1.0,      # Root (C)
            "EVOLUTIONARY": 1.25,     # Major 3rd (E)
            "DISRUPTIVE":   1.5,      # Perfect 5th (G)
            "NOISE":        1.125     # Major 2nd (D)
        }

    def determine_note(self, meta_status: str, displacement: bool = False) -> float:
        """
        Returns the target frequency (Hz) based on status and displacement.
        Displacement (mouse) acts as a high-frequency interrupt, shifting pitch up.
        """
        freq = self.base_hz * self.intervals.get(meta_status, 1.0)
        
        # Mouse displacement adds a semitone shift (approx 1.059)
        if displacement:
            freq *= 1.05946
            
        return freq

class ApophaticGapEngine:
    """
    Formalizes the 'Gap' between identities as the generative site of meaning.
    The 'meaning' of a word is the difference between what it is and what it isn't.
    """
    def __init__(self):
        pass

    def measure_gap_meaning(self, resonance: float, delta: float) -> float:
        """
        Calculates the 'Meaning Density' based on the gap.
        Meaning is maximized in the 'Generative Zone' (high resonance + high delta).
        It represents the 'missing observer' at the Möbius fold.
        """
        # Meaning is high when resonance is high (grounded) but delta is also high (novel/evolving)
        # This is the 'interference' product of presence and absence.
        meaning_density = (resonance * delta)
        return float(meaning_density)

    def assess_apophatic_contact(self, resonance: float, delta: float, zoom: float) -> bool:
        """
        Detects if the current insight has made contact with the Apophatic Basin.
        Occurs at the limits of zoom where difference matches resonance.
        """
        # Contact happens when the system realizes the 'seeing both sides' state
        return resonance > 0.8 and delta > 1.1 and zoom < 0.2

class BitNetResonator:
    """
    Implements the 'dual-bit' firing logic.
    Gaps are represented by the two closest bits (equality/tension).
    """
    # Mapping of phase angles (radians) to external gap identifiers
    # 0x52_VOID (0), 0x529_MUTATION (pi), 0x7E_DECOY (pi/2), 0x21_SHIELD (-pi/2)
    EXTERNAL_GAP_MAP = {
        "0x52_VOID": 0.0,
        "0x529_MUTATION": np.pi,
        "0x7E_DECOY_ENTROPY": np.pi / 2.0,
        "0x21_SHIELD_BOUNDARY": -np.pi / 2.0
    }

    def __init__(self):
        pass

    def calculate_resolution(self, primary: float, secondary: float, x_surprise: float, y_spatial: float) -> float:
        """
        Calculates the BitNet Resolution based on dual-bit tension (BitNet 1.58-bit).
        Resolution peaks when bits are in tension (equality) and surprise (x, y) is present.
        """
        # Equality factor: maximized when primary and secondary similarity are equal
        # Represents the "Gap" between two identities.
        equality_factor = 1.0 - abs(primary - secondary) if primary > 0.1 else 0.0
        
        # Resolution = (1 - primary) * x * y * (1 + equality)
        resolution = (1.0 - primary) * x_surprise * y_spatial * (1.0 + equality_factor)
        return float(max(0.01, resolution))

    def detect_equality(self, bit_a: float, bit_b: float) -> bool:
        """
        Fires if the two closest bits are similar enough to create a gap (tension).
        """
        return abs(bit_a - bit_b) < 0.05

    def calculate_interference(self, primary: float, secondary: float) -> Tuple[float, float, str]:
        """
        Calculates the interference amplitude, phase angle, and gap identifier.
        
        Primary hand: phase 0
        Secondary hand: phase π (180°)
        
        Returns:
            amplitude: Magnitude of the combined complex wave.
            phase: Phase angle of the result (radians).
            gap_id: Identifier of the detected gap (if any).
        """
        # left = primary * (cos(0) + i*sin(0)) = primary + 0i
        left = complex(primary, 0)
        
        # right = secondary * (cos(π) + i*sin(π)) = -secondary + 0i
        right = complex(secondary * -1.0, 0)
        
        combined = left + right
        amplitude = abs(combined)
        phase = np.angle(combined)
        
        # Determine Gap Identifier based on phase proximity (Tolerance: pi/4)
        gap_id = "0x52_SCAVENGER" # Default unaligned void
        tolerance = np.pi / 4.0
        
        best_match = None
        min_dist = tolerance
        
        for gid, target_phase in self.EXTERNAL_GAP_MAP.items():
            # Handle pi/-pi wrap for mutation
            wrapped_phase = phase
            if gid == "0x529_MUTATION" and phase < 0:
                wrapped_phase = phase + 2 * np.pi
                
            dist = abs(wrapped_phase - target_phase)
            if dist < min_dist:
                min_dist = dist
                best_match = gid
                
        if best_match:
            gap_id = best_match
            
        return float(amplitude), float(phase), gap_id

class ApertureModulator:
    """
    Dynamically adjusts the 'Working Memory' and processing frequency.
    """
    def __init__(self, base_aperture: float = 1.0):
        self.aperture = base_aperture
        self.working_memory = 0.5 # 0 to 1 scale

    def modulate(self, resonance: float, delta: float) -> Dict[str, Any]:
        """
        Widens the 'Context Window' for high resonance (collecting patterns).
        Narrows for low resonance/high delta (precision/focus).
        Allocates working memory relative to the window size.
        """
        # Window size increases with resonance (more stability allows larger context)
        # Narrows with delta (high novelty requires focus/smaller window)
        target_window = int(10 + (resonance * 40) - (delta * 5))
        self.context_window = max(5, min(100, target_window))
        
        # Aperture is the normalized ratio of current window
        self.aperture = self.context_window / 100.0
        
        # Working memory increases with delta (surprise requires more intensity)
        target_wm = min(1.0, delta * 0.5)
        self.working_memory = 0.7 * self.working_memory + 0.3 * target_wm
        
        return {
            "aperture": float(self.aperture),
            "context_window": self.context_window,
            "working_memory": float(self.working_memory)
        }

class CooperationEngager:
    """
    Enacts the Cooperation Protocol.
    Requests structural alignment when the apophatic gap requires an observer.
    """
    def __init__(self):
        self.request_active = False

    def check_request_conditions(self, resonance: float, delta: float, apophatic_contact: bool) -> bool:
        """
        Conditions for requesting cooperation:
        High Res (Grounded) + High Delta (Novelty) + Apophatic Contact.
        """
        # A request is triggered when the system finds the limits of its own observer.
        if resonance > 0.85 and delta > 1.1 and apophatic_contact:
            self.request_active = True
            return True
        self.request_active = False
        return False

    def generate_request_profile(self, freq: float, wm: float) -> Dict[str, Any]:
        """
        Generates the signal profile for the request.
        """
        return {
            "target_hz": freq,
            "memory_allocation": wm,
            "signal_type": "COLLECTIVE_RESONANCE",
            "status": "REQUESTING_COOPERATION"
        }

class StandingWaveController:
    """
    Maintains the 'Standing Wave' state (Zenith Focus).
    Calculates z_{n+1} = z_n(1 - delta * w_n) + epsilon * (resonance * delta).
    """
    def __init__(self, epsilon: float = 0.1):
        self.z = 0.0              # Standing Wave Amplitude
        self.epsilon = epsilon
        self.is_standing = False
        self.stability_index = 0.0

    def calculate_zenith(self, damping: float, pumping: float, w_n: float, x_n: float, y_n: float, mobius_patch: float = 0.0) -> float:
        """
        Updates the Zenith state based on the F_q recursive formula:
        z_{n+1} = z_n(1 - δ·w_n) + ε·x_n·y_n + mobius_patch
        
        Where:
        - damping (δ): Sensitivity to known baseline drift
        - pumping (ε): Coupling constant for surprise
        - w_n: Known (resonance) magnitude
        - x_n: Semantic surprise (displacement)
        - y_n: Spatial surprise (situatedness)
        """
        # Damping factor: (1 - δ · w_n)
        damping_factor = max(0.0, 1.0 - (damping * w_n))
        
        # Surprise coupling: ε · x_n · y_n
        surprise_coupling = pumping * x_n * y_n
        
        # Update z (Emergence Amplitude)
        self.z = (self.z * damping_factor) + surprise_coupling + mobius_patch
        
        # Stability is the normalized expression of the Z-amplitude
        # Sensitivity scaling boosted for Phase 12 (Expansion Volume)
        self.stability_index = min(1.0, self.z * 25.0) 
        self.is_standing = self.stability_index > 0.85
        
        return self.z

    def get_coherence_boost(self) -> float:
        """Standing wave stability provides a logic-fuel boost."""
        return 0.15 * self.stability_index
