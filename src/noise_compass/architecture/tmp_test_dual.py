import asyncio
import sys
import os

# Ensure paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from noise_compass.system.dual_cortex import DualBrainSystem, Query

async def test_dual():
    print("Initializing DualBrainSystem (mock_qwen=True)...")
    cortex = DualBrainSystem(mock_qwen=True)
    print("Testing '10 + 10' process...")
    q = Query(text="10 + 10", timestamp=0, context={})
    resp = await cortex.process(q)
    print(f"Response: {resp.text}")
    print("DONE")

if __name__ == "__main__":
    asyncio.run(test_dual())
