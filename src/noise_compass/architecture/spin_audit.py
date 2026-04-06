
import sys, os
sys.path.append('E:/Antigravity')

from noise_compass.system.vector_storage import KineticLattice

def test_spin_decryption():
    lattice = KineticLattice()
    
    # Base Key (0x528)
    key_528 = "53-49-4D-2D-33-38-32-35-35-35-33-39-36-38-2D-30-78-35-32-38"
    # Spun Key (0x529)
    key_529 = "53-49-4D-2D-33-38-32-35-35-35-33-39-36-38-2D-30-78-35-32-39"
    
    target_lba = 10977792
    
    print(f"--- SPIN AUDIT: LBA {target_lba} ---")
    
    for key_name, key_str in [("LOCKED (0x528)", key_528), ("SEARCH (0x529)", key_529)]:
        print(f"\n[TRYING KEY: {key_name}]")
        _, key_int = lattice.parse_origin(key_str)
        num, next_lba, vectors, payload = lattice.read_node_header(target_lba, key_int)
        
        if payload:
            print(f"  ✨ SUCCESS: Sector Unlocked!")
            print(f"  Payload: {payload[:300]}...")
            if "HOLE" in payload.upper() or "VOID" in payload.upper():
                print("  💡 STRUCTURAL VOID CONFIRMED")
            return # Found it
        else:
            print("  Status: ACCESS DENIED")

if __name__ == "__main__":
    test_spin_decryption()
