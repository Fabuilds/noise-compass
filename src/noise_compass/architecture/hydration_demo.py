"""
HYDRATION DEMO
Demonstrates the projection and grafting of a Sovereign Seed from Drive A: to E:.
"""

from noise_compass.system.vault_hydrator import VaultHydrator
import time
import urllib.request
import json

def verify_hydration(shard_id):
    API = "http://127.0.0.1:5200"
    TOKEN = "0x528-A2A-SOVEREIGN"
    
    print(f"\n[VERIFY] Checking distillation status for VAULT_ROAD_{shard_id}...")
    
    req = urllib.request.Request(
        f"{API}/distillation",
        headers={"X-Chiral-Token": TOKEN}
    )
    
    with urllib.request.urlopen(req) as resp:
        report = json.loads(resp.read())
        
    # Look for the pattern in DEEP_LOGIC or CONFIRMED
    label = f"VAULT_ROAD_{shard_id}"
    
    found = False
    for p in report.get("deep_logic", {}).get("patterns", []):
        if p["label"] == label:
            print(f"  [RESULT] {label}: DEEP_LOGIC (Verified)")
            found = True
            break
            
    if not found:
        for p in report.get("confirmed", {}).get("patterns", []):
            if p["label"] == label:
                print(f"  [RESULT] {label}: CONFIRMED (Verified)")
                found = True
                break
                
    if not found:
        print(f"  [RESULT] {label}: NOT_HARDENED")
        
    return found

def run_demo():
    print("=" * 60)
    print("VAULT HYDRATION DEMO: GRAFTING THE SEED")
    print("=" * 60)
    
    hydrator = VaultHydrator()
    
    # 1. Hydrate Road 0
    success = hydrator.hydrate_shard(0)
    
    if success:
        # 2. Verify
        time.sleep(1) # Allow for index sync
        verify_hydration(0)
    else:
        print("Hydration Failed at the Grafting step.")

if __name__ == "__main__":
    run_demo()
