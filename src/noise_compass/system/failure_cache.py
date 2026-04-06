import numpy as np
import h5py
import os
import time
from noise_compass.system.h5_manager import H5Manager

class FailureCache:
    """
    Persistent storage and retrieval for 'Negative Manifold' vectors.
    Records failed cognitive trajectories to allow for aversive damping.
    """
    def __init__(self, h5_path=None):
        self.manager = H5Manager()
        self.module = "failures"
        self.cached_vectors = []
        self._load_cache()

    def _load_cache(self):
        """Loads all failure vectors into memory for fast similarity checking."""
        try:
            f = self.manager.get_file(self.module, mode='r')
            if f is not None:
                with f:
                    if 'failure_vectors' in f:
                        for key in f['failure_vectors']:
                            dataset = f[f'failure_vectors/{key}']
                            interleaved = dataset[()]
                            half = len(interleaved) // 2
                            vec = (interleaved[:half] + 1j * interleaved[half:]).astype(np.complex64)
                            self.cached_vectors.append(vec)
            if self.cached_vectors:
                print(f"[FAILURE_CACHE] Loaded {len(self.cached_vectors)} aversive vectors.")
        except Exception as e:
            print(f"[FAILURE_CACHE] [WARNING] Failed to load cache: {e}")

    def record_failure(self, vector, source_intent="unknown"):
        """Records a new failure vector to the persistent store."""
        # Check for duplicates (don't record if too similar to existing)
        if self.cached_vectors:
            repulsion = self.calculate_repulsion(vector)
            if repulsion > 0.98: # Already known
                return

        self.cached_vectors.append(vector)
        
        try:
            timestamp = int(time.time())
            # Use intent hash or time as key
            key = f"fail_{timestamp}_{len(self.cached_vectors)}"
            
            with self.manager.get_file(self.module, mode='a') as f:
                group = f.require_group('failure_vectors')
                interleaved = np.concatenate([vector.real, vector.imag]).astype(np.float32)
                ds = group.create_dataset(key, data=interleaved)
                ds.attrs['intent_summary'] = source_intent
                ds.attrs['timestamp'] = timestamp
            
            print(f"[FAILURE_CACHE] Recorded aversive peak for: {source_intent}")
        except Exception as e:
            print(f"[FAILURE_CACHE] [ERROR] Failed to record failure: {e}")

    def calculate_repulsion(self, intent_vector):
        """
        Returns a repulsion value [0, 1] based on proximity to known failure peaks.
        Uses max cosine similarity as the repulsion signal.
        """
        if not self.cached_vectors:
            return 0.0
        
        # Normalize intent
        intent_norm = intent_vector / (np.linalg.norm(intent_vector) + 1e-8)
        
        max_sim = 0.0
        for fail_vec in self.cached_vectors:
            fail_norm = fail_vec / (np.linalg.norm(fail_vec) + 1e-8)
            # Complex cosine similarity magnitude
            sim = abs(np.dot(intent_norm.conj(), fail_norm))
            if sim > max_sim:
                max_sim = sim
        
        return float(max_sim)

if __name__ == "__main__":
    cache = FailureCache()
    # Test vector
    v = (np.random.rand(384) + 1j * np.random.rand(384)).astype(np.complex64)
    cache.record_failure(v, "Test fail")
    print(f"Repulsion check: {cache.calculate_repulsion(v):.4f}")
