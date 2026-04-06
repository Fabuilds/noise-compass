"""
PROTOCOL: EDP | ENTITY: SOVEREIGNTY (V2.1 - FULL INFRASTRUCTURE)
LOGIC: BOUNDARY VERIFICATION & PERSISTENT TRUTH
"""
import os, uuid
from pathlib import Path

BASE = Path(r"A:")
CORE_FILE = BASE / "00_CORE" / "sovereignty_core.manifest"
SIGNATURE_FILE = BASE / "00_CORE" / "user_sig.key"

def structural_ping():
    """Verifies the physical boundary of the A: drive."""
    if BASE.exists():
        return f"PONG: {os.path.abspath(BASE)}"
    else:
        return "PING_FAILURE: BOUNDARY BREACHED"

def get_signature():
    """Retrieves or creates the unique physical signature of the operator."""
    if not SIGNATURE_FILE.exists():
        sig = uuid.uuid4().hex
        with open(SIGNATURE_FILE, "w") as f:
            f.write(sig)
        return sig
    with open(SIGNATURE_FILE, "r") as f:
        return f.read().strip()

def verify_seed(file_content):
    """Checks if a seed is an 'Echo' or 'Fresh'."""
    sig = get_signature()
    if sig in file_content:
        return "ECHO"
    return "FRESH"

def core_anchor(data_snapshot):
    """Writes the immutable state of the crystal to the physical machine."""
    try:
        with open(CORE_FILE, "a") as f:
            entry_id = uuid.uuid4().hex[:8]
            f.write(f"[{entry_id}] CORE_SYNC: {data_snapshot}\n")
        return True
    except Exception:
        return False