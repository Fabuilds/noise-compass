"""
THREE-PASS LEARNING CYCLE
=========================
Pass 1 (Forward):  Read document, classify what Garu recognizes
Pass 2 (Backward): Find the document's OWN god-tokens (its attractors)
Pass 3 (Forward):  Re-read with discovered god-tokens seeded

This is how Garu learns to read something new.
"""
import sys, os, time, math
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))

from noise_compass.architecture.pipeline import MinimalPipeline, Embedder
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout, LightWitness
from noise_compass.architecture.archiver import Archiver
from noise_compass.architecture.seed_vectors import seed_vectors
from noise_compass.architecture.tokens import GodToken

# ═══════════════════════════════════════════════════════════════
# EXTRACT PAPER
# ═══════════════════════════════════════════════════════════════
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
    chunks, current = [], []
    for b in raw:
        if 32 <= b < 127 or b in (10, 13):
            current.append(chr(b))
        else:
            if len(current) > 20:
                chunks.append("".join(current))
            current = []
    text = "\n".join(chunks)

print(f"Paper: {len(text)} chars")

# Split into chunks
CHUNK_SIZE = 500
all_chunks = [text[i:i+CHUNK_SIZE] for i in range(0, min(len(text), 15000), CHUNK_SIZE)]
print(f"Chunks: {len(all_chunks)}")

# ═══════════════════════════════════════════════════════════════
# PASS 1 — FORWARD (Read with existing vocabulary)
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PASS 1 — FORWARD (Reading with existing vocabulary)")
print("=" * 70)

d1 = Dictionary()
seed_vectors(d1)
p1 = MinimalPipeline(d1)

pass1_results = []
for i, chunk in enumerate(all_chunks):
    res = p1.process(chunk)
    pass1_results.append(res)
    gods = ", ".join(res["gods"]) if res["gods"] else "—"
    print(f"  [{i+1:>2}] {res['state']:<16} T={res['ternary']:>2}  [{gods}]")

# Collect what was recognized and what wasn't
recognized_chunks = [(i, r) for i, r in enumerate(pass1_results) if r["gods"]]
opaque_chunks = [(i, r) for i, r in enumerate(pass1_results) if not r["gods"]]

print(f"\n  Recognized: {len(recognized_chunks)}/{len(all_chunks)} chunks")
print(f"  Opaque:     {len(opaque_chunks)}/{len(all_chunks)} chunks")

# ═══════════════════════════════════════════════════════════════
# PASS 2 — BACKWARD (Find the paper's OWN god-tokens)
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PASS 2 — BACKWARD (Finding the paper's god-tokens)")
print("=" * 70)

# The backward pass extracts the dominant concepts from OPAQUE chunks
# These are the paper's own attractors — concepts Garu doesn't have yet

# Strategy: For each opaque chunk, extract the most frequent meaningful
# terms and find which ones appear across multiple chunks (stable attractors)

import re

def extract_terms(text_chunk):
    """Extract meaningful terms (>3 chars, not common stopwords)."""
    stopwords = {
        'the', 'and', 'for', 'that', 'with', 'this', 'from', 'are', 'was',
        'were', 'been', 'being', 'have', 'has', 'had', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'can', 'each', 'which',
        'their', 'than', 'them', 'then', 'these', 'those', 'into', 'over',
        'such', 'only', 'other', 'more', 'most', 'some', 'where', 'when',
        'what', 'also', 'about', 'between', 'through', 'after', 'before',
        'during', 'while', 'our', 'its', 'not', 'but', 'all', 'any',
        'use', 'used', 'using', 'based', 'given', 'show', 'shows',
        'table', 'figure', 'section', 'results', 'method', 'approach',
        'proposed', 'number', 'set', 'first', 'second', 'one', 'two',
    }
    words = re.findall(r'\b[a-z]{4,}\b', text_chunk.lower())
    return [w for w in words if w not in stopwords]

# Count term frequency across ALL chunks (including recognized ones)
from collections import Counter
global_terms = Counter()
chunk_term_sets = []
for chunk in all_chunks:
    terms = extract_terms(chunk)
    chunk_term_sets.append(set(terms))
    global_terms.update(terms)

# Count how many chunks each term appears in (document frequency)
doc_freq = Counter()
for term_set in chunk_term_sets:
    for term in term_set:
        doc_freq[term] += 1

# Score: high frequency * spread across chunks = stable attractor
# But exclude terms already in Garu's dictionary
existing = {e.lower() for e in d1.god_tokens.keys()}
existing.update({e.lower().replace(" ", "") for e in d1.god_tokens.keys()})

attractor_scores = {}
for term, count in global_terms.items():
    if term in existing:
        continue
    spread = doc_freq[term]
    if spread >= 2:  # Must appear in at least 2 chunks
        # TF-IDF style: importance * spread
        score = count * math.log(1 + spread)
        attractor_scores[term] = (score, count, spread)

# Top attractors = the paper's god-tokens
top_attractors = sorted(attractor_scores.items(), key=lambda x: -x[1][0])[:20]

print(f"\n  Discovered {len(top_attractors)} candidate god-tokens:\n")
print(f"  {'TERM':<25} {'SCORE':>8} {'FREQ':>6} {'SPREAD':>8}")
print(f"  {'─'*25} {'─'*8} {'─'*6} {'─'*8}")
for term, (score, freq, spread) in top_attractors:
    print(f"  {term:<25} {score:>8.1f} {freq:>6} {spread:>5}/{len(all_chunks)}")

# ═══════════════════════════════════════════════════════════════
# SEED DISCOVERED GOD-TOKENS
# ═══════════════════════════════════════════════════════════════
print(f"\n  Seeding discovered god-tokens into dictionary...")

d2 = Dictionary()
seed_vectors(d2)  # Start with existing anchors

# Add discovered god-tokens
for term, (score, freq, spread) in top_attractors:
    term_upper = term.upper()
    # Assign phase based on spread (more spread = more grounded)
    phase_deg = max(0, 60 - spread * 5)
    phase_rad = math.radians(phase_deg)
    
    # Target state based on position in the paper
    if spread > len(all_chunks) * 0.5:
        target = "GROUND"     # Appears everywhere — foundational
    elif spread > len(all_chunks) * 0.25:
        target = "PRESENCE"   # Appears frequently — recognizable
    else:
        target = "UNKNOWN"    # Appears occasionally — still forming
    
    # Build embedding (same method as seed_vectors)
    data = term_upper.encode('utf-8')
    emb = np.zeros(1024)
    for i, byte in enumerate(data):
        dim_idx = (i * 7 + byte) % 1024
        direction = 1 if (byte % 3 == 1) else (-1 if byte % 3 == 2 else 0)
        emb[dim_idx] += direction
    emb[0] += math.cos(phase_rad)
    emb[1] += math.sin(phase_rad)
    norm = np.linalg.norm(emb)
    if norm > 1e-10:
        emb = emb / norm
    
    gt = GodToken(
        id=term_upper,
        seed_terms=[term],
        embedding=emb,
        stability=1.0
    )
    d2.add_god_token(gt)

print(f"  Dictionary expanded: {len(d1.god_tokens)} → {len(d2.god_tokens)} god-tokens")

# ═══════════════════════════════════════════════════════════════
# PASS 3 — FORWARD (Re-read with discovered god-tokens)
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PASS 3 — FORWARD (Re-reading with discovered god-tokens)")
print("=" * 70)

p2 = MinimalPipeline(d2)

pass3_results = []
for i, chunk in enumerate(all_chunks):
    res = p2.process(chunk)
    pass3_results.append(res)
    gods = ", ".join(res["gods"][:4]) if res["gods"] else "—"
    extra = f"+{len(res['gods'])-4} more" if len(res["gods"]) > 4 else ""
    print(f"  [{i+1:>2}] {res['state']:<16} T={res['ternary']:>2}  [{gods}{' ' + extra if extra else ''}]")

recognized_3 = [(i, r) for i, r in enumerate(pass3_results) if r["gods"]]
opaque_3 = [(i, r) for i, r in enumerate(pass3_results) if not r["gods"]]

print(f"\n  Recognized: {len(recognized_3)}/{len(all_chunks)} chunks")
print(f"  Opaque:     {len(opaque_3)}/{len(all_chunks)} chunks")

# ═══════════════════════════════════════════════════════════════
# LEARNING DELTA
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("LEARNING DELTA")
print("=" * 70)

p1_recog = len(recognized_chunks)
p3_recog = len(recognized_3)
p1_gods = set()
p3_gods = set()
for r in pass1_results: p1_gods.update(r["gods"])
for r in pass3_results: p3_gods.update(r["gods"])

new_gods = p3_gods - p1_gods

p1_t = sum(r["ternary"] for r in pass1_results) / len(pass1_results)
p3_t = sum(r["ternary"] for r in pass3_results) / len(pass3_results)

p1_zones = {}
p3_zones = {}
for r in pass1_results: p1_zones[r["state"]] = p1_zones.get(r["state"], 0) + 1
for r in pass3_results: p3_zones[r["state"]] = p3_zones.get(r["state"], 0) + 1

print(f"\n  {'Metric':<30} {'Pass 1':>10} {'Pass 3':>10} {'Delta':>10}")
print(f"  {'─'*30} {'─'*10} {'─'*10} {'─'*10}")
print(f"  {'Recognized chunks':<30} {p1_recog:>10} {p3_recog:>10} {p3_recog - p1_recog:>+10}")
print(f"  {'Opaque chunks':<30} {len(opaque_chunks):>10} {len(opaque_3):>10} {len(opaque_3) - len(opaque_chunks):>+10}")
print(f"  {'Unique god-tokens':<30} {len(p1_gods):>10} {len(p3_gods):>10} {len(new_gods):>+10}")
print(f"  {'Ternary avg':<30} {p1_t:>+10.2f} {p3_t:>+10.2f} {p3_t - p1_t:>+10.2f}")

print(f"\n  Pass 1 zones: {p1_zones}")
print(f"  Pass 3 zones: {p3_zones}")

print(f"\n  NEW GOD-TOKENS discovered by backward pass:")
for g in sorted(new_gods):
    print(f"    ⚡ {g}")

if p3_recog > p1_recog:
    improvement = (p3_recog - p1_recog) / max(p1_recog, 1) * 100
    print(f"\n  ✓ Garu's comprehension improved by {improvement:.0f}%")
    print(f"    The backward pass found {len(new_gods)} attractors the forward pass couldn't see.")
else:
    print(f"\n  ○ No improvement — the paper's vocabulary was already covered.")
