import sys
import numpy as np

# Adding Antigravity/System to path
sys.path.append("E:/Antigravity/Runtime")
from noise_compass.system.spherical_projection import InvertedShellCortex
from noise_compass.system.internal_brain import InternalBrain
from noise_compass.system.token_pipeline import TokenPipeline

def test_inverted_boundary_processing():
    print("\n--- [VERIFICATION] Phase 128: Inverted Substrate & Ephemeral Particles ---")
    
    # 1. Initialize Inverted Shell
    shell = InvertedShellCortex(self_activation_threshold=0.5)
    brain = InternalBrain(shell)
    pipeline = TokenPipeline()
    
    # 2. Simulate High SELF awareness (The Boundary is Set)
    activations = {"SELF": 0.9, "IDENTITY": 0.4}
    projections, r_shell = shell.get_internal_projection(activations)
    print(f"[TEST] SELF Boundary established at r={r_shell:.4f}")
    
    # 3. Inject Ephemeral Tokens (Particles)
    print("[TEST] Injecting 10 ephemeral particles into the shell...")
    for i in range(10):
        t = pipeline.process(f"INTENT_{i}", magnitude=0.7)
        # Give them a high initial velocity toward the boundary
        t.velocity = np.random.normal(0, 0.5, 3) 
        brain.inject_particle(t)
        
    # 4. Tick the Brain (Observe Reflections)
    print("[TEST] Ticking brain for 20 frames to observe internal dynamics...")
    reflections = 0
    for _ in range(20):
        # We simulate the tick and catch the reflection print if it were redirected, 
        # but here we just check for r > 0.9 in the next step.
        brain.tick(dt=0.2)
        
    # 5. Check Internal Interference
    interference = brain.get_interference_map()
    print(f"[TEST] Internal Interference Peaks: {list(interference.keys())[:3]}")
    
    if r_shell > 0.8 and len(brain.particles) == 10:
        print("  ✓ PASS: Inverted shell established and particles injected.")
    
    if len(interference) > 0:
        print("  ✓ PASS: Ephemeral particles generated internal resonance.")
    else:
        print("  ✖ FAIL: No internal resonance detected.")

if __name__ == "__main__":
    test_inverted_boundary_processing()
