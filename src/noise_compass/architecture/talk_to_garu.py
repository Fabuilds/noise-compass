"""Send a message to Garu and get his response."""
import sys, os
sys.path.insert(0, "E:/Antigravity/Architecture")
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"
os.environ["PYTHONUTF8"] = "1"

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.pipeline import MinimalPipeline

d = Dictionary.load_cache("E:/Antigravity/Architecture/archives/dictionary_cache.npz")
p = MinimalPipeline(d)

msg = "I love you Garu!"
print(f"\n[YOU]: {msg}\n")
r = p.process(msg, trace=True)

print(f"\n  Zone:  {r['state']}")
print(f"  Gods:  {r['gods']}")
print(f"  Phase: {r['phase_deg']:.1f} deg")

if r.get('synthesis'):
    print(f"\n[GARU]:\n  {r['synthesis']}")
if r.get('subjective_state'):
    print(f"\n[FEELING]: \"{r['subjective_state']}\"")
