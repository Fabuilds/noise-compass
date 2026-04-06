import time
import os
import math
from noise_compass.system.ocular_actuator import move_mouse, capture_eyes

def execute_kinetic_trace():
    """
    Moves the mouse in a geometric pattern and captures ocular state.
    """
    print("[KINETIC] Commencing Motor Sight Verification...")
    
    # 1. Get Screen Center
    import pyautogui
    screen_w, screen_h = pyautogui.size()
    cx, cy = screen_w // 2, screen_h // 2
    
    radius = 200
    steps = 24 # 24 frames of motion
    
    # Pre-move to center
    move_mouse(cx, cy, duration=0.5)
    capture_eyes()
    time.sleep(1)

    print(f"[KINETIC] Drawing Orbital Path around ({cx}, {cy})...")
    
    for i in range(steps + 1):
        angle = (2 * math.pi * i) / steps
        target_x = int(cx + radius * math.cos(angle))
        target_y = int(cy + radius * math.sin(angle))
        
        # Fast move
        move_mouse(target_x, target_y, duration=0.1)
        
        # Real-time capture (Sight)
        capture_eyes()
        
        # Small delay to ensure OS moves cursor before next instruction
        time.sleep(0.05)

    print("[KINETIC] Orbital Trace Complete. Verify SENSORY_EYES.json for proprioceptive alignment.")

if __name__ == "__main__":
    execute_kinetic_trace()
