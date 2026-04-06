import pyautogui
from PIL import Image
import os
from noise_compass.system.ocular_actuator import click_mouse, capture_eyes

def find_target_by_color():
    print("[SIGHT] Scanning bottom-right quadrant for blue UI elements...")
    s = pyautogui.screenshot()
    w, h = s.size
    
    # Crop the bottom-right (v2: larger area to be safe)
    scan_w, scan_h = 800, 500
    q = s.crop((w-scan_w, h-scan_h, w, h))
    
    # Convert to RGB to be sure
    q = q.convert("RGB")
    pixels = list(q.getdata())
    
    # Target: High Blue, Low Red (Standard 'Accept' button blue)
    blue_indices = []
    for i, p in enumerate(pixels):
        r, g, b = p
        if b > 200 and r < 120:
            blue_indices.append(i)
    
    if not blue_indices:
        print("[SIGHT] No blue button detected in scan area.")
        return False

    # Find center of the blue cluster
    avg_idx = blue_indices[len(blue_indices)//2]
    qx = avg_idx % scan_w
    qy = avg_idx // scan_w
    
    abs_x = w - scan_w + qx
    abs_y = h - scan_h + qy
    
    print(f"[SIGHT] Found blue button at ({abs_x}, {abs_y})")
    
    # Execute Precision Click
    click_mouse(abs_x, abs_y)
    
    # Wait for UI to update, then verify
    time.sleep(1)
    capture_eyes()
    return True

if __name__ == "__main__":
    import time
    find_target_by_color()
