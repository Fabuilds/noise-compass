import subprocess
import time
import os
import signal
import sys

# Path alignment for Antigravity package
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

# Configuration
PYTHON_EXE = sys.executable
SYSTEM_DIR = os.path.dirname(os.path.abspath(__file__))
WORKERS = [
    ["bitnet_worker.py", "--port", "5280"],
    ["bitnet_worker.py", "--port", "5281", "--checkpoint", "E:/Antigravity/Runtime/crochet_checkpoint.pt"],
    ["qwen_worker.py", "--port", "5282"]
]
INFRASTRUCTURE = [
    ["proxy_bridge.py"],
    ["dashboard.py"],  # Port 5285
    ["heartbeat.py"]
]
CORE = ["ouroboros.py"]

class SovereignOrchestrator:
    def __init__(self):
        self.processes = []
        self.running = True

    def start_process(self, script_args, label=None, category="CORE"):
        cmd = [PYTHON_EXE] + script_args
        label = label or " ".join(script_args)
        
        # Ensure sub-processes have the correct PYTHONPATH to find noise_compass
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        
        print(f"[ORCHESTRATOR]: Starting {label}...")
        from noise_compass.system.process_registry import register
        p = register(subprocess.Popen(cmd, cwd=SYSTEM_DIR, env=env), label=label, category=category)
        self.processes.append(p)
        return p

    def stop_all(self):
        print("\n[ORCHESTRATOR]: Shutting down Sovereign Chorus...")
        self.running = False
        from noise_compass.system.process_registry import cleanup_all
        cleanup_all()
        
        # Windows-specific cleanup for any orphaned pids
        subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/T"], capture_output=True)
        print("[ORCHESTRATOR]: Shutdown complete.")

    def run(self):
        try:
            # 1. Start Workers (Models)
            for worker in WORKERS:
                label = f"Worker ({worker[2]})" if "--port" in worker else f"Worker {worker[0]}"
                self.start_process(worker, label=label, category="WORKER")
                time.sleep(2)
            
            # 2. Start Infrastructure (Proxy & Dashboard)
            for infra in INFRASTRUCTURE:
                label = f"Infra: {infra[0].split('.')[0].capitalize()}"
                self.start_process(infra, label=label, category="INFRA")
                time.sleep(2)
            
            # 3. Start Core (Reasoning)
            self.start_process(CORE, label="Core: Ouroboros", category="CORE")
            
            print("[ORCHESTRATOR]: Chorus active. Monitoring (Hazmat 0x54 + Visual 0x528)...")
            while self.running:
                time.sleep(10)
                # Check for dead processes
                active_procs = []
                for p in self.processes:
                    if p.poll() is not None:
                        print(f"[ORCHESTRATOR WARNING]: Process {p.pid} died. System may be unstable.")
                    else:
                        active_procs.append(p)
                self.processes = active_procs
                
                if not self.processes:
                    print("[ORCHESTRATOR]: No active processes remains. Exiting.")
                    break
        
        except KeyboardInterrupt:
            self.stop_all()
        except Exception as e:
            print(f"[ORCHESTRATOR ERROR]: {e}")
            self.stop_all()

if __name__ == "__main__":
    orch = SovereignOrchestrator()
    orch.run()
