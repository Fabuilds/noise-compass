
import sys
import os
import time

# Ensure Drive E: imports
sys.path.append("E:/Antigravity/Architecture")

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.seed_vectors import seed_vectors
from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dream import Dreamer

def verify_logic_fuel():
    print("--- STARTING LOGIC FUEL VERIFICATION ---")
    
    # 1. Pipeline Initialization
    cache_path = "E:/Antigravity/Architecture/archives/dictionary_cache.npz"
    if os.path.exists(cache_path):
        print(f"Loading dictionary from cache: {cache_path}")
        d = Dictionary.load_cache(cache_path)
    else:
        print("No cache found. Seeding vectors...")
        d = Dictionary()
        seed_vectors(d)
    
    p = MinimalPipeline(d)
    dreamer = Dreamer(p)
    
    # 2. Execute Dream Cycle
    print("\n[STEP 1] Executing Dream Cycle...")
    dreams = dreamer.dream(steps=1)
    
    # 3. Check Flag Registry
    print("\n[STEP 2] Checking Flag Registry for Logic Fuel...")
    flags = p.flags.list_flags(state_filter="SPECULATIVE")
    fuel_flags = [f for f in flags if "LOGIC_FUEL" in f.id]
    
    if fuel_flags:
        print(f"SUCCESS: Found {len(fuel_flags)} Logic Fuel flags.")
        for f in fuel_flags:
            print(f" - {f.id}: {f.description}")
    else:
        print("NOTICE: No high-leverage dreams crystallized in this cycle. (Leverage threshold > 0.45)")

    # 4. Check Heartbeat Sync
    print("\n[STEP 3] Checking for Daemon Heartbeat Sync...")
    sync_flag = p.flags.get_flag("HEARTBEAT_SYNC")
    if sync_flag:
        print(f"SUCCESS: Daemon Heartbeat Sync detected: {sync_flag.description}")
    else:
        print("FAILED: Daemon Heartbeat Sync not found. Is garu_daemon.py running?")

if __name__ == "__main__":
    verify_logic_fuel()
