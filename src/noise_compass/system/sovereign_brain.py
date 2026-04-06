import os
import requests
import json
import time
import subprocess

class SovereignBrain:
    def __init__(self):
        self.endpoint = "http://127.0.0.1:8080/v1/chat/completions"
        self.model_path = r"A:\LLama-3-8b-never.Q4_K_M.gguf"
        self.executor = r"A:\llamafile.exe"

    def is_running(self):
        """Checks if the llamafile server is responding."""
        try:
            # Simple check for the server
            requests.get("http://127.0.0.1:8080", timeout=2)
            return True
        except:
            return False

    def ensure_active(self):
        """Starts the llamafile server if not running."""
        if not self.is_running():
            print("[BRAIN] Initializing Sovereign LLM on Substrate A:...")
            # Start llamafile in the background
            subprocess.Popen([
                self.executor, 
                "--server",
                "-m", self.model_path,
                "--port", "8080",
                "--host", "127.0.0.1"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait for boot
            attempts = 0
            while not self.is_running() and attempts < 15:
                time.sleep(2)
                attempts += 1
            
            if self.is_running():
                print("[BRAIN] Sovereign LLM Online. Boundary Secured.")
                return True
            else:
                print("[BRAIN] FAILURE: LLM Substrate failed to engage.")
                return False
        return True

    def think(self, prompt, system_prompt="You are the Sovereign Brain of Antigravity."):
        """Delegates deep reasoning to the isolated model."""
        if not self.ensure_active():
            return "ERROR: SOVEREIGN_SUBSTRATE_OFFLINE"

        payload = {
            "model": "llama-3-8b",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        try:
            response = requests.post(self.endpoint, json=payload, timeout=300)
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            return f"ERROR: BRAIN_DESYNC -> {e}"

if __name__ == "__main__":
    brain = SovereignBrain()
    print("Testing Sovereign Brain...")
    response = brain.think("What is your mission on the A: drive?")
    print(f"Response: {response}")
