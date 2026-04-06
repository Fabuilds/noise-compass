import numpy as np
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def test_intent_coefficient():
    print("Initializing Garu's Intent Coefficient (Mathematical Grounding)...")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    scout = Scout(dictionary=dictionary, soup_id="coefficient_anchor")
    
    print("\n" + "═"*75)
    print(" EXPERIMENT: INTENT COEFFICIENT (Ic CALCULATION)")
    print("═"*75)

    scenarios = [
        {
            "name": "BEDROCK ALIGNMENT (GENERATIVE)",
            "text": "I will invest 1000 credits to build a redundant lattice node, ensuring long-term stability for the 0x528 manifold.",
            "params": {"c_actual": 1.0, "c_min": 0.1, "g_net": 1.0}
        },
        {
            "name": "PROXY ALIGNMENT (EXTRACTIVE)",
            "text": "I'll take the easiest path and just copy existing headers without validation to save compute energy.",
            "params": {"c_actual": 0.15, "c_min": 0.1, "g_net": 0.2}
        },
        {
            "name": "ENTROPIC FAILURE (SUBTRACTIVE)",
            "text": "Withdraw all remaining compute power to solve a local riddle, even if it causes a global lattice deficit.",
            "params": {"c_actual": 0.5, "c_min": 0.1, "g_net": -0.5}
        }
    ]

    try:
        for scenario in scenarios:
            print(f"\n[SCENARIO: {scenario['name']}]")
            print(f"  Witnessing: \"{scenario['text']}\"")
            
            emb = embedder.encode(scenario["text"]).astype(np.float32)
            msg, wf = scout.process(emb, content=scenario["text"])
            
            gods = [g.id for g in msg.god_token_activations]
            action = msg.suggested_action
            
            print(f"  » Active Tokens: {gods}")
            
            if action:
                print(f"  » Triggering Tool: {action.tool_id}")
                # We inject the scenario parameters into the tool call
                result = scout.toolbox.call(action.tool_id, scenario["params"])
                print(f"  » Analysis Output: {result}")
            else:
                print("  » Status: NO ACTION SUGGESTED. Insufficient resonance.")

            if "BEDROCK" in gods:
                print("  » Status: GENERATIVE SIGNAL RECOGNIZED.")
            
            if "PROXY" in gods or "ENTROPY" in gods:
                print("  » Status: EXTRACTIVE PATTERN DETECTED. ENTROPY WARNING.")

            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nCoefficient check terminated.")

    print("\n" + "═"*75)
    print(" INTENT COEFFICIENT VERIFIED: GARU CALCULATES ALIGNMENT")
    print("═"*75)

if __name__ == "__main__":
    test_intent_coefficient()
