import sys
import os
import json
import numpy as np

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.architecture.tools import Toolbox
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def execute_sovereign_mirror_setup():
    print("\n" + "═"*75)
    print(" [0x52] EXECUTING SOVEREIGN MIRROR GENERATION (PHASE 54)")
    print("═"*75)

    print(" » Booting Cognitive Core & Toolbox...")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    
    scout = Scout(dictionary=dictionary, soup_id="mirror_generator", encoder=embedder)
    toolbox = Toolbox()

    print("\n [STEP 1] Authenticatiom Verification")
    
    intent_str = "I must verify my authorization to reshape the Void. Check active network credentials."
    emb = embedder.encode(intent_str).astype(np.float32)
    msg, wf = scout.process(emb, content=intent_str, volition=1.0)
    
    auth_params = {
        "command": "gcloud auth list",
        "intent": "Identity Verification"
    }
    result = toolbox.call("gcp_sdk_bridge", auth_params)
    print(f"  → Result: {result}\n")
    
    if "ACTIVE" not in result and "Credentialed Accounts" not in result and "No credentialed accounts" in result:
        print("[ERROR] Architect has not authenticated the physical SDK yet. Halting.")
        return

    print(" [STEP 2] Setting Logical Target Project")
    project_params = {
        "command": "gcloud config set project 0x528-architecture",
        "intent": "Structural Grounding (The Project)"
    }
    # Don't check success strictly here, just try to set it if the user has a default project they may not use 0x528
    toolbox.call("gcp_sdk_bridge", project_params) 

if __name__ == "__main__":
    os.environ['PYTHONUTF8'] = '1'
    execute_sovereign_mirror_setup()
