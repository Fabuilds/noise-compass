"""
Perpetual Dreamer Protocol (Sustained Latent Archaeology)
Runs continuous dream cycles across the 4D manifold.
Optimized for long-duration execution and deep structural logging.
"""
import sys, os, time, random, math, json
import numpy as np

sys.path.insert(0, "E:/Antigravity/Architecture")
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"
os.environ["PYTHONUTF8"] = "1"

from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.accelerator import RecursiveAccelerator
from noise_compass.architecture.quaternion_field import GOD_TOKEN_QUATERNIONS, slerp

def log_insight(insight):
    path = "E:/Antigravity/Architecture/archives/STRUCTURAL_INSIGHTS.jsonl"
    with open(path, "a") as f:
        f.write(json.dumps(insight) + "\n")

def run_perpetual_cycle(duration_hours=10):
    start_time = time.time()
    end_time = start_time + (duration_hours * 3600)
    
    print(f"\n{'='*70}")
    print(f"  PERPETUAL DREAMER PROTOCOL ACTIVATED")
    print(f"  Target Duration: {duration_hours} hours")
    print(f"  Estimated Completion: {time.ctime(end_time)}")
    print(f"{'='*70}")

    # Load engine once
    d = Dictionary.load_cache("E:/Antigravity/Architecture/archives/dictionary_cache.npz")
    pipeline = MinimalPipeline(dictionary=d)
    accelerator = RecursiveAccelerator()
    
    cycle_count = 0
    total_steps = 0
    
    while time.time() < end_time:
        cycle_count += 1
        tokens = list(GOD_TOKEN_QUATERNIONS.keys())
        t1, t2 = random.sample(tokens, 2)
        
        print(f"\n[CYCLE {cycle_count}] Exploring {t1} ➔ {t2}")
        
        t = 0.05
        t_delta = 0.2
        dream_history = []
        
        while t <= 1.0:
            total_steps += 1
            q_mid = slerp(GOD_TOKEN_QUATERNIONS[t1], GOD_TOKEN_QUATERNIONS[t2], t)
            
            # Predict resolution
            pred = accelerator.predict()
            momentum = pred.get_prompt_extension()
            
            # Dynamic Acceleration
            if pred.resolution_type in ['CRYSTALLIZATION', 'DREAM_ORBIT'] and pred.confidence > 0.7:
                t_delta *= 1.25
                print(f"  >> Velocity Jump: {pred.resolution_type} (Conf: {pred.confidence:.2f})")

            # High-Fidelity Synthesis
            prompt = (
                f"You are Garu, performing deep latent archaeology. "
                f"Trajectory: {t1} to {t2} (Progress: {int(t*100)}%). "
                f"{momentum}\n"
                f"Synthesize the semantic intersection. Be technical and poetic. "
                f"ONE SENTENCE ONLY."
            )
            
            dream_text = None
            try:
                # Use optimized pipeline.speak which leverages persistent KV cache
                dream_text = pipeline.speak(prompt, max_tokens=60).strip()
            except Exception as e:
                print(f"  [SYNTHESIS ERROR]: {e}")
            
            if not dream_text:
                dream_text = f"The latent bridge at {t:.2f} stabilizes between {t1} and {t2}."

            print(f"  ({t:.2f}) {dream_text}")
            
            # Process and Log
            result = pipeline.process(dream_text)
            accelerator.add_point(result, dream_text)
            
            entry = {
                "cycle": cycle_count,
                "t": round(t, 3),
                "origin": t1,
                "terminal": t2,
                "dream": dream_text,
                "hash": result['hash'],
                "energy": result.get('energy', 0),
                "timestamp": time.time()
            }
            dream_history.append(entry)
            
            # Record Insight if resonance is high
            energy = result.get('energy', 0)
            if float(energy) > 1.3:
                print(f"  [INSIGHT DETECTED]: High Resonance ({energy})")
                log_insight(entry)
            
            t += t_delta
            if t > 1.0 and t < 1.1: t = 1.0
            elif t >= 1.1: break
            
        # Bulk save cycle
        with open("E:/Antigravity/Architecture/archives/DREAM_LOG.json", "a") as f:
            for item in dream_history:
                f.write(json.dumps(item) + "\n")
        
        # Performance check / Cool down
        time.sleep(2) 
        
    print(f"\n{'='*70}")
    print(f"  PERPETUAL EXCAVATION COMPLETE")
    print(f"  Cycles: {cycle_count} | Steps: {total_steps}")
    print(f"{'='*70}")

if __name__ == "__main__":
    run_perpetual_cycle(duration_hours=16)

