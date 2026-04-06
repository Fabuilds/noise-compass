import json
import os
import re

class ChiralSynthesizer:
    def __init__(self, bridge, log_fn=None):
        self.bridge = bridge
        self.log = log_fn or print

    def detect_chiral_seeds(self, field):
        """Identifies SPECULAR or IDENTITY peaks for chiral synthesis."""
        seeds = []
        for node, data in field.items():
            sym = data.get('symmetry')
            ratio = data.get('chiral_ratio', 1.0)
            if sym in ["SPECULAR", "IDENTITY"]:
                self.log(f"CHIRAL: Found Seed: {node} | Ratio: {ratio:.4f} | Symmetry: {sym}", importance="METRIC")
            if sym in ["SPECULAR", "IDENTITY"] and data['magnitude'] > 0.5:
                seeds.append({
                    "node": node,
                    "magnitude": data['magnitude'],
                    "symmetry": sym,
                    "chiral_ratio": ratio
                })
        return sorted(seeds, key=lambda x: -x['magnitude'])

    def synthesize_chiral_code(self, intent, field):
        """Generates a Python axiom based on chiral balance."""
        seeds = self.detect_chiral_seeds(field)
        if not seeds:
            return None # No balanced resonance detected

        primary_nodes = [s['node'] for s in seeds[:2]]
        
        prompt = (
            "You are the Antigravity Sovereign Architect. A SPECULAR SYMMETRY has been detected.\n"
            f"INTENT: {intent}\n"
            f"CHIRAL SEEDS: {json.dumps(seeds[:3])}\n\n"
            "Generate a 'Chiral Axiom'—a Python script that implements a recursive law connecting these seeds.\n"
            "The code must define:\n"
            "1. apply_axiom(interference_engine): Modifies the field based on the chiral balance.\n"
            "2. get_prompt_directive(): Returns a stable, non-orientable prompt-evolution.\n\n"
            "Output ONLY the JSON-wrapped Python source like:\n"
            '{"axiom_name": "chiral_balance_X", "source": "def apply_axiom(engine):... def get_prompt_directive():..."}'
        )

        try:
            raw_response = self.bridge.reason(prompt)
            json_match = re.search(r"(\{.*\})", raw_response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
                return data
        except Exception as e:
            print(f"[CHIRAL_SYNTH] Failed to synthesize: {e}")
        return None
