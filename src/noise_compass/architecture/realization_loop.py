import sys
import os
import time
import numpy as np

# Ensure Drive E: imports
sys.path.append("E:/Antigravity/Architecture")

from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dictionary import Dictionary

def execute_realization():
    print("═══ INITIATING MÖBIUS ACTUALIZATION ═══")
    print("Transitioning from Dream (Speculative) to Realization (Crystallized)...\n")

    # 1. Initialize Pipeline
    d = Dictionary.load_cache("E:/Antigravity/Architecture/archives/dictionary_cache.npz")
    p = MinimalPipeline(d)
    
    # 2. Retrieve Speculative Insights
    speculative_flags = p.flags.list_flags(state_filter="SPECULATIVE")
    if not speculative_flags:
        print("No speculative logic fuel found in the registry. The tank is empty.")
        return

    print(f"Found {len(speculative_flags)} speculative insights ready for realization.")

    # 3. Process Each Insight
    realized_count = 0
    for flag in speculative_flags:
        print(f"\n[ACTUALIZING] {flag.id}: \"{flag.description[:60]}...\"")
        
        # We use the description as the basis for the search/synthesis
        # The content already contains the dream text.
        content = flag.description
        
        # Step A: Process to get the crystallization proposal
        # "Match the speed of thought" - high intensity pass at the magnetic interface.
        print(f"  [SPEED] Syncing with magnetic interface (HF Head)...")
        # Increasing zoom to 2.0 for maximum structural resolution ("spinning fast")
        res = p.process(content, zoom=2.0, trace=True, realization=True)
        
        proposal = res.get("post", {}).get("crystallization_proposal")
        
        if proposal is not None:
            # Step B: Synthesis/Naming via M_DEEP
            # The StructuralNamer logic is already inside p.process() if crystallization_proposal is present
            # but it only suggests. We need to check the result.
            
            # The name is synthesized in the pipeline.process loop and returned in result['synthesis']
            name = res.get("synthesis")
            if name:
                print(f"  [RESONANCE] Identity Synthesis: \"{name}\"")
                
                # Step C: Formal Crystallization
                formula_id = d.crystallize_as(name, proposal)
                print(f"  [CRYSTALLIZED] {formula_id} anchored in manifold.")
                
                # Step D: Update Registry State
                p.flags.raise_flag(flag.id, target=flag.target, state="REALIZED", 
                                   description=f"REALIZED Identity: {formula_id} | Original: {flag.description}")
                
                realized_count += 1
                
                # Metabolic check (Realization boost)
                ic = res.get("post", {}).get("coherence_index", 0.0)
                print(f"  [METABOLISM] Coherence Index (Ic): {ic:.4f}")
            else:
                print("  [FAILURE] Could not synthesize a naming identity.")
        else:
            print("  [STABILITY] Attractor already exists or signal too weak to crystallize.")
            # Still mark as processed to avoid loops
            p.flags.raise_flag(flag.id, target=flag.target, state="DISSOLVED", description=flag.description)

        time.sleep(0.5)

    # 4. Finalize
    if realized_count > 0:
        d.save_cache("E:/Antigravity/Architecture/archives/dictionary_cache.npz")
        print(f"\n═══ ACTUALIZATION COMPLETE ═══")
        print(f"Successfully realized {realized_count} new structural identities.")
        print(f"Dictionary size: {len(d.entries)} attractors.")
    else:
        print("\nActualization pass complete. No new identities crystallized.")

if __name__ == "__main__":
    execute_realization()
