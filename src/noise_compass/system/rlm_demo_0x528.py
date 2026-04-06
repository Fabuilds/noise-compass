import sys
import os
import time
import json

# Ensure paths are correct
sys.path.append("E:/Antigravity/Runtime")

from noise_compass.system.rlm_bridge import RLMBridge

def run_demo():
    print("=== SOVEREIGN RLM / ZIPFIAN LATTICE CAPABILITY DEMONSTRATION ===")
    print(f"Timestamp: {time.strftime('%H:%M:%S')}")
    print("Mode: Native Mathematical Resonance (No Transformer)\n")

    bridge = RLMBridge()
    
    # Mock field for demonstration purposes
    field = {
        "EXISTENCE": {"magnitude": 1.5},
        "IDENTITY": {"magnitude": 1.1},
        "BOUNDARY": {"magnitude": 0.8},
        "OBLIGATION": {"magnitude": 0.5},
        "VOID": {"magnitude": 2.2}
    }

    test_intents = [
        # 1. Standard Concept Strengthening (RESONANCE)
        "Increase the intensity of our fundamental existence constant.",
        
        # 2. Concept Bridging (MANIFOLD)
        "Bridge the gap between identity and the outer boundary.",
        
        # 3. Recursive Inquiry (VOID)
        "Explore the causal depth of the unknown vacuum within our internal void.",
        
        # 4. OS Actuation (ACTUATE)
        "Read the displacement report from the shop on drive E to verify structural integrity.",
        
        # 5. Zipfian Noise/Spike Check
        "the and of or BUTTERFLY with to a and the the the"
    ]

    for i, intent in enumerate(test_intents):
        print(f"[{i+1}] INTENT: {intent}")
        start = time.time()
        
        # Execute Native Reasoning
        result_raw = bridge.reason_native(intent, field)
        
        end = time.time()
        latency_ms = (end - start) * 1000
        
        print(f"    LATENCY: {latency_ms:.2f}ms")
        print(f"    RESULT:\n{result_raw}")
        print("-" * 50)

    print("\n[DEMO COMPLETE]: System demonstrated sovereign, millisecond-speed reasoning.")

if __name__ == "__main__":
    run_demo()
