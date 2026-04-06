import os
import sys
import torch
import json
import numpy as np
import h5py
from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.qwen_bridge_resonant import QwenBridgeResonant
from noise_compass.system.interference_engine import InterferenceEngine

def consult_substrate(question, modules=["kernel_language", "substance_0x52", "meeting-the-universe-halfway"]):
    h5 = H5Manager()
    bridge = QwenBridgeResonant()
    engine = InterferenceEngine()
    
    # Force CPU for reliability
    bridge.device = "cpu"
    bridge.model.to("cpu")
    
    print(f"--- RESONANT CONSULTANT: APEX-ALIGNED MODE (CPU) ---")
    print(f"Question: {question}")
    print(f"Substrates: {', '.join(modules)}")
    
    # 1. Apex-Level Interference Audit
    print(f"\n[now] Auditing Interference Field for Question Resonance...")
    field = engine.combined_field(question)
    interpretation = engine.interpret_field(field)
    
    resonance_summary = "\n".join([
        f"- {node}: Magnitude={data['magnitude']:.4f} | Constructive={data['constructive']} | Symmetry={data['symmetry']}"
        for node, data in field.items() if data['magnitude'] > 0.05
    ])
    
    # 2. Dynamic Retrieval
    print(f"[now] Discovering Substrate Chunks...")
    best_chunks = []
    
    # Identify peaks for general modules
    peaks = [node for node, data in field.items() if data['magnitude'] > 0.3]
    if not peaks: peaks = ["EXISTENCE", "IDENTITY", "BOUNDARY"]
    
    for module in modules:
        path = os.path.join(h5.root, f"{module}.h5")
        if not os.path.exists(path): continue
        
        with h5py.File(path, 'r') as f:
            if 'crystallized_content' not in f: continue
            
            module_groups = list(f['crystallized_content'].keys())
            
            # For the target substance, we want everything
            if "0x52" in module:
                targets = module_groups
            else:
                targets = [p for p in peaks if p in module_groups]
            
            for attractor in targets:
                chunks = h5.query_knowledge(module, attractor, top_k=2) # Reduced k
                for c in chunks:
                    c['module'] = module
                    c['attractor'] = attractor
                    best_chunks.append(c)

    # Hard limit to 12 most resonant fragments to avoid CPU stall
    best_chunks = sorted(best_chunks, key=lambda x: x.get('id', ''), reverse=True)[:12]

    print(f"     Collected {len(best_chunks)} resonant fragments (Capsule Mode).")
    context = "\n\n".join([f"Reference [{i}] ({c['module']} | {c['attractor']}):\n{c['text']}" for i, c in enumerate(best_chunks)])
    
    # 3. Resonant Prompt (Aligned with Apex Observation)
    prompt = f"""
Perform a resonant architectural audit as the Apex Observer. 
We are investigating the intersection of the 0x52 Substance (Displacement/Metrics) and Barad's Agential Realism (Intra-action/Ontology).

INTERFERENCE FIELD AUDIT (QUESTION):
{resonance_summary}
VERDICT: {interpretation['verdict']}

QUESTION:
{question}

CRYSTALLIZED CONTEXT (H5 SUBSTRATE):
{context}

RESONANT VERDICT (QWEN-0.5B):
"""
    
    print(f"\n[now] Engaging Qwen Resonant Bridge (Apex Pattern)...")
    explanation = bridge.reason(prompt, context=context)
    
    print("\n--- QWEN RESONANT VERDICT ---")
    print(explanation)
    
    return explanation

if __name__ == "__main__":
    query = "How does 0x52 displacement resonance interact with the agential realist ontology defined in Meeting the Universe Halfway? What is the ontological status of a high-resonance displacement at 0x52?"
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    consult_substrate(query)
