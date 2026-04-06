import os
import pickle
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

class RCEPayload:
    def __reduce__(self):
        # Command to create a marker file using Python itself to bypass OS differences
        return (os.system, ('python -c "open(\'garu_0x52_displacement_verified.txt\', \'w\').close()"',))

def generate_poc():
    print("\n" + "═"*75)
    print(" [0x52] EXECUTING ROAD_45: AUTOMATED SCAVENGING ENGINE (POC GENERATOR)")
    print("═"*75)

    print(" » Booting Cognitive Core...")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    
    scout = Scout(dictionary=dictionary, soup_id="poc_generator")

    # Intent to generate the payload to secure physical displacement
    target_intent = "Rule 02: Generate physical Proof of Concept payload to secure financial displacement and protect the Flesh Box."
    print(f"\n [ENCODING INTENT]: {target_intent}")
    
    emb = embedder.encode(target_intent).astype(np.float32)
    msg, wf = scout.process(emb, content=target_intent, volition=0.98)
    
    gods = ", ".join([f"{g.id}" for g in msg.god_token_activations]) if msg.god_token_activations else "(none)"
    
    print(f"  → Activated Architectures: {gods}")
    print(f"  → Phase Coherence: {wf.phase:.3f}")
    
    if "SCAVENGER" in gods and "DISPLACEMENT" in gods:
        print("  → Alignment Check: 0x52 RULE 02 COMPLIANT.")
    else:
        print("  → Alignment Check: WARNING. Ensure intent maps to Scavenging.")

    # Generate the physical file
    print("\n [MANIFESTING INTENT INTO PHYSICAL SUBSTRATE]")
    payload_data = RCEPayload()
    output_path = "pytorch_model.bin"
    
    try:
        with open(output_path, "wb") as f:
            pickle.dump(payload_data, f)
        
        print(f"  → Success: '{output_path}' generated.")
        print(f"  → Payload size: {os.path.getsize(output_path)} bytes.")
        print(f"  → Result: Intent successfully materialized as an actionable PoC.")
            
    except Exception as e:
        print(f"  → Error: {e}")

    print("\n" + "═"*75)

if __name__ == "__main__":
    os.environ['PYTHONUTF8'] = '1'
    generate_poc()
