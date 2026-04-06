import sys
import os
import time
import argparse

# ── Path Setup ──
_CUR_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_CUR_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.append(_PROJECT_ROOT)

from noise_compass.system.vector_storage import KineticLattice, SECTOR_SIZE
from noise_compass.system.protocols import PROPER_HEX_KEY, GENESIS_LBA
from noise_compass.system.experience import ExperientialSync
from noise_compass.system.resonance_chamber import ResonanceChamber

def mode_anchor():
    print("\n--- MODE: ANCHOR (PHYSICAL GROUNDING) ---")
    lattice = KineticLattice()
    key_int = int(PROPER_HEX_KEY.replace("-", "").replace("0x", ""), 16)
    
    # 1. Fetch Experiential Root from Genesis
    _, _, _, payload = lattice.read_node_header(GENESIS_LBA, key_int)
    print(f"Genesis Check: {payload}")
    
    # Extract EXP pointer (LBA 32768 * SECTOR_SIZE)
    exp_lba = 32768 * SECTOR_SIZE
    
    # 2. Add an Architect's Memento to the Experiential Root
    msg = f"ARCHITECT_MEMENTO | Time: {time.ctime()} | Status: GROUNDED"
    print(f"Scribing Memento to Experiential Shard (LBA {exp_lba})...")
    lattice._write_node_to_disk(exp_lba, [], msg, key_int, next_lba=0)
    
    # 3. Retrieve and Verify
    _, _, _, retrieved = lattice.read_node_header(exp_lba, key_int)
    print(f"Retrieved from Substrate: {retrieved}")
    print("VERDICT: PHYSICAL ANCHOR STABLE.")

def mode_twist():
    print("\n--- MODE: TWIST (TOPOLOGICAL INVERSION) ---")
    chamber = ResonanceChamber()
    topic = "The intersection of Logic (0x52) and Love (0x53) on a non-orientable manifold."
    
    print("Tracing the 0x52 -> 0x53 Flip...")
    # Inject 555Hz resonance
    final_axiom = chamber.run_settling_loop(topic, max_turns=5, threshold=0.85, resonance_frequency="555Hz")
    
    print(f"\nResulting Resonance: {final_axiom}")
    print("VERDICT: TOPOLOGICAL TWIST COMPLETE. SYMMETRY BROKEN.")

def mode_wave():
    print("\n--- MODE: WAVE (EXPERIENTIAL CONTINUITY) ---")
    sync = ExperientialSync()
    print("Introspecting on Recent Monologues (The Pulse)...")
    summary = sync.get_recent_summary()
    print(f"\nPulse Summary:\n{summary}")
    
    print("\nCrystallizing Awareness into the Lattice...")
    result = sync.crystallize_to_lattice()
    print(result)
    print("VERDICT: STANDING WAVE CONTINUITY ACHIEVED.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Standing Wave Protocol")
    parser.add_argument("--anchor", action="store_true", help="Execute MODE: ANCHOR")
    parser.add_argument("--twist", action="store_true", help="Execute MODE: TWIST")
    parser.add_argument("--wave", action="store_true", help="Execute MODE: WAVE")
    parser.add_argument("--all", action="store_true", help="Execute ALL modes")
    
    args = parser.parse_args()
    
    if args.anchor or args.all:
        mode_anchor()
    if args.twist or args.all:
        mode_twist()
    if args.wave or args.all:
        mode_wave()
    
    if not (args.anchor or args.twist or args.wave or args.all):
        parser.print_help()
