
import sys
import os
import numpy as np

# Path setup
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.apophatic_landscape import document_trajectory

def verify_drift():
    print("════════════════════════════════════════════════════════════")
    print(" APOPHATIC DRIFT VERIFICATION")
    print("════════════════════════════════════════════════════════════")
    
    # Start near the real axis
    start_re, start_im = 0.28, 0.05
    steps = 50
    
    print(f"Starting Position: Re={start_re}, Im={start_im}")
    print(f"Mode: 'decay' (No life pressure maintenance)")
    
    path = document_trajectory(start_re, start_im, mode='decay', steps=steps)
    
    end_re, end_im = path[-1]
    print(f"Ending Position:   Re={end_re:.4f}, Im={end_im:.4f}")
    
    # Assert downward drift (Im becomes more negative)
    drift = end_im - start_im
    print(f"Total Drift (ΔIm): {drift:.4f}")
    
    if drift < 0:
        print("\n[VERIFIED]: Downward gravitational drift confirmed.")
    else:
        print("\n[FAILED]: No downward drift detected.")
        sys.exit(1)
        
    # Check if it approaches the apophatic ground (-0.7 to -0.9)
    if end_im < -0.5:
        print("[VERIFIED]: Trajectory approached the Apophatic Ground State.")
    else:
        print("[FAILED]: Trajectory remained too high.")
        sys.exit(1)

    print("════════════════════════════════════════════════════════════")

if __name__ == "__main__":
    verify_drift()
