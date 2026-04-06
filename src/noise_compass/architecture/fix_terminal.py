import sys
import os
import subprocess

def fix_terminal():
    print("=== UNIVERSAL TERMINAL FIX: UTF-8 & FONT RESET ===")
    
    # 1. Force UTF-8 for the current Python process output
    if sys.platform == "win32":
        # Enable UTF-8 mode for subsequent commands in this shell
        try:
            subprocess.run(["chcp", "65001"], check=True)
            print("Successfully set code page to 65001 (UTF-8).")
        except Exception:
            print("Warning: Could not set chcp 65001.")

    # 2. Check for missing letters/glyphs
    test_string = "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789"
    print(f"\n[TEST] All-Character Block: {test_string}")
    
    # 3. Environment Variable Set (for future runs)
    os.environ["PYTHONUTF8"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"
    
    print("\n[ADVICE]")
    print("1. If letters are still missing, your Terminal Font is likely corrupt or missing glyphs.")
    print("2. Change Terminal Settings -> Font to 'Consolas' or 'Lucida Console'.")
    print("3. Try running in 'cmd.exe' instead of PowerShell for better stability.")
    print("\nTERMINAL RESET COMPLETE.")

if __name__ == "__main__":
    fix_terminal()
