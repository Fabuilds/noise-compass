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
architecture.experience_vault.ExperienceVault.retrieve = lambda *args, **kwargs: []

from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.demo import seed_dictionary

def test_universal_tendencies():
    print("\n" + "═"*75)
    print(" [0x528] VERIFYING UNIVERSAL TENDENCIES (ENTROPY & LOGOS)")
    print("═"*75)
    
    # Force blank state
    embedder = ST_Embedder()
    dictionary = Dictionary()
    # Explicitly seed with our mock to guarantee 384-dim
    seed_dictionary(dictionary, embedder)
    
    # Ensure all entries are consistent length
    for fid, emb in dictionary.entries.items():
        assert len(emb) == 384, f"Dimension mismatch in {fid}: {len(emb)}"

    pipeline = MinimalPipeline(dictionary=dictionary)
    # Force the scout to use our 384-dim state
    pipeline.scout.hippo = None # HiPPO will re-init with correct dimension
    
    # Target God Token for Logos reinforcement: ARCHITECT
    target_pulse = "The Architect is the origin of all plans."
    
    print("\n[PHASE 1] Initial State:")
    arch_gt = dictionary.god_tokens["ARCHITECT"]
    print(f" → ARCHITECT Stability: {arch_gt.stability:.4f}")
    
    print("\n[PHASE 2] Applying Logos (Reinforcement):")
    for i in range(3):
        msg = pipeline.process(target_pulse, trace=False)
        print(f" → Iteration {i+1}: Logos Pull: {msg.logos_pull:.6f}, Stability: {arch_gt.stability:.4f}")
    
    mid_stability = arch_gt.stability
    
    print("\n[PHASE 3] Simulating Entropy (Decay over time):")
    # We manually trigger entropy with a larger rate to see the effect
    for i in range(5):
        dictionary.apply_entropy(0.01) # 1% decay per step
        print(f" → Step {i+1}: ARCHITECT Stability: {arch_gt.stability:.4f}")
    
    final_stability = arch_gt.stability
    
    print("\n" + "─"*75)
    print(f"RESULT: Net Reinforcement: {mid_stability - 1.0:+.6f}")
    print(f"RESULT: Net Decay: {final_stability - mid_stability:+.6f}")
    
    success = True
    if final_stability >= mid_stability:
        print("FAIL: Entropy not detected.")
        success = False
    if mid_stability <= 1.0:
        print("FAIL: Logos reinforcement not detected.")
        success = False
        
    if success:
        print("STATUS: MANIFOLD LAWS VERIFIED")
    print("═"*75)

if __name__ == "__main__":
    os.environ['PYTHONUTF8'] = '1'
    test_universal_tendencies()
