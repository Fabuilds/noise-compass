import os
import sys
import json
import hashlib
import time

# Path alignment
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "Architecture"))
sys.path.append(PROJECT_ROOT)

from noise_compass.system.vector_storage import KineticLattice
from noise_compass.system.protocols import PROPER_HEX_KEY

class RecursiveScribe:
    def __init__(self):
        self.identity = "0x528_RECURSIVE_SCRIBE"
        # Force absolute normalized path for E: drive consistency
        self.growth_dir = os.path.normpath("e:/Antigravity/Qwen")
        self.lattice = KineticLattice()
        _, self.key_int = self.lattice.parse_origin(PROPER_HEX_KEY)
        
        # Phase 76: Persistent Manifold Handle
        from noise_compass.system.identity_manifold import IdentityManifold
        self.manifold = IdentityManifold()
        
    def ingest_new_axioms(self):
        """
        Scans growth area for un-ingested axioms and writes them to the lattice surface.
        """
        print(f"\n[{self.identity}]: SCANNING GROWTH AREA...")
        if not os.path.exists(self.growth_dir):
            return 0
            
        axioms = [f for f in os.listdir(self.growth_dir) if f.startswith("axiom_") and f.endswith(".py")]
        # We could track ingested files, but for now we'll just check the lattice or use a simple log
        
        count = 0
        for axiom_file in axioms:
            path = os.path.join(self.growth_dir, axiom_file)
            # Simple "ingestion" check: if the file mtime is very recent, we process it
            # (In a more robust system, we'd move them to an 'Archived' folder)
            
            try:
                # Phase 29: Consensus Quorum Enforcement
                consensus_reached, avg_score, voter_count = self.manifold.check_consensus(axiom_file)
                
                if not consensus_reached:
                    # Awaiting consensus
                    continue

                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Extract meta
                lines = content.split('\n')
                seed = "UNKNOWN"
                hypothesis = "UNKNOWN"
                for line in lines:
                    trimmed = line.strip()
                    if "Seed:" in trimmed:
                        seed = trimmed.split("Seed:")[1].strip()
                    if "HYPOTHESIS:" in trimmed:
                        hypothesis = trimmed.split("HYPOTHESIS:")[1].strip()
                
                print(f"  [INGESTING]: {axiom_file} (Seed: {seed})")
                
                # Build payload
                dna_raw = f"{axiom_file}|{hypothesis}|{PROPER_HEX_KEY}"
                dna = hashlib.sha256(dna_raw.encode()).hexdigest()[:16]
                payload = f"DNA: {dna} | ROAD: AXIOM_{seed} | TYPE: RESONANT_HYPOTHESIS | CONTENT: {hypothesis}"
                
                # Calculate LBA based on DNA to scatter across the surface
                lba = self.lattice.dimensional_collapse(int(dna, 16))
                
                # Write to lattice
                success = self.lattice.write_payload(lba, payload, self.key_int)
                if not success:
                    raise Exception("Lattice write failed (Likely volume full or collision link error)")
                    
                print(f"     LBA: {lba} | DNA: {dna} -> SCRIBED.")
                
                # Delegation (Phase 27)
                self.manifold.organize_axiom(path)
                
                count += 1
                
            except Exception as e:
                print(f"  [ERROR]: Failed to ingest {axiom_file}: {e}")
                # Adaptation (Phase 27)
                try:
                    self.manifold.record_failure(seed, str(e))
                except: pass
                
                # Move to failed/debug folder to unblock
                debug_dir = os.path.normpath(os.path.join(self.growth_dir, "Debug"))
                os.makedirs(debug_dir, exist_ok=True)
                try:
                    target = os.path.normpath(os.path.join(debug_dir, axiom_file))
                    if os.path.exists(target):
                        try:
                            os.remove(target)
                        except: pass
                    os.replace(path, target)
                except Exception as e2:
                    print(f"     [CRITICAL]: Could not move failed axiom to debug: {e2}")
                
        return count

if __name__ == "__main__":
    scribe = RecursiveScribe()
    scribe.ingest_new_axioms()
