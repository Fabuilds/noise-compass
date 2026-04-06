"""
FORWARD + BACKWARD PASS — Proper Apophatic Field Test
Forward:  polarity=+1 (cataphatic — what IS in the data)
Backward: polarity=-1 (apophatic — the Möbius twist, same data, inverted processing)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Extract paper text
pdf_path = "E:/Research_Papers/GoogleAISTATIC.pdf"
text = ""
try:
    from pypdf import PdfReader
    for page in PdfReader(pdf_path).pages:
        t = page.extract_text()
        if t: text += t + "\n"
except ImportError:
    with open(pdf_path, "rb") as f:
        raw = f.read()
    chunks = []
    current = []
    for b in raw:
        if 32 <= b < 127 or b in (10, 13):
            current.append(chr(b))
        else:
            if len(current) > 20:
                chunks.append("".join(current))
            current = []
    text = "\n".join(chunks)

print(f"Paper: {len(text)} chars")

from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.seed_vectors import seed_vectors

d = Dictionary()
seed_vectors(d)
p = MinimalPipeline(d)

chunk_size = 500
chunks = [text[i:i+chunk_size] for i in range(0, min(len(text), 10000), chunk_size)]

# ═══════════════════════════════════════════════
# FORWARD PASS (polarity=+1)
# ═══════════════════════════════════════════════
print("\n" + "=" * 60)
print("FORWARD PASS (polarity=+1) — What IS in the data")
print("=" * 60)

fwd = []
for i, chunk in enumerate(chunks):
    res = p.process(chunk, polarity=1)
    fwd.append(res)
    gods = ", ".join(res["gods"]) if res["gods"] else "—"
    print(f"  [{i+1:>2}] {res['state']:<20} T={res['ternary']:>2}  [{gods}]")

# ═══════════════════════════════════════════════
# BACKWARD PASS (polarity=-1, Möbius twist)
# ═══════════════════════════════════════════════
print("\n" + "=" * 60)
print("BACKWARD PASS (polarity=-1) — The Möbius Twist")
print("=" * 60)

bwd = []
for i, chunk in enumerate(chunks):
    res = p.process(chunk, polarity=-1)
    bwd.append(res)
    gods = ", ".join(res["gods"]) if res["gods"] else "—"
    print(f"  [{i+1:>2}] {res['state']:<20} T={res['ternary']:>2}  [{gods}]")

# ═══════════════════════════════════════════════
# APOPHATIC FIELD ANALYSIS
# ═══════════════════════════════════════════════
print("\n" + "=" * 60)
print("APOPHATIC FIELD ANALYSIS")
print("=" * 60)

fwd_z, bwd_z = {}, {}
fwd_g, bwd_g = {}, {}
for r in fwd:
    fwd_z[r["state"]] = fwd_z.get(r["state"], 0) + 1
    for g in r["gods"]: fwd_g[g] = fwd_g.get(g, 0) + 1
for r in bwd:
    bwd_z[r["state"]] = bwd_z.get(r["state"], 0) + 1
    for g in r["gods"]: bwd_g[g] = bwd_g.get(g, 0) + 1

print(f"\n  FORWARD ZONES:  {fwd_z}")
print(f"  BACKWARD ZONES: {bwd_z}")

print(f"\n  ZONE TRANSITIONS (Forward → Backward):")
transitions = {}
for f, b in zip(fwd, bwd):
    key = f"{f['state']:<20} → {b['state']}"
    transitions[key] = transitions.get(key, 0) + 1
for t, c in sorted(transitions.items(), key=lambda x: -x[1]):
    print(f"    {t}: {c}")

print(f"\n  FORWARD ANCHORS:")
for g, c in sorted(fwd_g.items(), key=lambda x: -x[1])[:10]:
    print(f"    {g}: {'█' * c} ({c})")

print(f"\n  BACKWARD ANCHORS (apophatic surface):")
if bwd_g:
    for g, c in sorted(bwd_g.items(), key=lambda x: -x[1])[:10]:
        print(f"    {g}: {'█' * c} ({c})")
else:
    print("    (complete void)")

# Invariant analysis
fwd_set = set(fwd_g.keys())
bwd_set = set(bwd_g.keys())
print(f"\n  FORWARD-ONLY:  {sorted(fwd_set - bwd_set) if fwd_set - bwd_set else '∅'}")
print(f"  BACKWARD-ONLY: {sorted(bwd_set - fwd_set) if bwd_set - fwd_set else '∅'}")
print(f"  INVARIANT:     {sorted(fwd_set & bwd_set) if fwd_set & bwd_set else '∅'}")

# Ternary comparison  
fwd_t = sum(r["ternary"] for r in fwd) / len(fwd)
bwd_t = sum(r["ternary"] for r in bwd) / len(bwd)
print(f"\n  TERNARY: Forward={fwd_t:+.2f}  Backward={bwd_t:+.2f}  Delta={fwd_t - bwd_t:+.2f}")

# Per-chunk comparison
print(f"\n  PER-CHUNK SYMMETRY:")
symmetric = 0
for i, (f, b) in enumerate(zip(fwd, bwd)):
    if f["state"] == b["state"]:
        symmetric += 1
    elif set(f["gods"]) & set(b["gods"]):
        print(f"    Chunk {i+1}: SHARED anchors across twist: {set(f['gods']) & set(b['gods'])}")

print(f"\n  Symmetric chunks: {symmetric}/{len(fwd)} ({100*symmetric//len(fwd)}%)")

if bwd_set - fwd_set:
    print(f"\n  ⚡ APOPHATIC DISCOVERY: Reversal revealed anchors invisible to forward pass!")
    print(f"     These exist only in the negative space: {sorted(bwd_set - fwd_set)}")
elif bwd_g:
    print(f"\n  The Möbius surface shows structure on both sides.")
else:
    print(f"\n  The backward pass sees void — the apophatic field is empty for this paper.")
