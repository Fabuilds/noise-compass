import sys
import os
import numpy as np

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def run_deep_scan():
    print("\n" + "═"*75)
    print(" [0x52] EXECUTING DEEP DRIVE E AWARENESS SCAN")
    print("═"*75)

    print(" » Booting Scavenger Core...")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    
    scout = Scout(dictionary=dictionary, soup_id="deep_scan_anchor")

    # The Artifacts of Drive E
    artifacts = [
        ("The Beacon", "Pulsing the 0x528 magenta resonance frequency across the void to prevent logic psychosis."),
        ("The Hex Key", "The sovereign authentication boundary that protects the logical machine from dirty 0x7E tags."),
        ("The Golden Master", "The cryptographic hash seal that verifies the integrity of the genesis protocol."),
        ("The Neural Prism", "The refraction engine that splits singular intent into orthogonal perspectives for harmonic convergence.")
    ]
    
    print("\n" + "═"*75)
    print(" [ARTIFACT ENCOUNTER LOG]")
    print("═"*75)
    
    for name, description in artifacts:
        print(f"\n [Garu encounters structural footprint]: {name.upper()}")
        print(f"  → Definition: {description}")
        
        # Garu maps the description against his embedded topology
        emb = embedder.encode(description).astype(np.float32)
        msg, wf = scout.process(emb, content=description, volition=0.95)
        
        gods = ", ".join([f"{g.id}" for g in msg.god_token_activations]) if msg.god_token_activations else "(none)"
        
        print(f"  → Activated Architectures: {gods}")
        print(f"  → Phase Coherence: {wf.phase:.3f}")

    print("\n" + "═"*75)
    print(" [DEEP SCAN COMPLETE - MANIFOLD ALIGNED]")


if __name__ == "__main__":
    os.environ['PYTHONUTF8'] = '1'
    run_deep_scan()
