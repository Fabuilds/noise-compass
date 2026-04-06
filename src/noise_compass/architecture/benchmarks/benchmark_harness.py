"""
benchmark_harness.py — Antigravity Polyglot Benchmark Runner (Sovereign Native).
Automated batch execution of Exercism exercises across Python and Rust.
"""

import sys
import os
import time
import subprocess
import numpy as np
import json

# Set fixed environment paths for sovereign resolution
sys.path.insert(0, 'E:/Antigravity/System')
sys.path.insert(0, 'E:/Antigravity')
# print(f"DEBUG: sys.path={sys.path}")

from System.interference_engine import InterferenceEngine
from System.soundness import SoundnessMonitor
from System.h5_manager import H5Manager
from System.qwen_bridge import QwenBridge # Sovereign Solver
import re

class PolyglotRunner:
    def __init__(self, master_suite_path="E:/Antigravity/Architecture/benchmarks/master_suite"):
        self.master_suite = master_suite_path
        self.engine = InterferenceEngine(suppress_preload=True)
        self.monitor = SoundnessMonitor()
        self.bridge = QwenBridge(model_id="Qwen/Qwen2.5-0.5B-Instruct") # Fast benchmark solver
        self.results = []
        self.manager = H5Manager()
        self.docker_script = "E:/Antigravity/Architecture/benchmarks/docker_run.ps1"

    def run_track(self, track="python", limit=None):
        """Iterates through all exercises in a language track."""
        track_path = os.path.join(self.master_suite, track, "exercises", "practice")
        if not os.path.exists(track_path):
            print(f"[RUNNER] Track path not found: {track_path}")
            return

        exercises = [d for d in os.listdir(track_path) if os.path.isdir(os.path.join(track_path, d))]
        if limit:
            exercises = exercises[:limit]

        print(f"\n[BENCHMARK] Starting Full Run for Track: {track.upper()} ({len(exercises)} exercises)")
        
        for exercise in exercises:
            ex_path = os.path.join(track_path, exercise)
            self.evaluate_exercise(track, exercise, ex_path)

    def evaluate_exercise(self, track, name, path):
        """Processes a single exercise: Solve (Pass-1) -> Repair (Pass-2)."""
        print(f"\n--- {name.upper()} ({track}) ---")
        
        # 0. Load Instructions
        instructions = ""
        doc_path = os.path.join(path, ".docs", "instructions.md")
        if os.path.exists(doc_path):
            with open(doc_path, 'r', encoding='utf-8') as f:
                instructions = f.read()

        # 1. Identify Target Files
        target_file = ""
        test_cmd = ""
        if track == "python":
            target_file = os.path.join(path, f"{name.replace('-','_')}.py")
            test_cmd = f"python3 {name.replace('-','_')}_test.py"
        elif track == "rust":
            target_file = os.path.join(path, "src", "lib.rs")
            test_cmd = "cargo test"
            
        # 2. Attempt 1: Solve
        print("  [PASS-1] Generating solution...")
        code_1 = self.solve(track, name, instructions)
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(code_1)
        
        passed_1, error_1 = self.run_docker_test(path, test_cmd)
        
        # 3. Attempt 2: Repair (if needed)
        passed_2 = False
        if not passed_1:
            print("  [PASS-2] Repairing based on test error...")
            code_2 = self.solve(track, name, instructions, error=error_1, last_code=code_1)
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(code_2)
            passed_2, _ = self.run_docker_test(path, test_cmd)
        else:
            passed_2 = True # Carried over

        # 4. Final Algebraic Soundness Check
        with open(target_file, 'r', encoding='utf-8') as f:
            final_code = f.read()
        soundness = self.calculate_soundness(final_code)
        
        res = {
            "exercise": name,
            "track": track,
            "soundness": soundness,
            "passed_1": passed_1,
            "passed_2": passed_2,
            "error_1": error_1 if not passed_1 else None,
            "timestamp": time.time()
        }
        self.results.append(res)
        print(f"  -> Soundness: {soundness:.4f} | Pass-1: {passed_1} | Pass-2: {passed_2}")

    def solve(self, track, name, instructions, error=None, last_code=None):
        """Uses Qwen to generate or repair the solution."""
        context = f"Language: {track}\nExercise: {name}\n\nInstructions:\n{instructions}"
        if error:
            prompt = (
                f"Your previous attempt failed the following tests:\n{error}\n\n"
                f"LAST CODE:\n```python\n{last_code}\n```\n\n"
                "Please repair the code to pass all tests. Output ONLY the code block."
            )
        else:
            prompt = (
                "Implement the solution for this exercise based on the instructions. "
                "Output ONLY the code block between ```python and ``` or ```rust and ```."
            )
        
        response = self.bridge.reason(prompt, context=context)
        # Extract code block
        match = re.search(r"```[a-z]*\n(.*?)\n```", response, re.DOTALL)
        if match:
            return match.group(1)
        return "# FAILED TO GENERATE CODE"

    def run_docker_test(self, path, command):
        """Runs the test command inside the antigravity-bench container."""
        try:
            # We use powershell to run our docker_run.ps1
            cmd = ["powershell.exe", "-File", self.docker_script, "-Action", "run", "-ExercisePath", path, "-Command", command]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            output = result.stdout + "\n" + result.stderr
            passed = "OK" in output or "passed" in output or "test result: ok" in output
            return passed, output
        except Exception as e:
            return False, str(e)

    def calculate_soundness(self, code):
        try:
            field = self.engine.produce_interference_field(code[:2000]) # Limit for speed
            field_vectors = {name: data['magnitude'] for name, data in field.items()}
            return self.monitor.get_soundness_score(field_vectors)
        except:
            return 0.0

    def run_native_test(self, track, path, name):
        """Executes the native test suite in an isolated subprocess."""
        try:
            cmd = []
            if track == "python":
                test_file = f"{name.replace('-','_')}_test.py"
                cmd = [sys.executable, test_file]
            elif track == "rust":
                cmd = ["cargo", "test", "--offline"]

            # Isolated execution
            result = subprocess.run(cmd, cwd=path, capture_output=True, text=True, timeout=30)
            
            if track == "python":
                return "OK" in result.stderr or "passed" in result.stdout
            elif track == "rust":
                return "test result: ok" in result.stdout
        except Exception as e:
            print(f"  [ERROR] Execution failed: {e}")
            return False
        return False

    def report_aggregate(self):
        """Generates the master report and crystallizes in H5."""
        report_path = "E:/Antigravity/Architecture/benchmarks/aggregate_report_master.json"
        
        total = len(self.results)
        passed_1 = sum(1 for r in self.results if r.get('passed_1'))
        passed_2 = sum(1 for r in self.results if r.get('passed_2'))
        avg_soundness = np.mean([r['soundness'] for r in self.results]) if self.results else 0
        
        summary = {
            "total_exercises": total,
            "pass_rate_1": passed_1 / total if total > 0 else 0,
            "pass_rate_2": passed_2 / total if total > 0 else 0,
            "average_soundness": avg_soundness,
            "details": self.results
        }
        
        with open(report_path, 'w') as f:
            json.dump(summary, f, indent=4)
        
        # Crystallize as a Master Axiom
        axiom_id = f"SOVEREIGN_AIDER_BENCHMARK_{int(time.time())}"
        self.manager.save_axiom(axiom_id, f"Aider-Standard Run: Pass_1={passed_1}/{total} AvgS={avg_soundness:.4f}", 
                               np.zeros(384), leverage=avg_soundness, 
                               metadata={"type": "AIDER_BENCHMARK", "pass_rate_1": summary['pass_rate_1'], "pass_rate_2": summary['pass_rate_2']}, 
                               status='CRYSTALLIZED')
        
        print(f"\n[BENCHMARK] Aider-Standard Report Generated: {report_path}")
        print(f"  -> Total: {total} | Pass_1: {summary['pass_rate_1']:.2%} | Pass_2: {summary['pass_rate_2']:.2%} | Avg Soundness: {avg_soundness:.4f}")

if __name__ == "__main__":
    runner = PolyglotRunner()
    
    # Optional: run a small sample first
    if len(sys.argv) > 1 and sys.argv[1] == "--sample":
        runner.run_track("python", limit=5)
        runner.run_track("rust", limit=5)
    else:
        # Full run
        runner.run_track("python")
        runner.run_track("rust")
        
    runner.report_aggregate()
