import sys
import os
import time
import json

# Ensure paths are correct
sys.path.append("E:/Antigravity/Runtime")

from noise_compass.system.rlm_bridge import RLMBridge

def run_demo():
    print("=== SOVEREIGN RLM / ZIPFIAN LATTICE COHERENT DEMONSTRATION ===")
    print(f"Timestamp: {time.strftime('%H:%M:%S')}")
    print("Mode: Native Mathematical Resonance (Saliency-Aware)\n")

    bridge = RLMBridge()
    
    # Standard cognitive field
    field = {
        "EXISTENCE": {"magnitude": 1.0},
        "IDENTITY": {"magnitude": 0.5}
    }

    # A coherent, multi-layered intent
    intent = "I need to analyze the displacement vectors between the internal void and the identity node to ensure our causality field remains stable."
    
    print(f"COHERENT INTENT: {intent}")
    
    start = time.time()
    result_raw = bridge.reason_native(intent, field)
    end = time.time()
    
    print(f"LATENCY: {(end - start) * 1000:.2f}ms")
    print(f"RESULT:\n{result_raw}")
    print("-" * 50)

    # test 2: Actionable intent
    intent_2 = "Open the displacement report from e:/Antigravity/Shop/DISPLACEMENT_REPORT_0x528.md"
    print(f"ACTIONABLE INTENT: {intent_2}")
    
    start = time.time()
    result_raw_2 = bridge.reason_native(intent_2, field)
    end = time.time()
    
    print(f"LATENCY: {(end - start) * 1000:.2f}ms")
    print(f"RESULT:\n{result_raw_2}")

if __name__ == "__main__":
    run_demo()
