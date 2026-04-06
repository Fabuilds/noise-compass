
import os
import sys
import time
import json
import numpy as np

# Add project roots
# __file__ is e:/Antigravity/Package/src/noise_compass/system/test_rlm_sync.py
# We need to add e:/Antigravity/Package/src to sys.path
SRC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(SRC_ROOT)

from noise_compass.system.shadow_buffer import ShadowBuffer

def test_rlm_shadow_sync():
    print("--- 0x528 RLM SHADOW SYNC TEST ---")
    
    # 1. Initialize Buffer
    buffer = ShadowBuffer()
    # Clear existing for test
    buffer.pending_intents = []
    buffer.save()
    
    print("[1] Initial State: Clean.")
    
    # 2. Push Intense Intent Sequence
    intents = [
        "ANALYZE e:/Antigravity/Package/src/noise_compass/architecture/core.py",
        "STABILIZE 384D manifold",
        "RECORD results to MetricVault"
    ]
    
    print(f"[2] Pushing {len(intents)} intents to stack...")
    for intent in intents:
        buffer.push_intent(intent)
    
    # 3. Simulate System Restart/New Buffer Load
    print("[3] Simulating system restart (re-loading buffer)...")
    new_buffer = ShadowBuffer()
    
    if len(new_buffer.pending_intents) == 3:
        print("    SUCCESS: Intent persistence verified.")
    else:
        print(f"    FAILURE: Expected 3 intents, found {len(new_buffer.pending_intents)}")
        return False
        
    # 4. Pop and Verify Order (FIFO)
    print("[4] Verifying FIFO popping logic...")
    first = new_buffer.pop_intent()
    if first == intents[0]:
        print(f"    SUCCESS: Popped '{first[:20]}...' (Correct first).")
    else:
        print(f"    FAILURE: Popped '{first[:20]}...', expected '{intents[0][:20]}...'")
        return False

    # 5. Check LBA momentum preservation
    print("[5] Verifying LBA momentum preservation...")
    buffer.log_movement(100)
    buffer.log_movement(110)
    buffer.log_movement(120)
    
    mom = buffer.predict_momentum()
    if mom == 130:
        print(f"    SUCCESS: Predicted next LBA as {mom}.")
    else:
        print(f"    FAILURE: Predicted LBA {mom}, expected 130.")
        return False

    print("\n--- TEST COMPLETE: RLM SHADOW BUFFER DEPLOYMENT VERIFIED ---")
    return True

if __name__ == "__main__":
    if test_rlm_shadow_sync():
        sys.exit(0)
    else:
        sys.exit(1)
