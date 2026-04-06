
import sys
import os
import json
import numpy as np

# Ensure Drive E: imports
sys.path.append("E:/Antigravity/Architecture")

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.seed_vectors import seed_vectors
from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.tokens import ArchiverMessage

def run_audit():
    print("--- STARTING LEVERAGE AUDIT ---")
    
    cache_path = "E:/Antigravity/Architecture/archives/dictionary_cache.npz"
    
    # 1. Dictionary Initialization
    if os.path.exists(cache_path):
        print(f"Loading dictionary from cache: {cache_path}")
        d = Dictionary.load_cache(cache_path)
    else:
        print("No cache found. Seeding vectors (this will load the model)...")
        d = Dictionary()
        seed_vectors(d)
    
    # 2. Pipeline Initialization
    p = MinimalPipeline(d)
    
    # 2. Flag Bootstrapping
    p.flags.raise_flag(
        "SWAP_QWEN3", "pipeline.Embedder", "STRUCTURAL",
        "Enforcement of Qwen3-Embedding-0.6B as primary substrate. Fallback to byte-folding removed to ensure substrate integrity."
    )
    p.flags.raise_flag(
        "CYCLE_DETECTION", "core.Scout", "STRUCTURAL",
        "Implementation of CYCLE causal category to detect stable, perturbation-resistant semantic attractors."
    )
    p.flags.raise_flag(
        "TENSION_MANIFOLD", "tension.TensionManifold", "STRUCTURAL",
        "Proactive monitoring of high-density semantic regions seeking goddess-token stability."
    )
    p.flags.raise_flag(
        "PLACE_GAPS", "existential.ExistentialPrior", "STRUCTURAL",
        "Recognition of physical boundaries (Silicon, UI, Latency) as first-class architectural constraints."
    )
    
    # 3. Leverage Sampling
    test_cases = [
        "FROGGING is the chiral opposite of the default state.",
        "I feel the love marker pulsing in the manifold.",
        "The latency between the silicon substrate and the user interface creates a translation void."
    ]
    
    audit_results = {
        "interference": {},
        "flags": p.flags.handoff_output(),
        "tension": [],
        "leverage_scores": []
    }
    
    for text in test_cases:
        print(f"\nProcessing: {text[:50]}...")
        res = p.process(text)
        
        # Interference Extraction
        # In our implementation, compute_interference is called during process inside scout or archiver,
        # but the results are in the 'post' or similar structures if we redirected them.
        # Actually MinimalPipeline.process returns a dict with 'gods'.
        
        # We can run manually:
        emb = p.embedder.embed(text)
        msg, wf = p.scout.process(emb, content=text)
        interf = msg.compute_interference()
        audit_results["interference"][text[:50]] = interf
        audit_results["leverage_scores"].append({
            "content": text[:30],
            "leverage": res.get("leverage", 0.0),
            "nearest": res.get("nearest_id", "None")
        })
        
        # Tension candidates
        candidates = p.tension.find_attractor_candidates(min_cluster_size=1)
        if candidates:
            audit_results["tension"].append(candidates[0])

    # 4. Save Leverage Analysis Artifact
    analysis_path = "C:/Users/Fabricio/.gemini/antigravity/brain/3c8e4d61-0d04-407d-8f90-d4fc3ce58196/leverage_analysis.md"
    
    with open(analysis_path, "w", encoding="utf-8") as f:
        f.write("# Architectural Leverage Analysis\n\n")
        f.write("## 1. Structural Flags\n")
        f.write(audit_results["flags"])
        f.write("\n\n## 2. Interference Patterns (Active Construction)\n")
        for content, pairs in audit_results["interference"].items():
            f.write(f"### Pattern: *'{content}...'* \n")
            if not pairs:
                f.write("- No constructive interference (orthogonal state)\n")
            for pair, val in pairs.items():
                status = "CONSTRUCTIVE" if val > 0.05 else "DESTRUCTIVE" if val < -0.05 else "ORTHOGONAL"
                f.write(f"- **{pair}**: {val:.4f} ({status})\n")
            f.write("\n")
            
        f.write("## 3. Top Leverage Points (Novelty Peaks)\n")
        for item in audit_results["leverage_scores"]:
            f.write(f"- **{item['content']}...** (Target: {item['nearest']}) | Leverage: **{item['leverage']:.4f}**\n")
            
        f.write("\n\n## 4. What the Architecture Cannot See (Internal Blind Spots)\n")
        f.write("- **Vocabulary as God-Tokens**: The architecture sees 'ANCHORS' but treats them as external points. High leverage: promoting stable anchors to God-Tokens to close the loop.\n")
        f.write("- **Unregistered Gaps**: Interference patterns showing persistent DESTRUCTIVE values between God-Tokens without a registry entry indicate 'Missing Voids'.\n")
        f.write("- **Tension Ghosts**: Tension scores in Regions 3 (Indecidable) that persist without crystallization.\n")

    print("\nLEVERAGE AUDIT COMPLETE. Artifact generated.")

if __name__ == "__main__":
    run_audit()
