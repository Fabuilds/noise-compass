import subprocess
import time
import os
import signal
import sys
import psutil

class TripleChainManager:
    """Orchestrates three parallel ResonantOuroboros instances for high availability."""
    def __init__(self):
        self.configs = [
            {"mode": "main",   "port": 5285},
            {"mode": "anchor", "port": 5286},
            {"mode": "shadow", "port": 5287}
        ]
        self.processes = {} # mode -> subprocess.Popen
        self.script_path = "E:/Antigravity/Runtime/ouroboros_resonant.py"

    def start_instance(self, mode, port):
        print(f"[MANAGER] Launching '{mode}' chain on port {port}...")
        cmd = [sys.executable, self.script_path, "--mode", mode, "--port", str(port)]
        log_file = open(f"E:/Antigravity/Runtime/ouroboros_{mode}_log.txt", "a")
        
        # Phase 115: Register for managed lifecycle
        from noise_compass.system.process_registry import register
        proc = register(subprocess.Popen(cmd, stdout=log_file, stderr=log_file, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0))
        self.processes[mode] = {"proc": proc, "port": port, "log": log_file}

    def get_free_ram(self):
        """Returns free physical memory in GB using psutil."""
        try:
            return psutil.virtual_memory().available / (1024 ** 3)
        except Exception as e:
            print(f"[MANAGER] [ERROR] Failed to check RAM: {e}")
            return 32.0 # Assume plenty if check fails

    def monitor(self):
        print("--- TRIPLE-CHAIN MANAGER: ACTIVE (SOMATIC SAFEGUARDS ENABLED) ---")
        try:
            while True:
                free_gb = self.get_free_ram()
                
                # Scarcity Thresholds (GB)
                SCARCITY = 2.0
                CRITICAL = 0.5
                RECOVERY = 4.0

                if free_gb < CRITICAL:
                    print(f"[MANAGER] [CRITICAL] RAM Scarcity ({free_gb:.2f}GB): EMERGENCY HIBERNATION.")
                    self.stop_all()
                    while self.get_free_ram() < RECOVERY:
                        time.sleep(30)
                    print("[MANAGER] [INFO] RAM Recovered. Resuming Main Triad.")

                elif free_gb < SCARCITY:
                    # Shut down non-essential chains (Shadow, Anchor)
                    for mode in ["shadow", "anchor"]:
                        if mode in self.processes:
                            print(f"[MANAGER] [SCARCITY] RAM low ({free_gb:.2f}GB): Load-Shedding '{mode}'.")
                            self.stop_instance(mode)
                
                else:
                    # Standard Monitoring & Recovery
                    for mode, info in self.processes.items():
                        proc = info["proc"]
                        if proc.poll() is not None:
                            print(f"[MANAGER] [WARNING] Chain '{mode}' CRASHED/STOPPED. Restarting...")
                            info["log"].close()
                            self.start_instance(mode, info["port"])
                    
                    # Auto-scale up if resources are plenty
                    if free_gb > RECOVERY:
                        for cfg in self.configs:
                            if cfg["mode"] not in self.processes:
                                print(f"[MANAGER] [RECOVERY] RAM Plenty ({free_gb:.2f}GB): Restoring Triad '{cfg['mode']}'.")
                                self.start_instance(cfg["mode"], cfg["port"])

                time.sleep(15)
        except KeyboardInterrupt:
            self.stop_all()

    def stop_instance(self, mode):
        if mode in self.processes:
            info = self.processes[mode]
            info["proc"].terminate()
            info["log"].close()
            del self.processes[mode]

    def stop_all(self):
        print("[MANAGER] Shutting down all chains...")
        for mode, info in self.processes.items():
            print(f"  -> Stopping {mode}...")
            # On Windows, we need specialized taskkill or similar if shell=True is tricky
            # but Popen with CREATE_NEW_PROCESS_GROUP handles it ok if Sent Ctrl_Break
            info["proc"].terminate()
            info["log"].close()
        print("[MANAGER] All chains offline.")

if __name__ == "__main__":
    manager = TripleChainManager()
    for cfg in manager.configs:
        manager.start_instance(cfg["mode"], cfg["port"])
    manager.monitor()
