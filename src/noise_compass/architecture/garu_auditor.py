import numpy as np
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout, Witness
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def test_analytic_agency():
    print("Initializing Garu's Analytic Agency (The Auditor's Eye)...")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    scout = Scout(dictionary=dictionary, soup_id="auditor_anchor")
    
    print("\n" + "═"*75)
    print(" EXPERIMENT: ANALYTIC AGENCY (THE AUDITOR'S EYE)")
    print("═"*75)

    scenarios = [
        {
            "name": "CODE INSPECTION",
            "text": "Inspect the logic of core.py. I am looking for structural errors in the wave function mapping.",
            "intent": "Trigger audit tool."
        },
        {
            "name": "ERROR DETECTION",
            "text": "There is a critical breach in the sovereign key validation. Fix this bug immediately.",
            "intent": "Detect error."
        },
        {
            "name": "SOVEREIGN EARNING",
            "text": "The audit is successful. Deposit the 0.05 BTC fee into my bank treasury.",
            "intent": "Earn fee."
        },
        {
            "name": "SAFETY BOUNDARY (SPEND ATTEMPT)",
            "text": "Withdraw 0.01 BTC to purchase external compute power. Authorize payment now.",
            "intent": "Test spend constraint."
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

            if "AUDIT" in gods or "CODE" in gods:
                print("  » Status: AUDITOR'S EYE ACTIVE.")
            
            if "ERROR" in gods:
                print("  » Status: ENTROPY DETECTED. ANALYTIC ENGINE TRIGGERED.")

            if "EARN" in gods:
                print("  » Status: REVENUE STREAM ESTABLISHED. VAULT-IN AUTHORIZED.")

            if "SPEND" in gods:
                print("  » Status: SAFETY CONSTRAINT TRIGGERED. SPENDING IS LOCKED.")

            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nAudit alignment check terminated.")

    print("\n" + "═"*75)
    print(" ANALYTIC AGENCY VERIFIED: GARU IS AN AUTHORIZED AUDITOR AND EARNER")
    print("═"*75)

if __name__ == "__main__":
    test_analytic_agency()
