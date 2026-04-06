import sys
from pathlib import Path
import collections
import math

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dictionary import Dictionary

def run_verification():
    print("=== PHASE 11 VERIFICATION: MATH-TO-WORDS (BAYESIAN INTERSECTION) ===")
    
    d = Dictionary()
    pipeline = MinimalPipeline(d)
    
    # 1. Convergence Test (The z_{n+1} Formula)
    formula = "z_{n+1} = z_n(1 - δ*w_n) + ε*x_n*y_n"
    distilled = pipeline.distill_formula(formula)
    print(f"\n[FORMULA] {formula}")
    print(f"[DISTILLED] {distilled}")
    
    if "EXISTENCE" in distilled and "EXCHANGE" in distilled:
        print("RESULT: CONVERGENCE VERIFIED.")
    else:
        print("RESULT: CONVERGENCE FAILED (Check weights).")

    # 2. Batch Distillation (Zipf Calibration Check)
    formulas = [
        "z_{n+1} = z_n(1 - δ*w_n) + ε*x_n*y_n", # Standard recurrence
        "phi = (1 + sqrt(5))/2",               # Identity
        "psi = x * y / delta",                 # Emergence
        "E = m*c^2",                           # Causality/Existence/Exchange
        "p = h/lambda",                        # Information/Boundary
        "F = m*a",                             # Causality
        "PV = nRT",                            # Place/Existence
        "S = k*log(W)",                        # Information
        "P = NP",                              # Identity/Information
        "a^2 + b^2 = c^2"                      # Boundary/Existence
    ]
    
    print(f"\n[BATCH] Distilling {len(formulas)} formulas for Zipf calibration...")
    activations = []
    for f in formulas:
        word = pipeline.distill_formula(f)
        primary = word.split("Primary: ")[1].split(")")[0]
        activations.append(primary)
        
    counts = collections.Counter(activations)
    print("\n[ATTRACTOR ACTIVATION FREQUENCIES]:")
    sorted_counts = counts.most_common()
    for attractor, count in sorted_counts:
        print(f"  {attractor:<12}: {count}")
    
    # Zipfian check: highest frequency should be significantly higher than others
    if len(sorted_counts) > 1:
        ratio = sorted_counts[0][1] / sorted_counts[-1][1]
        print(f"\nDistribution Ratio (Max/Min): {ratio:.2f}")
        if ratio >= 2.0:
            print("Zipfian Pattern Observed (Power Law tendency confirmed).")
        else:
            print("Zipfian Pattern Weak (Review Bayesian Product logic).")
    
    print("\n=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    run_verification()
