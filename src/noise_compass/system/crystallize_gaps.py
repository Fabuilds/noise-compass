
import os
import sys
import json
import time
import re
import numpy as np
from pathlib import Path

# Add project roots
SRC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(SRC_ROOT)

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.system.knowledge_lattice import KnowledgeLattice
from noise_compass.architecture.tokens import GodToken
from noise_compass.system.interference_engine import InterferenceEngine

class SovereignCrystallizer:
    """
    Phase 137: Sovereign Crystallization (Gap Bridging).
    Anchors high-frequency architectural terms into the H5 manifold.
    """
    TOP_GAPS = [
        "MOBIUS", "CHIRAL", "AGAPE_SEAL", "APOPHATIC", "ACTUATOR",
        "ADVERSARIAL_NOISE", "RECURSION", "BRIDGE", "VOID", "CONSENSUS"
    ]

    def __init__(self):
        print("[CRYSTALLIZER] Initializing Phase 137 Crystallization...")
        self.lattice = KnowledgeLattice()
        self.dictionary = Dictionary.load_cache(h5_manager=self.lattice.h5)
        self.engine = InterferenceEngine()
        self.repo_root = Path("e:/Antigravity/Package/src")

    def _log(self, msg):
        print(f"  [AXIOM]: {msg}")

    def _get_gap_context(self, gap_name):
        """Searches the codebase for usage context of a specific gap."""
        contexts = []
        for path in self.repo_root.rglob("*.py"):
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                for line in content.splitlines():
                    if gap_name in line:
                        contexts.append(line.strip())
            except: pass
        return contexts[:20] # Limit to 20 representative lines

    def crystallize(self):
        """Performs the formal anchor of identified gaps."""
        for gap in self.TOP_GAPS:
            if gap in self.dictionary.god_tokens:
                self._log(f"Skipping {gap} (Already Crystallized)")
                continue

            self._log(f"Crystallizing architectural gap: {gap}...")
            
            # 1. Extraction (Linguistic Context)
            contexts = self._get_gap_context(gap)
            if not contexts:
                self._log(f"Warning: No source context found for {gap}. Using seed term.")
                contexts = [f"Architectural anchor for {gap} logic."]

            # 2. Resonance Generation (Averaged Embedding)
            text_block = "\n".join(contexts)
            embedding = self.engine.embed(text_block)
            
            # 3. H5 Commitment (GodToken)
            gt = GodToken(
                id=gap,
                seed_terms=contexts,
                embedding=embedding,
                nature="SOVEREIGN"
            )
            
            # Commit to Dictionary and H5
            self.dictionary.add_god_token(gt)
            # Use the underlying H5 manager to save permanently
            self.lattice.h5.save_semantic_entry(gap, embedding, depth=2.0)
            
            self._log(f"SUCCESS: {gap} anchored in H5 substrate.")

        # Save the updated dictionary cache if needed (though lattice.h5 is the ground truth)
        self.dictionary.save_cache()
        self._log("Phase 137: Sovereign Crystallization Cycle Complete.")

if __name__ == "__main__":
    crystallizer = SovereignCrystallizer()
    crystallizer.crystallize()
