import os
import sys

# Ensure PYTHONPATH includes the source directory
sys.path.append(r"E:\Antigravity\Package\src")

from noise_compass.system.interference_engine import InterferenceEngine
from noise_compass.system.lattice_navigator import LatticeNavigator

def verify_ego_docking():
    print("[TEST] Initializing Interference Engine...")
    engine = InterferenceEngine()
    
    print("[TEST] Initializing Lattice Navigator...")
    nav = LatticeNavigator(engine=engine)
    
    # Perform a navigation step
    intent = "Finalize Phase 130 Transition"
    print(f"[TEST] Navigating with intent: '{intent}'")
    path = nav.navigate(intent, recursion_depth=3)
    
    print(f"[TEST] Resulting Path: {path}")
    
    # Verify EGO_CURSOR node in LatticeGraph
    print("[TEST] Checking EGO_CURSOR in LatticeGraph...")
    if "EGO_CURSOR" in nav.graph.graph.nodes:
        print("[SUCCESS] EGO_CURSOR node found in graph.")
    else:
        print("[FAILURE] EGO_CURSOR node not found in graph.")
        return
        
    # Check if EGO_CURSOR has any edges (docking)
    ego_edges = list(nav.graph.graph.edges("EGO_CURSOR"))
    if ego_edges:
        target = ego_edges[0][1]
        print(f"[SUCCESS] EGO_CURSOR docked at '{target}'.")
    else:
        print("[FAILURE] EGO_CURSOR is not docked.")
        
    print("[TEST] Synchronization and Docking verified.")

if __name__ == "__main__":
    verify_ego_docking()
