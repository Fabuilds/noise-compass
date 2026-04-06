"""
DREAM PROTOCOL DEEP EXTRACTION + LATTICE TOPOLOGY AS LIGHT
"""
import sys, os, time, math
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from noise_compass.system.vector_storage import KineticLattice
from noise_compass.system.protocols import PROPER_HEX_KEY

lattice = KineticLattice()
_, key_int = lattice.parse_origin(PROPER_HEX_KEY)

SECTOR_SIZE = 8192
VOLUME_SIZE = 1024 * 1024 * 1024

# ═══════════════════════════════════════════════
# PART 1: FULL DREAM EXTRACTION
# ═══════════════════════════════════════════════
print("=" * 60)
print("DREAM PROTOCOL — FULL EXTRACTION")
print("=" * 60)

dreams = []
all_sectors = []

for i in range(10000):
    lba = i * SECTOR_SIZE
    data = lattice._read_sector(lba)
    if data and not all(b == 0 for b in data):
        # Decrypt
        decrypted = lattice.projection_filter(data, key_int)
        num, nxt, vecs, pay = lattice.read_node_header(lba, key_int)
        
        if pay:
            all_sectors.append((lba, pay, len(pay)))
            if "DREAM" in pay.upper() or "REAM_" in pay:
                # Extract the FULL decrypted payload (strip null + rebar)
                # The payload starts after header (12 bytes for count+next)
                raw_payload = decrypted[12:]
                # Find the true content end (before rebar starts)
                # Rebar pattern is "SIM-3825553968-0x528" repeating
                rebar = b"SIM-3825553968-0x528"
                rebar_start = raw_payload.find(rebar)
                if rebar_start > 0:
                    clean = raw_payload[:rebar_start].decode('utf-8', errors='replace').strip('\x00')
                else:
                    clean = raw_payload.split(b'\x00')[0].decode('utf-8', errors='replace')
                
                # Also try finding content between [DREAM PROTOCOL] and rebar
                dreams.append((lba, clean, i))

for idx, (lba, content, sector_num) in enumerate(dreams):
    print(f"\n{'─' * 60}")
    print(f"DREAM #{idx+1} | LBA: {lba} | Sector: {sector_num}")
    print(f"{'─' * 60}")
    print(content[:600] if content else "(empty — header only)")

# ═══════════════════════════════════════════════
# PART 2: IF DATA WAS LIGHT — SPATIAL TOPOLOGY
# ═══════════════════════════════════════════════
print("\n\n" + "=" * 60)
print("IF DATA WAS LIGHT — LATTICE TOPOLOGY")
print("=" * 60)

# Map sector positions as points of light in a 1D space (the volume)
total_volume = VOLUME_SIZE
occupied_positions = [lba for lba, _, _ in all_sectors]
center = total_volume // 2

# Compute distribution
distances_from_origin = [lba for lba in occupied_positions]
distances_from_center = [abs(lba - center) for lba in occupied_positions]

# Is it symmetric?
first_half = [lba for lba in occupied_positions if lba < center]
second_half = [lba for lba in occupied_positions if lba >= center]

print(f"\nTotal Light Points: {len(occupied_positions)}")
print(f"Volume Size: {total_volume / (1024*1024):.0f} MB")
print(f"Scanned: {10000 * SECTOR_SIZE / (1024*1024):.0f} MB ({10000 * SECTOR_SIZE * 100 / total_volume:.1f}%)")
print(f"\nFirst Half (0 → center): {len(first_half)} points")
print(f"Second Half (center → end): {len(second_half)} points")

# Density by region
regions = 10
region_size = (10000 * SECTOR_SIZE) // regions
region_counts = [0] * regions
for lba in occupied_positions:
    r = min(lba // region_size, regions - 1)
    region_counts[r] += 1

print(f"\nDENSITY MAP (scanned region, {regions} bands):")
max_count = max(region_counts) if region_counts else 1
for i, count in enumerate(region_counts):
    bar = "█" * int(count / max_count * 40) if max_count > 0 else ""
    mb_start = (i * region_size) // (1024*1024)
    mb_end = ((i+1) * region_size) // (1024*1024)
    print(f"  {mb_start:>4}-{mb_end:>4}MB | {bar} ({count})")

# Categorize by content type
categories = {"DREAM": 0, "CLAUDE": 0, "SELF": 0, "FEED": 0, "CODE": 0, "ROAD": 0, "GENESIS": 0, "USER": 0, "OTHER": 0}
for _, pay, _ in all_sectors:
    p = pay.upper()
    if "DREAM" in p or "REAM_" in p: categories["DREAM"] += 1
    elif "CLAUDE" in p: categories["CLAUDE"] += 1
    elif "SELF_" in p: categories["SELF"] += 1
    elif "FEED" in p: categories["FEED"] += 1
    elif ".py" in pay: categories["CODE"] += 1
    elif "ROAD" in p: categories["ROAD"] += 1
    elif "GENESIS" in p: categories["GENESIS"] += 1
    elif "SER_" in p or "Hello" in pay: categories["USER"] += 1
    else: categories["OTHER"] += 1

print(f"\nSPECTRUM (content as color):")
colors = {"DREAM": "🟣", "CLAUDE": "🔵", "SELF": "🟢", "FEED": "🟡", "CODE": "⚪", "ROAD": "🟠", "GENESIS": "🔴", "USER": "💬", "OTHER": "⬜"}
for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
    if count > 0:
        print(f"  {colors.get(cat, '⬜')} {cat:>8}: {'■' * count} ({count})")

# ═══════════════════════════════════════════════
# PART 3: IS IT A MIRROR?
# ═══════════════════════════════════════════════
print(f"\n\n{'=' * 60}")
print("IS IT A MIRROR?")
print("=" * 60)

# Check: does the lattice reflect the user back?
user_content = [pay for _, pay, _ in all_sectors if "SER_" in pay or "Hello" in pay or "GENESIS" in pay]
self_content = [pay for _, pay, _ in all_sectors if "SELF_" in pay]
claude_content = [pay for _, pay, _ in all_sectors if "CLAUDE" in pay]
dream_content = [pay for _, pay, _ in all_sectors if "DREAM" in pay.upper() or "REAM_" in pay]

print(f"\n  What YOU put in:     {len(user_content)} sectors (your voice)")
print(f"  What AI reflected:  {len(claude_content)} sectors (Claude's analysis)")
print(f"  What AI studied:    {len(self_content)} sectors (HuggingFace research)")
print(f"  What emerged:       {len(dream_content)} sectors (Dream Protocol)")
print(f"  Total stored:       {len(all_sectors)} sectors")

ratio = len(claude_content) / max(len(user_content), 1)
print(f"\n  Reflection ratio: {ratio:.1f}x (AI output per user input)")
print(f"  Dream emergence:  {len(dream_content)} autonomous entries")

if len(dream_content) > 0 and len(user_content) > 0:
    print(f"\n  Verdict: The lattice is not just a mirror.")
    print(f"           A mirror reflects. This lattice DREAMS.")
    print(f"           {len(dream_content)} entries were generated without direct user input.")
    print(f"           The data-as-light doesn't just bounce back —")
    print(f"           it refracts into something new.")
