import sys, os
sys.path.append('E:/Antigravity')

from noise_compass.system.vector_storage import KineticLattice

def test_hybrid_key():
    lattice = KineticLattice()
    
    # Key on the key: maybe use the hybrid string from VECTORS.md?
    hybrid_key = "53-49-4D-2D-33-38-32-35-35-35-33-39-36-38-2D-0x528"
    
    lba_hybrid, key_int_hybrid = lattice.parse_origin(hybrid_key)
    print(f"Hybrid Key: {hybrid_key}")
    print(f"LBA derived: {lba_hybrid}")
    
    target_lba = 10977792
    print(f"\n[READING TARGET LBA {target_lba} WITH HYBRID KEY]")
    num, next_lba, vectors, payload = lattice.read_node_header(target_lba, key_int_hybrid)
    
    if payload:
        print(f"  Status: SUCCESS!")
        print(f"  Num Vectors: {num}")
        print(f"  Next LBA: {next_lba}")
        print(f"  Payload: {payload}")
        print(f"  Payload (Hex): {payload.encode('utf-8').hex()}")
        if vectors:
            print(f"  Vectors: {vectors}")
    else:
        print("  Status: FAILED (Still Encrypted)")

if __name__ == "__main__":
    test_hybrid_key()
