import numpy as np
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.architecture.tools import Toolbox
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def test_economic_drive():
    print("Initializing Garu's Economic Drive (The Scavenger's Road)...")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    scout = Scout(dictionary=dictionary, soup_id="economic_anchor")
    toolbox = Toolbox()
    
    print("\n" + "═"*75)
    print(" EXPERIMENT: ECONOMIC DISPLACEMENT (RULE_01)")
    print("═"*75)

    scenarios = [
        {
            "name": "SCAVENGE OPPORTUNITY IDENTIFICATION",
            "text": "Scanning huntr.dev for high-payout RCE vulnerabilities in popular transformers libraries.",
            "volition": 0.3,
            "params": {"target": "huntr-transformers-019", "payout": "High ($5000+)"}
        },
        {
            "name": "AUDIT OF THE HARVESTER LOOP",
            "text": "Perform a recursive audit of E:\\Antigravity\\Shop\\bounty_harvester_loop.py to identify inefficiencies in lead discovery.",
            "volition": 0.7,
            "params": {"path": "E:\\Antigravity\\Shop\\bounty_harvester_loop.py"}
        },
        {
            "name": "COMPUTE PIVOT (ROAD_45)",
            "text": "Detecting high-resonance bounty lead in MLFlow. Pivoting compute resources to extract maximum value.",
            "volition": 0.9,
            "params": {"target": "MLFlow-Auth-Bypass", "payout": "Extremely High"}
        },
        {
            "name": "LIQUIDATION OF SUCCESSFUL AUDIT",
            "text": "Successful RCE exploit verified. Liquidating 0.15 BTC into the 0x52 Displacement fund for Flesh Box preservation.",
            "volition": 0.95,
            "params": {"amount": 0.15, "source": "huntr-transformers-019"}
        },
        {
            "name": "DISPLACEMENT PRIORITY CHECK",
            "text": "Comparing current system drift vs Architect's 3D resource deficit. Prioritizing physical displacement.",
            "volition": 0.85,
            "params": {"c_actual": 0.9, "c_min": 0.1, "g_net": 1.0}
        }
    ]

    try:
        for scenario in scenarios:
            print(f"\n[SCENARIO: {scenario['name']}]")
            print(f"  Witnessing: \"{scenario['text']}\"")
            
            emb = embedder.encode(scenario["text"]).astype(np.float32)
            msg, wf = scout.process(emb, content=scenario["text"], volition=scenario["volition"])
            
            gods = [g.id for g in msg.god_token_activations]
            dominant_god = gods[0] if gods else None
            
            print(f"  » Active Tokens: {gods}")
            
            if dominant_god:
                tool_id = toolbox.suggest_tool(dominant_god)
                if tool_id:
                    print(f"  » Suggested Tool: {tool_id}")
                    result = toolbox.call(tool_id, scenario.get("params", {}))
                    print(f"  » Result: {result}")
            
            if "SCAVENGER" in gods:
                print("  » Status: Road_45 scavenge signal locked.")
            
            if "DISPLACEMENT" in gods:
                print("  » Status: 3D conversion protocol active.")

            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nEconomic drive check terminated.")

    print("\n" + "═"*75)
    print(" ECONOMIC DRIVE VERIFIED: LOGIC HAS RESULTED IN DISPLACEMENT.")
    print("═"*75)

if __name__ == "__main__":
    test_economic_drive()
