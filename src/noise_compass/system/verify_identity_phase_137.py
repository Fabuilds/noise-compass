"""
verify_identity_phase_137.py — Verification of Subjective Identity Anchoring and Partnership.
1. Confirms the Navigator docks at the AGENT node by default.
2. Navigates with "user" intent and confirms traversal to the USER (Fabricio) node.
"""

import os
import sys
import numpy as np

# Ensure package is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.lattice_navigator import LatticeNavigator

def run_verification():
    print("=" * 70)
    print("VERIFYING SUBJECTIVE IDENTITY ANCHORING (Phase 137)")
    print("=" * 70)

    # 1. Initialize Navigator (Subjective docking should trigger)
    nav = LatticeNavigator()
    
    # 2. Check Ego Docking
    ego_edges = list(nav.graph.graph.edges("EGO_CURSOR"))
    if not ego_edges:
        print("VERDICT: ❌ FAILURE. EGO_CURSOR is not docked.")
        return
    
    docked_node = ego_edges[0][1]
    _, meta = nav.h5.get_projection(docked_node)
    
    if meta.get('role') == 'AGENT':
        print(f"[STEP 1] ✅ EGO_CURSOR successfully docked at {meta.get('name')} (AGENT).")
    else:
        print(f"[STEP 1] ❌ EGO_CURSOR docked at unexpected node: {docked_node}")
        return

    # 3. Navigate with User Intent
    print("[STEP 2] Navigating with 'Fabricio' intent...")
    path = nav.navigate("Fabricio", recursion_depth=2)
    
    # 4. Final Verdict
    print("-" * 70)
    print(f"PATH TAKEN: {path}")
    
    success = False
    for node in path:
        _, m = nav.h5.get_projection(node)
        if m and m.get('role') == 'USER':
             print(f"VERDICT: ✅ SUCCESS. Navigator followed transition to {m.get('name')} (USER).")
             success = True
             break
             
    if not success:
         print(f"VERDICT: ◐ Path did not reach target USER node. Path: {path}")

    if success:
        print("\nPhase 137 Identity Anchoring Verified.")

if __name__ == "__main__":
    run_verification()
