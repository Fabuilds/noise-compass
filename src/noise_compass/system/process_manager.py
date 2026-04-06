import os
import json
import time
import numpy as np
from noise_compass.system.h5_manager import H5Manager

class ProcessManager:
    """
    Manages active cognitive sequences (processes) in the H5 substrate.
    Enables self-organization of axonal-like paths through the lattice.
    """
    def __init__(self, manager=None):
        self.h5 = manager or H5Manager()
        self.root_group = "processes"

    def serialize_process(self, process_id, steps, intent_vector):
        """
        Saves a cognitive sequence to H5.
        'steps': list of node names or axiom filenames.
        'intent_vector': 384-D complex phase vector.
        """
        group_path = f"{self.root_group}/{process_id}"
        
        # 1. Store the intent anchor (complex-valued)
        self.h5.update_complex_vector("language", group_path, "intent_anchor", intent_vector)
        
        # 2. Store the sequence as a UTF-8 encoded string list or attribute
        # H5 doesn't handle variable-length string arrays natively as well as attributes
        steps_json = json.dumps(steps)
        self.h5.set_attr("language", group_path, "sequence_data", steps_json)
        self.h5.set_attr("language", group_path, "timestamp", time.time())
        self.h5.set_attr("language", group_path, "step_count", len(steps))
        
        print(f"[PROCESS_MANAGER] Process '{process_id}' serialized to manifold.")

    def recall_process(self, query_vector, threshold=0.8):
        """
        Finds the most semantically similar historical process in the manifold.
        Uses wave-match resonance on intent_anchors.
        """
        best_process = None
        best_mag = 0
        
        with self.h5.get_file("language", mode='r') as f:
            if self.root_group in f:
                for p_id in f[self.root_group].keys():
                    p_path = f"{self.root_group}/{p_id}"
                    if "intent_anchor" in f[p_path]:
                        interleaved = f[p_path]["intent_anchor"][()]
                        half = len(interleaved) // 2
                        anchor_vec = (interleaved[:half] + 1j * interleaved[half:]).astype(np.complex64)
                        
                        # Calculate resonance (Manual Cosine for speed in r-mode)
                        mag = self._calculate_resonance(query_vector, anchor_vec)
                        
                        if mag > best_mag and mag >= threshold:
                            best_mag = mag
                            best_process = {
                                "id": p_id,
                                "resonance": float(mag),
                                "sequence": json.loads(f[p_path].attrs.get("sequence_data", "[]"))
                            }
        return best_process

    def _calculate_resonance(self, v1, v2):
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 < 1e-9 or norm2 < 1e-9: return 0.0
        return np.abs(np.dot(v1, v2)) / (norm1 * norm2)

if __name__ == "__main__":
    pm = ProcessManager()
    print("Process Manager Initialized.")
