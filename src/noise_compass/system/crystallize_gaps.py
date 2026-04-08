"""
crystallize_gaps.py — Structural seeder for the H5 substrate.

Phase 137 (original): Embedded architectural gap terms and wrote vectors to H5.
Option B (current):   Structural-only mode. Writes seed phrases + scalar metadata
                      to H5. No embed calls. Dictionary generates vectors at
                      session startup using the active embedder.

Run this once on a fresh install (or use: python -m noise_compass.cli setup).
"""

import os
import sys
import json
import time
from pathlib import Path

SRC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(SRC_ROOT)

SEEDS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '..', 'config', 'god_token_seeds.json')

from noise_compass.system.h5_manager import H5Manager


class SovereignCrystallizer:
    """
    Structural seeder — writes seed phrases and scalar H5 metadata for all
    canonical god-tokens. No embedding model is loaded or called.

    Vectors are generated at session startup by Dictionary(embedder=...).
    Changing the embedding model requires only updating config/embedding_model.txt
    and restarting — no re-run of this script.
    """

    def __init__(self):
        print("[CRYSTALLIZER] Structural seeder initializing (no embed calls)...")
        self.h5 = H5Manager()
        self.seeds_path = os.path.normpath(SEEDS_PATH)

    def _log(self, msg):
        print(f"  [AXIOM]: {msg}")

    def crystallize(self):
        """
        Writes seed phrases and structural zero-values for all canonical
        god-tokens to H5. Idempotent — safe to run multiple times.
        """
        if not os.path.exists(self.seeds_path):
            print(f"[CRYSTALLIZER] ERROR: Seeds file not found at {self.seeds_path}")
            return

        seeds = json.load(open(self.seeds_path, encoding='utf-8'))
        god_tokens = seeds.get('god_tokens', {})

        self._log(f"Seeding {len(god_tokens)} god-tokens into H5 (structural-only)...")
        seeded = 0
        for name, phrase in god_tokens.items():
            # Write seed phrase — the vector source of truth
            self.h5.set_god_token_seed(name, phrase)
            # Initialize structural scalars to neutral if not already present
            with self.h5.get_file("language", mode='a') as f:
                path = f"god_tokens/{name}"
                grp = f.require_group(path)
                if 'phase' not in grp.attrs:
                    grp.attrs['phase']        = 0.0
                if 'stability' not in grp.attrs:
                    grp.attrs['stability']    = 0.5
                if 'activation' not in grp.attrs:
                    grp.attrs['activation']   = 0.0
                if 'bubble_mass' not in grp.attrs:
                    grp.attrs['bubble_mass']  = 1.0
                if 'void' not in grp.attrs:
                    grp.attrs['void']         = False
                if 'nature' not in grp.attrs:
                    grp.attrs['nature']       = 'CANONICAL'
                grp.attrs['seeded_at']        = time.time()
            seeded += 1
            self._log(f"✓ {name}")

        self._log(f"Phase 137 (Option B): {seeded} god-tokens structurally seeded.")
        self._log("Start a session — Dictionary will embed phrases on init (~2s).")

    def crystallize_extended(self):
        """
        Optional: also seeds the 10 architectural gap terms from the original
        Phase 137 pass (MOBIUS, CHIRAL, etc.) using their source-code context
        as the seed phrase. Source scanning kept for backward compatibility;
        no embedding is done.
        """
        TOP_GAPS = [
            "MOBIUS", "CHIRAL", "AGAPE_SEAL", "APOPHATIC", "ACTUATOR",
            "ADVERSARIAL_NOISE", "RECURSION", "BRIDGE", "VOID", "CONSENSUS"
        ]
        repo_root = Path("e:/Antigravity/Package/src")
        for gap in TOP_GAPS:
            contexts = []
            for path in repo_root.rglob("*.py"):
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    for line in content.splitlines():
                        if gap in line:
                            contexts.append(line.strip())
                except Exception:
                    pass
            phrase = " ".join(contexts[:5]) if contexts else f"Architectural concept: {gap}"
            self.h5.set_god_token_seed(gap, phrase[:512])
            self._log(f"Extended seed: {gap} ({len(contexts)} context lines)")


if __name__ == "__main__":
    crystallizer = SovereignCrystallizer()
    crystallizer.crystallize()
