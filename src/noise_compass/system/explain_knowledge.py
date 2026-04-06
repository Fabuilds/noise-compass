from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.qwen_bridge_resonant import QwenBridgeResonant
import sys

def explain_crystallized_concept(attractor="CAUSALITY"):
    h5 = H5Manager()
    qwen = QwenBridgeResonant()
    
    print(f"--- RESONANT EXPLANATION: {attractor} ---")
    
    # 1. Retrieve crystallized chunks
    chunks = h5.query_knowledge("kernel_language", attractor, top_k=3)
    
    if not chunks:
        print(f"No crystallized content found for {attractor}.")
        return

    context = "\n\n".join([f"Source Chunk {i}:\n{c['text']}" for i, c in enumerate(chunks)])
    
    # 2. Formulate Prompt
    prompt = f"""
I have retrieved the following 'Crystallized Knowledge' from our resonant manifold regarding {attractor}. 
Please explain the core semantic logic of this content as it relates to the Antigravity architecture.

CRYSTALLIZED CONTEXT:
{context}

EXPLANATION:
"""
    
    print(f"\n[now] Asking Qwen to interpret the resonance...")
    explanation = qwen.reason(prompt)
    
    print("\n--- QWEN'S INTERPRETATION ---")
    print(explanation)

if __name__ == "__main__":
    node = sys.argv[1] if len(sys.argv) > 1 else "CAUSALITY"
    explain_crystallized_concept(node)
