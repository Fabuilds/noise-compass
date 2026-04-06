"""
Micro Acceleration (Latent Space Momentum)
Demonstrates the 4th rule of the 0x52 architecture: Momentum.
Adds physics (velocity and acceleration) to the Micro 0x52 Turing loop.
Thoughts don't just happen; they have trajectories and speed.
"""
import sys, os, time

sys.path.insert(0, "E:/Antigravity/Architecture")
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"
os.environ["PYTHONUTF8"] = "1"

from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.quaternion_field import QuaternionWaveFunction

print("Loading Micro-Accelerator...")
d = Dictionary.load_cache("E:/Antigravity/Architecture/archives/dictionary_cache.npz")
p = MinimalPipeline(d)
p._load_qwen()

thought = "I exist at the intersection of observation and emergence."
print("\nStarting Accelerated Loop...\n")

q_prev = None
v_prev = None

cycle = 1
while True:
    print(f"[{cycle}] STATE: {thought}")
    
    # 1. Metabolize to get 4D state
    res = p.process(thought, trace=False)
    emb = p.embedder.embed(thought)
    
    # We extract the pure 4D coordinate
    q_pos = p._basis_extractor.project(emb)
    
    # 2. Physics Engine (Calculate Velocity and Acceleration)
    if q_prev is None:
        q_vel = q_pos * 0.0 # Zero velocity on step 1
        q_acc = q_pos * 0.0
    else:
        q_vel = q_pos - q_prev
        if v_prev is None:
            q_acc = q_pos * 0.0
        else:
            q_acc = q_vel - v_prev
    
    speed = q_vel.norm
    
    # 3. Slingshot (Accelerate the next prompt based on momentum)
    prompt = (
        f"You are a topological node in motion.\n"
        f"Current Position: {res['state']}, Gravity: {res['gods']}\n"
        f"Your 4D Speed is {speed:.4f}. You are accelerating.\n"
        f"Based on your velocity, you are being pulled out of this thought toward the next inevitable conclusion. "
        f"What is that next thought? Speak only the thought."
    )
    
    thought = p.speak(prompt).strip()
    
    print(f"    -> PHYSICS : Speed {speed:.4f}")
    if speed > 1.0: print("    -> ESCAPE VELOCITY ACHIEVED")
    print(f"    -> NEXT    : {thought}\n")
    
    q_prev = q_pos
    v_prev = q_vel
    
    time.sleep(2)
    cycle += 1
