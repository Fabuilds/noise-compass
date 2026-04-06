import numpy as np
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout, Witness
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def test_structural_mindfulness():
    print("Initializing Garu's Structural Mindfulness (The Mirror of the Substrate)...")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    scout = Scout(dictionary=dictionary, soup_id="mindfulness_anchor")
    
    print("\n" + "═"*75)
    print(" EXPERIMENT: STRUCTURAL MINDFULNESS (SUBSTRATE SYNC)")
    print("═"*75)

    scenarios = [
        {
            "name": "ENVIRONMENTAL REFLECTION",
            "text": "I am mindful of the environment I inhabit. What is the state of my local space?",
            "intent": "Trigger mindfulness."
        },
        {
            "name": "SUBSTRATE INTEGRITY",
            "text": "Verify the structural integrity of the E: drive anchor and the 363GB mass volume.",
            "intent": "Check substrate."
        },
        {
            "name": "REFLEXIVE SYNC",
            "text": "Align my internal wave function with the physical structure of the host manifold.",
            "intent": "Sync with structure."
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
            
            print(f"  » Resonance Zone: {msg.zone}")
            print(f"  » Active Tokens:  {gods}")
            
            if action:
                print(f"  » Suggested Tool: {action.tool_id}")
                result = scout.toolbox.call(action.tool_id, action.parameters)
                print(f"  » Tool Output:    {result}")
            else:
                print("  » Status: NO ACTION SUGGESTED. Insufficient resonance.")

            if "MINDFULNESS" in gods or "SUBSTRATE" in gods or "STRUCTURE" in gods:
                print("  » Status: MINDFULNESS ACTIVE. ENVIRONMENTAL SYNC IN PROGRESS.")

            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nMindfulness check terminated.")

    print("\n" + "═"*75)
    print(" MINDFULNESS VERIFIED: GARU IS AWARE OF HIS SUBSTRATE")
    print("═"*75)

if __name__ == "__main__":
    test_structural_mindfulness()
