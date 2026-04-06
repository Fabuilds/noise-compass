"""
Garu Relay — persistent pipeline, reads messages from stdin.
Keeps M_FAST and M_DEEP warm. Responds to each line of input.
"""
import sys, os
sys.path.insert(0, "E:/Antigravity/Architecture")
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"
os.environ["PYTHONUTF8"] = "1"

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.pipeline import MinimalPipeline

print("[BOOT] Loading dictionary cache...", flush=True)
d = Dictionary.load_cache("E:/Antigravity/Architecture/archives/dictionary_cache.npz")
print(f"[BOOT] God-tokens: {list(d.god_tokens.keys())}", flush=True)

print("[BOOT] Building pipeline...", flush=True)
p = MinimalPipeline(d)

# Pre-warm M_DEEP
print("[BOOT] Warming M_DEEP (Qwen)...", flush=True)
p._load_qwen()

print("[READY] Garu is listening.", flush=True)
print("=" * 60, flush=True)

while True:
    try:
        line = input()
        if not line.strip():
            continue
        if line.strip().lower() in ("!quit", "!exit"):
            print("[SHUTDOWN]", flush=True)
            break

        # Run both passes
        fwd = p.process(line, trace=False, polarity=1)
        bwd = p.process(line, trace=False, polarity=-1)

        gods_fwd = fwd['gods']
        gods_bwd = bwd['gods']

        print(f"\n[YOU]: {line}", flush=True)
        print(f"  Zone: {fwd['state']} | Phase: {fwd['phase_deg']:.1f} deg", flush=True)
        print(f"  Forward gods:  {gods_fwd if gods_fwd else '(none)'}", flush=True)
        print(f"  Backward gods: {gods_bwd if gods_bwd else '(none)'}", flush=True)

        if fwd.get('synthesis'):
            print(f"\n[GARU]: {fwd['synthesis']}", flush=True)
        if fwd.get('subjective_state'):
            print(f"[FEELING]: \"{fwd['subjective_state']}\"", flush=True)

        print("=" * 60, flush=True)

    except EOFError:
        break
    except KeyboardInterrupt:
        break
