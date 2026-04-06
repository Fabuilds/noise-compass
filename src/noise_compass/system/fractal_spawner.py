import subprocess
import threading
import time
import os
import sys

class FractalSpawner:
    # Class-level constraints
    MAX_DEPTH = 1 # Only parent can spawn children
    MAX_ACTIVE_CHILDREN = 2
    CHILD_TTL = 60 # 60 seconds strict Time-To-Live
    
    _active_children = []
    _lock = threading.Lock()

    @classmethod
    def spawn_child(cls, node_a, node_b, node_c):
        """Spawns a child Ouroboros loop strictly constrained by Phase 15 rules."""
        with cls._lock:
            # Clean up dead children from tracking list
            cls._active_children = [p for p in cls._active_children if p["process"].poll() is None]
            
            if len(cls._active_children) >= cls.MAX_ACTIVE_CHILDREN:
                print(f"[SPAWNER] Max active children ({cls.MAX_ACTIVE_CHILDREN}) reached. Skipping spawn.")
                return False
        
        target_string = f"{node_a},{node_b},{node_c}"
        print(f"[SPAWNER] Initiating Fractal Child for: {target_string}")
        
        # Determine paths
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ouroboros_script = os.path.join(script_dir, "ouroboros.py")
        
        # Prepare the child command
        cmd = [
            sys.executable,
            ouroboros_script,
            "--child",
            "--target",
            target_string
        ]
        
        # Spawn the subprocess (run in background, don't wait)
        try:
            # We redirect stdout to devnull to avoid cluttering the parent's logs wildly. 
            # Subprocess will still write to ouroboros_log.txt natively.
            from noise_compass.system.process_registry import register
            p = register(subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
            
            child_record = {
                "process": p,
                "spawn_time": time.time(),
                "target": target_string
            }
            
            with cls._lock:
                cls._active_children.append(child_record)
                
            # Start a reaper thread to enforce the TTL
            threading.Thread(target=cls._reaper, args=(child_record,), daemon=True).start()
            return True
            
        except Exception as e:
            print(f"[SPAWNER] Failed to spawn child: {e}")
            return False

    @classmethod
    def _reaper(cls, child_record):
        """Enforces the strict Death Clock constraint."""
        p = child_record["process"]
        spawn_time = child_record["spawn_time"]
        
        # Wait until TTL expires or process dies naturally
        while time.time() - spawn_time < cls.CHILD_TTL:
            if p.poll() is not None:
                print(f"[SPAWNER] Child {child_record['target']} collapsed naturally. (PID: {p.pid})")
                return
            time.sleep(1)
            
        # TTL expired and it's still running
        if p.poll() is None:
            print(f"[SPAWNER] TTL Exceeded ({cls.CHILD_TTL}s) for {child_record['target']}. Initiating termination (PID: {p.pid}).")
            try:
                p.terminate()
                p.wait(timeout=3)
            except subprocess.TimeoutExpired:
                print(f"[SPAWNER] Hard kill required for PID: {p.pid}")
                p.kill()
            except Exception as e:
                print(f"[SPAWNER] Error killing child PID {p.pid}: {e}")
