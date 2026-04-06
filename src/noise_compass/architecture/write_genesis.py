"""
GENESIS SECTOR WRITE — Seeding LBA 0
Seeds the origin sector with the 0x528 identity genesis payload.
"""
import sys, os, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from noise_compass.system.vector_storage import KineticLattice
from noise_compass.system.protocols import PROPER_HEX_KEY, GENESIS_LBA, GENESIS_SEED, PROTOCOL_ID

print("=" * 60)
print("GENESIS SECTOR WRITE (LBA 0)")
print("=" * 60)

lattice = KineticLattice()
_, key_int = lattice.parse_origin(PROPER_HEX_KEY)

print(f"Key: {PROPER_HEX_KEY}")
print(f"Key Int: {key_int}")
print(f"Genesis LBA: {GENESIS_LBA}")
print(f"Genesis Seed: {GENESIS_SEED}")
print(f"Protocol: {PROTOCOL_ID}")

# The Genesis Payload
genesis_payload = (
    f"GENESIS_MAP | "
    f"SEED={GENESIS_SEED} | "
    f"PROTOCOL={PROTOCOL_ID} | "
    f"ORIGIN=SIM-{GENESIS_SEED}-{PROTOCOL_ID} | "
    f"TIMESTAMP={time.strftime('%Y-%m-%dT%H:%M:%S')} | "
    f"SIGNATURE=BOUNDARY_CHECK:SECTOR_99_LOCKED | "
    f"STATUS=ALIVE"
)

print(f"\nPayload: {genesis_payload}")
print(f"\nWriting to LBA {GENESIS_LBA}...")

success = lattice.write_payload(GENESIS_LBA, genesis_payload, key_int)

if success:
    print("\n[GENESIS] Write successful.")
else:
    print("\n[ERROR] Write failed.")

# Verify by reading it back
print("\n" + "=" * 60)
print("VERIFICATION — Reading LBA 0")
print("=" * 60)

num, next_lba, vectors, payload = lattice.read_node_header(GENESIS_LBA, key_int)
print(f"Num vectors: {num}")
print(f"Next LBA: {next_lba}")
print(f"Payload: {payload}")

if "GENESIS_MAP" in payload and str(GENESIS_SEED) in payload:
    print("\n[VERIFIED] Genesis sector is ALIVE.")
else:
    print("\n[WARNING] Verification mismatch.")

print("=" * 60)
