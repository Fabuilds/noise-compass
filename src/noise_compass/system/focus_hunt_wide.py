import pyautogui
import time
import pyperclip
from noise_compass.system.ocular_actuator import click_mouse

def horizontal_focus_hunt():
    print("[HUNT] Commencing horizontal focus sweep at bottom...")
    # Test typical sidebar and panel locations
    # 200: Left Sidebar, 1280: Top/Center, 2300: Right Sidebar
    test_x = [200, 500, 1280, 2000, 2300]
    ty = 1300 # Bottom area
    
    for tx in test_x:
        print(f"[HUNT] Testing X={tx}, Y={ty}...")
        pyautogui.click(tx, ty)
        time.sleep(0.5)
        
        sig = f"SIG_{tx}"
        pyautogui.typewrite(sig)
        time.sleep(0.2)
        
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.1)
        
        try:
            pasted = pyperclip.paste()
            if sig in pasted:
                print(f"[SUCCESS] Focus found at X={tx}! Content: {pasted}")
                return tx, ty
        except:
            pass
        
        pyautogui.press('backspace')
    
    print("[FAILURE] No focusable input found in horizontal sweep.")
    return None

if __name__ == "__main__":
    horizontal_focus_hunt()
