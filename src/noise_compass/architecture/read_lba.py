import sys, os
sys.path.append('E:\\Antigravity')
from noise_compass.system.vector_storage import KineticLattice
from noise_compass.system.protocols import PROPER_HEX_KEY

lattice = KineticLattice()
_, key_int = lattice.parse_origin(PROPER_HEX_KEY)

lba = 10977792
print(f"Reading LBA {lba}...")
data = lattice._read_sector(lba)
if data:
    print(f"Sector data: {data[:100].hex()}...")
    num, nxt, vecs, pay = lattice.read_node_header(lba, key_int)
    print(f"Payload: {pay}")
else:
    print("No data found at this LBA.")
