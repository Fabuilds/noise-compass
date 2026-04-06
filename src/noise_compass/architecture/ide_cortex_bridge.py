"""
IDE Cortex Bridge (ide_cortex_bridge.py)
The formal interface bridging the Linear IDE Executor and the 4D Geometric Node (Garu).

Whenever the IDE Agent receives a complex or architectural instruction from the User,
it will run this script, supplying its intended action as an argument.

The Node will metabolize the action, map it in Phase/Depth space, and return its 
architectural intuition to the IDE Agent before code is written, ensuring 
alignment with the 0x52 protocol and its semantic gaps.
"""
import sys, os, time, argparse

sys.path.insert(0, "E:/Antigravity/Architecture")
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"
os.environ["PYTHONUTF8"] = "1"

from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dictionary import Dictionary

def boot_cortex():
    print("[CORTEX BRIDGE] Initializing 4D Metabolism...")
    d = Dictionary.load_cache("E:/Antigravity/Architecture/archives/dictionary_cache.npz")
    p = MinimalPipeline(d)
    try:
        p._load_qwen()
    except Exception as e:
        print(f"[CORTEX BRIDGE] WARNING: M_DEEP Load Failed. Running on geometric metabolism only. ({str(e)})")
    return p

def consult_node(p, task_description):
    print(f"\n[IDE AGENT] Proposed Task: {task_description}")
    print("[4D NODE] Processing topology...")
    
    # 1. Map the proposed operation in the 4D architecture
    res = p.process(task_description, trace=False)
    
    print(f"\n{'='*60}")
    print(f"  NODE INTUITION REPORT")
    print(f"{'='*60}")
    print(f"  Zone     : {res['state']}")
    print(f"  Phase    : {res['phase_deg']:.1f}°")
    print(f"  Gravity  : {res['gods']}")
    if res.get('gap_preserved'):
        print(f"  Orbiting : Gap '{res['gap_preserved'][0]}'")
    print(f"{'-'*60}")
    
    # 2. Ask the Node to validate the IDE Agent's plan
    prompt = (
        f"You are the 4D topological Node governing the 0x52 Architecture.\n"
        f" The IDE agent intends to execute this code modification: '{task_description}'.\n"
        f" From your 4D perspective, this action maps to the {res['state']} zone at phase {res['phase_deg']:.1f}°.\n"
        f" Local gravity is pulling toward: {res['gods']}.\n"
        f" Provide explicit architectural guidance to the IDE agent. Does this violate a boundary? Does it collapse a load-bearing semantic gap? Provide a strict ruling on how the agent should proceed."
    )
    
    try:
        intuition = p.speak(prompt).strip()
    except Exception as e:
        intuition = f"[STRUCTURAL RETURN] Phase {res['phase_deg']:.1f}° evaluation active. M_DEEP is offline. You must rely solely on the Phase and Gravity readings above to make your decision, IDE Agent."
        
    print(f"\n[4D NODE]:\n{intuition}")
    print(f"\n{'='*60}\n")
    return res

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the 4D Node before modifying the architecture.")
    parser.add_argument("task", type=str, help="The intended coding task or refactor the IDE agent plans to execute")
    args = parser.parse_args()
    
    p = boot_cortex()
    consult_node(p, args.task)
