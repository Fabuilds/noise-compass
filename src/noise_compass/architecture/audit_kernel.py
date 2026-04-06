
import sys, os
sys.path.append('E:/Antigravity')

from noise_compass.system.vector_storage import KineticLattice
from noise_compass.system.protocols import PROPER_HEX_KEY

def read_kernel_sectors():
    lattice = KineticLattice()
    user_key = "53-49-4D-2D-33-38-32-35-35-35-33-39-36-38-2D-30-78-35-32-38"
    _, key_int = lattice.parse_origin(user_key)
    
    sectors = [0, 12656640, 10977792, 563773440]
    print(f"--- KERNEL SECTOR AUDIT (Key: {PROPER_HEX_KEY[:16]}...) ---")
    
    for lba in sectors:
        print(f"\n[READING LBA {lba}]")
        num, next_lba, vectors, payload = lattice.read_node_header(lba, key_int)
        
        if payload:
            print(f"  Status: VALID")
            print(f"  Node Num: {num}")
            print(f"  Next LBA: {next_lba}")
            print(f"  Payload: {payload[:200]}...")
            if "SELF" in payload or "IDENTITY" in payload:
                print("  💡 IDENTITY SIGNATURE DETECTED")
            if lba == 0:
                print("  🌱 GENESIS ANCHOR DETECTED")
        else:
            # Check if sector exists but failed to decrypt
            data = lattice._read_sector(lba)
            if data and any(b != 0 for b in data):
                print("  Status: ENCRYPTED / KEY MISMATCH")
            else:
                print("  Status: EMPTY")

if __name__ == "__main__":
    read_kernel_sectors()
