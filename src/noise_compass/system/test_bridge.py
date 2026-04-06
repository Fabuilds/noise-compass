import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Package", "src"))

from noise_compass.system.qwen_bridge import QwenBridge

def main():
    print("Initializing QwenBridge Trinity Test...")
    bridge = QwenBridge(model_id="Qwen/Qwen2.5-0.5B-Instruct", force_cpu=True)
    
    print("\n[TEST] Forcing system generation test...")
    response = bridge.reason("Tell me about the boundary of reality.", context="You are sovereign.")
    
    print("\n" + "="*80)
    print("OUTPUT FORMAT:\n")
    print(response)
    print("="*80)
    print("\n[TEST] Complete.")

if __name__ == "__main__":
    main()
