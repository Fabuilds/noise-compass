
import os
import sys
import json
import time
import re
from pathlib import Path

# Add project roots
SRC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(SRC_ROOT)

from noise_compass.system.neural_prism import NeuralPrism
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.system.knowledge_lattice import KnowledgeLattice

class SovereignScanner:
    """
    Phase 136: Sovereign Deep-Scan.
    Performs a recursive architectural audit using Phase 135 linguistic invariants.
    """
    def __init__(self, root_dir="e:/Antigravity/Package/src", fast_mode=False, expansion_mode=False):
        print("[SOVEREIGN_SCANNER] Initializing Architectural Audit...")
        self.root = Path(root_dir)
        self.fast_mode = fast_mode
        self.expansion_mode = expansion_mode
        self.lattice = KnowledgeLattice()
        self.dictionary = Dictionary.load_cache(h5_manager=self.lattice.h5)
        self.prism = NeuralPrism(dictionary=self.dictionary)
        self.results = {
            "timestamp": time.ctime(),
            "summary": {"total": 0, "ENG": 0, "CODE": 0, "SOV": 0},
            "divergences": [],
            "gaps": set(),
            "tension_nodes": [],
            "inventory": []
        }

    def _log(self, msg):
        print(f"  [SCAN]: {msg}")

    def crawl(self):
        """Phase 1: The Crawl (Repo Collection)"""
        self._log(f"Starting crawl at {self.root}")
        for path in self.root.rglob("*"):
            if path.is_file() and path.suffix in [".py", ".md"]:
                if any(x in str(path) for x in ["Model_Cache", ".git", "__pycache__"]):
                    continue
                self._classify_file(path)
                
    def _classify_file(self, path):
        """Phase 2: Classification (Invariant Logic)"""
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            # Focus on the first 4K for initial classification
            sample = content[:4096]
            invariant = self.prism.identify_invariant(sample)
            
            self._log(f"Classified: {path.name} -> {invariant}")
            
            self.results["summary"]["total"] += 1
            self.results["summary"][invariant] += 1
            
            file_data = {
                "file": str(path.relative_to(self.root)),
                "type": invariant,
                "size": path.stat().st_size
            }
            
            if invariant == "SOV":
                # Deep Scrutiny for Sovereign Logic
                self._scrutinize_sov(path, content, file_data)
                
            self.results["inventory"].append(file_data)
            
        except Exception as e:
             self._log(f"Error processing {path.name}: {e}")

    def _scrutinize_sov(self, path, content, file_data):
        """Phase 3: Scrutiny (Resonance & Gap Analysis)"""
        # 1. God-Token Extraction
        matches = re.findall(r'\b[A-Z_]{4,}\b', content)
        untracked = [m for m in matches if m not in self.dictionary.god_tokens and not m.startswith("0x")]
        if untracked:
            file_data["gaps"] = list(set(untracked))
            self.results["gaps"].update(untracked)
            
        # 1.5. Tension Detection (Phase 144)
        if self.expansion_mode:
            self._detect_tension(path, content, file_data)
            
        # 2. Structural Resonance Check (Phase 135)
        if not self.fast_mode:
            refraction = self.prism.refract(content[:1024])
            resonance = sum(d['projection_magnitude'] for d in refraction.values())
            file_data["resonance"] = resonance
            
            if resonance < 0.3: # Threshold for architectural drift
                self.results["divergences"].append({
                    "file": file_data["file"],
                    "reason": "Low Structural Resonance (Drift Detected)",
                    "score": resonance
                })
        else:
            file_data["resonance"] = "SKIPPED"

    def _detect_tension(self, path, content, file_data):
        """Phase 144: Tension Analysis (Axiom Clashing)"""
        # Find anchored axioms (markers from Phase 142)
        anchors = re.findall(r"#\s*\[AXIOM\]:\s*([A-Z_]+)", content)
        if len(anchors) > 2:
            self._log(f"Tension Found in {path.name}: {anchors}")
            self.results["tension_nodes"].append({
                "file": str(path.relative_to(self.root)),
                "anchors": anchors,
                "density": len(anchors) / max(1, content.count("\n")) * 100
            })

    def run(self):
        self.crawl()
        self._synthesis()

    def _synthesis(self):
        """Phase 4: Synthesis (Generate Artifact)"""
        # Convert gaps to list for JSON serialization
        self.results["gaps"] = list(self.results["gaps"])
        
        report_path = Path("C:/Users/Fabricio/.gemini/antigravity/brain/68bfd41f-64eb-45b0-8f1c-1da82771221e/DEEP_SCAN_RESULTS.md")
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# SOVEREIGN DEEP-SCAN RESULTS\n\n")
            f.write(f"**Audit Timestamp:** {self.results['timestamp']}\n\n")
            f.write(f"**Mode:** {'FAST (Inventory Only)' if self.fast_mode else 'DEEP (Full Resonance)'}\n\n")
            
            f.write("## 🧬 Repo manifold Summary\n")
            f.write(f"- **Total Files Scanned:** {self.results['summary']['total']}\n")
            f.write(f"- **Sovereign Logic (SOV):** {self.results['summary']['SOV']}\n")
            f.write(f"- **Generic Code (CODE):** {self.results['summary']['CODE']}\n")
            f.write(f"- **Natural Language (ENG):** {self.results['summary']['ENG']}\n\n")
            
            if self.results["divergences"]:
                f.write("## ⚠️ Architectural Divergences (Drift)\n")
                for div in self.results["divergences"]:
                    f.write(f"- **{div['file']}**: {div['reason']} (Score: {div['score'] if isinstance(div['score'], str) else f'{div[score]:.4f}'})\n")
                f.write("\n")
            
            if self.results["gaps"]:
                f.write("## 🕳️ Apophatic Gaps (Untracked Tokens)\n")
                f.write("The following terms are mentioned in SOV files but lack H5 Dictionary crystallization:\n")
                for gap in sorted(self.results["gaps"]):
                    f.write(f"- `{gap}`\n")
                f.write("\n")
                
            if self.results["tension_nodes"]:
                f.write("## 🧬 Tension Nodes (Structural Clashing)\n")
                for node in self.results["tension_nodes"]:
                    f.write(f"- **{node['file']}**: {len(node['anchors'])} anchors ({', '.join(node['anchors'])}) | Density: {node['density']:.2f}%\n")
                f.write("\n")
            
            f.write("## 📁 File Inventory\n")
            f.write("| File | Invariant | Resonance |\n")
            f.write("| :--- | :--- | :--- |\n")
            for item in sorted(self.results["inventory"], key=lambda x: (x["type"], x["file"])):
                 res = item.get('resonance', 'N/A')
                 if isinstance(res, float): res = f"{res:.4f}"
                 f.write(f"| {item['file']} | {item['type']} | {res} |\n")

        self._log(f"Deep Scan Synthesis Complete. Report saved to: {report_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--expansion", action="store_true")
    args = parser.parse_args()
    
    scanner = SovereignScanner(fast_mode=args.fast, expansion_mode=args.expansion)
    scanner.run()
