import pyautogui
import time
import os

class WindowNav:
    """
    High-level Windows Navigation Utility for the Antigravity Machine.
    Abstracts away timing and shortcut complexities for smaller LLMs.
    """
    
    @staticmethod
    def launch_app(app_name):
        print(f"[WINDOW_NAV] Clearing Overlays...")
        pyautogui.press('esc')
        time.sleep(0.5)
        pyautogui.press('esc')
        time.sleep(0.5)
        print(f"[WINDOW_NAV] Clearing Desktop...")
        pyautogui.hotkey('win', 'd')
        time.sleep(1.0)
        print(f"[WINDOW_NAV] Launching: {app_name}")
        pyautogui.hotkey('win', 'r')
        time.sleep(1.5)
        pyautogui.typewrite(app_name)
        pyautogui.press('enter')
        # Wait for app to initialize
        time.sleep(5.0)
    
    @staticmethod
    def type_text(text):
        print(f"[WINDOW_NAV] Typing text...")
        pyautogui.typewrite(text)
        time.sleep(1.0)
        pyautogui.press('enter')
    
    @staticmethod
    def save_file(file_path):
        directory = os.path.abspath(os.path.dirname(file_path))
        filename = os.path.basename(file_path)
        
        print(f"[WINDOW_NAV] Initiating Save...")
        pyautogui.hotkey('ctrl', 's')
        # Wait for dialog
        time.sleep(3.0)
        
        if directory:
            print(f"[WINDOW_NAV] Navigating to directory: {directory}")
            # Focus Address Bar
            pyautogui.hotkey('alt', 'd')
            time.sleep(1.0)
            # Clear it
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            time.sleep(0.5)
            # Type directory path
            pyautogui.typewrite(directory, interval=0.01)
            time.sleep(0.5)
            pyautogui.press('enter')
            # Wait for navigation to complete
            time.sleep(2.0)
            
        print(f"[WINDOW_NAV] Typing filename: {filename}")
        # Focus File Name field
        pyautogui.hotkey('alt', 'n')
        time.sleep(0.5)
        # Clear existing
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        time.sleep(0.5)
        # Type filename
        pyautogui.typewrite(filename, interval=0.01)
        time.sleep(1.0)
        # Save
        pyautogui.press('enter')
        time.sleep(3.0)
        # Attempt to confirm if overwrite dialog pops up (safe bet for test scripts)
        pyautogui.press('y')
        time.sleep(1.0)

    @staticmethod
    def browse_explorer(path):
        print(f"[WINDOW_NAV] Opening Explorer: {path}")
        pyautogui.hotkey('win', 'r')
        time.sleep(1.0)
        pyautogui.typewrite(f"explorer.exe \"{path}\"")
        pyautogui.press('enter')
        time.sleep(4.0)

    @staticmethod
    def select_all(): pyautogui.hotkey('ctrl', 'a'); time.sleep(0.5)
    @staticmethod
    def copy(): pyautogui.hotkey('ctrl', 'c'); time.sleep(0.5)
    @staticmethod
    def paste(): pyautogui.hotkey('ctrl', 'v'); time.sleep(0.5)
    @staticmethod
    def close_window(): pyautogui.hotkey('alt', 'f4'); time.sleep(0.5)

if __name__ == "__main__":
    # Test script
    WindowNav.browse_explorer("e:/Antigravity/Runtime")
    WindowNav.select_all()
    WindowNav.close_window()
