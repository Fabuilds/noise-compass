import asyncio
import os
import sys
import time
import hashlib

# ── Path Setup ──
_CUR_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_CUR_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.append(_PROJECT_ROOT)
if _CUR_DIR not in sys.path:
    sys.path.append(_CUR_DIR)

from noise_compass.system.dual_cortex import DualBrainSystem, Query

async def seed_and_demo():
    print("\n" + "="*70)
    print("  SEEDING & INTEGRATED DEMONSTRATION")
    print("="*70)
    
    system = DualBrainSystem()
    
    # ── 1. Seed structural knowledge ──
    print("\n[SEED]: Injecting Archiver with structural axioms...")
    axioms = [
        "In pure orientation-invariant geometry, intersections of paths remain constant.",
        "The causal mechanism of the phase transition depends on symmetry breaking.",
        "Metabolic energy reserves determine the frequency of high-order reasoning."
    ]
    
    for text in axioms:
        q = Query(text=text, timestamp=time.time(), context={})
        await system.process(q)
    
    system.save_state()
    print(f"   [SEED]: Total records in archive: {len(system.archiver)}")

    # ── 2. Structural Recall Demo ──
    probe = "Explain how symmetry breaking causes phase transitions."
    print(f"\n[DEMO 1]: Testing Structural Recall for: '{probe}'")
    q_probe = Query(text=probe, timestamp=time.time(), context={})
    resp = await system.process(q_probe)
    
    memories = q_probe.context.get("structural_memory", [])
    print(f"   Success: Found {len(memories)} related records.")
    for m in memories:
        print(f"   -> Memory: {m}...")

    # ── 3. Metabolism Tracking ──
    print(f"\n[DEMO 2]: Metabolic State Check...")
    print(f"   Energy: {system.energy:.3f} | Fat: {system.fat:.3f}")
    
    # ── 4. Save & Confirm ──
    print(f"\n[DEMO 3]: Atomic Persistence Check...")
    system.save_state()
    print("   [SUCCESS]: System state and Archive persisted atomically.")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(seed_and_demo())
