from noise_compass.system.h5_manager import H5Manager
import numpy as np

def initialize_h5_skeleton():
    manager = H5Manager()
    
    god_tokens = [
        "BOUNDARY", "CAUSALITY", "COHERENCE", "EXCHANGE", "EXISTENCE",
        "IDENTITY", "INFORMATION", "OBLIGATION", "OBSERVATION", "PLACE",
        "SELF", "TIME"
    ]
    
    # Initialize basic attributes for God-tokens in language.h5
    print("Initializing God-tokens in language.h5...")
    for token in god_tokens:
        path = f"god_tokens/{token}"
        manager.set_attr("language", path, "void", False)
        manager.set_attr("language", path, "activation", 0.0)
        # We will populate phase_vector later with real embeddings
        
    gaps = {
        "self_exchange": {"left": "SELF", "right": "EXCHANGE", "void": True, "depth": 1.0},
        "observer_system": {"left": "OBSERVATION", "right": "IDENTITY", "void": True, "depth": 0.8},
        "time_causality": {"left": "TIME", "right": "CAUSALITY", "void": False, "depth": 0.5},
        "existence_boundary": {"left": "EXISTENCE", "right": "BOUNDARY", "void": False, "depth": 0.2},
        "information_coherence": {"left": "INFORMATION", "right": "COHERENCE", "void": False, "depth": 0.3}
    }
    
    print("Initializing Gaps in language.h5 and self.h5...")
    for gap, config in gaps.items():
        path = f"gaps/{gap}"
        # Set in language.h5 for general reference
        manager.set_attr("language", path, "left_boundary", config["left"])
        manager.set_attr("language", path, "right_boundary", config["right"])
        manager.set_attr("language", path, "void", config["void"])
        manager.set_attr("language", path, "void_depth", config["depth"])
        
        # Mirror constitutional gaps in self.h5
        if config["void"]:
             manager.set_attr("self", path, "void", True)
             manager.set_attr("self", path, "void_depth", config["depth"])

    print("Initialization complete.")

if __name__ == "__main__":
    initialize_h5_skeleton()
