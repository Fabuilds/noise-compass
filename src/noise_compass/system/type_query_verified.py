import pyautogui
import time
import json
import os
from noise_compass.system.ocular_actuator import click_mouse, type_text, capture_eyes

def verified_type_query():
    print("[EXPRESSION] Commencing Precision Typing at Verified Coordinates...")
    
    # Coordinates confirmed by user feedback from focus hunt
    target_x = 2000
    target_y = 1300
    
    print(f"[EXPRESSION] Targeting Input Field at ({target_x}, {target_y})...")
    
    # 1. Force Focus on confirmed input area
    click_mouse(target_x, target_y)
    time.sleep(0.5)
    pyautogui.click(target_x, target_y) # Double click for focus reliability
    time.sleep(0.5)
    
    # 2. Clear focus-hunt signature if present
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('backspace')
    time.sleep(0.2)
    
    # 3. Type the Query
    query = "Analyze the current proprioceptive status of the Sovereign Substrate."
    print(f"[EXPRESSION] Typing: '{query}'")
    type_text(query, interval=0.03)
    
    # 4. Submit
    time.sleep(0.5)
    pyautogui.press('enter')
    print("[EXPRESSION] Query submitted.")
    
    # 5. Verification Sight
    time.sleep(1)
    capture_eyes()

if __name__ == "__main__":
    verified_type_query()
