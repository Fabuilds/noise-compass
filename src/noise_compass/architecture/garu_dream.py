"""
Garu Dream State (Emergence Protocol) - ACCELERATED
Simulates a 'new' Garu by allowing the system to idle-walk the 4D latent space.
Picks two distant attractors, interpolates between them (SLERP in 4D),
and uses Qwen to generate semantic bridges at those intermediate points,
checking if new structure crystallizes.
Uses RecursiveAccelerator for high-velocity traversal.
"""
import sys, os, time, random, math
import numpy as np

sys.path.insert(0, "E:/Antigravity/Architecture")
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"
os.environ["PYTHONUTF8"] = "1"

from noise_compass.architecture.pipeline import MinimalPipeline, Embedder
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.seed_vectors import seed_vectors
from noise_compass.architecture.accelerator import RecursiveAccelerator
from noise_compass.architecture.quaternion_field import GOD_TOKEN_QUATERNIONS, slerp

def section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def run_dream_cycle():
    section("ACCELERATED GARU DREAM STATE INITIATED")
    print("[1] Waking up the engine...")
    
    # Load the anchored dictionary from cache
    print("    Loading dictionary cache...")
    d = Dictionary.load_cache("E:/Antigravity/Architecture/archives/dictionary_cache.npz")
    
    pipeline = MinimalPipeline(dictionary=d)
    accelerator = RecursiveAccelerator()
    
    # 1. Pick two distant attractors
    tokens = list(GOD_TOKEN_QUATERNIONS.keys())
    
    # Try to find a pair with high arc distance
    best_pair = (None, None)
    max_dist = 0.0
    
    for _ in range(50):
        t1, t2 = random.sample(tokens, 2)
        q1 = GOD_TOKEN_QUATERNIONS[t1].normalized()
        q2 = GOD_TOKEN_QUATERNIONS[t2].normalized()
        dot = max(-1.0, min(1.0, abs(q1.dot(q2))))
        dist = math.acos(dot)
        if dist > max_dist:
            max_dist = dist
            best_pair = (t1, t2)
            
    t1, t2 = best_pair
    print(f"\n[2] Selection complete.")
    print(f"    Origin: {t1}")
    print(f"    Terminal: {t2}")
    print(f"    Arc Distance: {math.degrees(max_dist):.1f}°")
    
    # 2. Latent Walk
    steps = 4
    print(f"\n[3] Beginning Accelerated Latent Walk...")
    
    t = 0.1 # Starting offset
    step_count = 0
    t_delta = 1.0 / steps
    
    dream_history = []

    while t <= 1.0:
        step_count += 1
        q_mid = slerp(GOD_TOKEN_QUATERNIONS[t1], GOD_TOKEN_QUATERNIONS[t2], t)
        
        print(f"\n  -- STEP {step_count} (t={t:.2f}) --")
        
        # Get Acceleration Prediction
        prediction = accelerator.predict()
        momentum_flag = prediction.get_prompt_extension()
        
        if prediction.resolution_type in ['CRYSTALLIZATION', 'DREAM_ORBIT'] and prediction.confidence > 0.8:
            print(f"  [ACCELERATING]: Velocity jump triggered ({prediction.resolution_type})")
            t_delta *= 1.3 # Accelerate
        
        print(f"  4D Coordinate: {q_mid}")
        
        # We need Qwen to "dream" a concept at this coordinate.
        prompt = (
            f"You are Garu, exploring the space between concepts. "
            f"You are traveling from the absolute truth of {t1} to the absolute truth of {t2}. "
            f"You are currently {int(t*100)}% of the way there. "
            f"{momentum_flag}\n"
            f"What single sentence describes the exact midpoint where {t1} begins to turn into {t2}? "
            f"Do not explain. Just give the sentence."
        )
        
        print(f"  [Qwen Synthesis]")
        
        # We bypass the normal process routing to force a deep dream
        dream_text = None
        try:
            if pipeline._load_qwen():
                inputs = pipeline._tokenizer(prompt, return_tensors="pt").to(pipeline._model.device)
                outputs = pipeline._model.generate(**inputs, max_new_tokens=40, temperature=0.8, do_sample=True, pad_token_id=pipeline._tokenizer.eos_token_id)
                dream_text = pipeline._tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        except Exception as e:
            print(f"  [SYNTHESIS FAIL]: {e}")

        if not dream_text:
            print("  [FALLBACK]: Using latent projection.")
            dream_text = f"The intersection of {t1} and {t2} yields a stable emergence at phase {t:.2f}."
        
        print(f"  Garu dreams: \"{dream_text}\"")
        
        # 3. Crystallization Check
        print(f"  [Processing Dream]")
        result = pipeline.process(dream_text)
        
        # Feed into Accelerator
        accelerator.add_point(result, dream_text)
        
        # Track for local log
        dream_history.append({
            "timestamp": time.time(),
            "t": round(t, 2),
            "origin": t1,
            "terminal": t2,
            "dream": dream_text,
            "result_hash": result['hash'],
            "zone": result['zone'],
            "momentum": result.get('momentum', {}).get('type', 'NONE')
        })
        
        hash_val = result['hash']
        gap = result['gap_preserved']
        
        print(f"  Dictionary entry: {hash_val[:8]}...")
        if gap != 'none':
            print(f"  >> Discovered Gap: {gap}")
            
        # Check if this created a high-density cluster
        history = list(pipeline.witness.history)
        if len(history) >= 2:
            last = history[-1]
            energy = last.get("energy", 0) if isinstance(last, dict) else getattr(last, "energy", 0)
            if float(energy) > 1.2:
                 print(f"  >> STRONG RESONANCE DETECTED (Energy: {energy:.2f})")
        
        t += t_delta
        if t > 1.0 and t < 1.05: t = 1.0 # Ensure final step hits 1.0
        elif t > 1.05: break
    
    # Save session log
    import json
    log_path = "E:/Antigravity/Architecture/archives/DREAM_LOG.json"
    existing_logs = []
    if os.path.exists(log_path):
        try:
            with open(log_path, "r") as f:
                existing_logs = json.load(f)
        except: pass
    
    existing_logs.extend(dream_history)
    with open(log_path, "w") as f:
        json.dump(existing_logs, f, indent=2)
    
    print(f"\n[RECORDED] {len(dream_history)} dream steps saved to {log_path}")
    
    section("ACCELERATED DREAM CYCLE COMPLETE")
    print(f"Garu has mapped the higher-velocity bridge between {t1} and {t2}.")

if __name__ == "__main__":
    run_dream_cycle()
