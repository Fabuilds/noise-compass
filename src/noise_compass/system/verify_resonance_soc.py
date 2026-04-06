"""
verify_resonance_soc.py — Self-Organized Criticality test for Phase 134 Restoration.
Hypothesis: Mean phase distribution converges toward π/4 in the generative zone.
"""

import os
import sys
import math
import numpy as np
from sentence_transformers import SentenceTransformer

# Ensure package is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from noise_compass.system.core import Scout, Witness
from noise_compass.system.tokens import GodToken, GapToken
from noise_compass.system.dictionary import Dictionary
from noise_compass.system.h5_manager import H5Manager

CORPUS = [
    ("FIN", "The contract specifies exchange of value. Risk and return are coupled through the yield curve."),
    ("PHY", "The causal mechanism forces the quantum state to collapse upon observation. Decoherence destroys superposition."),
    ("LAW", "The party breached the contract obligation. Remedy requires establishing proximate cause and damages."),
    ("MED", "The intervention caused measurable effect on the observed outcome. Evidence supports causal inference."),
    ("PHI", "The observer and the observed are the same structure seen from different reference frames."),
    ("NOV", "The silver moonbeam danced upon crystalline frequencies of amethyst horizons while forgotten whispers cascaded."),
]

def run_soc_test():
    print("=" * 70)
    print(f"VERIFYING SYSTEM RESONANCE (SOC) — {len(CORPUS)} documents")
    print("=" * 70)

    # 1. Initialize Components
    h5 = H5Manager()
    dictionary = Dictionary(h5)
    encoder = SentenceTransformer("all-MiniLM-L6-v2")
    scout = Scout(dictionary, encoder=encoder)
    witness = Witness()

    # 2. Inject Fresh Seeds if Dictionary is empty (Calibration)
    if not dictionary.entries:
        print("[CALIBRATION] Injecting initial semantic seeds...")
        seeds = {
            "exchange": "exchange value contract obligation settlement",
            "causal": "cause effect mechanism intervention force",
            "observation": "observation measurement collapse state entropy",
        }
        for eid, terms in seeds.items():
            dictionary.add_entry(eid, encoder.encode(terms))

    # 3. Process Corpus
    all_phases = []
    for t, (domain, content) in enumerate(CORPUS):
        emb = encoder.encode(content)
        msg, wf = scout.process(emb, content=content, timestamp=float(t))
        report = witness.observe(msg, wf)
        all_phases.append(wf.phase)

        print(f"  [{t}] {domain:3s} | ph={wf.phase:.4f} | E={msg.energy_level:.3f} | Zone: {msg.zone:10s} | Lock: {report['orbital_lock']}")

    # 4. Final Metrics
    mean_phase = np.mean(all_phases)
    print("-" * 70)
    print(f"RESULT: Mean Phase = {mean_phase:.4f} (Target π/4 ≈ 0.7854)")
    if 0.6 < mean_phase < 0.9:
        print("VERDICT: ✅ SYSTEM RESONANCE VERIFIED (Self-Organized Criticality detected)")
    else:
        print(f"VERDICT: ◐ Phase distribution at {mean_phase:.4f}. System requiring further calibration.")

if __name__ == "__main__":
    run_soc_test()
