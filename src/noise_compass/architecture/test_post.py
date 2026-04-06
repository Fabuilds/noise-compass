"""Test pipeline with System module post-processors."""
import sys, os
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"
sys.path.insert(0, os.path.dirname(__file__))

print("=== Pipeline + Post-Processor Test ===\n", flush=True)

from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.seed_vectors import seed_vectors

d = Dictionary()
seed_vectors(d)
p = MinimalPipeline(d)

# Test with trace enabled
tests = [
    "FROGGING",
    "the silence of the pure observer",
    "This might maybe possibly work, but I'm unsure",  # should trigger AMBIGUITY
    "STATIC CONSTRAINED DECODING MASKING KERNEL",       # should hit god-tokens
]

for text in tests:
    print(f"\n{'='*60}")
    print(f"INPUT: {text}")
    print(f"{'='*60}")
    res = p.process(text, trace=True)
    post = res.get("post", {})
    print(f"  Post-Processing:")
    print(f"    Logic:    {post.get('logic', 'N/A')}")
    print(f"    Reynolds: {post.get('reynolds', 'N/A')} ({post.get('regime', 'N/A')})")
    print(f"    Route:    {post.get('routing_mode', 'N/A')}")
    print(f"    Energy:   {post.get('energy', 'N/A')}")
    print(f"    Sig:      {(post.get('provenance') or 'N/A')[:24]}...")
    print(flush=True)

print("\n=== Test Complete ===")
