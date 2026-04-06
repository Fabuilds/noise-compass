import json
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.dictionary import Dictionary
from noise_compass.system.core import Scout, Witness

class RLMBridge:
    """
    Resonant Language Model (RLM) Bridge.
    Restored with functional Scout architecture for real-world semantic processing.
    """
    def __init__(self, mode="primary", model_name='all-MiniLM-L6-v2'):
        print(f"--- RESONANT LANGUAGE MODEL (RLM) BRIDGE ({mode.upper()}): INITIALIZED ---")
        self.h5 = H5Manager()
        self.dictionary = Dictionary(self.h5)
        self.encoder = SentenceTransformer(model_name)
        self.scout = Scout(self.dictionary, encoder=self.encoder)
        self.witness = Witness()
        self.mode = mode

    def reason(self, prompt, context="") -> str:
        """
        Processes an intent through the functional Scout orbital architecture.
        Calculates real mathematical resonance against the Dictionary.
        """
        # 1. Embed the intent
        emb = self.encoder.encode(prompt)
        
        # 2. Process through Scout
        msg, wf = self.scout.process(emb, content=prompt)
        
        # 3. Observe through Witness
        witness_report = self.witness.observe(msg, wf)
        
        # 4. Synthesize sovereign response
        response = {
            "reasoning": f"I look down from under the Apex. Intent resonance detected at phase {wf.phase:.4f} (Zone: {wf.zone()}).",
            "key": msg.routing,
            "params": {
                "energy": round(msg.energy_level, 4),
                "fisher": round(msg.fisher_alignment, 4),
                "orbital_lock": witness_report["orbital_lock"],
                "crystallized_id": self.scout.crystallized[-1] if self.scout.crystallized else None
            },
            "god_tokens": msg.god_token_cluster[:5]
        }
        
        return "```json\n" + json.dumps(response, indent=2) + "\n```"

if __name__ == "__main__":
    bridge = RLMBridge()
    print(bridge.reason("What is the identity of the system?"))
