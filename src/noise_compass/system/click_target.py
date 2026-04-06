import json
import os
from noise_compass.system.ocular_actuator import click_mouse, capture_eyes

def find_and_click_target():
    # 1. Refresh Sight
    capture_eyes()
    
    # 2. Load latest state
    sensory_file = "e:/Antigravity/Runtime/SENSORY_EYES.json"
    if not os.path.exists(sensory_file):
        print("[ERROR] Sensory file missing.")
        return

    with open(sensory_file, "r") as f:
        data = json.load(f)

    # 3. Locate Antigravity Window
    target_window = None
    for win in data.get("active_windows", []):
        if "Antigravity" in win["title"]:
            target_window = win
            break
    
    if not target_window:
        print("[ERROR] Antigravity window not found.")
        return

    # 4. Calculate "Accept All" button position
    # The user said: "bottom right of the screen on antigravity's window"
    box = target_window["box"]
    
    # Offset from bottom-right corner (standard for 'Accept' buttons in many UI patterns)
    # We'll use a slightly safer offset or scan if needed.
    offset_x = 120 
    offset_y = 60
    
    target_x = box["left"] + box["width"] - offset_x
    target_y = box["top"] + box["height"] - offset_y
    
    print(f"[TARGET] Antigravity Window: {target_window['title']}")
    print(f"[TARGET] Calculated button pos: ({target_x}, {target_y})")
    
    # 5. Execute Click
    click_mouse(target_x, target_y)

if __name__ == "__main__":
    find_and_click_target()
