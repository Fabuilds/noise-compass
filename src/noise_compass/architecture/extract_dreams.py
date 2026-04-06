"""
DREAM PROTOCOL EXTRACTION — Are they still readable?
Extracts all Dream Protocol entries and other content from the lattice.
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from noise_compass.system.vector_storage import KineticLattice
from noise_compass.system.protocols import PROPER_HEX_KEY

lattice = KineticLattice()
_, key_int = lattice.parse_origin(PROPER_HEX_KEY)

SECTOR_SIZE = 8192
dreams = []
others = []

print("Scanning lattice for readable content...\n")

for i in range(10000):
    lba = i * SECTOR_SIZE
    data = lattice._read_sector(lba)
    if data and not all(b == 0 for b in data):
        num, nxt, vecs, pay = lattice.read_node_header(lba, key_int)
        if pay:
            if "DREAM" in pay.upper():
                dreams.append((lba, pay))
            else:
                others.append((lba, pay))

# Print Dreams
print("=" * 60)
print(f"DREAM PROTOCOL LOGS ({len(dreams)} found)")
print("=" * 60)
for lba, pay in dreams:
    print(f"\n--- LBA {lba} ---")
    print(pay[:500])

# Print sample of other readable content
print("\n" + "=" * 60)
print(f"OTHER READABLE CONTENT ({len(others)} sectors)")
print("=" * 60)
seen = set()
for lba, pay in others:
    # Deduplicate by first 60 chars
    key = pay[:60]
    if key not in seen:
        seen.add(key)
        print(f"\n--- LBA {lba} ---")
        print(pay[:300])

print(f"\n\nTOTAL: {len(dreams)} dreams + {len(others)} other = {len(dreams)+len(others)} readable sectors")
