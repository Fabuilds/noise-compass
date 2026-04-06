import os
import json
import time
import random
from noise_compass.system.knowledge_lattice import KnowledgeLattice

class ChiralEngine:
    def __init__(self, lattice: KnowledgeLattice):
        self.lattice = lattice
        self.sanity_depth = lattice.sanity_depth
        
    def run_model_a(self, seed_node):
        """Model A: Constructive Traversal (Forward)"""
        path = [seed_node]
        current_folder = self.lattice.get_path(seed_node)
        
        self.lattice.record_traversal("A", path, "forward", "start")
        
        # Simulation of traversal logic for Phase 34
        # In a real scenario, this would follow 'paths.json'
        for depth in range(2, self.sanity_depth + 1):
            if self.lattice.is_void(current_folder):
                self.lattice.record_traversal("A", path, "forward", "void")
                return path
            
            # Placeholder for actual semantic adjacency logic
            # For now, it might move to a random connected 'god_token'
            next_nodes = ["EXISTENCE", "IDENTITY", "INFORMATION", "COHERENCE"]
            next_node = random.choice(next_nodes)
            path.append(next_node)
            current_folder = self.lattice.get_path(next_node)
            
            if depth >= self.sanity_depth:
                self.lattice.record_traversal("A", path, "forward", "depth_limit")
                return path
                
        return path

    def run_model_b(self, seed_node):
        """Model B: Reductive Traversal (Backward)"""
        path = [seed_node]
        current_folder = self.lattice.get_path(seed_node)
        
        self.lattice.record_traversal("B", path, "backward", "start")
        
        # Reductive always seeks root (Depth 1)
        for depth in range(self.lattice.get_depth(current_folder), 0, -1):
             if self.lattice.is_void(current_folder):
                self.lattice.record_traversal("B", path, "backward", "void")
                return path
             
             # Placeholder for converge logic
             path.append("SELF") # Reductive anchor
             if depth <= 1:
                 self.lattice.record_traversal("B", path, "backward", "root")
                 return path
                 
        return path

class ApexObserver:
    def __init__(self, lattice: KnowledgeLattice):
        self.lattice = lattice

    def observe(self, model_a_record, model_b_record):
        """
        Apex: Identifies 'The Fold' and computes phase angle.
        """
        path_a = model_a_record["path"]
        path_b = model_b_record["path"]
        
        # Find intersection (The Fold)
        intersection = list(set(path_a) & set(path_b))
        
        # Phase Angle computation (heuristic for Phase 34)
        # 0.0 (Apophatic) to 3.14 (Crystallized)
        if not intersection:
            phase = 0.2 # Near apophatic
        else:
            # More intersection = higher phase
            phase = min(3.14, len(intersection) * 0.5)
            
        verdict = "SUPERPOSITION"
        if phase > 2.5: verdict = "CRYSTALLIZED"
        elif phase < 0.5: verdict = "APOPHATIC"
        
        return {
            "phase_angle": phase,
            "fold_positions": intersection,
            "verdict": verdict
        }
