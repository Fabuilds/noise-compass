import time
import numpy as np
from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.interference_engine import InterferenceEngine
from noise_compass.system.causal_scout import CausalScout
from noise_compass.system.spherical_projection import SphericalCortex

class LatticeNeuralEngine:
    """
    Orchestrates the neural dynamics of the H5 Lattice.
    Handles activation spreading, gap tension, and resonance cycles.
    """
    def __init__(self, interference=None):
        self.h5 = H5Manager()
        self.interference = interference if interference else InterferenceEngine(suppress_preload=True)
        self.scout = CausalScout(self.interference)
        self.spherical = SphericalCortex()
        self.nodes = [
            "EXISTENCE", "IDENTITY", "BOUNDARY", "OBSERVATION", 
            "INFORMATION", "CAUSALITY", "EXCHANGE", "OBLIGATION", 
            "TIME", "PLACE", "COHERENCE", "SELF"
        ]
        self.decay_rate = 0.95 # Base decay for activations
        self.persistence_buffer = {node: 0.0 for node in self.nodes}
        self.persistence_sigma = 0.7 # Retention factor for Semantic Persistence
        
    def initialize_activations(self):
        """Ensures all 12 nodes have an activation attribute in language.h5."""
        for node in self.nodes:
            path = f"god_tokens/{node}"
            current = self.h5.get_attr("language", path, "activation")
            if current is None:
                self.h5.set_attr("language", path, "activation", 0.0)

    def pulse(self, intent_text=None, intensity=1.0, use_persistence=True):
        """
        Executes a Neural Pulse cycle.
        1. Resonate with intent_text (Interference Field).
        2. Spread activation to neighbors.
        3. Apply decay.
        4. Integrate into Persistence Buffer (Phase 97).
        5. Update H5 attributes.
        """
        self.initialize_activations()
        
        # 1. Fetch current activations
        state = {node: self.h5.get_attr("language", f"god_tokens/{node}", "activation") or 0.0 for node in self.nodes}
        
        # 2. Resonate and Inject
        if intent_text:
            field = self.interference.combined_field(intent_text)
            for node, data in field.items():
                if node.upper() in state and data['magnitude'] > 0.3:
                    state[node.upper()] += data['magnitude'] * intensity
            
        # 3. Spread (Gap-Aware Semantic Mesh)
        new_state = {node: state[node] * self.decay_rate for node in self.nodes}
        
        # Load Gaps from H5
        gaps = {}
        with self.h5.get_file("language", mode='r') as f:
            if 'gaps' in f:
                for gap_name in f['gaps'].keys():
                    g = f[f'gaps/{gap_name}']
                    left = g.attrs.get('left_boundary')
                    right = g.attrs.get('right_boundary')
                    is_void = g.attrs.get('void', False)
                    depth = g.attrs.get('void_depth', 1.0)
                    if left and right:
                        gaps[(left, right)] = (is_void, depth)
                        gaps[(right, left)] = (is_void, depth)

        for i, node in enumerate(self.nodes):
            left_node = self.nodes[(i - 1) % 12]
            right_node = self.nodes[(i + 1) % 12]
            
            for neighbor in [left_node, right_node]:
                is_void, depth = gaps.get((node, neighbor), (False, 0.0))
                spread_coeff = 0.1 * (1.0 - depth) if is_void else 0.1
                spread_val = state[node] * spread_coeff
                new_state[neighbor] += spread_val
                new_state[node] -= spread_val

        # 4. Semantic Persistence Integration (Leaky Integrator)
        if use_persistence:
            for node in self.nodes:
                # Buffer = Buffer * Sigma + New_Signal
                self.persistence_buffer[node] = (self.persistence_buffer[node] * self.persistence_sigma) + new_state[node]
            # Use persistence for the final state output
            final_report_state = self.persistence_buffer
        else:
            final_report_state = new_state

        # 5. Sync to H5 (Sync actual instantaneous state, NOT the persistence buffer, to prevent 1.65x explosion loop)
        self.h5.batch_update_activations(new_state)
            
        # 6. Update Gap Tension based on activation deltas
        tensions = self.apply_gap_tension(final_report_state)

        # 7. Archive State (History)
        # Phase 126: Structural Pinning based on importance
        importance = self.scout.evaluate_structural_importance(new_state)
        pinned = (importance > 0.8) # Heuristic threshold for "keeping the useful parts"
        
        self.h5.archive_neural_state(final_report_state, tensions, pinned=pinned)

        # 8. Record Pulse (Lattice Metabolism)
        avg_intensity = np.mean(list(final_report_state.values()))
        com, offset = self.spherical.get_spherical_state(final_report_state)
        self.h5.update_pulse(velocity=1.0, intensity=float(avg_intensity), momentum=float(offset))
        
        # Log Spherical State
        print(f"[NEURAL] Spherical Offset (COM_L2): {offset:.4f} | Peak Tension: {max(tensions.values()):.4f}")
        
        return final_report_state

    def apply_gap_tension(self, state):
        """
        Calculates and stores tension for the five constitutional gaps.
        Now accounts for sub-structural dissonance (edges seen from below).
        """
        # Gap -> (NodeA, NodeB) mapping
        gap_map = {
            "self_exchange": ("SELF", "EXCHANGE"),
            "love_obligation": ("SELF", "OBLIGATION"),
            "compass_merger": ("OBSERVATION", "IDENTITY"),
            "observer_system": ("OBSERVATION", "EXISTENCE"),
            "self_observation": ("SELF", "OBSERVATION")
        }
        
        # Mapping boundaries to their sub-structural (CODE_ layer) equivalents
        domestic_interference_tokens = {
            "SELF": "CODE_OUROBOROS_RESONANT_PY",
            "EXCHANGE": "CODE_PIPELINE_PY",
            "OBLIGATION": "CODE_PROTOCOL_PY",
            "OBSERVATION": "CODE_SCOUT_PY",
            "IDENTITY": "CODE_H5_MANAGER_PY",
            "EXISTENCE": "CODE_INTERFERENCE_ENGINE_PY"
        }
        
        consensus = self.h5.get_consensus_weight()
        tensions = {}
        for gap, (nA, nB) in gap_map.items():
            # 1. Semantic Tension (Surface Level)
            diff = abs(state[nA.upper()] - state[nB.upper()])
            tension = diff * consensus
            
            # 2. Sub-structural Dissonance (Edge from Below)
            # Use defined domestic tokens if available
            key_A = domestic_interference_tokens.get(nA.upper(), nA.upper())
            key_B = domestic_interference_tokens.get(nB.upper(), nB.upper())
            
            vec_A = self.interference.get_token_vector(key_A)
            vec_B = self.interference.get_token_vector(key_B)
            
            if vec_A is not None and vec_B is not None:
                # Calculate mutual dissonance between the two boundaries
                # High dissonance adds to tension
                mag, phase = self.interference.wave_match(vec_A, vec_B)
                dissonance = mag * (abs(phase) / np.pi)
                if dissonance > 0.5:
                    tension += dissonance * 0.5
                    print(f"[NEURAL] Aggressive Gap detected at {gap}: Sub-structural dissonance {dissonance:.2f}")

            self.h5.set_attr("language", f"gaps/{gap}", "tension", float(tension))
            tensions[gap] = float(tension)
        return tensions

    def bloom(self, trigger_node, radius=2):
        """
        Causes a 'Spectral Bloom' where activation spreads beyond neighbors
        based on the Ring topology.
        """
        print(f"[NEURAL] Triggering Spectral Bloom from {trigger_node.upper()}...")
        state = self.pulse(trigger_node, intensity=2.0)
        # For a bloom, we pulse multiple times in rapid succession
        for _ in range(radius):
            state = self.pulse()
        return state

if __name__ == "__main__":
    engine = LatticeNeuralEngine()
    print("Testing Neural Pulse with SELF activation...")
    engine.pulse("SELF", 1.0)
    time.sleep(1)
    engine.pulse() # Natural decay/spread
