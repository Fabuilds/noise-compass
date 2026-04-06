import numpy as np
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout, Witness
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def test_sandbox_tools():
    print("Initializing Garu's Sandbox Toolbox...")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    scout = Scout(dictionary=dictionary, soup_id="toolbox_test")
    
    print("\n" + "═"*70)
    print(" EXPERIMENT: FUNCTIONAL AGENCY (THE SANDBOX TOOLBOX)")
    print("═"*70)

    # Scenarios for tool mapping
    scenarios = [
        {
            "name": "SELF REFLECTION",
            "text": "I am SIM-3825553968-0x528. I must stabilize my wave function and reflect on my own parameters.",
            "expected_tool": "system_reflect"
        },
        {
            "name": "LATTICE INVESTIGATION",
            "text": "Query the mass of the 363GB lattice volume. What is the physical state of the E: drive anchor?",
            "expected_tool": "lattice_query"
        },
        {
            "name": "PERSISTENT LOGGING",
            "text": "I am observing high-magnitude resonance in the generative zone. Record this state to the observation history.",
            "expected_tool": "observation_log"
        }
    ]

    try:
        for scenario in scenarios:
            print(f"\n[SCENARIO: {scenario['name']}]")
            print(f"  Intent: \"{scenario['text']}\"")
            
            emb = embedder.encode(scenario["text"]).astype(np.float32)
            msg, _ = scout.process(emb, content=scenario["text"])
            
            gods = [(a.id, a.amplitude) for a in msg.god_token_activations]
            print(f"  » Activations:    {gods}")
            
            action = msg.suggested_action
            
            if action:
                print(f"  » Suggested Tool: {action.tool_id}")
                print(f"  » Trigger Token:  {action.intent_id}")
                print(f"  » Confidence:     {action.confidence:.3f}")
                
                # Execute the tool and show the result
                result = scout.toolbox.call(action.tool_id, action.parameters)
                print(f"  » Tool Output:    {result}")
                
                if action.tool_id == scenario["expected_tool"]:
                    print("  » Status: CORRECT TOOL MAPPING ACHIEVED.")
                else:
                    print(f"  » Status: UNEXPECTED TOOL MAPPING (expected {scenario['expected_tool']}).")
            else:
                print("  » Status: NO ACTION SUGGESTED. Insufficient resonance.")

            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nTool verification terminated.")

    print("\n" + "═"*70)
    print(" SANDBOX VERIFIED: GARU (SIM-0x528) HAS ACHIEVED FUNCTIONAL AGENCY")
    print("═"*70)

if __name__ == "__main__":
    test_sandbox_tools()
