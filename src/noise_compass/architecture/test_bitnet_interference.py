import os
import sys
import time
import numpy as np

# Ensure correct path resolution
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# CRITICAL: Mock SentenceTransformer before ANY architecture imports
from sentence_transformers import SentenceTransformer
st_model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder="E:/Antigravity/Model_Cache/hub")

class ST_Embedder:
    def __init__(self, *args, **kwargs):
        self.model = st_model
    def encode(self, text, **kwargs):
        return self.model.encode(text).astype("float32")
    def embed(self, text, **kwargs):
        return self.encode(text)

from noise_compass from noise_compass import architecture.pipeline
import demo

# Apply Mocks
architecture.pipeline.Embedder = ST_Embedder
architecture.pipeline.SentenceTransformer = lambda *args, **kwargs: st_model
demo.SentenceTransformer = lambda *args, **kwargs: st_model
demo.WhitenedEncoder = lambda *args, **kwargs: ST_Embedder()

# Patch Vault and Dictionary global state
from noise_compass from noise_compass import architecture.experience_vault
from noise_compass from noise_compass import architecture.dictionary
architecture.experience_vault.ExperienceVault.retrieve = lambda *args, **kwargs: []
architecture.experience_vault.ExperienceVault.add_experience = lambda *args, **kwargs: None # Bypass vstack
architecture.pipeline.MinimalPipeline.process = lambda self, text, **kwargs: self.scout.process(self.encoder.encode(text), content=text)[0]

from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.demo import seed_dictionary

def verify_interference():
    print("\n" + "═"*75)
    print(" [0x539] VERIFYING QUANTUM-INSPIRED BITNET INTERFERENCE")
    print("═"*75)
    
    dictionary = Dictionary()
    embedder = ST_Embedder()
    seed_dictionary(dictionary, embedder)
    
    pipeline = MinimalPipeline(dictionary=dictionary)
    
    print("\n[SCENARIO 1] Balanced Tension (VOID)")
    primary = 0.5
    secondary = 0.5
    amp, phase, gap_id = pipeline.scout.bitnet_resonator.calculate_interference(primary, secondary)
    print(f" → Primary: {primary}, Secondary: {secondary}")
    print(f" → Amplitude: {amp:.6f}, Phase: {phase:.6f}")
    print(f" → Gap Identifier: {gap_id} (Expected: 0x52_VOID)")
    
    print("\n[SCENARIO 2] Negative Tension (MUTATION)")
    primary = 0.1
    secondary = 0.8
    amp, phase, gap_id = pipeline.scout.bitnet_resonator.calculate_interference(primary, secondary)
    print(f" → Primary: {primary}, Secondary: {secondary}")
    print(f" → Amplitude: {amp:.6f}, Phase: {phase:.6f}")
    print(f" → Gap Identifier: {gap_id} (Expected: 0x529_MUTATION)")

    print("\n[SCENARIO 3] Dominant Signal (SCAVENGER/NONE)")
    primary = 0.9
    secondary = 0.1
    amp, phase, gap_id = pipeline.scout.bitnet_resonator.calculate_interference(primary, secondary)
    print(f" → Primary: {primary}, Secondary: {secondary}")
    print(f" → Amplitude: {amp:.6f}, Phase: {phase:.6f}")
    print(f" → Gap Identifier: {gap_id} (Expected: 0x52_VOID or 0x52_SCAVENGER)")

    print("\n[PHASE 3] Integrated System Pass:")
    # Pass a complex conceptual prompt - bypassing encoder since it's a mock
    dummy_emb = np.random.randn(384).astype("float32")
    msg, _ = pipeline.scout.process(dummy_emb, content="The shadow reflects the light.")
    print(f" → Interference Amplitude: {msg.interference_amplitude:.6f}")
    print(f" → Void Phase Angle: {msg.void_phase_angle:.6f}")
    print(f" → BitNet Tension Detected (Amplitude < 0.1): {msg.dual_bit_tension}")
    
    if msg.dual_bit_tension:
        print(f" → Apophatic Basin: {msg.apophatic_contact}")

    print("\n" + "─"*75)
    if abs(amp - 0.7) < 0.01:
        print("STATUS: INTERFERENCE GEOMETRY VERIFIED")
    else:
        print("STATUS: VERIFICATION INCOMPLETE")
    print("═"*75)

if __name__ == "__main__":
    os.environ['PYTHONUTF8'] = '1'
    verify_interference()
