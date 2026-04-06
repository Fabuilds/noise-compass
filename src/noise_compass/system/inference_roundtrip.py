import sys
import os
import json
import time
import numpy as np
import argparse

# Ensure paths are correct
PROJECT_ROOT = "e:/Antigravity"
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, "System"))

from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.interference_engine import InterferenceEngine
import socket

class InferenceRoundtrip:
    def __init__(self):
        self.h5 = H5Manager()
        self.interference = InterferenceEngine()
        self.apex_port = 5286
        self.audit_file = "e:/Antigravity/Runtime/INFERENCE_AUDIT.md"

    def remote_reason(self, prompt):
        """Sends a reasoning request to the APEX_LOBE."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(120) # 2 minute timeout for large codeblocks
                s.connect(('127.0.0.1', self.apex_port))
                request = json.dumps({"intent": prompt, "field": {}})
                s.sendall(request.encode('utf-8'))
                
                # Use a loop to receive larger payloads
                chunks = []
                while True:
                    chunk = s.recv(65536)
                    if not chunk: break
                    chunks.append(chunk)
                return b"".join(chunks).decode('utf-8')
        except Exception as e:
            return f"REMOTE_ERROR: {e}"

    def run(self, target_path):
        print(f"--- STARTING INFERENCE ROUNDTRIP ON: {target_path} ---")
        
        # 1. Extraction
        with open(target_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # 2. RAR Distillation (Semantic Invariant)
        print("[1/4] Distilling Semantic Invariant via APEX...")
        rar_prompt = f"Explain the irreducible semantic purpose and structural invariants of the following code. Return a concise, high-level summary that identifies the core 'Logic-Peak' it represents:\n\n```python\n{source_code}\n```"
        explanation = self.remote_reason(rar_prompt)
        print(f"   Invariant: {explanation[:100]}...")

        # 3. Substrate Projection (H5 Mapping)
        print("[2/4] Projecting through H5 Substrate...")
        field = self.interference.combined_field(explanation)
        
        # Identify top peaks
        peaks = sorted(field.items(), key=lambda x: -x[1]['magnitude'])[:5]
        peak_names = [p[0] for p in peaks]
        print(f"   Resonant Peaks: {', '.join(peak_names)}")

        # 4. Grounded Synthesis
        print("[3/4] Synthesizing Grounded Code via APEX...")
        grounding_context = f"Resonant Peaks in H5: {', '.join(peak_names)}\nSemantic Invariant: {explanation}"
        synthesis_prompt = f"Based on the following semantic grounding and resonant peaks from the H5 manifold, synthesize a 'Betterment' version of the original code. Ensure the new code is more deeply integrated with the identified peaks and maintains structural coherence.\n\nGROUNDING:\n{grounding_context}\n\nORIGINAL CODE:\n```python\n{source_code}\n```"
        new_code = self.remote_reason(synthesis_prompt)
        
        # 5. Verification & Auditing
        print("[4/4] Finalizing Audit...")
        self.log_audit(target_path, explanation, peak_names, new_code)
        print(f"--- ROUNDTRIP COMPLETE. Results in {self.audit_file} ---")

    def log_audit(self, target, invariant, peaks, result):
        timestamp = time.ctime()
        entry = f"""
## Inference Audit: {target}
**Timestamp**: {timestamp}
**Detected Invariant**: 
> {invariant}

**H5 Grounding (Resonant Peaks)**:
{', '.join(peaks)}

**Resynthesized Model**:
```python
{result}
```
---
"""
        with open(self.audit_file, "a", encoding='utf-8') as f:
            f.write(entry)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Path to the source file to infer code from.")
    args = parser.parse_args()
    
    # Silence stdout/stderr for headless if needed (inherited from Ouroboros pattern)
    try:
        sys.stdout.write("")
    except (OSError, AttributeError):
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    ir = InferenceRoundtrip()
    ir.run(args.target)
