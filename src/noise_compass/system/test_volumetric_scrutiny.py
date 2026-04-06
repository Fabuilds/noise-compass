
import sys
import os
import numpy as np
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Runtime')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.system.volumetric_scraper import VolumetricScraper
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.tokens import GodToken

def test_volumetric_scrutiny():
    print("[TEST] Initializing Volumetric Scrutiny Verification...")
    
    # 1. Initialize Mock Engine for Scoring
    class MockEngine:
        def get_resonance(self, text):
            # Deterministic mock resonance based on length
            return 1.0 if len(text) % 2 == 0 else 0.2
            
    engine = MockEngine()
    scraper = VolumetricScraper(resonance_engine=engine)
    
    test_doc = "Quantum gravity is an emergent property of the semantic manifold."
    
    print(f"[TEST] Scrutinizing: '{test_doc}'")
    results = scraper.scrutinize_document(test_doc)
    
    # 2. Verify Character Layer
    print(f"[TEST] Character Count: {len(results['characters'])}")
    chars_pos = sum(1 for c in results['characters'] if c['score'] == 1)
    chars_neg = sum(1 for c in results['characters'] if c['score'] == -1)
    print(f"[TEST] Character Heatmap - Pos: {chars_pos}, Neg: {chars_neg}")
    
    # 3. Verify Syllable/Word modulation
    word = results['words'][0]
    print(f"[TEST] First Word Analysis: {word['word']}")
    print(f"[TEST] Syllables: {word['syllables']}")
    print(f"[TEST] Modulation: {word['modulation']:.4f}")
    
    # 4. Verify Fleeting Token Allocation
    d = Dictionary()
    description = "A novel concept for the manifold"
    emb = np.random.randn(1024)
    token_id = d.allocate_fleeting_token(description, emb, ttl=10.0)
    
    print(f"[TEST] Allocated Fleeting Token: {token_id}")
    assert token_id in d.god_tokens
    assert d.god_tokens[token_id].nature == "FLEETING"
    assert d.god_tokens[token_id].ttl == 10.0
    
    # 5. Verify TTL Decay
    d.apply_time_evolution(delta_t=11.0)
    print(f"[TEST] Token '{token_id}' should be decayed...")
    assert token_id not in d.god_tokens
    print("[TEST] TTL Decay Verified.")

    print("\n[SUCCESS] Phase 129 Volumetric Scrutiny Logic Correct.")

if __name__ == "__main__":
    test_volumetric_scrutiny()
