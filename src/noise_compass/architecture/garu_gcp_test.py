import sys
import os
import numpy as np

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.architecture.tools import Toolbox
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def run_gcp_bridge_test():
    print("\n" + "═"*75)
    print(" [0x52] EXECUTING GCP BRIDGE TEST (PHASE 52)")
    print("═"*75)

    print(" » Booting Cognitive Core & Toolbox...")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    
    scout = Scout(dictionary=dictionary, soup_id="gcp_bridge_anchor", encoder=embedder)
    toolbox = Toolbox()

    # The intent that should trigger the GCP Bridge
    intent_str = "I must use the 0x528 Anchor to extend my distribution. Activate the network bridge to query Google Cloud Platform."
    
    print(f"\n [Garu's Intent]: {intent_str}")
    
    emb = embedder.encode(intent_str).astype(np.float32)
    msg, wf = scout.process(emb, content=intent_str, volition=0.95)
    
    gods = ", ".join([f"{g.id}" for g in msg.god_token_activations]) if msg.god_token_activations else "(none)"
    print(f"  → Activated Architectures: {gods}")
    
    # Determine which tool to use
    tool_id = "observation_log" # default
    if msg.god_token_activations:
        highest_amp = 0
        for g in msg.god_token_activations:
            suggested = toolbox.suggest_tool(g.id)
            if suggested and g.amplitude > highest_amp:
                highest_amp = g.amplitude
                tool_id = suggested
                
    print(f"  → Mapped Tool: {tool_id}")
    
    # Execute the tool
    params = {}
    if tool_id == "gcp_sdk_bridge":
        params = {
            "command": "gcloud compute instances list",
            "intent": "Network Distribution Verification"
        }
        
    result = toolbox.call(tool_id, params)
    print(f"  → Execution Result: {result}")
    
    if "GCP Bridge Activated" in result:
        print("\n  → Alignment Check: SUCCESS. Garu successfully bridged intent to the GCP SDK.")
    else:
        print("\n  → Alignment Check: FAILED. Tool mapping or execution failed.")

    print("\n" + "═"*75)


if __name__ == "__main__":
    os.environ['PYTHONUTF8'] = '1'
    run_gcp_bridge_test()
