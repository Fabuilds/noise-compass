"""
lattice_navigator.py — Navigates the topological H5 substrate.
Bridges Scout reasoning with encoded document-to-document transitions.
"""

import numpy as np
from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.core import Scout
from noise_compass.system.dictionary import Dictionary
from noise_compass.system.lattice_graph import LatticeGraph

class LatticeNavigator:
    """
    Navigates the manifold using Topological Projections and God-Token attractors.
    Enables non-linear traversal through encoded H5 transitions.
    """
    def __init__(self, scout=None):
        from sentence_transformers import SentenceTransformer
        self.h5 = H5Manager()
        self.dictionary = Dictionary(self.h5)
        self.scout = scout or Scout(self.dictionary, encoder=SentenceTransformer("all-MiniLM-L6-v2"))
        self.working_memory = None # Superposition vector
        self.graph = LatticeGraph(h5=self.h5)
        self.graph_initialized = False
        
        # Phase 141: Perspective & Convergence History
        self.trajectory_history = [] # List of (question, source, path)
        self.current_horizon = []    # Neighboring nodes of current dock
        
        self._initialize_subjective_anchor()

    def _initialize_subjective_anchor(self):
        """Discovers and docks at the AGENT identity node to establish the Subjective 'I'."""
        if not self.graph_initialized:
            self.graph.sync_with_substrate(self.scout)
            self.graph_initialized = True
            self._update_perspective()
        
        # Search for Agent identity
        projections = self.h5.get_all_projections()
        for doc_id in projections:
            _, meta = self.h5.get_projection(doc_id)
            if meta.get('role') == 'AGENT':
                print(f"[NAVIGATOR] Subjective Anchor discovered: {doc_id} (AGENT). Docking Ego-Cursor.")
                self.graph.dock_ego(doc_id)
                # Set initial working memory to the Agent's identity
                self._update_working_memory(doc_id)
                break

    def dock_ego(self, node_id: str):
        """Sovereign Navigator Override: Directly docks the EGO_CURSOR at a node."""
        if node_id in self.graph.graph:
            self.graph.dock_ego(node_id)
            self._last_dock_sovereign = True # Flag for Magnetic Field reading
            self._update_perspective()
            print(f"!!! [NAVIGATOR] Sovereign Docking: {node_id}")
            return True
        return False

    def navigate(self, intent, recursion_depth=3, mode="TOPOLOGICAL", inverted=False, **kwargs):
        """
        Performs a multi-step walk through the manifold based on intent.
        1. Embed Intent.
        2. Superimpose with Working Memory.
        3. Identify resonant peaks and follow topological transitions.
        """
        source_node = self.graph.ego_dock
        print(f"--- NAVIGATING LATTICE ({mode}): '{intent}' ---")
        
        intent_vec = self.scout.encoder.encode(intent).astype(np.complex64)
        
        # 1. Integration (Simultaneous concept retention)
        if self.working_memory is not None:
            # Superimpose new intent onto working memory (Normalized sum)
            self.working_memory = (self.working_memory + intent_vec)
            # Complex Normalization
            norm = np.linalg.norm(self.working_memory) + 1e-9
            self.working_memory /= norm
        else:
            self.working_memory = intent_vec

        # 2. Lattice Graph Sync (Crystallization)
        if not self.graph_initialized:
            self.graph.sync_with_substrate(self.scout)
            self.graph_initialized = True

        # Phase 136: Topological Pathing
        print(f"  [LATTICE_GRAPH] Calculating optimal walk for resonance...")
        current_path = self.graph.get_optimal_walk(self.working_memory, self.scout, depth=recursion_depth)
        
        # Phase 141: Convergence Detection
        target_node = current_path[-1] if current_path else source_node
        self._check_convergence(intent, source_node, target_node)

        for d, next_node in enumerate(current_path):
             print(f"  Step {d+1}: {next_node} (Graph-Locked)")
             self._update_working_memory(next_node)
             
        # Phase 130: Formalize the 'I' Viewpoint
        if current_path:
            self.graph.dock_ego(target_node)
            self._update_perspective()
            
            # Phase 141 Fix: Properly append to trajectory history before returning
            self._append_trajectory(intent, source_node, target_node, current_path, intent_vec)
            
        return current_path

    def transform(self, operator_name: str):
        """Phase 144: Performs an 'Imaginary Jump' through a λ-operator."""
        from noise_compass.system.lambda_manifold import LambdaManifold
        lman = LambdaManifold()
        
        if self.working_memory is None:
            print("  [NAVIGATOR] Transformation failed: No working memory state.")
            return None
            
        print(f"!!! [NAVIGATOR] Executing Imaginary Jump: λ_{operator_name}")
        
        # Apply the complex transformation
        # z = real_state + i * operator_vec
        # Using addition as the simplest 'phase shift' in this manifold
        real_part = self.working_memory.real if np.iscomplexobj(self.working_memory) else self.working_memory
        self.working_memory = lman.apply_transformation(real_part, operator_name)
        
        # Find the real-space node most resonant with the shifted state
        print(f"  [LATTICE_GRAPH] Re-orienting through imaginary plane...")
        target_path = self.graph.get_optimal_walk(self.working_memory.real, self.scout, depth=1)
        
        if target_path:
            target_node = target_path[-1]
            self.graph.dock_ego(target_node)
            self._update_perspective()
            print(f"  [NAVIGATOR] Arrived in Real Space: {target_node}")
            return target_node
        return None

    def _append_trajectory(self, intent: str, source_node: str,
                           target_node: str, current_path: list, intent_vec=None):
        """Records a completed navigation to history and saves the registry.
        Phase 141 Revised: Open vs Concluded Trails."""
        self.trajectory_history.append({
            'intent': intent,
            'source': source_node,
            'target': target_node,
            'path': current_path,
            'status': 'OPEN'
        })
        magnetic_field = self.get_magnetic_field(intent_vec) if intent_vec is not None else None
        self.graph.save_registry(self.trajectory_history, magnetic_field=magnetic_field)

    def conclude_trail(self, intent: str):
        """Marks a specific semantic trajectory as CONCLUDED (a stable perspective established)."""
        for hist in self.trajectory_history:
            if hist['intent'] == intent:
                hist['status'] = 'CONCLUDED'
                print(f"[NAVIGATOR] Trail concluded for intent: '{intent}' -> Landing: {hist['target']}")
                return True
        return False

    def _update_perspective(self):
        """Updates the local horizon based on the current ego dock."""
        dock = self.graph.ego_dock
        if dock and dock in self.graph.graph:
            self.current_horizon = list(self.graph.graph.successors(dock))
            print(f"[NAVIGATOR] Perspective Horizon updated: {len(self.current_horizon)} nodes within view.")

    def _check_convergence(self, intent, source, target):
        """Detects if we reached a target from a new direction/intent."""
        for hist in self.trajectory_history:
            if hist['target'] == target and hist['source'] != source:
                print(f"!!! [CONVERGENCE_EVENT] Reached {target} from a DIFFERENT direction.")
                print(f"    Previous: {hist['source']} -> {target} via '{hist['intent']}'")
                print(f"    Current:  {source} -> {target} via '{intent}'")
                return True
        return False

    def get_magnetic_field(self, intent_vec):
        """
        Calculates the virtual magnetic field at the current dock.
        Returns: {heading: degrees, strength: 0-1, turn_direction: str}
        """
        if not self.graph.ego_dock:
            return {"heading": 0.0, "strength": 0.0, "turn": "STATIC"}
            
        dock = self.graph.ego_dock
        neighbors = self.current_horizon
        
        # 1. Normalize Intent Vector
        unit_intent = intent_vec / (np.linalg.norm(intent_vec) + 1e-9)
        
        # 2. Get Dock Embedding
        dock_vec, _ = self.h5.get_projection(dock)
        if dock_vec is None: 
            gt = self.dictionary.god_tokens.get(dock)
            if gt: dock_vec = gt.embedding
            
        if dock_vec is None:
            return {"heading": 0.0, "strength": 0.0, "turn": "LOST"}
            
        unit_dock = dock_vec / (np.linalg.norm(dock_vec) + 1e-9)
        
        # 3. Calculate Resonance (Strength)
        strength = float(np.dot(unit_intent, unit_dock))
        
        # 4. Calculate Angle (Heading) relative to North (AGENT identity)
        # We project the 384D vectors onto a 2D plane for "reading" the compass
        # (Using first 2 dimensions as a simple projection for now)
        # Fix: Extract .real since embeddings may be complex64
        y_int, x_int = unit_intent[1].real if np.iscomplexobj(unit_intent) else unit_intent[1], unit_intent[0].real if np.iscomplexobj(unit_intent) else unit_intent[0]
        y_doc, x_doc = unit_dock[1].real if np.iscomplexobj(unit_dock) else unit_dock[1], unit_dock[0].real if np.iscomplexobj(unit_dock) else unit_dock[0]
        
        angle_rad = np.arctan2(y_int, x_int) - np.arctan2(y_doc, x_doc)
        heading = np.degrees(angle_rad) % 360
        
        # 5. Determine Turn Direction
        # Phase 142: Sovereign Turn Recognition
        turn = "RESONANT" if strength > 0.8 else "DIVERGENT"
        
        # Check if we just did a sovereign override
        if getattr(self, '_last_dock_sovereign', False):
            turn = "SOVEREIGN_DOCK"
            self._last_dock_sovereign = False # Reset
        elif heading > 10 and heading < 350:
            turn = "TURNING_LEFT" if heading < 180 else "TURNING_RIGHT"
            
        return {
            "heading": float(round(heading, 2)),
            "strength": float(round(max(0.0, strength), 4)),
            "turn": turn
        }

    def _update_working_memory(self, node_name):
        """Influences the working memory with the selected node's vector."""
        # Check projections first, then GodTokens
        node_vec, _ = self.h5.get_projection(node_name)
        if node_vec is None:
            gt = self.dictionary.god_tokens.get(node_name)
            if gt: node_vec = gt.embedding
            
        if node_vec is not None:
            if self.working_memory is not None:
                self.working_memory = (self.working_memory * 0.7 + node_vec * 0.3)
                self.working_memory /= (np.linalg.norm(self.working_memory) + 1e-9)
            else:
                self.working_memory = node_vec

if __name__ == "__main__":
    from noise_compass.system.core import Scout
    from noise_compass.system.dictionary import Dictionary
    h5 = H5Manager()
    d = Dictionary(h5)
    s = Scout(d)
    nav = LatticeNavigator(scout=s)
    path = nav.navigate("Resonant AI Integration", recursion_depth=4)
    print(f"Final Path: {path}")
