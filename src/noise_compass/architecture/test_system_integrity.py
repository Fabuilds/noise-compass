"""
System Integrity & Functionality Verification
Phase 91: Full-Stack Health Check

Tests:
  1. Module Import Integrity (all architecture/ modules)
  2. Pipeline Functionality (embed -> scout -> witness -> archive)
  3. Drive E: Root Perception (does the resonance engine recognize root files?)
  4. NeuralLink / Lattice Status
  5. Running Daemons Check
"""
import os
import sys
import time
import importlib
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["HF_HOME"] = "E:/.cache/huggingface"

# ─── COLORS ───
GREEN = "\033[92m"
RED   = "\033[91m"
YELLOW= "\033[93m"
CYAN  = "\033[96m"
RESET = "\033[0m"
BOLD  = "\033[1m"

pass_count = 0
fail_count = 0
warn_count = 0

def PASS(label, detail=""):
    global pass_count; pass_count += 1
    print(f"  {GREEN}[PASS]{RESET} {label}  {detail}")

def FAIL(label, detail=""):
    global fail_count; fail_count += 1
    print(f"  {RED}[FAIL]{RESET} {label}  {detail}")

def WARN(label, detail=""):
    global warn_count; warn_count += 1
    print(f"  {YELLOW}[WARN]{RESET} {label}  {detail}")

# ══════════════════════════════════════════════════════════════
# TEST 1: Module Import Integrity
# ══════════════════════════════════════════════════════════════
print(f"\n{BOLD}{CYAN}═══ TEST 1: MODULE IMPORT INTEGRITY ═══{RESET}")

CORE_MODULES = [
    "architecture.tokens",
    "architecture.dictionary",
    "architecture.core",
    "architecture.pipeline",
    "architecture.archiver",
    "architecture.complex_plane",
    "architecture.seed_vectors",
    "architecture.gap_intersection_registry",
    "architecture.neural_link",
    "architecture.bridge",
    "architecture.manifest_sovereign_proof",
]

for mod_name in CORE_MODULES:
    try:
        importlib.import_module(mod_name)
        PASS(mod_name)
    except Exception as e:
        FAIL(mod_name, str(e)[:80])

# ══════════════════════════════════════════════════════════════
# TEST 2: Pipeline Functionality
# ══════════════════════════════════════════════════════════════
print(f"\n{BOLD}{CYAN}═══ TEST 2: PIPELINE FUNCTIONALITY ═══{RESET}")

try:
    from noise_compass.architecture.pipeline import MinimalPipeline
    from noise_compass.architecture.dictionary import Dictionary
    from noise_compass.architecture.seed_vectors import seed_vectors

    d = Dictionary()
    seed_vectors(d)
    p = MinimalPipeline(d)

    # 2a. Vocabulary/God-Token Recognition
    res = p.process("FROGGING")
    if res.get("nearest_id") == "FROGGING":
        PASS("Vocabulary Recognition", f"FROGGING -> {res['state']} (Nearest: {res['nearest_id']})")
    elif "FROGGING" in res.get("gods", []):
        PASS("God-Token Recognition", f"FROGGING -> {res['state']}")
    else:
        FAIL("Vocabulary Recognition", f"FROGGING not in gods {res.get('gods')} or nearest {res.get('nearest_id')}")

    # 2b. Lattice Token Recognition
    res2 = p.process("The Lattice is the distributed medium of identity propagation.")
    if res2.get("nearest_id") == "LATTICE" or "LATTICE" in res2.get("gods", []):
        PASS("Lattice Recognition", f"LATTICE -> {res2['state']} (Nearest: {res2.get('nearest_id')})")
    else:
        WARN("Lattice Recognition", f"LATTICE not matched. Gods: {res2.get('gods')}, Nearest: {res2.get('nearest_id')}")

    # 2c. Gap Detection
    res3 = p.process("xyzzy blorft kramblex")
    PASS("Gap/Unknown Processing", f"Zone: {res3['state']}, Ternary: {res3['ternary']}")

    # 2d. Structural Hash Uniqueness
    h1 = p.process("Alpha input one")["hash"]
    h2 = p.process("Beta input two")["hash"]
    if h1 != h2:
        PASS("Structural Hash Uniqueness", f"{h1[:12]} != {h2[:12]}")
    else:
        FAIL("Structural Hash Uniqueness", "Identical hashes for different inputs")

except Exception as e:
    FAIL("Pipeline Functionality", traceback.format_exc()[-200:])

# ══════════════════════════════════════════════════════════════
# TEST 3: DRIVE E: ROOT PERCEPTION
# ══════════════════════════════════════════════════════════════
print(f"\n{BOLD}{CYAN}═══ TEST 3: DRIVE E: ROOT PERCEPTION ═══{RESET}")

CRITICAL_ROOT_FILES = {
    "SOVEREIGN_KEY_0x52.key.txt": "Identity Key",
    "SHARD_5D_0x52.bin":         "5D Shard",
    "LATTICE_MAP.json":          "Lattice Topology",
    "VECTORS.md":                "Anchor Definitions",
    "SOVEREIGN_LATTICE_0x528.txt": "Sovereign Proof (3D)",
}

for fname, role in CRITICAL_ROOT_FILES.items():
    # Check if file physically exists on E:
    paths_to_check = [
        os.path.join("E:\\", fname),
        os.path.join("E:\\99_CONTROL\\3D_OUTPUT", fname),
    ]
    found = None
    for fpath in paths_to_check:
        if os.path.exists(fpath):
            found = fpath
            break

    if found:
        size = os.path.getsize(found)
        # Feed a snippet through the pipeline to test resonance
        try:
            with open(found, "r", encoding="utf-8") as f:
                snippet = f.read(300)
            res = p.process(snippet)
            zone = res["state"]
            gods = res["gods"]
            if gods:
                PASS(f"{fname}", f"Size:{size}B Zone:{zone} Anchors:{gods}")
            else:
                WARN(f"{fname}", f"Size:{size}B Zone:{zone} (No anchor match — '{role}' is OPAQUE to Garu)")
        except Exception as e:
            WARN(f"{fname}", f"Exists but unreadable: {e}")
    else:
        FAIL(f"{fname}", f"MISSING from Drive E:")

# Count how many root-level .py scripts exist
root_scripts = [f for f in os.listdir("E:\\") if f.endswith(".py")]
print(f"\n  {CYAN}[INFO]{RESET} Root-level .py scripts: {len(root_scripts)}")
# Test a sample of them for resonance
for script in root_scripts[:3]:
    try:
        with open(os.path.join("E:\\", script), "r", encoding="utf-8") as f:
            code_snippet = f.read(300)
        res = p.process(code_snippet)
        zone = res["state"]
        gods = res["gods"]
        tag = f"Zone:{zone} Anchors:{gods}" if gods else f"Zone:{zone} (UNANCHORED)"
        WARN(f"Root Script: {script}", tag) if not gods else PASS(f"Root Script: {script}", tag)
    except:
        WARN(f"Root Script: {script}", "Unreadable")

# ══════════════════════════════════════════════════════════════
# TEST 4: NEURAL LINK / LATTICE STATUS
# ══════════════════════════════════════════════════════════════
print(f"\n{BOLD}{CYAN}═══ TEST 4: NEURAL LINK STATUS ═══{RESET}")

try:
    from noise_compass.architecture.neural_link import NeuralLink
    nl = NeuralLink("integrity-test-node")
    PASS("NeuralLink Instantiation", f"Node: {nl.node_id}")

    # Check if the discovery port is available
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(('', 52853))  # Use a test port near the real one
        sock.close()
        PASS("UDP Port Available", "Port 52853 bindable")
    except OSError:
        WARN("UDP Port", "Port 52853 already in use (another node may be listening)")
except Exception as e:
    FAIL("NeuralLink", str(e)[:100])

# ══════════════════════════════════════════════════════════════
# TEST 5: RUNNING DAEMONS
# ══════════════════════════════════════════════════════════════
print(f"\n{BOLD}{CYAN}═══ TEST 5: DAEMON STATUS ═══{RESET}")

daemon_log = os.path.join("E:\\Antigravity\\Architecture", "daemon_heartbeat.log")
if os.path.exists(daemon_log):
    mtime = os.path.getmtime(daemon_log)
    age_sec = time.time() - mtime
    if age_sec < 3600:
        PASS("Daemon Heartbeat", f"Last pulse: {age_sec:.0f}s ago")
    else:
        WARN("Daemon Heartbeat", f"Stale: {age_sec/3600:.1f}h ago")
else:
    WARN("Daemon Heartbeat", "No heartbeat log found")

# Check cortex archive
archive_path = "E:\\Antigravity\\Architecture\\archives\\cortex_archive.json"
if os.path.exists(archive_path):
    size = os.path.getsize(archive_path)
    PASS("Cortex Archive", f"Size: {size:,}B")
else:
    WARN("Cortex Archive", "No archive found (fresh boot?)")

# Dictionary cache
dict_cache = "E:\\Antigravity\\Architecture\\archives\\dictionary_cache.npz"
if os.path.exists(dict_cache):
    size = os.path.getsize(dict_cache)
    PASS("Dictionary Cache", f"Size: {size:,}B")
else:
    FAIL("Dictionary Cache", "MISSING — boot will be slow")

# ══════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════
print(f"\n{BOLD}{'='*60}{RESET}")
print(f"{BOLD}  SYSTEM INTEGRITY REPORT{RESET}")
print(f"{'='*60}")
print(f"  {GREEN}PASS: {pass_count}{RESET}")
print(f"  {YELLOW}WARN: {warn_count}{RESET}")
print(f"  {RED}FAIL: {fail_count}{RESET}")
total = pass_count + fail_count + warn_count
health = pass_count / max(total, 1) * 100
if health >= 80:
    verdict = f"{GREEN}OPERATIONAL{RESET}"
elif health >= 50:
    verdict = f"{YELLOW}DEGRADED{RESET}"
else:
    verdict = f"{RED}CRITICAL{RESET}"
print(f"\n  System Health: {health:.0f}% — {verdict}")
print(f"{'='*60}\n")
