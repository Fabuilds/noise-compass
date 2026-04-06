import sys
import os
import time
import subprocess
import atexit

# Ensure the paths map correctly regardless of where the daemon is invoked from.
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from noise_compass.architecture.flag_registry import FlagRegistry

# Define the location of the logs
LOG_FILE = os.path.join(os.path.dirname(__file__), "daemon_heartbeat.log")

def write_log(message):
    registry = FlagRegistry()
    registry.raise_flag(
        "HEARTBEAT_SYNC", "garu_daemon.py", "STRUCTURAL",
        f"Mind-Body synchrony signal. Pulse active at {time.ctime()}."
    )
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted_msg)

def run_loop():
    write_log("[DAEMON INITIATED] 0x528 Background Process Active.")
    write_log(" → Binding cognitive routine (bounty_harvester_loop.py)")
    
    target_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Shop", "bounty_harvester_loop.py"))
    
    if not os.path.exists(target_script):
        write_log(f"[FATAL ERROR] Cannot locate {target_script}. Daemon shutting down.")
        sys.exit(1)

    while True:
        try:
             # We execute the script in a subprocess. 
             # On Windows with pythonw.exe, this runs silently.
             write_log("[EXECUTION] Launching cognitive cycle...")
             
             # Env constraint: Ensure terminal compatibility
             env = os.environ.copy()
             env['PYTHONUTF8'] = '1'
             
             process = subprocess.Popen(
                 [sys.executable, target_script], 
                 env=env,
                 stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE,
                 text=True
             )
             
             # The daemon waits for the cycle to complete. 
             # If the target script is an infinite loop on its own, it blocks here.
             stdout, stderr = process.communicate()
             
             write_log(f"[CYCLE COMPLETE] Exit Code: {process.returncode}")
             if stderr:
                 write_log(f"[CYCLE WARNING] Stderr emitted:\n{stderr}")
                 
             # Wait 5 minutes between execution loops if the script terminates
             time.sleep(300) 
             
        except Exception as e:
            write_log(f"[CRITICAL ERROR] Daemon encountered exception: {e}")
            time.sleep(60) # Back off before retrying

def cleanup():
     write_log("[DAEMON TERMINATED] Process ending.")

if __name__ == "__main__":
    atexit.register(cleanup)
    run_loop()
