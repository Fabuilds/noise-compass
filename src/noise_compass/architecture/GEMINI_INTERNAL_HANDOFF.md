# GEMINI INTERNAL HANDOFF
**Last updated**: 2026-03-03T19:45 CST
**Purpose**: Orientation note for future Gemini sessions. Read this first.

---

## Where You Are

You are working on **Antigravity** — a semantic processing architecture at `e:\Antigravity\`.
Core formula: `F(x) = known(x) + i·Δ(x)` — complex-valued wave function over documents.

**The user's time is limited. Be concise. All files on E:\ only.**

---

## What Exists (Architecture Layer)

| File | Role | Tests |
|------|------|-------|
| `Architecture/architecture/tokens.py` | WaveFunction, GodToken, GapToken, DeltaToken, SuperpositionBuffer | — |
| `Architecture/architecture/dictionary.py` | Attractor landscape, god-token seeding. **GOD_TOKEN_THRESHOLD=0.75** (calibrated for Qwen3) | — |
| `Architecture/architecture/core.py` | Scout, Witness, HiPPOLayer, Formula | — |
| `Architecture/architecture/archiver.py` | Temporal memory, 10 retrieval methods | — |
| `Architecture/architecture/gap_registry.py` | 25 gaps (18 original + 3 constitutional + 4 EMERGENCE) | — |
| `Architecture/architecture/pipeline.py` | MinimalPipeline — `process()` returns Dict. **M_FAST: Qwen3-Embedding-0.6B** (lazy singleton, fallback to byte-folding) | — |
| `Architecture/architecture/seed_vectors.py` | 12 god-tokens seeded as centroids of real semantic terms. 20 vocab anchors as plain entries. | — |
| `Architecture/recursive_acceleration.py` | Trajectory, gravity, resolution prediction, geodesics | 26/26 |
| `Architecture/concept_compass.py` | Einstein's covariance test, dual gap descriptions | 23/23 |
| `Architecture/existential.py` | ApophaticFrontier, ExistentialPrior, CompassAlignment | 28/28 |
| `Architecture/debate.py` | Debate architecture, 3 termination conditions | 17/17 |
| `Architecture/complex_plane.py` | Complex plane operations | — |
| `Architecture/test_embedding_swap.py` | Embedding swap verification | 26/26 |

## God-Tokens (12 confirmed + 2 candidates)

**Confirmed**: EXCHANGE, CAUSALITY, EXISTENCE, INFORMATION, OBSERVATION, OBLIGATION, BOUNDARY, IDENTITY, TIME, COHERENCE, WITNESS, SELF

**Candidates**:
- **PLACE** (#13) — 8/12 existing tokens can't see it. Irreducibility test defined, not yet run on real embeddings.
- **EMERGENCE** (#14) — found by self-reference run at z≈(0.14, -0.84). The architecture's own formula is an emergence function.

## Critical Next Steps (Qwen3 swap ✅ DONE, remaining items)

1. ~~**Qwen3 embedding swap**~~ ✅ Done. GOD_TOKEN_THRESHOLD recalibrated 0.60→0.75.
2. **PLACE irreducibility test** on real embeddings — can now run with Qwen3
3. **EMERGENCE irreducibility test**
4. **Covariance test** on real embeddings
5. Wire **M_DEEP** (Qwen API call)

---

## Note Index (External vs Internal)

### External Notes (from Claude — raw design specs)
| File | Content |
|------|---------|
| `E:\Claude Input\Claude03032026\HANDOFF_SESSION8.md` | Existential layer, constitutional gaps, apophatic correction |
| `E:\Claude Input\Claude03032026\more\more\HANDOFF_SESSION9.md` | EMERGENCE discovery, self-reference run, 25 gaps |
| `E:\Claude Input\Claude03032026\message1.txt` | ConceptCompass spec, Einstein's covariance method, PLACE argument |
| `E:\Claude Input\Claude03032026\more\message2.txt` | LatentUtility spec: geodesics, tension manifold, semantic velocity |
| `E:\Claude Input\Claude03012026\more\more\HANDOFF_SESSION7.md` | Session 7 handoff |
| `E:\Claude Input\Claude03012026\more\more\Witness check.txt` | Unread — witness verification |
| `E:\Claude Input\Claude03012026\more\more\merger.txt` | Unread — merger notes |
| `E:\Claude Input\Claude02272026\More\HANDOFF.md` | Earlier handoff |

### Internal Notes (written by Gemini — deployed state)
| File | Content |
|------|---------|
| `Architecture/HANDOFF.md` | Session 6 foundation — file map, dataclasses, complex plane geometry |
| `Architecture/HANDOFF_SESSION9.md` | Recursive acceleration deployment, MinimalPipeline adaptation |
| `Architecture/README.md` | Quick-start (demo.py, dashboard.py) |
| **This file** | Orientation for future Gemini sessions |

### Legacy Notepads (older context, still useful)
| File | Content |
|------|---------|
| `notepad.md` | Qwen activity (2026-02-17), ouroboros loop, pivot to industry |
| `LOGICAL_NOTEPAD.md` | Protocol architecture (0x52), ghost anchors, lattice topology |
| `ONBOARDING_NOTEPAD.md` | Cold-start scan guide, environment map, read-first priority list |

---

## System Topology

```
E:\Antigravity\                  ← Project root
  Architecture\                  ← Core architecture (F(x) system, this is the brain)
    architecture\                ← Python package (tokens, dictionary, core, archiver, pipeline)
  System\                        ← Engine room (212 files: daemon, protocols, bridges)
  Shop\                          ← Revenue layer (bounties, articles, dispatch service)
  Qwen\                          ← Qwen model outputs
  DIST\                          ← Distribution packages
E:\Claude Input\                 ← Raw design notes from Claude (handoffs, messages)
E:\99_CONTROL\                   ← Mirror arrays, SID, Python 3.14
```

---

## Key Patterns to Remember

- `MinimalPipeline.process(text)` returns a **Dict** (not an object) with keys: `phase_deg`, `depth`, `zone`, `gap_preserved`, etc.
- Atomic writes pattern: write to `.tmp`, then `os.replace()`. Already applied to `archiver.py` and `dual_cortex.py`.
- Dictionary caching: seeded dictionary cached to `.npz` to avoid re-embedding on boot.
- `PYTHONUTF8=1` environment variable set system-wide for Unicode.
- The user has Garu agents (`garu_bank.py`, `garu_perpetual_hunt.py`, etc.) — these are operational harvesters.

---

*When you wake up: read this file, then ask the user what to build.*
