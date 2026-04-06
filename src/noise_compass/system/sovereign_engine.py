"""
sovereign_engine.py — The Continuous Sovereign Engine.
Persistent orchestrator for autonomous code generation and verification.
"""

import sys
import os
import time
import json
import subprocess
import socket

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from noise_compass.system.bitnet_tools import ask_bitnet
from noise_compass.system.soi_protocol import SOIProtocol
from noise_compass.system.sandbox import Sandbox

class SovereignEngine:
    def __init__(self):
        print("--- INITIALIZING CONTINUOUS SOVEREIGN ENGINE ---")
        self.protocol = SOIProtocol()
        self.sandbox = Sandbox()
        self.workers_launched = False
        self.log_file = "e:/Antigravity/Runtime/SOVEREIGN_ENGINE_LOG.txt"
        
    def log(self, msg):
        timestamp = time.ctime()
        entry = f"[{timestamp}] {msg}\n"
        print(entry, end="")
        with open(self.log_file, "a") as f:
            f.write(entry)

    def ensure_workers(self):
        """Checks if ports 5280-5282 are active; if not, launches them."""
        ports = [5280, 5281, 5282]
        missing_ports = []
        for port in ports:
            reachable = False
            last_err = 0
            for _ in range(5): # 5 attempts
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(3)
                    last_err = s.connect_ex(('localhost', port))
                    if last_err == 0:
                        reachable = True
                        break
                time.sleep(2)
            if not reachable:
                self.log(f"[DEBUG]: Port {port} is unresponsive (connect_ex: {last_err}).")
                missing_ports.append(port)
        
            launch_script = r"E:\Antigravity\System\launch_trinity.ps1"
            if not os.path.exists(launch_script):
                self.log(f"[WARNING]: {launch_script} NOT FOUND. Cannot launch workers.")
                self.workers_launched = False
                return

            # Phase 115: IDE-Centric State Guard
            try:
                import psutil
                for p in psutil.process_iter(['cmdline']):
                    if p.info['cmdline'] and "launch_trinity.ps1" in " ".join(p.info['cmdline']):
                        self.log("[ENGINE]: Trinity launch already in progress. Waiting...")
                        return
            except:
                pass

            self.log(f"[ENGINE]: Workers {missing_ports} offline. Launching Trinity Ensemble...")
            try:
                from noise_compass.system.process_registry import register
                register(subprocess.Popen(["powershell", "-ExecutionPolicy", "Bypass", "-File", launch_script], 
                                 creationflags=subprocess.CREATE_NEW_CONSOLE))
                self.log("[ENGINE]: Launch signal sent via PowerShell.")
            except Exception as e:
                self.log(f"[ERROR]: Failed to launch workers: {e}")
            # NO RECURSION: The 60s heart beat in run_cycle() will handle next check.
        else:
            self.log("[ENGINE]: Trinity Ensemble is confirmed active.")
            self.workers_launched = True

    def get_consensus_score(self, thought):
        """Averages resonance from the Trinity Ensemble."""
        ports = [5280, 5281, 5282]
        total_score = 0.0
        count = 0
        for port in ports:
            try:
                res = ask_bitnet("RESONANCE", thought, port=port)
                if "score" in res:
                    total_score += res["score"]
                    count += 1
            except:
                continue
        return total_score / count if count > 0 else 0.0

    def identify_task(self):
        """Asks Qwen to identify the next semantic gap to fill."""
        # 0. Observe Substrate (Project State Context)
        try:
            with open(os.path.join(PROJECT_ROOT, "task.md"), "r") as f:
                task_content = f.read()
        except:
            task_content = "No task.md."
            
        sys_files = [f for f in os.listdir(os.path.join(PROJECT_ROOT, "System")) if f.endswith(".py")]
        
        context = (
            f"OBJECTIVE_SUBSTRATE:\n"
            f"Logic Files: {sys_files}\n"
            f"Mobius Core: mobius_engine.py, mobius_lens.py\n"
            f"Current Tasks: {task_content[:500]}...\n"
            f"Sandbox Tools: print, open, range, len, sum, math, random, time, json, collections, re, os (safe wrapper)"
        )
        
        prompt = (
            f"SYSTEM_CONTEXT:\n{context}\n\n"
            "STRICT ARCHITECTURAL DIRECTIVE:\n"
            "1. Inspect the 'Logic Files' listed above.\n"
            "2. Identify one REAL missing logic component or a gap in the implementation of these specific files.\n"
            "3. DO NOT hallucinate directories like 'SystemAnalysis' or '/path/to'.\n"
            "4. Propose a concrete implementation task name to Manifest that will be implemented as a NEW script in the 'System/' directory.\n"
            "5. The task should be a high-performance logic primitive or a diagnostic tool for the existing files."
        )
        
        res = ask_bitnet("DISTILL", prompt, port=5282)
        if "error" in res:
             self.log(f"[DEBUG]: identify_task error: {res['error']}")
        
        axioms = res.get("axioms", res.get("thoughts", []))
        candidate = axioms[0] if axioms else "Implement a high-performance parity checker for LBA streams."
        
        # 2. Extract Meaning (The Pull Protocol)
        self.log(f"[ENGINE]: Grounding task: '{candidate}' via Pull Protocol...")
        pull_payload = {
            "focus": candidate,
            "context": context,
            "pulls": 20 # Optimized for local speed
        }
        pull_res = ask_bitnet("PULL", pull_payload, port=5282)
        if "error" in pull_res:
             self.log(f"[DEBUG]: PULL task error: {pull_res['error']}")
        terminal_word = pull_res.get("terminal_word", "RESONANCE")
        
        self.log(f"[ENGINE]: Meaning Extracted: {terminal_word}")
        return f"TASK: {candidate} | GROUNDING: {terminal_word}"

    def synthesize_code(self, task):
        """Asks Qwen to synthesize the solution."""
        # Extract Grounding Word from the task string
        grounding = "RESONANCE"
        if "GROUNDING:" in task:
             parts = task.split("|")
             task_desc = parts[0].replace("TASK:", "").strip()
             grounding = parts[1].replace("GROUNDING:", "").strip()
        else:
             task_desc = task

        prompt = (
            f"GOAL: {task_desc}\n"
            f"MECHANISTIC GROUNDING: {grounding}\n\n"
            "STRICT ARCHITECTURAL RULES:\n"
            f"1. GUIDANCE: Use the principle of '{grounding}' to structure the logic.\n"
            "2. OUTPUT: Respond ONLY with a raw Python code block between ```python and ```.\n"
            "3. HERMETIC: Use only standard libs, numpy, or scipy. No external frameworks.\n"
            "4. VALIDATION: Include an 'if __name__ == \"__main__\":' block that tests the logic and prints '[PASS]' on success.\n"
            "5. CONTEXT: Ensure the script accurately addresses the gap identified in the target files."
        )
        res = ask_bitnet("DISTILL", prompt, port=5282)
        if "error" in res:
             self.log(f"[FAIL]: Synthesis error: {res['error']}")
             return None
             
        # Often axioms returns the list
        code_axioms = res.get("axioms", [])
        if not code_axioms:
             self.log(f"[FAIL]: Synthesis returned no axioms. Content: {str(res)[:100]}")
             return None
        for axiom in code_axioms:
            if "```python" in axiom:
                import re
                match = re.search(r"```python\n(.*?)```", axiom, re.DOTALL)
                if match:
                    return match.group(1).strip()
        return None

    def run_cycle(self):
        if not self.protocol.is_active():
            self.log("[ENGINE]: SOI Protocol is in SUPERVISED mode. Cycle skipped.")
            return

        self.log("\n--- NEW SOVEREIGN CYCLE START ---")
        
        # 1. Identify Task
        task = self.identify_task()
        self.log(f"[TASK]: {task}")
        
        # 2. Synthesize
        code = self.synthesize_code(task)
        if not code:
            self.log("[FAIL]: Code synthesis failed.")
            return
            
        # 3. Verify in Sandbox
        self.log("[VERIFY]: Executing in Sandbox...")
        out, err = self.sandbox.execute(code)
        
        if err:
            self.log(f"[FAIL]: Sandbox Verification Error: {err[:1000]}")
            return
            
        # 4. Resonance Check
        resonance = self.get_consensus_score(f"CODE_LOGIC: {code[:200]}")
        self.log(f"[RESONANCE]: {resonance:.4f}")
        
        # 5. Commitment
        if self.protocol.evaluate_resonance(resonance):
            self.log("[COMMIT]: Code meets FLAWLESS standard. Archiving to System/Autonomous_Output.")
            filename = f"flawless_{int(time.time())}.py"
            output_dir = "e:/Antigravity/Runtime/Autonomous_Output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
                f.write(code)
            self.protocol.log_ingest(filename)
        else:
            self.log("[STASIS]: Resonance too low for commitment.")

    def start(self):
        self.ensure_workers()
        self.log("[ENGINE]: Continuous Engine Active.")
        try:
            while True:
                self.run_cycle()
                time.sleep(60) # 1 minute heartbeat
        except KeyboardInterrupt:
            self.log("[ENGINE]: Shutdown signaled.")

if __name__ == "__main__":
    engine = SovereignEngine()
    # For testing, we force autonomous mode
    engine.protocol.enter_overnight_mode(24) 
    engine.start()
