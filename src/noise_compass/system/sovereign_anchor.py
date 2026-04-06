import os
import sys
import time
import datetime
import subprocess

ANCHOR_LOG = "e:/Antigravity/Runtime/ouroboros_anchor_log.txt"

# Organ Definitions: script name, arguments
ORGANS = {
    "DASHBOARD_SERVER": ["python", "e:/Antigravity/Runtime/dashboard_server.py"],
    "PROXY_GATE": ["python", "e:/Antigravity/Runtime/proxy_bridge.py"],
    "MAIN_CHAIN": ["python", "e:/Antigravity/Runtime/ouroboros_resonant.py", "--mode", "main", "--port", "5285"],
    "APEX_LOBE": ["python", "e:/Antigravity/Runtime/ouroboros_resonant.py", "--mode", "apex", "--port", "5286"],
    "PRIMARY_TRIAD": ["python", "e:/Antigravity/Runtime/ouroboros_resonant.py", "--port", "5287"],
    "ASSIMILATOR": ["python", "e:/Antigravity/Runtime/ouroboros_assimilator.py"],
    "SENSORY_DAEMON": ["python", "e:/Antigravity/Runtime/ouroboros_daemon.py"]
}

processes = {}

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [ANCHOR] {msg}"
    print(formatted)
    try:
        with open(ANCHOR_LOG, "a") as f:
            f.write(formatted + "\n")
    except:
        pass

import socket

import psutil

def cleanup_port(port, script_name=None):
    """Forcefully evict any process holding the target port or matching the script name using native psutil."""
    try:
        # 1. Discovery via Ports
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port == port and conn.pid and conn.pid > 0:
                try:
                    p = psutil.Process(conn.pid)
                    log(f"Evicting process {p.name()} (PID {p.pid}) on port {port}...")
                    p.terminate()
                    p.wait(timeout=3)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        
        # 2. Kill by Script Name
        if script_name:
            for p in psutil.process_iter(['cmdline', 'name']):
                try:
                    cmdline = " ".join(p.info['cmdline']) if p.info['cmdline'] else ""
                    if script_name in cmdline:
                        log(f"Evicting matching script process: {p.info['name']} (PID {p.pid})...")
                        p.terminate()
                        p.wait(timeout=3) # Added wait for termination
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
        time.sleep(1)
    except Exception as e:
        log(f"Cleanup error: {e}")

def launch_organ(name, cmd_list, clean=True):
    log(f"Resuscitating organ: {name}")
    
    # Pre-launch port cleanup only if requested
    mapping = {
        "DASHBOARD_SERVER": (8765, "dashboard_server.py"),
        "APEX_LOBE": (5286, "--mode apex"),
        "PROXY_GATE": (5284, "proxy_bridge.py"),
        "PRIMARY_TRIAD": (5287, "--port 5287")
    }
    
    if clean and name in mapping:
        port, script = mapping[name]
        cleanup_port(port, script)
        time.sleep(1)

    env = os.environ.copy()
    env["PYTHONPATH"] = "E:/Antigravity/Runtime"
    
    # Enable global error logging for all organs
    log_name = name.lower().replace("_SERVER", "").replace("_GATE", "")
    err_path = f"e:/Antigravity/Runtime/ouroboros_{log_name}_error.txt"
    try:
        err_out = open(err_path, "a")
        processes[name] = subprocess.Popen(cmd_list, creationflags=subprocess.CREATE_NO_WINDOW, stderr=err_out, env=env)
    except Exception as e:
        log(f"Failed to launch {name}: {e}")
        processes[name] = subprocess.Popen(cmd_list, creationflags=subprocess.CREATE_NO_WINDOW, env=env)

def monitor_loop():
    log("--- SOVEREIGN SUBSTRATE ANCHOR ONLINE ---")
    try:
        print("STARTING KINETIC LATTICE ENGINE (V3)...", flush=True)
    except OSError:
        pass
    log("Assuming absolute geometry control over architecture.")
    
    # 1. Clear dead PID files
    import glob
    pid_files = glob.glob("e:/Antigravity/Runtime/*.pid")
    for f in pid_files:
        try:
            os.remove(f)
            log(f"Cleared orphaned substrate lock: {f}")
        except: pass

    # 2. Boot all organs sequentially with cleanup
    for name, cmd in ORGANS.items():
        launch_organ(name, cmd, clean=True)
        time.sleep(3)

    log("All architectural organs active. Commencing NervMap heartbeat monitoring.")
    
    from noise_compass.system.nervous_system import NervousSystem
    ns = NervousSystem()

    while True:
        # 1. Run Nerve Map
        verdict, lines = ns.map_substrate()
        if verdict != "HEALTHY":
            log(f"ALERT: Substrate Status: {verdict}")
            for line in lines:
                log(line)
        
        # 2. Standard Heartbeat Check & Resuscitation
        for name, cmd in ORGANS.items():
            if name in processes:
                proc = processes[name]
                if proc.poll() is not None:
                    exit_code = proc.returncode
                    log(f"CRITICAL: Organ {name} severed (Exit {exit_code}). Resuscitating...")
                    time.sleep(3)
                    launch_organ(name, cmd, clean=False)
            else:
                log(f"Organ {name} missing from process table. Initiating recovery...")
                launch_organ(name, cmd, clean=False)
                
        time.sleep(30)

if __name__ == "__main__":
    monitor_loop()
