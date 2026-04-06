import os
import time
import json
import socket
from pathlib import Path

class LogConsumator:
    def __init__(self, bridge_port=5282):
        self.bridge_port = bridge_port
        self.qwen_port = bridge_port # Phase 24: Corrected port mapping
        self.archive_dir = Path("e:/Antigravity/Runtime/Autonomous_Output")
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.historical_accretion_path = self.archive_dir / "HISTORICAL_ACCRETIONS.md"
        
    def _log(self, msg):
        print(f"[LOG_CONSUMATOR]: {msg}")

    def distill_log(self, text):
        """Sends log text to Qwen logic anchor for summarization. Uses exponential backoff."""
        prompt = (
            "You are the Antigravity Memory Distiller. Summarize the following system logs into a set of 'Semantic Invariants'. "
            "Ignore technical repetition and focus on emergent logic, stability trends, and manifold progress. "
            "Output the summary as a concise markdown section.\n\n"
            "LOGS:\n"
        ) + text[:10000] # Limit to avoid socket bloat
        
        task = {"type": "DISTILL", "payload": prompt}
        
        max_retries = 3
        backoff = 2
        for attempt in range(max_retries):
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.settimeout(120.0)
                client.connect(('127.0.0.1', self.qwen_port))
                client.sendall(json.dumps(task).encode('utf-8'))
                client.shutdown(socket.SHUT_WR)
                
                chunks = []
                while True:
                    chunk = client.recv(65536)
                    if not chunk: break
                    chunks.append(chunk)
                client.close()
                
                resp = json.loads(b"".join(chunks).decode('utf-8'))
                axioms = resp.get("axioms", [])
                return axioms[0] if axioms else "No semantic invariants extracted."
            except Exception as e:
                self._log(f"Distillation Attempt {attempt+1} Failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(backoff ** (attempt + 1))
                else:
                    raise e
        return "ERROR: Distillation process timed out."

    def consume(self, log_path, threshold_mb=2.0, lines_to_keep=200, line_threshold=1000):
        """Checks log size or line count, distills if necessary, and rotates."""
        path = Path(log_path)
        if not path.exists():
            return False
            
        size_mb = path.stat().st_size / (1024 * 1024)
        
        # Read lines for count check
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            line_count = len(lines)
        except:
            return False

        if size_mb < threshold_mb and line_count < line_threshold:
            # self._log(f"Log size {size_mb:.2f}MB and {line_count} lines below thresholds. Skipping.")
            return False
            
        self._log(f"DEBUG: Log exceeds threshold ({size_mb:.2f}MB / {line_count} lines). Initiating... (Keep: {lines_to_keep})")
        
        try:
            if line_count <= lines_to_keep:
                self._log("DEBUG: Line count <= keep. Skipping.")
                return False
            
            # Block to distill (all but the last lines_to_keep)
            distill_block = "".join(lines[:-lines_to_keep])
            keep_block = "".join(lines[-lines_to_keep:])
            
            # Perform distillation
            self._log(f"DEBUG: Distilling {len(distill_block)} chars...")
            summary = self.distill_log(distill_block[-10000:]) # Distill last 10k chars for efficiency
            
            # Archive the summary
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(self.historical_accretion_path, "a", encoding="utf-8") as f:
                f.write(f"\n## HISTORICAL ACCRETION [{timestamp}]\n")
                f.write(summary)
                f.write("\n\n---\n")
                
            # Truncate log
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"[{time.ctime()}] LOG_CONSUMPTION: Truncated {len(lines) - lines_to_keep} lines. Distillation archived.\n")
                f.write(keep_block)
                
            self._log(f"Consumption complete. {len(lines) - lines_to_keep} lines compressed.")
            return True
        except Exception as e:
            import traceback
            self._log(f"Consumption Failed: {e}\n{traceback.format_exc()}")
            return False

if __name__ == "__main__":
    # Test consumption
    consumer = LogConsumator()
    consumer.consume("e:/Antigravity/Runtime/ouroboros_log.txt", threshold_mb=0.1)
