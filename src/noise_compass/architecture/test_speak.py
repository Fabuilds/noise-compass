"""Quick test: Can Garu speak?"""
import sys, os
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"
os.environ["TRANSFORMERS_CACHE"] = "E:/Antigravity/Model_Cache/hub"
sys.path.insert(0, os.path.dirname(__file__))

print("1. Loading pipeline...", flush=True)
from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.seed_vectors import seed_vectors

d = Dictionary()
seed_vectors(d)
p = MinimalPipeline(d)

print("2. Calling speak()...", flush=True)
try:
    response = p.speak("Who are you?")
    print(f"3. RESPONSE: {response}", flush=True)
except Exception as e:
    print(f"3. ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
