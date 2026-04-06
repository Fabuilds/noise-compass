
import os
import sys
import time
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.velocity_dream import VelocityDreamer
from noise_compass.architecture.tension import TensionManifold

def run_excavation(batch_size=5, steps_per_dream=3):
    print("═══ INITIATING GREAT EXCAVATION (VELOCITY) ═══")
    print(f"Target: Semantic Manifold (Accelerated Exploration)")
    
    # 1. Load System
    dict_cache = "E:/Antigravity/Architecture/archives/dictionary_cache.npz"
    if not os.path.exists(dict_cache):
        from noise_compass.architecture.seed_vectors import seed_vectors
        d = Dictionary()
        seed_vectors(d)
    else:
        d = Dictionary.load_cache(dict_cache)
        
    p = MinimalPipeline(d)
    dreamer = VelocityDreamer(p)
    
    print(f"\n[SYSTEM] Local manifold loaded. Dictionary size: {len(d.entries)}")
    print(f"[REGR] Flag Registry connected. Speculative logic active.")
    
    # 2. Check Tension Report
    print(f"\n{p.tension.tension_report()}")
    
    # 3. Execute Dream Batch
    all_results = []
    print(f"\n[CYCLE] Starting batch of {batch_size} dreams...")
    
    for i in range(batch_size):
        print(f"\n--- Dream {i+1}/{batch_size} ---")
        try:
            # Use a slightly varied zoom to test manifold resolution
            zoom = 1.0 if i % 2 == 0 else 1.2
            results = dreamer.dream(steps=steps_per_dream, zoom=zoom)
            all_results.extend(results)
            
            # Check for Möbius detection in individual steps
            for res in results:
                if res.get('momentum', {}).get('type') == 'MÖBIUS_CAPTURE':
                    print(f"  [!!!] MÖBIUS CAPTURE DETECTED: {res.get('hash', 'anon')}")
                    print(f"  [SIGNAL] Trajectory trapped in self-reinforcing loop.")
                
                # Session 16: Display Clarity updates
                if res.get('clarity', 1.0) < 0.8:
                    print(f"  [OPTICAL] Clarity: {res['clarity']} -> {res['optical_state']}")
                
                # Session 16: Metabolic Display
                meta = res.get('post', {}).get('metabolic_state', {})
                if meta:
                    print(f"  [METABOLISM] Coherence: {meta['coherence']} | Exertion: {meta['exertion']}s | Cost: {meta['cost_acc']}")
                
                # Expose God Tokens for the user
                gods = res.get('gods', [])
                if gods:
                    print(f"  [GOD-TOKENS] Active: {', '.join(gods)}")
                else:
                    print(f"  [GOD-TOKENS] None (Orthogonal State)")
                
        except Exception as e:
            print(f"[ERROR] Dream {i+1} collapsed: {e}")
            
    # 4. Final Summary
    print("\n═══ EXCAVATION BATCH COMPLETE ═══")
    leverage_points = [r for r in all_results if r.get('leverage', 0.0) > 0.4]
    print(f"Processed {len(all_results)} concept steps.")
    print(f"Found {len(leverage_points)} high-leverage structural candidates.")
    
    # Report finalized logic fuel
    from noise_compass.architecture.flag_registry import FlagRegistry
    registry = FlagRegistry()
    recent_fuel = registry.list_flags(state_filter="SPECULATIVE")
    print(f"Current Speculative Logic Fuel: {len(recent_fuel)} flags.")

if __name__ == "__main__":
    # Ensure UTF-8
    os.environ['PYTHONUTF8'] = '1'
    run_excavation(batch_size=20, steps_per_dream=5) 
