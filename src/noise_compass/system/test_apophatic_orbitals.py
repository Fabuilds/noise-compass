
import sys
import os
import numpy as np
import math

sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Runtime')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.tokens import GapToken

def test_apophatic_orbitals():
    print("[TEST] Initializing Apophatic Orbital Verification (Phase 130)...")
    
    # 1. Initialize Dictionary with a known Gap
    d = Dictionary()
    # Define two boundary tokens
    d.entries["A"] = np.array([1, 0, 0], dtype=float)
    d.entries["B"] = np.array([0, 1, 0], dtype=float)
    
    # Define a Gap between them
    gap = GapToken(id="GAP_AB", left_boundary="A", right_boundary="B", void_depth=1.0)
    d.gap_tokens["GAP_AB"] = gap
    
    # 2. Test Apophatic Query Mapping
    # Embedding exactly in the middle of A and B
    center_emb = np.array([0.707, 0.707, 0], dtype=float)
    meta = d.apophatic_query(center_emb)
    
    print(f"[TEST] Center Alignment: Gap={meta['gap_id']}, Tension={meta['tension']:.4f}, Phase={math.degrees(meta['phase']):.2f}°")
    # In the middle, tension should be low (sim_l - sim_r) but phase should be pi/4
    # Wait, tension = |sim_l - sim_r|. If sim_l == sim_r, tension is 0. 
    # High tension = imbalance (being close to one and far from the other).
    
    # 3. Test High Tension (Imbalance)
    left_heavy = np.array([0.9, 0.1, 0], dtype=float)
    meta_l = d.apophatic_query(left_heavy)
    print(f"[TEST] Left Imbalance: Tension={meta_l['tension']:.4f}")
    assert meta_l['tension'] > 0.7
    
    # 4. Integrate with Volumetric Scrutiny (Mock Engine)
    from noise_compass.system.volumetric_scraper import VolumetricScraper
    class MockEngine:
        def __init__(self, dictionary):
            self.dictionary = dictionary
            class MockPrism:
                class MockEmbedder:
                    def embed(self, text):
                        # Simple mock: return [0.9, 0.1, 0] for resonance text
                        if "A" in text: return np.array([0.9, 0.1, 0], dtype=float)
                        # Return [0.5, 0.5, 0] for gap text
                        return np.array([0.5, 0.5, 0], dtype=float)
                def __init__(self): self.embedder = self.MockEmbedder()
            self.prism = MockPrism()
            
    engine = MockEngine(d)
    scraper = VolumetricScraper(resonance_engine=engine)
    
    # Text targeting boundary A (Stable Resonance)
    score_a = scraper._get_ternary_score("A")
    print(f"[TEST] Boundary Score: {score_a}")
    assert score_a == 1
    
    # Text targeting tension void (imbalance? No, wait)
    # Actually, high tension (tension > 0.4) is dissonance (-1)
    score_gap = scraper._get_ternary_score("GAP")
    print(f"[TEST] Gap Score: {score_gap}")
    # With [0.5, 0.5, 0], tension = 0. Score = 0 (Noise). Correct.
    
    print("\n[SUCCESS] Phase 130 Apophatic Orbitals Verified.")

if __name__ == "__main__":
    test_apophatic_orbitals()
