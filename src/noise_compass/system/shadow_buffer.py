import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import json
import time
from collections import deque

RUNTIME_DIR = "E:/Antigravity/Runtime"
SHADOW_FILE = os.path.join(RUNTIME_DIR, 'SHADOW_BUFFER.json')
os.makedirs(RUNTIME_DIR, exist_ok=True)

class ShadowBuffer:
    def __init__(self, max_len=1000):
        self.max_len = max_len
        self.buffer = deque(maxlen=max_len)
        self.pending_intents = [] # RLM: Recursive Intent Stack
        self.load()
        
    def log_movement(self, lba, context="TRAVERSAL"):
        """Records a physical movement to the Shadow Index."""
        entry = {
            "ts": time.time(),
            "lba": lba,
            "ctx": context
        }
        self.buffer.append(entry)
        
        # Periodic Save (Every 10 updates)
        if len(self.buffer) % 10 == 0:
            self.save()

    def push_intent(self, intent, task_type="PHYSICAL", task_invariant="ENG"):
        """RLM: Adds a categorized intent to the recursion stack."""
        entry = {"intent": intent, "type": task_type, "invariant": task_invariant}
        if entry not in self.pending_intents:
            self.pending_intents.append(entry)
            self.save()

    def pop_intent(self):
        """RLM: Retrieves the next categorized intent from the stack."""
        if self.pending_intents:
            entry = self.pending_intents.pop(0)
            self.save()
            return entry
        return None
            
    def predict_momentum(self):
        """
        Analyzes the last few movements to predict the next LBA area.
        Returns a 'Center of Gravity' LBA or None.
        """
        if len(self.buffer) < 2:
            return None
            
        # 1. Extract recent LBAs
        recent = list(self.buffer)[-10:]
        
        # 2. Calculate Velocity (Delta LBA)
        lbas = [r['lba'] for r in recent]
        delta_sum = 0
        for i in range(1, len(lbas)):
            delta_sum += (lbas[i] - lbas[i-1])
            
        avg_velocity = delta_sum / (len(lbas) - 1)
        
        # 3. Predict Next
        last_lba = lbas[-1]
        next_lba = int(last_lba + avg_velocity)
        return next_lba

    def save(self):
        try:
            data = {
                "buffer": list(self.buffer),
                "pending_intents": self.pending_intents
            }
            with open(SHADOW_FILE, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"[SHADOW]: Save Error -> {e}")

    def load(self):
        if os.path.exists(SHADOW_FILE):
            try:
                with open(SHADOW_FILE, "r") as f:
                    raw = json.load(f)
                    if isinstance(raw, dict):
                        self.buffer = deque(raw.get("buffer", []), maxlen=self.max_len)
                        self.pending_intents = raw.get("pending_intents", [])
                    else:
                        # Legacy format (just a list)
                        self.buffer = deque(raw, maxlen=self.max_len)
                        self.pending_intents = []
            except Exception:
                self.buffer = deque(maxlen=self.max_len)
                self.pending_intents = []
