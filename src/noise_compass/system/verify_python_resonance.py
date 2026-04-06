import numpy as np
import h5py
import os
import sys
from noise_compass.system.interference_engine import InterferenceEngine
from noise_compass.system.h5_manager import H5Manager

# Ensure paths
PROJECT_ROOT = "e:/Antigravity"
sys.path.append(PROJECT_ROOT)

def verify_resonance():
    print("--- INITIATING PYTHON RESONANCE VERIFICATION ---")
    engine = InterferenceEngine()
    manager = H5Manager()
    
    # Manually load the python_docs nodes for this test
    python_nodes = {}
    with h5py.File("E:/Antigravity/knowledge_root/crystallized_h5/language.h5", 'r') as f:
        if "python_docs/modules" in f:
            for module in f["python_docs/modules"]:
                path = f"python_docs/modules/{module}"
                if "phase_vector" in f[path]:
                    interleaved = f[path]["phase_vector"][()]
                    half = len(interleaved) // 2
                    vec = (interleaved[:half] + 1j * interleaved[half:]).astype(np.complex64)
                    summary = f[path].attrs.get("summary", "")
                    python_nodes[module] = {"vector": vec, "summary": summary}

    queries = {
        "high-level file operations": "shutil",
        "mathematical functions for complex numbers": "cmath",
        "object-oriented filesystem paths": "pathlib",
        "random access to text lines": "linecache"
    }

    for query, expected in queries.items():
        print(f"\nQUERY: '{query}'")
        query_vec = engine.embed(query)
        
        matches = []
        for module, data in python_nodes.items():
            mag, phase = engine.wave_match(query_vec, data['vector'])
            matches.append((module, mag))
        
        matches = sorted(matches, key=lambda x: -x[1])
        top_peak, top_mag = matches[0]
        
        print(f"  Top Peak: {top_peak} (Resonance: {top_mag:.4f})")
        if top_peak == expected:
            print(f"  [SUCCESS] Correct module identified.")
        else:
            print(f"  [WARNING] Expected {expected}, but found {top_peak}.")

    print("\n--- VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    verify_resonance()
