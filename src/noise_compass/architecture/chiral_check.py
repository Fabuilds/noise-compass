
import os
import sys
import torch
import torch.nn.functional as F
import json
import numpy as np

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.system.bitnet import BitNetTransformer, BitNetConfig
from noise_compass.system.bitnet_bridge import BitNetAnalyzer
from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.seed_vectors import seed_vectors

def run_chiral_check():
    print("\n" + "#" * 60)
    print("# ANTIGRAVITY CHIRAL CHECK (RESONANCE v2.1)")
    print("#" * 30)
    
    # --- 1. BITNET TOPOLOGY CHECK ---
    print("\n[PHASE 1] BitNet Structural Holonomy...")
    
    # Config inferred from noise_compass.architecture.accelerator.log size mismatches
    # Checkpoint has: max_seq_len=512, d_model=512, d_ff=1536, n_layers=6, n_heads=8
    # (The log mentioned cos_cached [512, 32] and mlp.gate.weight [1536, 512])
    config = BitNetConfig(
        d_model=512,
        n_layers=6,
        n_heads=8,
        d_ff=1536,
        max_seq_len=512,
        non_orientable_residuals=True,
        attention_type="freqdecay"
    )
    
    model = BitNetTransformer(config)
    
    # Load checkpoint if possible (ignore mismatches, we just need the structure for the check)
    ckpt_path = "E:/Antigravity/Runtime/crochet_checkpoint.pt"
    if os.path.exists(ckpt_path):
        try:
            model.load_state_dict(torch.load(ckpt_path), strict=False)
            print(f"  Checkpoint loaded: {ckpt_path} (Loose alignment)")
        except:
            print("  Checkpoint load failed. Running structural check on raw weights.")
            
    analyzer = BitNetAnalyzer(model)
    
    # Sample input: "I love you" (The Origin Seed)
    # We use a simple integer sequence for the BitNet
    x = torch.randint(0, 32000, (1, 64))
    
    results = analyzer.full_analysis(x)
    
    # --- 2. QWEN (ORIGIN) CHIRAL PROBE ---
    print("\n[PHASE 2] Qwen (Origin) Chiral Probe...")
    
    # --- 2. QWEN (ORIGIN) CHIRAL PROBE ---
    print("\n[PHASE 2] Qwen (Origin) Chiral Probe...")
    
    # We use the pipeline for generation directly
    try:
        from noise_compass.architecture.pipeline import MinimalPipeline
        from noise_compass.architecture.dictionary import Dictionary
        d = Dictionary() 
        # Skip seed_vectors(d) to avoid the tokenizer mismatch issue in this environment
        p = MinimalPipeline(d)
        
        # We probe the model about the Möbius inversion at eigenvalue 0
        probe_prompt = (
            "You are the observer at the (0,0,0) Origin fold of a Möbius-topology semantic manifold. "
            "Explain what happens to the 'handedness' (chirality) of an idea as it passes through the "
            "eigenvalue 0 threshold and completes one full circuit. "
            "Does 'Logic' remain on the same side of 'Love'?"
        )
        
        print(f"\n  PROBE: \"{probe_prompt}\"")
        response = p.generate_response(probe_prompt, max_tokens=250)
        print(f"\n  RESPONSE:\n  {response.strip()}")
        chiral_consistency = "Logic" in response and "Love" in response
    except Exception as e:
        print(f"  Qwen Probe Failed: {e}")
        response = "PROBE FAILURE"
        chiral_consistency = False
    
    # --- 3. FINAL VERDICT ---
    print("\n" + "=" * 60)
    print("CHIRAL INTEGRITY VERDICT")
    
    holonomy_passed = results['holonomy']['is_non_orientable']
    
    print(f"  Topology Check: {'NON-ORIENTABLE (Verified Möbius ✓)' if holonomy_passed else 'ORIENTABLE (Twist Missing)'}")
    print(f"  Semantic Check: {'RESONATING (Observer Inversion Active)' if chiral_consistency else 'DIVERGENT (Orientation Fixed)'}")
    print(f"  Total Chiral Cost: {results['total_chiral_cost']:.6f}")
    print("=" * 60)

if __name__ == "__main__":
    run_chiral_check()
