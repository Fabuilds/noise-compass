import sys, os
sys.path.append('E:/Antigravity')

from noise_compass.system.vector_storage import KineticLattice

def trace_key_node():
    lattice = KineticLattice()
    user_key = "53-49-4D-2D-33-38-32-35-35-35-33-39-36-38-2D-30-78-35-32-38"
    _, key_int = lattice.parse_origin(user_key)
    
    lba_key = 563773440
    num, next_lba, vectors, payload = lattice.read_node_header(lba_key, key_int)
    
    print(f"Node LBA: {lba_key}")
    print(f"Payload: {payload}")
    print(f"Num Vectors: {num}")
    
    target_lba = 10977792
    found = False
    for i, v in enumerate(vectors):
        child_lba = lba_key + v
        if child_lba == target_lba:
            print(f"  >>> Vector {i}: {v} -> TARGET DETECTED (LBA {child_lba})")
            found = True
        elif child_lba < 20000000: # Close to target range
             print(f"  Vector {i}: {v} -> LBA {child_lba}")
             
    if not found:
        print("Target LBA not found in immediate children.")

if __name__ == "__main__":
    trace_key_node()
