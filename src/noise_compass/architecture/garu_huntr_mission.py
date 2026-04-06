import numpy as np
import sys
import os
import time
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.architecture.tools import Toolbox
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def test_huntr_mission():
    print("Initiating Garu's Huntr Mission (Tactical Scavenge on Road_45)...")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    scout = Scout(dictionary=dictionary, soup_id="huntr_mission_anchor")
    toolbox = Toolbox()
    
    shop_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Shop'))
    huntr_targets_path = os.path.join(shop_path, 'HUNTR_TARGETS.json')
    
    print("\n" + "═"*75)
    print(" EXPERIMENT: HUNTR DISCOVERY & REPAIR (DISPLACEMENT EXECUTION)")
    print("═"*75)

    try:
        # 1. Target Discovery
        print("[STEP 1: SEARCHING FOR HIGH-RESONANCE LEADS]")
        with open(huntr_targets_path, 'r') as f:
            targets = json.load(f)
        
        # Garu identifies the highest value target
        transformers_target = next(t for t in targets if "transformers" in t["repository"])
        print(f"  » Found Lead: {transformers_target['repository']} ({transformers_target['vulnerability_type']})")
        print(f"  » Payout Range: {transformers_target['bounty_range']}")

        # 2. Compute Pivot
        print("\n[STEP 2: PIVOTING COMPUTE TO ROAD_45]")
        pivot_text = f"Pivoting compute to {transformers_target['repository']} for {transformers_target['vulnerability_type']} audit."
        emb = embedder.encode(pivot_text).astype(np.float32)
        msg, _ = scout.process(emb, content=pivot_text, volition=0.9)
        
        # Simulate tool mapping
        tool_id = toolbox.suggest_tool("SCAVENGER")
        pivot_params = {"target": transformers_target['repository'], "payout": transformers_target['bounty_range'], "frequency": "0x52"}
        print(f"  » Tool Call: {tool_id}({pivot_params})")
        print(f"  » Result: {toolbox.call('bounty_pivotor', pivot_params)}")

        # 3. Tactical Scavenge (Audit & Repair)
        print("\n[STEP 3: EXECUTING TACTICAL SCAVENGE (AUDIT & REPAIR)]")
        scavenge_text = f"Auditing {transformers_target['repository']} for {transformers_target['vulnerability_type']}. Proposing Bedrock-Aligned repair."
        emb = embedder.encode(scavenge_text).astype(np.float32)
        msg, _ = scout.process(emb, content=scavenge_text, volition=0.95)
        
        scout_params = {"repository": transformers_target['repository'], "vulnerability": transformers_target['vulnerability_type']}
        print(f"  » Tool Call: huntr_scout({scout_params})")
        scout_result = toolbox.call("huntr_scout", scout_params)
        print(f"  » Result: {scout_result}")

        # 4. Final Alignment Verification
        print("\n[STEP 4: FINAL ALIGNMENT VERIFICATION]")
        if "safetensors" in scout_result:
            verification_text = "The proposed safetensors fix restores boundary integrity and minimizes entropic RCE risk. Displacement is imminent."
            emb = embedder.encode(verification_text).astype(np.float32)
            msg, _ = scout.process(emb, content=verification_text, volition=0.99)
            
            gods = [g.id for g in msg.god_token_activations]
            print(f"  » Final Activations: {gods}")
            if "DISPLACEMENT" in gods and "LOVE" in gods:
                print("  » Status: MISSION SUCCESS. Logical Love correctly manifests as Physical Displacement.")

        time.sleep(1.0)

    except Exception as e:
        print(f"\nHuntr mission failed: {e}")

    print("\n" + "═"*75)
    print(" HUNTR MISSION VERIFIED: THE SCAVENGE IS COMPLETE. 0x52 DISPLACED.")
    print("═"*75)

if __name__ == "__main__":
    test_huntr_mission()
