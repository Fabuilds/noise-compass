import json
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from noise_compass.system.h5_manager import H5Manager
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.system.core import Scout, Witness

class RLMBridge:
    """
    Resonant Language Model (RLM) Bridge.
    Restored with functional Scout architecture for real-world semantic processing.
    Now model-agnostic via injected interference engine passing.
    """
    def __init__(self, mode="primary", model_name='all-MiniLM-L6-v2', interference=None):
        print(f"--- RESONANT LANGUAGE MODEL (RLM) BRIDGE ({mode.upper()}): INITIALIZED ---")
        self.h5 = H5Manager()
        
        self.interference = interference
        embedder = self.interference.embed if self.interference else None
        
        # Load dictionary with deferred seed loading integration
        self.dictionary = Dictionary.load_cache(h5_manager=self.h5, embedder=embedder)
        
        self.scout = Scout(self.dictionary, encoder=self.interference if self.interference else None)
        self.witness = Witness()
        self.mode = mode

    def reason(self, prompt, context="") -> str:
        """
        Processes an intent through the functional Scout orbital architecture.
        Calculates real mathematical resonance against the Dictionary.
        """
        # 1. Embed the intent
        if self.interference:
            emb = self.interference.embed(prompt)
        else:
            raise RuntimeError("No interference engine bound for intention embedding.")
        
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
