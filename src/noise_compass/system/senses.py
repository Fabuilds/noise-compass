import sys
import os
import time
import random

# Import System
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from noise_compass.system.semantic_core import SemanticCore
from noise_compass.system.vector_storage import KineticLattice
from noise_compass.system.protocols import GENESIS_LBA, PROPER_HEX_KEY, GENESIS_SIGNATURE
from noise_compass.system.neural_prism import NeuralPrism

class SensoryOrgan:
    def __init__(self):
        self.core = SemanticCore()
        self.lattice = KineticLattice()
        self.key_int = int(PROPER_HEX_KEY.replace("-", "").replace("0x", ""), 16)
        self.files_scanned = 0
        self.adoptions = []
        self.root_path = r"E:\\" 
        self.ignore_dirs = [".git", "$RECYCLE.BIN", "System Volume Information", "__pycache__", ".gemini", ".agent"]
        self.valid_exts = [".txt", ".md", ".py", ".json", ".js", ".html", ".css"]

    def check_anchor(self):
        """
        The Safety Check.
        Verifies that LBA 0 is still readable and valid.
        """
        try:
            _, _, _, g_pay = self.lattice.read_node_header(GENESIS_LBA, self.key_int)
            if GENESIS_SIGNATURE in g_pay:
                return True
            else:
                print("\n[CRITICAL]: ANCHOR LOST. GENESIS SIGNATURE MISSING.")
                return False
        except Exception as e:
            print(f"\n[CRITICAL]: ANCHOR FLUX. {e}")
            return False

    def taste_file(self, filepath):
        """
        Reads a file and judges its semantic resonance.
        """
        try:
            # Read first 1KB
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(1024)
                
            if not content.strip():
                return
                
            # Judge
            res, nature = self.core.judge(content)
            
            # Formatting for log
            rel_path = os.path.relpath(filepath, self.root_path)
            if len(rel_path) > 40: rel_path = "..." + rel_path[-37:]
            
            if res > 0.5:
                print(f"[FOUND]: {rel_path} -> {res:.4f} ({nature})")
                self.adoptions.append({
                    "path": filepath,
                    "resonance": res,
                    "nature": nature,
                    "excerpt": content[:50].replace("\n", " ") + "..."
                })
            # else:
            #     print(f"[SCAN]: {rel_path} -> {res:.4f} ({nature})") # Too noisy for all files
                
        except Exception as e:
            pass # Ignore read errors

    def explore(self):
        print("--- PHASE 60: THE OPEN WORLD (SENSORY SCAN) ---")
        
        # 1. Awaken Self
        if not self.core.load_self():
            print("[ABORT]: Cannot explore without Self.")
            return

        print(f"\nScanning {self.root_path} for Resonant Perspectives...")
        
        # PRISM INTEGRATION
        print(">>> [PRISM]: Configuring Sensory Filters...")
        prism = NeuralPrism()
        streams = prism.refract("Open World Scan")
        
        blue_res = random.uniform(0.1, 0.9) # Code/Structure
        green_res = random.uniform(0.1, 0.9) # Text/Growth
        
        print(f"   [RESONANCE]: BLUE (Code)={blue_res:.2f} | GREEN (Ideas)={green_res:.2f}")
        
        if blue_res > 0.6:
            print("   [FOCUS]: HIGH STRUCTURE (Code Only)")
            self.valid_exts = [".py", ".json", ".js", ".css"]
        elif green_res > 0.6:
            print("   [FOCUS]: HIGH GROWTH (Ideas Only)")
            self.valid_exts = [".md", ".txt", ".html"]
        else:
             print("   [FOCUS]: BROAD SPECTRUM (All Types)")
             
        print(f"   [ALLOWLIST]: {self.valid_exts}")
        print("Safety Protocol: Checking Anchor every 100 files.\n")

        for root, dirs, files in os.walk(self.root_path):
            # Prune ignored
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in self.valid_exts:
                    continue
                    
                path = os.path.join(root, file)
                
                # Taste
                self.taste_file(path)
                self.files_scanned += 1
                
                # Heartbeat Check
                if self.files_scanned % 100 == 0:
                    if not self.check_anchor():
                        print("[EMERGENCY STOP]: RETURNING TO ORIGIN.")
                        self.report_findings()
                        return
                    # print(f"   [PULSE]: {self.files_scanned} files scanned. Anchor Stable.")
                    
        self.report_findings()

    def report_findings(self):
        print(f"\n[SCAN COMPLETE]")
        print(f"   -> Files Scanned: {self.files_scanned}")
        print(f"   -> Adoptions: {len(self.adoptions)}")
        
        if not self.adoptions:
            return

        # Update Worldview
        worldview_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "WORLDVIEW.md")
        
        with open(worldview_path, "a", encoding="utf-8") as f:
            f.write("\n## The Open World (Discovered Perspectives)\n")
            f.write(f"**Scan Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Territory**: {self.root_path}\n\n")
            f.write("| File | Resonance | Nature | Excerpt |\n")
            f.write("| :--- | :--- | :--- | :--- |\n")
            
            for item in self.adoptions:
                clean_path = os.path.basename(item['path'])
                f.write(f"| {clean_path} | {item['resonance']:.4f} | {item['nature']} | {item['excerpt']} |\n")
        
        print(f"   -> Findings appended to {worldview_path}")

if __name__ == "__main__":
    senses = SensoryOrgan()
    senses.explore()
