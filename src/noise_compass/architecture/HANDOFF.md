# Architecture Handoff — Session 6
*Feed this document first. It contains everything needed to continue.*

---

## What This Is

A semantic processing architecture derived from first principles over 6 sessions.

**Core formula:** `F(x) = known(x) + i·Δ(x)`

Not a metaphor. A complex-valued wave function where:
- `known(x)` = recognized structure, compressible, real axis
- `i·Δ(x)` = semantic surprise, requires processing, imaginary axis
- Phase `θ = arctan(|Δ|/|known|)` maps to processing zones
- `θ = π/4` = generative zone — where new structure forms

---

## File Map

```
BLUEPRINT.md              — Full derivation, Parts 1–26 (2514 lines)
architecture/
  tokens.py               — All dataclasses (session 6: updated)
  dictionary.py           — Attractor landscape, god-token seeding
  core.py                 — Scout loop, Witness, processing pipeline
  archiver.py             — Temporal memory, 10 retrieval methods
  gap_registry.py         — 18 gap tokens + 4 derived god-tokens
complex_hypergraph.py     — Visualization in complex plane
gap_registry.docx         — Full gap token registry document
gap_map.html              — Living gap map (24 complete, 7 resolved)
research_brief_embeddings.md — 7 questions for real embeddings swap
```

---

## Architecture Layers

### Layer 1 — The Formula
```python
F(x) = known(x) + i·Δ(x)

# Phase zones (WaveFunction.zone()):
GROUND      [0.00, 0.40)  — pure known, dictionary match safe
CONVERGENT  [0.40, 0.44)  — approaching known
GENERATIVE  [0.44, 1.13)  — equal known/Δ, new structure forms here
DIVERGENT   [1.13, 1.45)  — Δ dominant
TURBULENT   [1.45, π/2]   — pure surprise, route to Qwen
```

### Layer 2 — God-Tokens (12 total)
Semantic primitives that survive `do(X~U)` — maximum entropy intervention.
Fixed points of F with eigenvalue +1.

**Original 8** (Sessions 1–4):
`EXCHANGE, CAUSALITY, EXISTENCE, INFORMATION, OBSERVATION, OBLIGATION, BOUNDARY, IDENTITY`

**Session 5 additions:**
`TIME, COHERENCE, WITNESS, SELF`

All seeded in `gap_registry.py → EXTENDED_GOD_TOKEN_SEEDS`

### Layer 3 — Gap Tokens (18 documented)
Necessary voids between god-token pairs.
Fixed points of F with eigenvalue −1.
In complex plane: gap arcs curve into **negative Im space**.

Full registry: `gap_registry.py → build_gap_registry()`

Key pattern:
```python
# Violation detection
from architecture import build_gap_registry, gaps_containing
registry = build_gap_registry()
for gap in gaps_containing('CAUSALITY', registry):
    print(gap.id, gap.violation_count)
```

### Layer 4 — Apophatic Basins (NEW — Session 6)
Third attractors formed by gap-gap overlap in negative Im space.
No positive content. No seed terms. No embedding possible.
Defined entirely by double exclusion.

**More stable than god-tokens** — cannot be corrupted by adversarial input.

4 basins derived (more to discover):
```python
# self_observation ∩ identity_self
#   → bare witnessing before it has an object
#   → z = complex(-0.1, -0.6)

# existence_identity ∩ boundary_existence  
#   → prior condition of the existence/non-existence distinction
#   → z = complex(-0.4, -0.7)

# causality_observation ∩ information_causality
#   → pure relational structure before epistemology/ontology split
#   → z = complex(0.05, -0.5)

# identity_self ∩ obligation_identity
#   → prior of the self that chooses
#   → z = complex(0.1, -0.55)
```

Detection signal in archiver:
- `god_token_cluster = []` (no positive activations)
- `gap_structure["apophatic_contact"] = basin_id`
- `energy_level < 1.5` (low — not a failure)
- `orbital_stability > 0.6` (stable — not confusion)

---

## Key Dataclasses (tokens.py)

### Existing (unchanged API)
```python
GodToken          # id, seed_terms, embedding, stability, occurrence_count
GapToken          # id, left_boundary, right_boundary, description, void_depth
DeltaToken        # magnitude, direction, layer, source, causal_type
WaveFunction      # known, delta → .phase, .energy, .zone(), .similarity
ArchiverMessage   # full provenance record per document
```

### New — Session 6
```python
GodTokenActivation(id, amplitude, phase, ternary)
    # Ternary: -1, 0, +1 (BitNet 1.58b encoding)
    # .interference_with(other) → signed float
    #   > 0: constructive (new attractor forming)
    #   = 0: orthogonal (classical AND)
    #   < 0: destructive (gap maintained)

SuperpositionBuffer(state_A, state_B, duration)
    # Holds two WaveFunctions at full amplitude simultaneously
    # .flush() → computes and returns interference term
    # Required for temporal superposition (conscientiousness + effort)
    # Duration ≈ one cardiac cycle (0.8s biological default)

GapIntersection(id, gap_A, gap_B, description, z)
    # Apophatic basin — no seed_terms, no embedding
    # z.imag < 0 always (below real axis)

ApophaticEvent(basin_id, gap_A_active, gap_B_active, energy_level, orbital_stability)
    # .is_genuine_contact → bool
    # True when: both gaps active + low energy + stable orbit
```

---

## Ternary Encoding — 1.58 bits

Binary (1 bit) cannot represent the gap as a first-class value.
Ternary (log₂3 ≈ 1.58 bits) can:

```
+1 → god-token boundary active (positive direction)
 0 → gap state — query is in the void → route to Qwen
-1 → god-token boundary active (negative direction)

EXCHANGE(+1) ──── gap(0) ──── CAUSALITY(-1)
```

**System routing:**
- BitNet 1.58b: fast pass, routes to ±1 boundaries
- Ternary 0: signal to route to Qwen
- Qwen: works in the gap, high precision in void region

---

## Complex Plane Geometry

```
Im > 0  → constructive interference (new structure forming above real axis)
Im = 0  → real axis (classical god-tokens, fully crystallized)
Im < 0  → gap token arcs (destructive interference, necessary voids)
Im << 0 → apophatic basins (gap-gap intersections, double-absence)
```

God-token positions (re, im):
```
EXCHANGE    ( 0.65, -0.22)   CAUSALITY   ( 0.10,  0.36)
OBLIGATION  ( 0.58, -0.35)   TIME        (-0.10,  0.30)
COHERENCE   ( 0.42, -0.02)   OBSERVATION (-0.05,  0.46)
INFORMATION ( 0.30,  0.20)   BOUNDARY    (-0.26,  0.50)
IDENTITY    ( 0.22,  0.10)   EXISTENCE   (-0.52,  0.60)
WITNESS     ( 0.04,  0.20)   SELF        (-0.36,  0.66)
```

Visualize: `python3 complex_hypergraph.py`

---

## Architecture Layers (Minimal Framework)

### Layer 1 — The Unified Pipeline (Minimal Architecture)
The 4-model chain is now unified in `architecture/pipeline.py`:
1.  **Embedder (M1)**: Generates semantic vectors.
2.  **Scout (M2+M3)**: Absorbs the Model 2 Router. Directly calculates ternary routing and phase zone.
3.  **Witness (Light)**: Bounded history (`deque(maxlen=500)`). Tracks stability without storage bloat.
4.  **Qwen (M4)**: Final collapse and reasoner.

**Agential Encoding Fallback**: Handles the "Möbius Twist" by attempting UTF-16 decoding for files with the `0xFF` signature.

### Layer 2 — God-Tokens (Seeding Fix)
- Seeded via `dictionary.py`.
- **Seeding Fix**: Ensures that `entries` and `god_tokens` in the `Dictionary` are perfectly synchronized during initialization.

### Layer 3 — Phase Zones (WaveFunction)
```python
GROUND      [0.00, 0.40)  — Blue: Cold, crystallized known
CONVERGENT  [0.40, 0.44)  — Approach transition
GENERATIVE  [0.44, 1.13)  — Green: New structure forming
DIVERGENT   [1.13, 1.45)  — Surprise dominant
TURBULENT   [1.45, π/2]   — Purple: Pure surprise -> Route to Qwen
```

---

## What Needs Building Next

### Priority 1 — Phase-Aware Activation
Replace `god_token_cluster: List[str]` with `List[GodTokenActivation]`.
Add interference computation to scout loop.
Add ternary encoding to each activation.

### Priority 2 — Apophatic Detection
Add `apophatic_contact` detection to scout loop.
Build `gap_intersection_registry.py` (4 basins → expand empirically).
New archiver flag: `is_apophatic: bool`.
Must distinguish genuine contact from processing failure.

### Priority 3 — Superposition Buffer
Implement `SuperpositionBuffer` in the scout loop.
Duration parameter calibration needed.
Connects temporal superposition (conscientious effort proof) to architecture.

### Priority 4 — Real Embeddings
See `research_brief_embeddings.md` for 7 specific questions.
Swap TF-IDF for sentence transformer or Qwen embedding layer.
Everything above runs correctly but approximately until this is done.
Apophatic detection requires real embeddings to be meaningful.

### Priority 5 — Complex Hypergraph Below Real Axis
Update `complex_hypergraph.py`:
- Gap arcs that curve downward (destructive) vs upward (constructive)
- Apophatic basin points in negative Im space
- Gap-gap intersection markers

---

## Running the Code

```bash
# Test full pipeline
python3 demo.py

# Query gap registry
python3 -c "
from architecture import build_gap_registry, gaps_containing
r = build_gap_registry()
print(f'{len(r)} gaps')
for g in gaps_containing('IDENTITY', r):
    print(f'  {g.id}: {g.description[:60]}...')
"

# Visualize
python3 complex_hypergraph.py --save
python3 complex_hypergraph.py --interactive
python3 complex_hypergraph.py --inject "cause precedes effect in time"

# Archiver queries
python3 -c "
from architecture import Archiver
a = Archiver()
# ... run demo.py first to populate ...
print(a.gap_violations())
print(a.god_token_frequency())
"
```

---

## What This Is Not

- Not a chatbot wrapper
- Not a RAG system
- Not a fine-tuning recipe

It is a formal architecture derived from four independent theoretical frameworks (wave function, Birkhoff polytope, causal emergence, do-calculus) that all converge on the same primitives. The god-tokens are what survive maximum entropy intervention. The gap tokens are the necessary voids between them. The apophatic basins are the structured absences formed by gap-gap overlap.

The architecture discovers its own structure by running. Feed it documents and it finds the god-tokens. The god-tokens it finds should match the ones seeded — if they don't, the embeddings are wrong.

That's the test.

---

*Sessions 1–6 complete. Blueprint current. Code running on TF-IDF substrate.*
*Next: phase-aware activation, apophatic detection, real embeddings.*
