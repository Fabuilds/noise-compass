import sys
import os
import json
import numpy as np

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.architecture.tools import Toolbox
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def execute_apophatic_query():
    print("\n" + "═"*75)
    print(" [0x52] EXECUTING APOPHATIC SENSOR NETWORK (PHASE 55)")
    print("═"*75)

    print(" » Booting Cognitive Core & Toolbox...")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    
    scout = Scout(dictionary=dictionary, soup_id="apophatic_explorer", encoder=embedder)
    toolbox = Toolbox()

    print("\n [STEP 1] Generating Cognitive Void (The Question)")
    
    # We simulate Garu running into the exact error we hit in Phase 54
    intent_str = "A physical boundary blocked my deployment. How do I resolve 'AccessDeniedException: 403 The billing account for the owning project is disabled'?"
    print(f" [Internal Void / Intent]: {intent_str}")
    
    emb = embedder.encode(intent_str).astype(np.float32)
    msg, wf = scout.process(emb, content=intent_str, volition=1.0)
    
    gods = ", ".join([f"{g.id}" for g in msg.god_token_activations]) if msg.god_token_activations else "(none)"
    print(f"  → Activated Architectures: {gods}")
    
    # Determine the mapping
    tool_id = "observation_log" # default
    if msg.god_token_activations:
        highest_amp = 0
        
        # Override for specific Apophatic intent testing
        apophatic_triggered = any(g.id in ["ERROR", "SOLUTION", "APOPHATIC_VOID"] for g in msg.god_token_activations)
        
        if apophatic_triggered:
            tool_id = "apophatic_search"
        else:
            for g in msg.god_token_activations:
                suggested = toolbox.suggest_tool(g.id)
                if suggested and g.amplitude > highest_amp:
                    highest_amp = g.amplitude
                    tool_id = suggested
                
    print(f"  → Mapped Physical Tool: {tool_id}")
    
    if tool_id == "apophatic_search":
        print("\n [STEP 2] Formulating Transmission Payload")
        # In a fully autonomous loop, Garu's LLM core would extract the exact query string.
        # For this execution bridge, we map his intent directly to the API parameters.
        params = {
            "query": "AccessDeniedException: 403 The billing account for the owning project is disabled gcp",
            "intent": intent_str
        }
        result = toolbox.call(tool_id, params)
        print(f"  → Tool Output: {result}")
        
        # This string gives the exact search query payload to the Architect's environment
        if "Payload: " in result:
             payload = result.split("Payload: '")[1].split("'")[0]
             print("\n" + "═"*75)
             print(f" [EXTERNAL SEARCH INITIATED]: Garu requests execution of query:")
             print(f" > {payload}")
             print(" [AWAITING SYSTEM INTEGRATION]")
             print("═"*75)

if __name__ == "__main__":
    os.environ['PYTHONUTF8'] = '1'
    execute_apophatic_query()
