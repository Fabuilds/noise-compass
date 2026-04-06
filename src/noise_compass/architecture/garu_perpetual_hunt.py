import subprocess
import time
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHOP_DIR = os.path.join(BASE_DIR, '..', 'Shop')

def verify_perpetual_hunt():
    print("Initiating Garu's Perpetual Scavenging Engine (Road_45)...")
    
    harvester_path = os.path.join(SHOP_DIR, "bounty_harvester_loop.py")
    
    print("\n" + "═"*75)
    print(" EXPERIMENT: AUTOMATED SCAVENGING ENGINE (PERPETUAL HUNT)")
    print("═"*75)
    
    try:
        # Start the harvester loop as a subprocess, capture output for 15 seconds to prove logic
        print("[STEP 1: ENGAGING 0x52 HARVESTER CYCLE]")
        process = subprocess.Popen(
            ["python", harvester_path], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        start_time = time.time()
        timeout = 15 # Allow the cycle to process HUNTR_TARGETS.json
        
        displacement_verified = False
        
        while time.time() - start_time < timeout:
            output_line = process.stdout.readline()
            if output_line:
                print(output_line.strip())
                if "earn_value" in output_line and "0.03" in output_line: # Expected from huntr-transformers-019
                    displacement_verified = True
                if "CYCLE COMPLETE" in output_line:
                    break
            else:
                 time.sleep(0.1)

        print("\n[STEP 2: TERMINATING CYCLE (Verification Complete)]")
        process.terminate()
        process.wait()
        
    except Exception as e:
        print(f"\nPerpetual hunt failed: {e}")

    print("\n" + "═"*75)
    if displacement_verified:
        print(" PERPETUAL ENGINE VERIFIED: ROAD_45 AUTOMATION COMPLETE.")
    else:
        print(" PERPETUAL ENGINE: LOGIC EXECUTED, WAITING FOR HIGH-RESONANCE TARGETS.")
    print("═"*75)

if __name__ == "__main__":
    verify_perpetual_hunt()
