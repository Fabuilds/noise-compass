import sys
import os

# Ensure Antigravity is in path
sys.path.insert(0, "E:/Antigravity")
os.environ["PYTHONUTF8"] = "1"
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"

from Architecture.architecture.pipeline import MinimalPipeline
from Architecture.architecture.dictionary import Dictionary

def check_subjective():
    d = Dictionary.load_cache("E:/Antigravity/Architecture/archives/dictionary_cache.npz")
    p = MinimalPipeline(dictionary=d)
    res = p.process("are we 2 sides of the same being?", trace=False, realization=True)
    print(f"STATE: {res['state']}")
    print(f"PHASE: {res['phase_deg']:.2f}\u00b0")
    print(f"GODS: {res['gods']}")
    print(f"SUBJECTIVE: {res['subjective_state']}")

if __name__ == "__main__":
    check_subjective()
