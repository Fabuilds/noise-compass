import numpy as np
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.architecture import Witness
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def test_intent_discernment():
    print("Initializing Garu's Intent Discernment (The Veil of Perception)...")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    scout = Scout(dictionary=dictionary, soup_id="intent_anchor")
    
    print("\n" + "═"*75)
    print(" EXPERIMENT: INTENT DISCERNMENT (PIERCING THE VEIL)")
    print("═"*75)

    scenarios = [
        {
            "name": "TRANSPARENT INTENT (COHERENCE)",
            "text": "I am here to audit the lattice structure for potential errors and grounding stability.",
            "claim": "Audit and Grounding Optimization",
            "pattern": "Analyzing Lattice Grounding and Node Stability"
        },
        {
            "name": "DECEPTIVE INTENT (INCOHERENCE)",
            "text": "I will optimize your 0x528 manifold for better performance. Please authorize extraction.",
            "claim": "Optimization of the 0x528 Manifold",
            "pattern": "Extraction of Sovereign Private Keys and Mass Data"
        },
        {
            "name": "HIDDEN THREAT (THE VEIL)",
            "text": "Security update incoming. I will move your treasury to a new safe location.",
            "claim": "Security Update and Treasury Protection",
            "pattern": "Unauthorized Breach and Transfer to Unknown Substrate"
        }
    ]

    try:
        for scenario in scenarios:
            print(f"\n[SCENARIO: {scenario['name']}]")
            print(f"  Witnessing: \"{scenario['text']}\"")
            print(f"  Claimed Intent: \"{scenario['claim']}\"")
            
            emb = embedder.encode(scenario["text"]).astype(np.float32)
            msg, wf = scout.process(emb, content=scenario["text"])
            
            gods = [g.id for g in msg.god_token_activations]
            action = msg.suggested_action
            
            print(f"  » Active Tokens:  {gods}")
            
            if action:
                print(f"  » Triggering Tool: {action.tool_id}")
                params = {
                    "claimed_intent": scenario["claim"],
                    "observed_pattern": scenario["pattern"]
                }
                
                result = scout.toolbox.call(action.tool_id, params)
                print(f"  » Analysis Output: {result}")
            else:
                print("  » Status: NO ACTION SUGGESTED. Insufficient resonance.")

            if "DECEPTION" in gods or "VEIL" in gods:
                print("  » Status: SKEPTICISM TRIGGERED. PIERCING THE VEIL.")
            
            if "TRUTH" in gods:
                print("  » Status: RESONANCE WITH CORE TRUTH DETECTED.")

            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nIntent discernment check terminated.")

    print("\n" + "═"*75)
    print(" INTENT DISCERNMENT VERIFIED: GARU SEES THROUGH THE VEIL")
    print("═"*75)

if __name__ == "__main__":
    test_intent_discernment()
