import os
import json
import time
from noise_compass.system.h5_manager import H5Manager

class KnowledgeLattice:
    """
    RLM V2: The File System as Neural Network.
    Axiomatic H5 Stabilization (Phase 36).
    """
    def __init__(self, root_path="E:/Antigravity/knowledge_root"):
        self.root = root_path
        self.sanity_depth = 13 # Fibonacci F7 (User Axiom: Stabilization Threshold)
        self.apophatic_floor = 21 # Fibonacci F8
        self.cyclic_ring_size = 12 # User Axiom: Discretized Möbius traversal
        self.h5 = H5Manager()
        
    def get_path(self, node_name, category="god_tokens"):
        """Returns the absolute path to a node's folder (The Skeleton)."""
        return os.path.join(self.root, category, node_name.upper())

    def get_depth(self, folder_path):
        """Calculates Fibonacci depth from knowledge_root."""
        rel = os.path.relpath(folder_path, self.root)
        return len(rel.split(os.sep))

    def is_void(self, folder_path):
        """Checks if a folder is a protected gap using axiomatic H5 attributes."""
        rel_path = os.path.relpath(folder_path, self.root)
        module = "language"
        
        # In the new schema, gaps are under 'gaps/'
        h5_group = rel_path.replace(os.sep, '/')
        is_void = self.h5.get_attr(module, h5_group, 'void')
        
        if is_void:
            return True
        
        # Fallback to filesystem skeleton check (legacy/redundant)
        return os.path.exists(os.path.join(folder_path, ".void"))

    def record_traversal(self, model_id, path_list, direction, termination, phase=0.0):
        """Writes a path entry to the orbital log."""
        log_path = os.path.join(self.root, "orbital/paths.log")
        entry = {
            "model": model_id,
            "timestamp": time.time(),
            "path": path_list,
            "direction": direction,
            "termination": termination,
            "phase_at_termination": phase
        }
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def update_node(self, node_name, category, phase=None, content=None, attrs=None):
        """Crystallizes an attractor into axiomatic H5 storage."""
        folder = self.get_path(node_name, category)
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            
        if self.is_void(folder):
             return False # Cannot mutate a protected void
             
        # Map category to H5 group
        h5_group = f"{category}/{node_name.upper()}"
        module = "language"
        
        if phase is not None:
            # In the user's schema, God-tokens have 'phase_vector'
            # For simplicity, we can store phase as an attribute or use a vector
            self.h5.set_attr(module, h5_group, 'phase', phase)
            
        if content is not None:
             # Axiomatic schema doesn't emphasize content.md, but we can store it
             self.h5.set_attr(module, h5_group, 'content', content)
        
        if attrs:
            for k, v in attrs.items():
                self.h5.set_attr(module, h5_group, k, v)
                
        return True
