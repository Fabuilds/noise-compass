import psutil
import os
import time

def nuclear_purge():
    my_pid = os.getpid()
    print(f"[PURGE] My PID: {my_pid}")
    
    # Target all python processes
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if p.pid == my_pid:
                continue
            
            name = (p.info['name'] or "").lower()
            cmdline = " ".join(p.info['cmdline'] if p.info['cmdline'] else [])
            
            if 'python' in name or 'ouroboros' in cmdline or 'sovereign' in cmdline:
                print(f"[PURGE] Killing PID {p.pid}: {cmdline[:100]}")
                p.kill()
        except:
            pass
            
    # Wait for OS to catch up
    time.sleep(2)
    
    # Verify
    leftovers = []
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if p.pid == my_pid: continue
            name = (p.info['name'] or "").lower()
            if 'python' in name:
                leftovers.append(p.pid)
        except: pass
        
    if not leftovers:
        print("[PURGE] Substrate is now VACUUM state. Clean.")
    else:
        print(f"[PURGE] WARNING: {len(leftovers)} processes remaining.")

if __name__ == "__main__":
    nuclear_purge()
