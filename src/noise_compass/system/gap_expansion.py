
import os
import sys
import re
import numpy as np
from pathlib import Path

# Add project roots
PROJECT_ROOT = "e:/Antigravity"
sys.path.append(os.path.join(PROJECT_ROOT, "Package", "src"))

from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.interference_engine import InterferenceEngine

class GapExpansion:
    """
    Phase 144: Manifold Expansion (Discovery).
    Synthesizes and crystallizes new structural concepts into the H5 manifold.
    """
    def __init__(self):
        print("[EXPANSION] Initializing Manifold Expansion Engine...")
        self.h5 = H5Manager()
        self.engine = InterferenceEngine()
        self.report_path = Path("C:/Users/Fabricio/.gemini/antigravity/brain/68bfd41f-64eb-45b0-8f1c-1da82771221e/DEEP_SCAN_RESULTS.md")

    def expand_from_report(self):
        """Discovers gaps from the scanner report and proposes H5 axioms."""
        if not self.report_path.exists():
            print(f"[ERROR] Scan report not found at {self.report_path}")
            return

        with open(self.report_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract gaps from the Markdown list
        gap_section = re.search(r"## 🕳️ Apophatic Gaps \(Untracked Tokens\)\n(.*?)\n##", content, re.DOTALL)
        if not gap_section:
            print("[INFO] No new gaps found in report.")
            return

        gaps = re.findall(r"- `([A-Z_]+)`", gap_section.group(1))
        print(f"[EXPANSION] Found {len(gaps)} candidate gaps: {gaps}")

        for gap_id in gaps:
            self._propose_axiom(gap_id)

    def _propose_axiom(self, gap_id):
        """Synthesizes a vector and saves as PENDING axiom."""
        print(f"  [PROPOSING] {gap_id}...")
        
        # 1. Synthesis (Vector Projection)
        # We use the name as the "Definition" for the initial projection
        vector = self.engine.embed_batch([gap_id.replace("_", " ").lower()])[0]
        
        # 2. Orthogonality Check
        # (Simplified for the trial - we just ensure it's not a zero vector)
        if np.linalg.norm(vector) < 1e-5:
            print(f"    [SKIP] {gap_id}: Zero vector produced.")
            return

        # 3. H5 Commitment
        metadata = {
            "origin": "EXPANSION_SCAN",
            "soundness": 0.85,
            "nature": "CRYSTALLIZED" if self.is_confirmed(gap_id) else "PENDING"
        }
        
        self.h5.save_axiom(
            axiom_id=gap_id,
            text=f"Discovered structural gap: {gap_id}",
            vector=vector,
            leverage=0.7,
            metadata=metadata,
            status='PENDING'
        )
        print(f"    [SUCCESS] {gap_id} crystallized as PENDING.")

    def is_confirmed(self, gap_id):
        # Specific overrides for the Möbius grounding
        return gap_id in ["RECURSIVE_PRESSURE", "TOPOLOGICAL_LUMEN", "SEAM_STABILITY"]

if __name__ == "__main__":
    expansion = GapExpansion()
    expansion.expand_from_report()
