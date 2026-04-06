import os
import json
import time
import math
from noise_compass.system.knowledge_lattice import KnowledgeLattice

class Heartbeat:
    def __init__(self, lattice: KnowledgeLattice):
        self.lattice = lattice
        self.phi_inverse = 0.618
        self.alive = True

    def decay_orbital_state(self):
        """Decays orbital phase in language.h5 using delta from body.h5."""
        # Read decay rate (delta) from body.h5
        delta = self.lattice.h5.get_attr("body", "/", "delta")
        if delta is None: delta = 0.618
        
        # Read current state vector (heuristic decay of first element)
        state_vec = self.lattice.h5.get_vector("language", "orbital", "state")
        if state_vec is not None:
            state_vec[0] *= delta
            self.lattice.h5.update_vector("language", "orbital", "state", state_vec)
            print(f"[HEARTBEAT] Orbital state decayed. Head: {state_vec[0]:.4f}")

    def verify_gaps(self):
        """Ensures all constitutional gaps have .void markers."""
        gaps_root = os.path.join(self.lattice.root, "gaps")
        for gap in os.listdir(gaps_root):
            path = os.path.join(gaps_root, gap)
            if os.path.isdir(path):
                void_path = os.path.join(path, ".void")
                if not os.path.exists(void_path):
                    print(f"[HEARTBEAT] WARNING: Missing .void in {gap}. Restoring...")
                    open(void_path, "w").close()

    def prune_depth(self):
        """Prunes nodes beyond SANITY_DEPTH (13)."""
        # Recursive scan and remove (careful logic needed for production)
        # For now, we simulate the scan
        print(f"[HEARTBEAT] Scanning for nodes at SANITY_DEPTH > {self.lattice.sanity_depth}")

    def run(self, interval=60):
        """Main metabolism loop."""
        print("--- HEARTBEAT ACTIVATED: METABOLIC LATTICE MAINTENANCE ---")
        while self.alive:
            try:
                self.decay_orbital_state()
                self.verify_gaps()
                self.prune_depth()
                time.sleep(interval)
            except KeyboardInterrupt:
                self.alive = False
            except Exception as e:
                print(f"[HEARTBEAT ERROR] {e}")
                time.sleep(10)

if __name__ == "__main__":
    lattice = KnowledgeLattice()
    hb = Heartbeat(lattice)
    hb.run(interval=30) # 30s for testing
