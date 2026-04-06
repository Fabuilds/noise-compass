"""
verify_topology_phase_136.py — Verification of Document Projection and Topological Traversal.
1. Projects Document A and B.
2. Encodes a strong transition A -> B.
3. Verifies that the Navigator follows the encoded path.
"""

import os
import sys
import numpy as np

# Ensure package is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.projection_engine import ProjectionEngine
from noise_compass.system.lattice_navigator import LatticeNavigator

def run_verification():
    print("=" * 70)
    print("VERIFYING TOPOLOGICAL PROJECTION & TRAVERSAL (Phase 136)")
    print("=" * 70)

    # 1. Initialize Components
    pe = ProjectionEngine()
    nav = LatticeNavigator(scout=pe.scout)

    # 2. Project Documents
    doc_a_text = "The FIRST structural axiom defines the H5 substrate as the immutable projection layer."
    doc_b_text = "The SECOND structural axiom establishes topological navigation between document nodes."
    
    print("[STEP 1] Projecting Documents...")
    id_a = pe.project(doc_a_text, metadata={'step': 1})
    id_b = pe.project(doc_b_text, metadata={'step': 2})

    # 3. Encode Topology (Traversable Path)
    print("[STEP 2] Encoding Topological Link: A -> B")
    pe.link(id_a, id_b, weight=2.0) # High weight causal transition

    # 4. Refresh Graph and Navigate
    print("[STEP 3] Navigating from ID_A using Topological Intent...")
    nav.working_memory = pe.encoder.encode(doc_a_text) # Set start position
    nav.graph.dock_ego(id_a)
    
    path = nav.navigate("navigation", recursion_depth=2)
    
    # 5. Final Verdict
    print("-" * 70)
    print(f"PATH TAKEN: {path}")
    
    success = False
    if len(path) >= 1:
        if id_b in path:
             print("VERDICT: ✅ SUCCESS. Navigator followed encoded transition to ID_B.")
             success = True
        else:
             print(f"VERDICT: ◐ Path did not include target ID_B. Path: {path}")
    else:
        print("VERDICT: ❌ FAILURE. No path generated.")

    if success:
        print("\nPhase 136 Infrastructure Verified.")

if __name__ == "__main__":
    run_verification()
