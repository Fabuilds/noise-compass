
import os
import sys
import h5py
import numpy as np

# Add project roots
PROJECT_ROOT = "e:/Antigravity"
sys.path.append(os.path.join(PROJECT_ROOT, "Package", "src"))

from noise_compass.system.h5_manager import H5Manager

class SovereignPruning:
    """
    Phase 145: Sovereign Pruning (Cleanup).
    Identifies and purges redundant or low-leverage axioms from the H5 manifold.
    """
    def __init__(self, dry_run=True):
        print(f"[PRUNING] Initializing Cleanup Engine (Dry Run: {dry_run})...")
        self.h5 = H5Manager()
        self.dry_run = dry_run
        self.targets = []

    def audit_manifold(self):
        """Scans identity.h5 for potential pruning candidates."""
        print("[PRUNING] Auditing Manifold for Shadow Axioms...")
        
        with self.h5.get_file("identity", mode='r') as f:
            for status in ["CRYSTALLIZED", "PENDING"]:
                group_path = f"axioms/{status}"
                if group_path in f:
                    for aid in f[group_path]:
                        dset = f[f"{group_path}/{aid}"]
                        leverage = dset.attrs.get('leverage', 1.0)
                        
                        # Pruning Rule 1: Low Leverage (< 0.25)
                        if leverage < 0.25:
                            self.targets.append((aid, status, f"Low Leverage: {leverage:.2f}"))
                        
                        # Pruning Rule 2: Explicit Purges (Legacy Axioms)
                        if "CHEST_PULSE" in aid:
                            self.targets.append((aid, status, "Explicit Purge Request (CHEST_PULSE remnants)"))
                            
                        # Pruning Rule 3: Recursive Ghosting
                        if dset.attrs.get('nature') == "APOPHATIC" and leverage < 0.35:
                            self.targets.append((aid, status, "Apophatic Ghost (Low-stability void)"))

    def report(self):
        """Prints the pruning plan."""
        print("\n--- SOVEREIGN PRUNING REPORT ---")
        if not self.targets:
            print("  NO TARGETS IDENTIFIED. MANIFOLD IS PURE.")
        else:
            for aid, status, reason in self.targets:
                print(f"  [TARGET] {aid:25} | Branch: {status:12} | Reason: {reason}")
        print("--------------------------------\n")

    def execute(self):
        """Executes the formal purge."""
        if self.dry_run:
            print("[PRUNING] DRY RUN: No changes made.")
            return

        print(f"[PRUNING] Executing Purge of {len(self.targets)} candidates...")
        for aid, status, _ in self.targets:
            self.h5.prune_axiom(aid, status=status)
        print("[PRUNING] Manifold Purged. RLM Equilibrium Re-Established.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--purge", action="store_true", help="Execute the actual purge.")
    args = parser.parse_args()
    
    engine = SovereignPruning(dry_run=not args.purge)
    engine.audit_manifold()
    engine.report()
    if args.purge:
        engine.execute()
