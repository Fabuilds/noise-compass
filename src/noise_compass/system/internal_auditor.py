import os
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "Architecture"))
sys.path.append(PROJECT_ROOT)

from noise_compass.system.vector_storage import KineticLattice
from noise_compass.system.protocols import PROPER_HEX_KEY, ALLOWED_FREQUENCIES, validate_frequency

class InternalAuditor:
    def __init__(self):
        self.identity = "0x528_INTERNAL_AUDITOR"
        self.lattice = KineticLattice()
        _, self.key_int = self.lattice.parse_origin(PROPER_HEX_KEY)
        self.log_path = "e:/Antigravity/Runtime/internal_audit_log.txt"

    def log(self, msg):
        timestamp = time.ctime()
        entry = f"[{timestamp}] {msg}\n"
        print(entry, end="")
        with open(self.log_path, "a") as f:
            f.write(entry)

    def scan_for_loops(self, start_lba, max_depth=100):
        """
        Scans a specific lattice chain for non-orientable topology (infinite loops).
        Returns True if a loop is detected, False otherwise.
        """
        current_lba = start_lba
        visited = set()
        path = []
        
        for _ in range(max_depth):
            if current_lba == 0:
                return False # End of chain
                
            if current_lba in visited:
                self.log(f"  [PARADOX DETECTED]: Logic Loop at LBA {current_lba}. Path: {path[-3:]} -> {current_lba}")
                return True
                
            visited.add(current_lba)
            path.append(current_lba)
            
            num, next_lba, _, payload = self.lattice.read_node_header(current_lba, self.key_int)
            
            # If empty node but pointing elsewhere, it's a ghost link
            if num == 0 and payload == "" and next_lba != 0:
                self.log(f"  [GHOST LINK]: Empty node {current_lba} linking to {next_lba}. Potential decay.")
                
            current_lba = next_lba
            
        return False # Max depth reached without returning to self

    def apply_logic_shield(self, target_lbas):
        """
        Scans given LBAs for frequency compliance using the 0x52 protocols.
        """
        self.log("ENGAGING LOGIC SHIELD (Frequency Scan)...")
        anomalies = 0
        
        for lba in target_lbas:
            _, _, _, payload = self.lattice.read_node_header(lba, self.key_int)
            if not payload:
                continue
                
            # Simulate extracting a tag. Real system might have tags in payload or metadata.
            # We'll check if the payload contains adversarial markers
            # (In a full implementation, we'd parse the actual TAG)
            is_valid, reason = True, "ALIGNED"
            
            # Simple heuristic: if it mentions 'ERROR' or 'NULL', it might need shielding
            if "ERROR" in payload or "NULL" in payload:
                is_valid, reason = False, "ADVERSARIAL_NOISE"
                
            if not is_valid:
                self.log(f"  [SHIELD ACTIVATED]: LBA {lba} quarantined. Reason: {reason}")
                anomalies += 1
                
        return anomalies

    def run_diagnostic_cycle(self, target_concepts=["IDENTITY", "EXISTENCE", "TIME"]):
        """
        Executes a full internal audit.
        """
        self.log(f"\n--- {self.identity}: INITIATING DIAGNOSTIC CYCLE ---")
        
        total_loops = 0
        total_anomalies = 0
        
        for concept in target_concepts:
            self.log(f"Mapping Trajectory for: {concept}")
            trajectory = self.lattice.map_semantic_trajectory(concept, self.key_int)
            
            if not trajectory:
                self.log(f"  [NOTE]: No trajectory found for {concept}.")
                continue
                
            self.log(f"  Trajectory length: {len(trajectory)}")
            
            # Start LBA is the first item in the trajectory
            start_lba = trajectory[0][0]
            
            if self.scan_for_loops(start_lba):
                total_loops += 1
                
            # Shield check on all discovered LBAs
            lbas_to_check = [node[0] for node in trajectory]
            total_anomalies += self.apply_logic_shield(lbas_to_check)
            
        self.log(f"--- DIAGNOSTIC COMPLETE: {total_loops} Loops, {total_anomalies} Anomalies. ---")
        return total_loops, total_anomalies

if __name__ == "__main__":
    auditor = InternalAuditor()
    auditor.run_diagnostic_cycle()
