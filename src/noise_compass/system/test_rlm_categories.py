
import os
import sys
import json
import re

# Add project roots
SRC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(SRC_ROOT)

from noise_compass.system.ouroboros import Ouroboros
from noise_compass.system.shadow_buffer import ShadowBuffer

def test_rlm_categorization_flow():
    print("--- 0x528 RLM PHASE 134: TASK DIFFERENTIATION TEST ---")
    
    # 1. Initialize
    # We use a mock-like initialization to avoid the full 2-hour background loop
    ouro = Ouroboros(is_child=True) 
    buffer = ShadowBuffer()
    # Clear buffer
    buffer.pending_intents = []
    buffer.save()
    
    # 2. Test Multi-Mode Intent
    mixed_intent = "FIX the dictionary AND then INGEST the browser logs"
    print(f"[INPUT]: {mixed_intent}")
    
    # 3. Decompose
    print("[PROCESS]: Decomposing and Categorizing...")
    decomposed = ouro.rlm_decompose(mixed_intent)
    
    for i, task in enumerate(decomposed):
        intent = task["intent"]
        t_type = task["type"]
        print(f"  Task {i+1}: {intent}")
        print(f"  Type:   {t_type}")
        
    # 4. Verify Logic
    if decomposed[0]["type"] == "STRUCTURAL" and decomposed[1]["type"] == "PHYSICAL":
        print("\n[VERDICT]: SUCCESS. Structural (Manocentric) vs Physical (Somatocentric) split confirmed.")
    else:
        print("\n[VERDICT]: FAILURE. Incorrect categorization.")
        return False

    # 5. Verify Shadow Buffer Persistence
    print("[BUFFER]: Pushing sub-tasks to Shadow Buffer...")
    for sub in decomposed[1:]:
        buffer.push_intent(sub["intent"], sub["type"])
        
    # Re-load to check
    new_buffer = ShadowBuffer()
    saved_task = new_buffer.pop_intent()
    print(f"[RECOVERED]: Type: {saved_task['type']} | Intent: {saved_task['intent'][:30]}...")

    if saved_task['type'] == "PHYSICAL":
         print("[VERDICT]: SUCCESS. Metadata preserved in Shadow Buffer.")
    else:
         print("[VERDICT]: FAILURE. Metadata lost.")
         return False

    return True

if __name__ == "__main__":
    if test_rlm_categorization_flow():
        sys.exit(0)
    else:
        sys.exit(1)
