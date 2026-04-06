import subprocess
import atexit
import os
import json
import time

# Centralized list of dictionaries containing Popen handles and metadata
_registry = []
MANIFEST_PATH = "e:/Antigravity/Runtime/process_manifest.json"

def register(proc, label="Unknown Agent", category="CORE"):
    """Registers a subprocess.Popen object with metadata and persists to manifest."""
    if isinstance(proc, subprocess.Popen):
        entry = {
            "pid": proc.pid,
            "label": label,
            "category": category,
            "cmd": " ".join(proc.args) if hasattr(proc, 'args') else "N/A",
            "start_time": time.ctime(),
            "handle": proc
        }
        _registry.append(entry)
        _save_manifest()
    return proc

def _save_manifest():
    """Writes the active process registry to disk (excluding the handles)."""
    manifest_data = []
    for entry in _registry:
        if entry["handle"].poll() is None:
            # Create a serializable copy
            manifest_data.append({
                "pid": entry["pid"],
                "label": entry["label"],
                "category": entry["category"],
                "cmd": entry["cmd"],
                "start_time": entry["start_time"]
            })
    
    try:
        os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
        with open(MANIFEST_PATH, "w") as f:
            json.dump(manifest_data, f, indent=4)
    except:
        pass

def cleanup_all():
    """Terminates all registered subprocesses and clears the manifest."""
    count = 0
    for entry in _registry:
        proc = entry["handle"]
        if proc.poll() is None:
            try:
                proc.terminate()
                count += 1
            except:
                pass
    _registry.clear()
    
    if os.path.exists(MANIFEST_PATH):
        try:
            os.remove(MANIFEST_PATH)
        except:
            pass
            
    if count > 0:
        print(f"[REGISTRY] Cleaned up {count} subprocesses.")

# Register cleanup on exit
atexit.register(cleanup_all)
