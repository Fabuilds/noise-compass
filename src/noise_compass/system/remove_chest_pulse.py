
import os
import sys
import h5py
from pathlib import Path

# Add project roots
SRC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(SRC_ROOT)

from noise_compass.system.h5_manager import H5Manager

def remove_chest_pulse():
    print("[REMOVER] Initiating removal of CHEST_PULSE axiom...")
    h5 = H5Manager()
    
    # 1. Remove from identity.h5 (Axioms)
    with h5.get_file("identity", mode='a') as f:
        crystal_path = "axioms/CRYSTALLIZED/CHEST_PULSE"
        pending_path = "axioms/PENDING/CHEST_PULSE"
        accreted_path = "axioms/accreted/CHEST_PULSE"
        
        removed = False
        for path in [crystal_path, pending_path, accreted_path]:
            if path in f:
                del f[path]
                print(f"  [H5] Removed {path} from identity.h5")
                removed = True
    
    # 2. Remove from language.h5 (Semantic Manifold)
    with h5.get_file("language", mode='a') as f:
        semantic_path = f"semantic_manifold/CHEST_PULSE"
        god_token_path = f"god_tokens/CHEST_PULSE"
        
        for path in [semantic_path, god_token_path]:
            if path in f:
                del f[path]
                print(f"  [H5] Removed {path} from language.h5")
                removed = True
                
    if removed:
        print("[PROCESS] CHEST_PULSE axiom successfully purged from Substrate.")
    else:
        print("[WARNING] CHEST_PULSE not found in manifold.")

if __name__ == "__main__":
    remove_chest_pulse()
