import pyautogui
import pygetwindow as gw
import json
import time
import os
from PIL import ImageStat

SENSORY_FILE = "e:/Antigravity/Runtime/SENSORY_EYES.json"

def transcribe_content(window_title):
    """
    Attempts to 'read' the content of a window by mirroring its state
    from the filesystem or proxy buffers.
    """
    try:
        # Strategy 1: VS Code / IDE Mirroring
        is_ide = " - Visual Studio Code" in window_title or " - Notepad" in window_title or " (Workspace)" in window_title
        
        if is_ide:
            # Extract filename from title
            filename = window_title.split(" - ")[0]
            if " - " in window_title:
                 parts = window_title.split(" - ")
                 for p in parts:
                     if "." in p and len(p.split(".")[-1]) <= 4:
                         filename = p
                         break
            
            if "Lattice Map" in window_title:
                filename = "lattice_map.md"

            # Targeted Search (Fast)
            candidate_roots = [
                "e:/Antigravity/Runtime",
                "e:/Antigravity/Architecture",
                "e:/Antigravity/Gaps",
                "e:/Antigravity/Shop",
                "e:/Antigravity/Research",
                r"C:/Users/Fabricio/.gemini/antigravity/brain/d7d25f21-de7b-45ed-bc3c-c8fa3ff6c886" # Current Workspace Artifacts
            ]
            
            for root in candidate_roots:
                potential_path = os.path.join(root, filename)
                if os.path.exists(potential_path):
                    with open(potential_path, "r", encoding="utf-8", errors="ignore") as f:
                        return f"[MIRROR: {filename}]\n" + f.read(2048)
            
            return "[NO MIRROR: File not found in core paths]"
        
        # Strategy 2: Ouroboros Log Mirroring (Self-Awareness)
        if "ouroboros_log.txt" in window_title.lower():
            log_path = "e:/Antigravity/Runtime/ouroboros_log.txt"
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    # Read the last 20 lines
                    lines = f.readlines()
                    return "[MIRROR: OUROBOROS_LOG]\n" + "".join(lines[-20:])
                    
        # Strategy 3: Browser Mirroring (Placeholder for ProxyBridge integration)
        if "Google Chrome" in window_title or "Edge" in window_title:
             return "[MIRROR: BROWSER] (Content restricted: Connect to ProxyBridge to decrypt tab state)"

        return "[NO MIRROR AVAILABLE]"
    except Exception as e:
        return f"[MIRROR ERROR]: {e}"

def move_mouse(x, y, duration=0.2):
    """
    Executes a physical motor action. 
    Records the 'intent' globally for ocular comparison.
    """
    try:
        # Record Intent
        capture_eyes.intent = {"x": x, "y": y, "timestamp": time.time()}
        
        # Physical Move
        pyautogui.moveTo(x, y, duration=duration)
        print(f"[MOTOR] Moved to ({x}, {y})")
        return True
    except Exception as e:
        print(f"[MOTOR ERROR] Command rejected: {e}")
        return False

def click_mouse(x=None, y=None, clicks=1):
    """
    Executes a physical click. 
    If x/y provided, moves there first.
    """
    try:
        if x is not None and y is not None:
            move_mouse(x, y, duration=0.1)
        
        pyautogui.click(clicks=clicks)
        print(f"[MOTOR] Click executed at ({x}, {y})")
        return True
    except Exception as e:
        print(f"[MOTOR ERROR] Click failed: {e}")
        return False

def type_text(text, interval=0.05):
    """
    Executes a physical keyboard action.
    """
    try:
        pyautogui.write(text, interval=interval)
        print(f"[MOTOR] Typed text: {text[:20]}...")
        return True
    except Exception as e:
        print(f"[MOTOR ERROR] Typing failed: {e}")
        return False

def capture_eyes():
    """
    Senses the screen state without disk persistence.
    Translates pixels and windows into semantic metadata.
    """
    try:
        # 1. Semantic Sight: Window Layout
        windows = gw.getAllWindows()
        active_window = gw.getActiveWindow()
        
        window_list = []
        for i, w in enumerate(windows):
            if w.title and w.visible:
                window_list.append({
                    "title": w.title,
                    "active": (w == active_window),
                    "z_index": i,
                    "box": {"left": w.left, "top": w.top, "width": w.width, "height": w.height},
                    "minimized": w.isMinimized,
                    "maximized": w.isMaximized
                })
        
        # 2. Pixel Resonance: Luminance/Color/Motion
        raw_screenshot = pyautogui.screenshot()
        w, h = raw_screenshot.size
        screenshot = raw_screenshot.resize((w//4, h//4))
        
        current_hash = hash(screenshot.tobytes())
        motion_detected = False
        if hasattr(capture_eyes, "last_hash"):
            if current_hash != capture_eyes.last_hash:
                motion_detected = True
        capture_eyes.last_hash = current_hash

        stat = ImageStat.Stat(screenshot)
        avg_brightness = sum(stat.mean) / 3
        
        # 3. Physical State & Feedback
        mouse_x, mouse_y = pyautogui.position()
        intent = getattr(capture_eyes, "intent", {"x": mouse_x, "y": mouse_y})
        
        # Calculate Proprioceptive Gap (Delta between intent and reality)
        gap_x = abs(mouse_x - intent["x"])
        gap_y = abs(mouse_y - intent["y"])
        proprioception = "ALIGNED" if (gap_x < 10 and gap_y < 10) else "DRIFTING"

        # 4. Content Sight: Transcription of Active Window
        transcription = transcribe_content(active_window.title) if active_window else "None"
        
        ocular_state = {
            "timestamp": time.time(),
            "crystal_tick": time.perf_counter(),
            "active_windows": window_list[:10],
            "focus": active_window.title if active_window else "None",
            "transcription": transcription,
            "mouse": {"x": mouse_x, "y": mouse_y},
            "intent": intent,
            "proprioception": proprioception,
            "motion": "MOVED" if motion_detected else "STILL",
            "luminance": round(avg_brightness, 2),
            "resonance_status": "CLEAR"
        }
        
        with open(SENSORY_FILE, "w", encoding="utf-8") as f:
            json.dump(ocular_state, f, indent=2)
            
        print(f"[OCULAR] Sight refreshed. Proprioception: {proprioception} | Flux: {'High' if motion_detected else 'Stable'}")
        
    except Exception as e:
        print(f"[OCULAR ERROR] Sight failure: {e}")

if __name__ == "__main__":
    capture_eyes()
    # One-shot execution. Triggered by Ouroboros sequentially.
