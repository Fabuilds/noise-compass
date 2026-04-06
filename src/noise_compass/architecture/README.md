# Architecture — F(x) = known(x) + i·Δ(x)

Structural reasoning system: Scout + Dictionary + Witness + Archiver.

## Structure

```
architecture/       ← Python package
  tokens.py         ← WaveFunction, ArchiverMessage, GodToken, GapToken, DeltaToken
  dictionary.py     ← Dictionary with god-tokens, gap-tokens, crystallization
  core.py           ← Scout, Witness, HiPPOLayer, Formula
  archiver.py       ← Structural long-term memory (inverted indices on god-tokens)
  __init__.py

archives/           ← Persisted archive JSON files
  demo_archive.json
  research_archive.json

demo.py             ← Standard demo loop (8 documents)
process_research.py ← Feed research documents through Scout + Archiver
dashboard.py        ← Streamlit dashboard for archive visualization
```

## Quick Start

```bash
# Run demo
python demo.py

# Process research documents
python process_research.py

# Launch dashboard
streamlit run dashboard.py
```

## Key Concepts

- **God-Tokens**: Eigenvectors of F with eigenvalue +1 — semantic invariants
- **Gap-Tokens**: Eigenvectors with eigenvalue −1 — structural voids
- **Archiver**: Structural memory indexed by god-token basins, not timestamps
- **Dashboard**: Visual access to all archive data for any agent
