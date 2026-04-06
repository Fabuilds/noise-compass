import pyautogui
import time
import json
import os
from noise_compass.system.ocular_actuator import click_mouse, type_text, capture_eyes

def precision_type_query():
    print("[EXPRESSION] Starting Precision Typing Sequence...")
    
    # 1. Use anchor from previous successful blue-button find
    # The button was at (2515, 1279).
    # We'll target the same Y but the middle of the screen for X.
    screen_w, screen_h = pyautogui.size()
    cx = screen_w // 2
    cy = 1279 # Anchor from the blue button found in Phase 47
    
    print(f"[EXPRESSION] Targeting Input Field at ({cx}, {cy})...")
    
    # 2. Force Focus
    pyautogui.click(cx, cy)
    time.sleep(0.5)
    pyautogui.click(cx, cy) # Double click to be sure
    time.sleep(0.5)
    
    # 3. Clear existing text (Safety)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('backspace')
    time.sleep(0.2)
    
    # 4. Type the Query
    query = "Analyze the current proprioceptive status of the Sovereign Substrate."
    print(f"[EXPRESSION] Typing: '{query}'")
    type_text(query, interval=0.03) # Slightly faster
    
    # 5. Submit
    time.sleep(0.5)
    pyautogui.press('enter')
    print("[EXPRESSION] Query submitted.")
    
    # 6. Verification Sight
    time.sleep(1)
    capture_eyes()

if __name__ == "__main__":
    precision_type_query()
