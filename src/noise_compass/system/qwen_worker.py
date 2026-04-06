import os
import sys
import json
import time
import socket
import threading
from concurrent.futures import ThreadPoolExecutor

# Add parent and Architecture dir
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Architecture"))

from noise_compass.system.qwen_bridge import QwenBridge

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "QWEN_WORKER_LOG.txt")

def log(msg):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{time.ctime()}] {msg}\n")

class QwenWorker:
    def __init__(self, port=5282):
        self.port = port
        log(f"Initializing Qwen Worker on port {port}...")
        self.bridge = QwenBridge()
        log("Qwen Bridge Loaded.")

    def get_resonance(self, text):
        try:
             res = self.bridge.reason(f"RESONANCE_CHECK: {text}. Output only a float from 0.0 to 1.0.", max_tokens=10)
             import re
             match = re.search(r"([01]\.\d+)|(\d\.\d+)|(\d+)", res)
             if match:
                 score_str = match.group(0)
                 try:
                     score = float(score_str)
                     if score > 1.0 and score <= 100.0: score /= 100.0 # Handle percentage
                     return min(1.0, max(0.0, score))
                 except: pass
             log(f"WARNING: Qwen resonance match failed for output: '{res}'")
             return 0.7
        except Exception as e:
             log(f"ERROR: get_resonance failed: {e}")
             return 0.5

    def handle_client(self, client, addr):
        try:
            # Read large payloads with buffering
            chunks = []
            while True:
                chunk = client.recv(65536)
                if not chunk:
                    break
                chunks.append(chunk)
            
            if not chunks:
                return
            
            data = b"".join(chunks).decode('utf-8')
            task_data = json.loads(data)
            task_type = task_data.get("type")
            payload = task_data.get("payload")
            
            start_time = time.time()
            log(f"[({addr[0]}, {addr[1]})] Processing Qwen Task: {task_type}")
            
            result = {}
            if task_type == "RESONANCE" or task_type == "DISTANCE":
                result["score"] = self.get_resonance(str(payload))
            elif task_type == "DISTILL":
                result["axioms"] = [self.bridge.reason(f"DISTILL_LOGS:\n{payload}", max_tokens=512)]
            else:
                result["error"] = "Unknown task type"
            
            end_time = time.time()
            compute_time = float(end_time - start_time)
            result["compute_time"] = compute_time
            
            client.sendall(json.dumps(result).encode('utf-8'))
            log(f"Qwen Task Completed: {task_type} (Time: {compute_time:.4f}s)")
            
        except Exception as e:
            import traceback
            log(f"ERROR [{addr}]: {e}\n{traceback.format_exc()}")
        finally:
            client.close()

    def run_loop(self):
        port = self.port
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind(('127.0.0.1', port))
        except OSError as e:
            log(f"[ERROR]: Port {port} is busy. ({e})")
            return
            
        server.listen(10)
        log(f"Qwen Multi-Threaded Socket Server listening on 127.0.0.1:{port}...")
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            while True:
                client, addr = server.accept()
                executor.submit(self.handle_client, client, addr)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5282)
    args = parser.parse_args()
    
    worker = QwenWorker(port=args.port)
    worker.run_loop()
