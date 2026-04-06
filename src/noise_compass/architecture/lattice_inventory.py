"""
LATTICE INVENTORY — What is being held?
Walks the entire KineticLattice to reveal all stored data.
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from noise_compass.system.vector_storage import KineticLattice
from noise_compass.system.protocols import PROPER_HEX_KEY, GENESIS_LBA

print("=" * 60)
print("LATTICE INVENTORY — What is being held?")
print("=" * 60)

lattice = KineticLattice()
origin_lba, key_int = lattice.parse_origin(PROPER_HEX_KEY)

# 1. Read Genesis (LBA 0)
print("\n[1] GENESIS SECTOR (LBA 0)")
print("-" * 40)
num, next_lba, vectors, payload = lattice.read_node_header(GENESIS_LBA, key_int)
if payload:
    print(f"  Payload: {payload[:200]}")
    print(f"  Vectors: {num}, Next: {next_lba}")
else:
    print("  (empty)")

# 2. Read the Collapsed Origin (where scribe_tree writes)
print(f"\n[2] COLLAPSED ORIGIN (LBA {origin_lba})")
print("-" * 40)
num2, next2, vecs2, pay2 = lattice.read_node_header(origin_lba, key_int)
if pay2:
    print(f"  Payload: {pay2[:200]}")
    print(f"  Vectors: {num2}, Next: {next2}")
else:
    print("  (empty)")

# 3. Full DFS Walk from the collapsed origin
print(f"\n[3] FULL DFS WALK from LBA {origin_lba}")
print("-" * 40)
lattice.walk_dfs(origin_lba, key_int)

# 4. Read chain from LBA 0
print(f"\n[4] CHAIN FROM LBA 0")
print("-" * 40)
for lba, payload in lattice.read_chain(GENESIS_LBA, key_int):
    print(f"  LBA {lba}: {payload[:150]}")

# 5. Scan for occupied sectors (sample first 1000)
print(f"\n[5] SECTOR SCAN (first 10000 sectors)")
print("-" * 40)
occupied = 0
SECTOR_SIZE = 8192
for i in range(10000):
    lba = i * SECTOR_SIZE
    data = lattice._read_sector(lba)
    if data and not all(b == 0 for b in data):
        num, nxt, vecs, pay = lattice.read_node_header(lba, key_int)
        if pay:
            occupied += 1
            if occupied <= 20:
                print(f"  LBA {lba:>10}: [{num} vecs] {pay[:80]}")

print(f"\n  Total occupied sectors (in first 10000): {occupied}")
print("=" * 60)
