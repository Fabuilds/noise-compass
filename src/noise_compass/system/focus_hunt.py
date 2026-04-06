import os
import time
import json
import pyautogui
import pyperclip # Assuming this is available or I can use a fallback
from noise_compass.system.ocular_actuator import click_mouse, capture_eyes

def focus_hunt():
    print("[HUNT] Commencing vertical focus sweep...")
    cx = 1280 # Horizontal center
    start_y = 1100
    end_y = 1350
    step = 40
    
    for ty in range(start_y, end_y + 1, step):
        print(f"[HUNT] Testing Y={ty}...")
        pyautogui.click(cx, ty)
        time.sleep(0.5)
        
        # Type a unique signature
        sig = f"SIG_{ty}"
        pyautogui.typewrite(sig)
        time.sleep(0.2)
        
        # Try to select all and copy
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.1)
        
        try:
            pasted = pyperclip.paste()
            if sig in pasted:
                print(f"[SUCCESS] Focus found at Y={ty}! Content: {pasted}")
                return ty
        except Exception as e:
            print(f"[ERR] Clipboard access: {e}")
        
        # Clear field for next attempt
        pyautogui.press('backspace')
    
    print("[FAILURE] No focusable input detected in sweep.")
    return None

if __name__ == "__main__":
    focus_hunt()
