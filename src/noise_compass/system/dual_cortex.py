import json
import time
from typing import Dict, List, Optional
from noise_compass.system.token_pipeline import DeltaToken, CausalType

class ArchiverMessage:
    """
    Standardized Ouroboros-to-Observer communication protocol (Session 12).
    Wraps the current intent, detected invariants, and causal trajectories.
    """
    def __init__(self, intent: str, delta_tokens: List[DeltaToken], gap_structure: Optional[Dict] = None):
        self.timestamp = time.time()
        self.intent = intent
        self.delta_tokens = delta_tokens
        self.gap_structure = gap_structure or {}
        self.fisher_alignment = self._calculate_fisher()
        self.ssm_id = f"SSM_{int(self.timestamp*1000)}"

    def _calculate_fisher(self) -> float:
        """
        Heuristic Fisher Information alignment.
        High alignment = Structural Invariant (INTERVENTION).
        """
        if not self.delta_tokens: return 0.0
        causal_count = sum(1 for t in self.delta_tokens if t.causal_type == CausalType.INTERVENTION)
        return causal_count / len(self.delta_tokens)

    def to_json(self) -> str:
        tokens_data = []
        for t in self.delta_tokens:
            tokens_data.append({
                "id": t.token_id,
                "magnitude": t.magnitude,
                "causal_type": t.causal_type.value,
                "layer": t.layer
            })
            
        return json.dumps({
            "intent": self.intent,
            "timestamp": self.timestamp,
            "ssm_id": self.ssm_id,
            "fisher_alignment": self.fisher_alignment,
            "tokens": tokens_data,
            "gap_structure": self.gap_structure
        }, indent=2)

class DualBrainSystem:
    """
    Coordinates the BitNet (Hot/Fast) and Qwen (Cold/Slow) brains.
    Manages the ARCHIVER_MESSAGE pipeline.
    """
    def __init__(self, bitnet_worker=None, qwen_bridge=None):
        self.bitnet = bitnet_worker
        self.qwen = qwen_bridge
        self.log_path = "e:/Antigravity/Runtime/archiver_logs.json"

    def emit_archiver_message(self, message: ArchiverMessage):
        """Broadcasts the message to the observer substrate."""
        data = message.to_json()
        print(f"[ARCHIVER] Message Emitted (Fisher: {message.fisher_alignment:.2f})")
        
        try:
            with open(self.log_path, "a", encoding='utf-8') as f:
                f.write(data + "\n---\n")
        except: pass

if __name__ == "__main__":
    # Test Archiver Message
    from noise_compass.system.token_pipeline import DeltaToken, CausalType
    import numpy as np
    
    t1 = DeltaToken("DT_1", 0.9, np.zeros(384), 2, "SOURCE", CausalType.INTERVENTION)
    t2 = DeltaToken("DT_2", 0.4, np.zeros(384), 1, "SOURCE", CausalType.GRADIENT)
    
    msg = ArchiverMessage("Test Intent", [t1, t2])
    print(msg.to_json())
