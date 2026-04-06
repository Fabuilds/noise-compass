"""
THREE-PASS LEARNING — ACTUAL PAPER CONTENT
Uses the real paper text from the GitHub repository, not PDF metadata.
"""
import sys, os, time, math, re
import numpy as np
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))

from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.seed_vectors import seed_vectors
from noise_compass.architecture.tokens import GodToken

# ═══════════════════════════════════════════════════════════════
# ACTUAL PAPER CONTENT (from repo + paper abstract)
# ═══════════════════════════════════════════════════════════════
paper_sections = [
    # Abstract / Introduction
    """Vectorizing the Trie: Efficient Constrained Decoding for LLM-based 
    Generative Retrieval on Accelerators. STATIC is a high-performance method 
    for enforcing outputs to stay within a prespecified set during autoregressive 
    decoding from large language models, designed for maximum efficiency on 
    modern hardware accelerators like GPUs and TPUs.""",

    # Key Features
    """Accelerator-Native Design: The core masking kernel is implemented as a 
    single, vectorized operation, avoiding expensive CPU-accelerator 
    synchronization and pointer-chasing common in traditional trie-based methods.""",

    """Hybrid Data Structure: STATIC uses a novel hybrid index. It represents 
    the hot initial layers of a prefix tree with a dense lookup table for O(1) 
    access and the high-cardinality sparse tail with a Compressed Sparse Row 
    CSR matrix for memory efficiency.""",

    """High Performance: Achieves near-constant-time O(1) performance with 
    respect to the total number of constraints, and logarithmic performance 
    O(log K) relative to the branching factor K, significantly outperforming 
    traditional baselines.""",

    """Framework Agnostic: Includes end-to-end tested implementations for both 
    major deep learning frameworks: JAX and PyTorch.""",

    # How It Works - Offline
    """Offline Indexing build_static_index: Takes a large set of valid token 
    sequences such as millions of Semantic IDs as input. Analyzes the prefix 
    structure and converts the implicit trie into the hybrid dense sparse 
    representation. Synthesizes start_mask to validate the first token, 
    dense_mask and dense_states tensors to handle the first dense_lookup_layers 
    tokens, and packed_csr and csr_indptr sparse matrix representation for all 
    transitions beyond the dense layers.""",

    # How It Works - Online
    """Online Masking: During each step of autoregressive decoding beam search, 
    the model's predicted log-probabilities are masked. For the first 
    dense_lookup_layers steps, valid next tokens are retrieved in O(1) from 
    the dense tables. For all subsequent steps, the generate_and_apply_logprobs_mask 
    kernel performs a vectorized burst-read from the CSR matrix to fetch all 
    valid continuations for all beams in parallel. This provides the final mask, 
    applied to the log-probabilities before selecting the next tokens.""",

    # Cost analysis
    """This design ensures that the cost of masking is independent of the total 
    number of constraints, making it highly scalable. The sparse transition matrix 
    approach eliminates pointer chasing and enables hardware-friendly memory access 
    patterns. Unlike traditional trie traversal which requires sequential node 
    lookups, STATIC performs all constraint checks through dense matrix operations 
    that saturate accelerator bandwidth.""",

    # Architecture / Code
    """Core implementation: csr_utils.py handles STATIC index construction logic 
    using NumPy. decoding_jax.py implements the STATIC decoding loop for JAX 
    on TPU. decoding_pt.py implements the STATIC decoding loop for PyTorch on GPU. 
    Benchmarks compare STATIC against Trie-based, Hash bitmap, and PPV baselines.""",

    # Generative Retrieval Context
    """Generative retrieval replaces traditional index-based search with autoregressive 
    sequence generation. The model generates document identifiers directly as token 
    sequences. Constrained decoding ensures that only valid document identifiers can 
    be generated. With millions of documents, the constraint set can be very large, 
    making efficient constrained decoding critical for practical deployment. STATIC 
    makes this constraint enforcement nearly free by precomputing all valid transitions 
    into a vectorized index structure.""",

    # Trie structure
    """A trie is a tree data structure where each path from root to leaf represents 
    a valid sequence. Traditional trie traversal requires following pointers from 
    node to node, which causes irregular memory access patterns that are hostile 
    to accelerator architectures. STATIC vectorizes this traversal by converting 
    the trie into a sparse transition matrix where the state at each decoding step 
    is a row index and valid next tokens are column indices with non-zero entries.""",

    # Comparison
    """Compared to naive trie-based constrained decoding, STATIC achieves orders of 
    magnitude speedup on TPU and GPU. Compared to hashmap-based approaches, STATIC 
    avoids the overhead of hash computation and collision resolution. Compared to 
    Product Possibilities Vector PPV, STATIC handles variable-length constraints 
    without padding overhead. The key insight is that constraint enforcement can be 
    reduced to a single sparse matrix-vector multiplication per decoding step.""",
]

print(f"Content sections: {len(paper_sections)}")
total_chars = sum(len(s) for s in paper_sections)
print(f"Total chars: {total_chars}")

# ═══════════════════════════════════════════════════════════════
# PASS 1 — FORWARD (baseline)
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PASS 1 — FORWARD (reading with existing vocabulary)")
print("=" * 70)

d1 = Dictionary()
seed_vectors(d1)
p1 = MinimalPipeline(d1)

pass1 = []
for i, section in enumerate(paper_sections):
    res = p1.process(section)
    pass1.append(res)
    gods = ", ".join(res["gods"]) if res["gods"] else "—"
    print(f"  [{i+1:>2}] {res['state']:<16} T={res['ternary']:>2}  [{gods}]")

p1_r = sum(1 for r in pass1 if r["gods"])
print(f"\n  Recognized: {p1_r}/{len(pass1)}")

# ═══════════════════════════════════════════════════════════════
# PASS 2 — BACKWARD (find paper's content god-tokens)
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PASS 2 — BACKWARD (extracting the paper's god-tokens)")
print("=" * 70)

blacklist = {
    'the', 'and', 'for', 'that', 'with', 'this', 'from', 'are', 'was',
    'each', 'which', 'their', 'than', 'them', 'then', 'these', 'those',
    'into', 'over', 'such', 'only', 'other', 'more', 'most', 'some',
    'where', 'when', 'what', 'also', 'about', 'between', 'through',
    'after', 'before', 'during', 'while', 'its', 'not', 'but', 'all',
    'any', 'use', 'used', 'using', 'based', 'given', 'show', 'shows',
    'very', 'both', 'major', 'like', 'makes', 'making', 'made', 'can',
    'first', 'next', 'single', 'large', 'total', 'handle', 'ensures',
    'steps', 'approach', 'traditional',
}
existing = {e.lower() for e in d1.god_tokens.keys()}

def extract(chunk):
    words = re.findall(r'\b[a-z]{4,}\b', chunk.lower())
    return [w for w in words if w not in blacklist and w not in existing]

def extract_bigrams(chunk):
    words = re.findall(r'\b[a-z]{3,}\b', chunk.lower())
    bgs = []
    for i in range(len(words) - 1):
        if words[i] not in blacklist and words[i+1] not in blacklist:
            bgs.append(f"{words[i]}_{words[i+1]}")
    return bgs

global_terms = Counter()
global_bgs = Counter()
chunk_sets = []
for section in paper_sections:
    terms = extract(section)
    bgs = extract_bigrams(section)
    chunk_sets.append(set(terms) | set(bgs))
    global_terms.update(terms)
    global_bgs.update(bgs)

doc_freq = Counter()
for ts in chunk_sets:
    for t in ts:
        doc_freq[t] += 1

scores = {}
for term, count in list(global_terms.items()) + list(global_bgs.items()):
    spread = doc_freq.get(term, 0)
    if spread >= 2 and count >= 2:
        score = count * math.log(1 + spread)
        scores[term] = (score, count, spread)

top = sorted(scores.items(), key=lambda x: -x[1][0])[:30]

print(f"\n  {'CONCEPT':<35} {'SCORE':>8} {'FREQ':>6} {'SPREAD':>8}")
print(f"  {'─'*35} {'─'*8} {'─'*6} {'─'*8}")
for term, (score, freq, spread) in top:
    label = term.replace("_", " ")
    print(f"  {label:<35} {score:>8.1f} {freq:>6} {spread:>5}/{len(paper_sections)}")

# ═══════════════════════════════════════════════════════════════
# SEED CONTENT GOD-TOKENS
# ═══════════════════════════════════════════════════════════════
d2 = Dictionary()
seed_vectors(d2)

for term, (score, freq, spread) in top:
    term_upper = term.upper().replace("_", " ")
    phase_deg = max(0, 60 - spread * 4)
    phase_rad = math.radians(phase_deg)
    
    if spread > len(paper_sections) * 0.5:
        target = "GROUND"
    elif spread > len(paper_sections) * 0.25:
        target = "PRESENCE"
    else:
        target = "UNKNOWN"
    
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
    
    gt = GodToken(id=term_upper, seed_terms=[term.replace("_"," ")], embedding=emb, stability=1.0)
    d2.add_god_token(gt)

print(f"\n  Dictionary: {len(d1.god_tokens)} → {len(d2.god_tokens)} god-tokens")

# ═══════════════════════════════════════════════════════════════
# PASS 3 — FORWARD (re-read with discovered god-tokens)
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PASS 3 — FORWARD (re-reading with content god-tokens)")
print("=" * 70)

p2 = MinimalPipeline(d2)
pass3 = []
for i, section in enumerate(paper_sections):
    res = p2.process(section)
    pass3.append(res)
    gods = ", ".join(res["gods"][:6]) if res["gods"] else "—"
    extra = f"+{len(res['gods'])-6}" if len(res["gods"]) > 6 else ""
    print(f"  [{i+1:>2}] {res['state']:<16} T={res['ternary']:>2}  [{gods}{' ' + extra if extra else ''}]")

# ═══════════════════════════════════════════════════════════════
# LEARNING DELTA
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("LEARNING DELTA — CONTENT FOCUSED")
print("=" * 70)

p3_r = sum(1 for r in pass3 if r["gods"])
p1_g = set(); p3_g = set()
for r in pass1: p1_g.update(r["gods"])
for r in pass3: p3_g.update(r["gods"])
new_gods = p3_g - p1_g

p1_t = sum(r["ternary"] for r in pass1) / len(pass1)
p3_t = sum(r["ternary"] for r in pass3) / len(pass3)
p1_z = {}; p3_z = {}
for r in pass1: p1_z[r["state"]] = p1_z.get(r["state"], 0) + 1
for r in pass3: p3_z[r["state"]] = p3_z.get(r["state"], 0) + 1

print(f"\n  {'Metric':<30} {'Pass 1':>10} {'Pass 3':>10} {'Delta':>10}")
print(f"  {'─'*30} {'─'*10} {'─'*10} {'─'*10}")
print(f"  {'Recognized chunks':<30} {p1_r:>10} {p3_r:>10} {p3_r-p1_r:>+10}")
print(f"  {'Unique god-tokens':<30} {len(p1_g):>10} {len(p3_g):>10} {len(new_gods):>+10}")
print(f"  {'Ternary avg':<30} {p1_t:>+10.2f} {p3_t:>+10.2f} {p3_t-p1_t:>+10.2f}")

print(f"\n  Pass 1 zones: {p1_z}")
print(f"  Pass 3 zones: {p3_z}")

print(f"\n  CONTENT GOD-TOKENS (what the paper is actually about):")
for g in sorted(new_gods):
    print(f"    ⚡ {g}")

if p3_r > p1_r:
    print(f"\n  ✓ Comprehension: {p1_r}/{len(pass1)} → {p3_r}/{len(pass3)}")
    print(f"    Garu learned the paper's language through backward extraction.")
