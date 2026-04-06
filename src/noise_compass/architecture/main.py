"""
main.py — Main REPL entry point for the Antigravity Architecture.
Provides interactive control over the DualBrainSystem with structural memory.

Usage:
    python main.py
"""

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

from noise_compass.system.dual_cortex import DualBrainSystem, Query, BrainType

def print_banner():
    print("\n" + "="*70)
    print("  ANTIGRAVITY DUAL-CORTEX REPL")
    print("  F(x) = known(x) + i·Δ(x)")
    print("="*70 + "\n")

async def main():
    print_banner()
    print("   [BOOT]: Initializing Dual Brain System...")
    
    # Check if we should use mock Qwen for testing if no environment key is found
    mock_qwen = False
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("GEMINI_API_KEY"):
        # We don't have a check for specific bridges here, so we'll assume standard init
        # unless user environment is missing keys for typical big-brain bridges.
        pass

    system = DualBrainSystem()
    print(f"   [BOOT]: System ready. Energy: {system.energy:.2f} | Fat: {system.fat:.2f}")
    print("   Type your query below. Commands: !save, !stats, !memo, !plan <file>, !exit\n")

    while True:
        try:
            user_input = input(">> ").strip()
            if not user_input:
                continue

            if user_input.lower() == "!exit":
                print("   [SHUTDOWN]: Saving state...")
                system.save_state()
                break

            if user_input.lower() == "!save":
                system.save_state()
                continue

            if user_input.lower() == "!stats":
                print(f"\n   [STATS]:")
                print(f"   Energy:       {system.energy:.3f}")
                print(f"   Fat/Reserves: {system.fat:.3f}")
                print(f"   Temperature:  {system.temperature:.3f}")
                print(f"   Total Queries: {system.stats['queries_total']}")
                print(f"   Brain Usage:  Small={system.stats['small_brain_used']} | Big={system.stats['big_brain_used']}")
                print(f"   Escalations:  {system.stats['escalations']}\n")
                continue

            if user_input.lower() == "!memo":
                if len(system.archiver) == 0:
                    print("   [MEMORY]: Archive is empty.")
                else:
                    print(f"\n   [RECENT MEMORIES] ({len(system.archiver)} total):")
                    # Show last 5 records
                    for i, record in enumerate(system.archiver._records[-5:]):
                        print(f"   · [{record.timestamp:.1f}] {record.content_preview[:60]}...")
                    print()
                continue

            if user_input.lower().startswith("!plan "):
                plan_file = user_input.split(" ", 1)[1]
                if os.path.exists(plan_file):
                    system.load_plan(plan_file)
                    print(f"   [PLAN]: Loaded {plan_file}. Execute steps via '!step'.")
                else:
                    print(f"   [ERROR]: Plan file not found: {plan_file}")
                continue

            if user_input.lower() == "!step":
                if system.plan:
                    await system.execute_plan_step()
                else:
                    print("   [PLAN]: No active plan. Load one with '!plan <file>'.")
                continue

            # Process standard query
            query = Query(
                text=user_input,
                timestamp=time.time(),
                context={},
                priority=1
            )

            print("   [THINKING]...", end="\r")
            response = await system.process(query)
            
            brain_name = "BitNet (1.58-bit)" if response.brain_used == BrainType.SMALL else "Qwen (Big Brain)"
            print(f"   [{brain_name}] ({response.confidence:.2f}):")
            print(f"   {response.text}\n")
            
            if response.escalation_reason:
                print(f"   [NOTE]: Escalated due to {response.escalation_reason}")

            # Update metabolism after process
            system.update_metabolism(1.0)

        except KeyboardInterrupt:
            print("\n   [SHUTDOWN]: Interrupted. Saving...")
            system.save_state()
            break
        except Exception as e:
            print(f"\n   [ERROR]: {e}")

if __name__ == "__main__":
    asyncio.run(main())
