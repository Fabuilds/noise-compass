import psutil
import os

def surgical_purge():
    current_pid = os.getpid()
    print(f"[PURGE] Investigating process tree from PID {current_pid}...")
    
    # We want to find the "Antigravity" cluster.
    # From the user's screenshot, it seems many processes are grouped under one heading.
    
    target_names = ['powershell.exe', 'conhost.exe', 'cmd.exe']
    purged_count = 0
    
    # Identify our active worker PIDs to PROTECT them
    protected_pids = set([current_pid])
    
    # Try to find the TripleChainManager and its known workers
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = " ".join(proc.info['cmdline']) if proc.info['cmdline'] else ""
            if "triple_chain_manager.py" in cmdline or "ouroboros_resonant.py" in cmdline:
                protected_pids.add(proc.info['pid'])
        except:
            continue

    print(f"[PURGE] Protected PIDs: {protected_pids}")

    # Now, find all other powershell/conhost that are "Ghostly"
    # Ghostly = No main window, and NOT in our protected list.
    for proc in psutil.process_iter(['pid', 'name', 'ppid', 'status']):
        try:
            if proc.info['name'] in target_names:
                if proc.info['pid'] not in protected_pids:
                    # Additional check: If it's a child of a process that is also a ghost, or orphaned
                    print(f"[PURGE] Terminating ghost process: {proc.info['name']} (PID: {proc.info['pid']})")
                    proc.terminate()
                    purged_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    print(f"[PURGE] Cleanup complete. Removed {purged_count} orphaned processes.")

if __name__ == "__main__":
    surgical_purge()
