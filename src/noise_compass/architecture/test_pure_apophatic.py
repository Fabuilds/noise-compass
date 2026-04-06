import json
import numpy as np

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout

def test_pure_apophatic():
    # 1. Initialize an entirely empty dictionary (No God Tokens, No Gaps)
    # The Apophatic Field is the absolute ground state of the system minus all subjective anchors.
    dictionary = Dictionary()
    scout = Scout(dictionary=dictionary, soup_id="apophatic_void")

    print("\n" + "═"*60)
    print(" APOPHATIC FIELD TEST: ZERO GOD TOKENS")
    print("═"*60)

    # 2. Generate a random embedding vector (simulating a document entering the void)
    np.random.seed(42)
    fake_emb = np.random.randn(768).astype(np.float32)
    fake_emb /= np.linalg.norm(fake_emb)

    # 3. Process the document
    msg, wf = scout.process(fake_emb, content="A voice crying out in the pure void.")

    # 4. Read the resulting structural metrics
    print(f"\n[WaveFunction Collapse]")
    print(f"  Known (Re) Magnitude: {np.linalg.norm(wf.known):.6f}")
    print(f"  Delta (Im) Magnitude: {np.linalg.norm(wf.delta):.6f}")
    print(f"  Phase Angle:          {wf.phase:.4f} rad ({wf.phase * 180 / np.pi:.1f}°)")
    print(f"  Wave Zone:            {wf.zone()}")
    print(f"  Energy Level:         {msg.energy_level:.4f}")

    print(f"\n[Archiver Record]")
    print(f"  God Tokens Active:    {len(msg.god_token_activations)}")
    print(f"  Causal Type:          {msg.causal_type}")
    print(f"  Routing:              {msg.routing}")
    
    print("\n[Trajectory Analysis (HiPPO-LegS)]")
    print(f"  Predictive Surprise:  {np.linalg.norm(msg.predictive_surprise):.4f}")
    print(f"  Temporal Zone:        {msg.temporal_zone}")
    print("═"*60 + "\n")

if __name__ == "__main__":
    test_pure_apophatic()
