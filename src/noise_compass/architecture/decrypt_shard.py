import base64
import struct

print("=" * 60)
print("SHARD DECRYPTION — SOVEREIGN KEY x SHARD_5D_0x52")
print("=" * 60)

# 1. Decode the Sovereign Key
sig = "Qk9VTkRBUllfQ0hFQ0s6IFNFQ1RPUl85OV9MT0NLRUR"
padding = "=" * (4 - len(sig) % 4)
key_decoded = base64.b64decode(sig + padding)
print(f"\n[KEY] Base64 Decoded: {key_decoded}")
print(f"[KEY] Hex: {key_decoded.hex()}")
print(f"[KEY] Length: {len(key_decoded)} bytes")

# 2. Decode the User's Hex Identifier
user_hex = "53-49-4D-2D-33-38-32-35-35-35-33-39-36-38-2D-30-78-35-32-38"
sim_bytes = bytes(int(b, 16) for b in user_hex.split("-"))
sim_ascii = sim_bytes.decode("ascii")
print(f"\n[SIM] Hex Input Decoded: {sim_ascii}")
print(f"[SIM] Bytes: {sim_bytes.hex()}")
print(f"[SIM] Length: {len(sim_bytes)} bytes")

# 3. Read the Shard
shard = open("E:/SHARD_5D_0x52.bin", "rb").read()
print(f"\n[SHARD] Hex: {shard.hex()}")
print(f"[SHARD] Length: {len(shard)} bytes")

# 4. Pass 1: SHARD ^ SOVEREIGN_KEY
print("\n" + "=" * 60)
print("PASS 1: SHARD XOR SOVEREIGN_KEY")
print("=" * 60)
key1 = key_decoded
key1c = (key1 * ((len(shard) // len(key1)) + 1))[:len(shard)]
dec1 = bytes(a ^ b for a, b in zip(shard, key1c))
print(f"  Hex: {dec1.hex()}")
print(f"  Latin1: {dec1.decode('latin-1')}")

# 5. Pass 2: SHARD ^ SIM_IDENTIFIER
print("\n" + "=" * 60)
print("PASS 2: SHARD XOR SIM_IDENTIFIER")
print("=" * 60)
key2 = sim_bytes
key2c = (key2 * ((len(shard) // len(key2)) + 1))[:len(shard)]
dec2 = bytes(a ^ b for a, b in zip(shard, key2c))
print(f"  Hex: {dec2.hex()}")
print(f"  Latin1: {dec2.decode('latin-1')}")

# 6. Pass 3: SHARD ^ KEY ^ SIM (Triple XOR)
print("\n" + "=" * 60)
print("PASS 3: SHARD XOR KEY XOR SIM (Triple)")
print("=" * 60)
dec3 = bytes(a ^ b for a, b in zip(dec1, key2c))
print(f"  Hex: {dec3.hex()}")
print(f"  Latin1: {dec3.decode('latin-1')}")

# 7. Ghost Anchor Analysis (0x52)
print("\n" + "=" * 60)
print("GHOST ANCHOR (0x52 = 'R')")
print("=" * 60)
for label, data in [("Raw Shard", shard), ("Dec1 (Key)", dec1), ("Dec2 (SIM)", dec2), ("Dec3 (Key^SIM)", dec3)]:
    positions = [i for i, b in enumerate(data) if b == 0x52]
    if positions:
        print(f"  [{label}] Ghost 0x52 at offsets: {positions}")
    else:
        print(f"  [{label}] No ghost anchor found")

# 8. LBA0 (First 16 bytes)
print("\n" + "=" * 60)
print("LBA0 ANALYSIS (First 16 bytes)")
print("=" * 60)
for label, data in [("Raw Shard", shard), ("Dec1 (Key)", dec1), ("Dec2 (SIM)", dec2), ("Dec3 (Key^SIM)", dec3)]:
    print(f"\n  [{label}]")
    print(f"    Hex: {data[:16].hex()}")
    v1 = struct.unpack("<Q", data[:8])[0]
    v2 = struct.unpack(">Q", data[:8])[0]
    print(f"    LE uint64: {v1} (hex: {hex(v1)})")
    print(f"    BE uint64: {v2} (hex: {hex(v2)})")

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
