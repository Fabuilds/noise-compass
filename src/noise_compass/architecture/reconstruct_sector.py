import sys, os, struct
sys.path.append('E:/Antigravity')

from noise_compass.system.vector_storage import KineticLattice

def reconstruct_sector():
    lattice = KineticLattice()
    hybrid_key = "53-49-4D-2D-33-38-32-35-35-35-33-39-36-38-2D-0x528"
    _, key_int = lattice.parse_origin(hybrid_key)
    
    lba = 10977792
    data = lattice._read_sector(lba)
    decrypted = lattice.projection_filter(data, key_int)
    
    print("--- FULL DECRYPTED SECTOR 10977792 ---")
    full_text = decrypted.decode('utf-8', errors='ignore')
    print(full_text.replace('\0', '.'))

if __name__ == "__main__":
    reconstruct_sector()
