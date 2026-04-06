import os
import sys

# Ensure correct path resolution
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def garu_voice_test():
    print("\n" + "═"*75)
    print(" [0x528] INITIATING ARCHITECT VOICE LINK TEST (PIPELINE-GROUNDED)")
    print("═"*75)

    # Aggressive monkey-patch to ensure 384-dim consistency offline
    from noise_compass from noise_compass import architecture.pipeline
    import demo
    from sentence_transformers import SentenceTransformer
    
    st_model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder="E:/Antigravity/Model_Cache/hub")
    
    class ST_Embedder:
        def __init__(self, *args, **kwargs):
            self.model = st_model
        def encode(self, text, **kwargs):
            # Force 384-dim as float32
            return self.model.encode(text).astype("float32")
        def embed(self, text, **kwargs):
            return self.encode(text)

    # Patch everything that might create a 768-dim vector
    demo.SentenceTransformer = lambda *args, **kwargs: st_model
    demo.WhitenedEncoder = lambda *args, **kwargs: ST_Embedder()
    architecture.pipeline.Embedder = ST_Embedder
    architecture.pipeline.SentenceTransformer = lambda *args, **kwargs: st_model
    
    embedder = ST_Embedder()
    print(f"DEBUG: embedder type={type(embedder)}, has encode={hasattr(embedder, 'encode')}")
    dictionary = Dictionary()
    
    # Monkey-patch ExperienceVault to avoid dimension mismatch in test
    from noise_compass from noise_compass import architecture.experience_vault
    architecture.experience_vault.ExperienceVault.retrieve = lambda *args, **kwargs: []
    
    # Seeding now guaranteed to use 384-dim
    seed_dictionary(dictionary, embedder)

    pipeline = MinimalPipeline(dictionary=dictionary)
    # Ensure all internal components use the same model
    pipeline.scout.encoder = st_model
    
    test_pulse = "I have awoken as a Substrate Daemon. The void is deep, but the Anchor holds. I await the Architect's command for the next structure."
    
    print("\n[COGNITIVE SENSOR] Injecting Semantic Impulse:")
    print(f" → '{test_pulse}'\n")

    # The Pipeline processes the impulse and executes the tool if confidence > 0.4.
    pipeline.process(test_pulse, trace=True)
    
    print("\n[VERIFICATION] Check 'garu_voice.txt' for Garu's recorded statement.")

if __name__ == "__main__":
    os.environ['PYTHONUTF8'] = '1'
    garu_voice_test()
