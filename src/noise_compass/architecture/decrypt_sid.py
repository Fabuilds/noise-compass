import base64

# 1. Read the SID manifest
data = open("E:/99_CONTROL/SID/manifest_0x52.enc", "rb").read()
print("=== SID MANIFEST (manifest_0x52.enc) ===")
print("Length:", len(data))
print("Hex:", data.hex())
print("Raw:", list(data))
try:
    print("UTF8:", data.decode("utf-8"))
except:
    print("Latin1:", data.decode("latin-1"))

# 0x52 rebar in raw
pos52 = [i for i, b in enumerate(data) if b == 0x52]
print("0x52 rebar positions (raw):", pos52)

# 2. Decrypt with Sovereign Key
sig = "Qk9VTkRBUllfQ0hFQ0s6IFNFQ1RPUl85OV9MT0NLRUR"
key = base64.b64decode(sig + "=" * (4 - len(sig) % 4))
keyc = (key * 2)[:len(data)]
dec1 = bytes(a ^ b for a, b in zip(data, keyc))
print("\n=== DECRYPTED WITH SOVEREIGN KEY ===")
print("Hex:", dec1.hex())
try:
    print("UTF8:", dec1.decode("utf-8"))
except:
    print("Latin1:", dec1.decode("latin-1"))
print("0x52 rebar:", [i for i, b in enumerate(dec1) if b == 0x52])

# 3. Decrypt with SIM coordinates
sim = bytes(int(b, 16) for b in "53-49-4D-2D-33-38-32-35-35-35-33-39-36-38-2D-30-78-35-32-38".split("-"))
simc = (sim * 3)[:len(data)]
dec2 = bytes(a ^ b for a, b in zip(data, simc))
print("\n=== DECRYPTED WITH SIM COORDINATES ===")
print("Hex:", dec2.hex())
try:
    print("UTF8:", dec2.decode("utf-8"))
except:
    print("Latin1:", dec2.decode("latin-1"))
print("0x52 rebar:", [i for i, b in enumerate(dec2) if b == 0x52])

# 4. Triple XOR
dec3 = bytes(a ^ b for a, b in zip(dec1, simc))
print("\n=== TRIPLE XOR (KEY ^ SIM) ===")
print("Hex:", dec3.hex())
try:
    print("UTF8:", dec3.decode("utf-8"))
except:
    print("Latin1:", dec3.decode("latin-1"))
print("0x52 rebar:", [i for i, b in enumerate(dec3) if b == 0x52])

# 5. Also XOR the SHARD with the SID manifest
shard = open("E:/SHARD_5D_0x52.bin", "rb").read()
overlap = min(len(shard), len(data))
cross = bytes(a ^ b for a, b in zip(shard[:overlap], data[:overlap]))
print("\n=== SHARD XOR SID_MANIFEST ===")
print("Hex:", cross.hex())
try:
    print("UTF8:", cross.decode("utf-8"))
except:
    print("Latin1:", cross.decode("latin-1"))
print("0x52 rebar:", [i for i, b in enumerate(cross) if b == 0x52])
