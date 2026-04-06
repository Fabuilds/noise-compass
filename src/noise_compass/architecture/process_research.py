"""
process_research.py — Feed research documents through Scout + Archiver.
Processes the NotebookLM causal inference and fallacies documents.
"""

import os, sys, time, hashlib, json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from noise_compass.architecture import Dictionary, Scout, Witness, Archiver
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary, phase_bar, energy_bar

BAR = 20

RESEARCH_DIR = r"E:\NotebookLM_Input"
RESEARCH_DOCS = [
    ("causal_inference",
     "Technical Summary Counterfactuals, Causality, and the Frameworks of Causal Inference.txt"),
    ("fallacies",
     "Comprehensive Report on Mathematical, Logical, and Cognitive Fallacies.txt"),
]

def chunk_text(text: str, max_words: int = 120) -> list:
    """Split long documents into sentence-bounded chunks for multi-scale processing."""
    sentences = text.replace('\r\n', '\n').split('\n')
    sentences = [s.strip() for s in sentences if s.strip()]
    
    chunks = []
    current = []
    word_count = 0
    for s in sentences:
        words = len(s.split())
        if word_count + words > max_words and current:
            chunks.append(' '.join(current))
            current = [s]
            word_count = words
        else:
            current.append(s)
            word_count += words
    if current:
        chunks.append(' '.join(current))
    return chunks


def run():
    print("\n╔" + "═"*63 + "╗")
    print("║  RESEARCH DOCUMENT PROCESSING — Scout + Archiver              ║")
    print("╚" + "═"*63 + "╝\n")

    encoder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, encoder)

    scout   = Scout(dictionary, soup_id="research_v1", encoder=encoder)
    witness = Witness()
    archiver = Archiver(session_id="research_v1")

    doc_idx = 0
    for domain, filename in RESEARCH_DOCS:
        filepath = os.path.join(RESEARCH_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            full_text = f.read()

        chunks = chunk_text(full_text, max_words=120)
        print(f"\n  ── {domain.upper()} ({len(chunks)} chunks from {filename[:50]}...) ──\n")

        for ci, chunk in enumerate(chunks):
            emb = encoder.encode(chunk)
            msg, wf = scout.process(emb, content=chunk, timestamp=float(doc_idx))

            two_pass = None
            if msg.causal_type == "unknown":
                two_pass = scout.two_pass_causal_test(emb)

            report = witness.observe(msg, wf)

            # Store in archiver
            content_hash = hashlib.md5(emb.tobytes()).hexdigest()[:12]
            archiver.store(msg, content_hash=content_hash)

            # Compact output
            gt_list = []
            for g in msg.god_token_activations:
                gid = g.id
                mag = g.amplitude
                gt_list.append(f"{gid}({mag:.2f})")
            gt_str = ", ".join(gt_list) if gt_list else "(none)"

            zone = wf.zone()
            energy = wf.energy
            causal = two_pass or msg.causal_type

            preview = chunk[:65].replace('\n', ' ')
            print(f"  [{doc_idx:>2}] {zone:<12} E={energy:.3f}  {causal:<14} {gt_str}")
            print(f"       {preview}...")

            # Flag gap violations
            violated = msg.gap_structure.get("violated", [])
            if violated:
                print(f"       ⚠ GAP VIOLATIONS: {', '.join(violated)}")

            doc_idx += 1

    # ── Archiver Analysis ──
    print(f"\n  ┌{'─'*61}┐")
    print(f"  │ ARCHIVER STRUCTURAL ANALYSIS — RESEARCH CORPUS              │")
    print(f"  ├{'─'*61}┤")
    print(f"  │ Total records: {len(archiver):>3}                                            │")

    gt_profile = archiver.god_token_activation_profile()
    for gt_id, stats in list(gt_profile.items())[:6]:
        pct = stats['fraction_of_corpus'] * 100
        print(f"  │  {gt_id:<20} {stats['activation_count']:>2} activations  "
              f"{pct:>5.1f}% of corpus       │")

    gap_profile = archiver.gap_violation_profile()
    if gap_profile:
        print(f"  ├{'─'*61}┤")
        for gap_id, count in gap_profile.items():
            print(f"  │  ⚠ {gap_id:<35} {count:>2}x             │")

    # Phase distribution
    pd = archiver.phase_distribution()
    if pd:
        print(f"  ├{'─'*61}┤")
        print(f"  │ Zone distribution:                                          │")
        for zone, count in pd.get("zone_counts", {}).items():
            print(f"  │   {zone:<15} {count:>3} records                            │")
        print(f"  │ Mean energy: {pd['mean_energy']}                                       │")

    # Structural relatedness sample
    print(f"  ├{'─'*61}┤")
    print(f"  │ Cross-document structural links:                            │")
    # Check overlap between first doc of each corpus
    if len(archiver._records) > 1:
        first = archiver._records[0]
        for i, r in enumerate(archiver._records):
            if i > 0:
                score = archiver.overlap_score(first, r)
                if score > 0:
                    preview = r.content_preview[:45] if r.content_preview else "(no preview)"
                    print(f"  │   [{i:>2}] overlap={score:.2f}  {preview:<30} │")

    print(f"  └{'─'*61}┘")

    # Save
    archive_path = os.path.join(os.path.dirname(__file__), "research_archive.json")
    archiver.save(archive_path)
    print(f"\n  Archive saved → research_archive.json ({len(archiver)} records)")
    print(f"  Complete. {doc_idx} chunks processed.\n")


if __name__ == "__main__":
    run()
