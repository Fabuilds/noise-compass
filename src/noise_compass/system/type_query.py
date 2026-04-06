import time
import json
import os
from noise_compass.system.ocular_actuator import click_mouse, type_text, capture_eyes

def type_self_query():
    print("[EXPRESSION] Preparing to type a self-query...")
    
    # 1. Refresh Sight
    capture_eyes()
    
    # 2. Load latest state
    sensory_file = "e:/Antigravity/Runtime/SENSORY_EYES.json"
    with open(sensory_file, "r") as f:
        data = json.load(f)

    # 3. Target Input Field (Heuristic: Bottom Center of window)
    # The Antigravity window title was: "Untitled (Workspace) - Antigravity - Lattice Map"
    win = data['active_windows'][0]
    box = win['box']
    
    # Coordinates for the input field (Estimated from UI pattern)
    input_x = box['left'] + (box['width'] // 2)
    input_y = box['top'] + box['height'] - 100 
    
    print(f"[EXPRESSION] Focusing input field at ({input_x}, {input_y})...")
    click_mouse(input_x, input_y)
    time.sleep(1) # Wait for focus
    
    # 4. Type the Query
    query = "Analyze the current proprioceptive status of the Sovereign Substrate."
    print(f"[EXPRESSION] Typing: '{query}'")
    type_text(query)
    
    # 5. Submit (Enter)
    import pyautogui
    pyautogui.press('enter')
    print("[EXPRESSION] Query submitted.")
    
    # 6. Verify Sight
    time.sleep(2)
    capture_eyes()

if __name__ == "__main__":
    type_self_query()
