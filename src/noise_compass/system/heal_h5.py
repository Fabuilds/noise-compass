import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h5py
import numpy as np
from noise_compass.system.h5_manager import H5Manager

def heal_h5():
    path = "E:/Antigravity/knowledge_root/crystallized_h5/language.h5"
    if not os.path.exists(path):
        print("H5 file not found!")
        return

    print("Healing language.h5 from geometry explosions...")
    with h5py.File(path, 'a') as f:
        # Cap all numerical scalar attributes anywhere in the tree
        def cap_attrs(name, node):
            for key, val in node.attrs.items():
                if isinstance(val, (int, float, np.float32, np.float64)):
                    if abs(val) > 100.0:
                        capped = 100.0 if val > 0 else -100.0
                        node.attrs[key] = capped
                        print(f"Capped attribute {key} at /{name} from {val} to {capped}")

        f.visititems(cap_attrs)

        # Cap phase vectors
        if 'god_tokens' in f:
            for token in f['god_tokens'].keys():
                node = f[f'god_tokens/{token}']
                if 'phase_vector' in node:
                    vec = node['phase_vector'][()]
                    # Normalize vectors that have exploded
                    norm = np.linalg.norm(vec)
                    if norm > 100.0:
                        node['phase_vector'][...] = (vec / norm) * 10.0 # Normalize safely to 10
                        print(f"Normalized phase_vector at {token}")
                
                # Check for historical activations or tension values
                for attr_key in ['activation', 'magnitude', 'tension']:
                    if attr_key in node.attrs:
                        val = node.attrs[attr_key]
                        if abs(val) > 100.0:
                            node.attrs[attr_key] = 100.0 if val > 0 else -100.0
                            print(f"Capped {attr_key} in {token}")

        if 'gaps' in f:
            for gap in f['gaps'].keys():
                node = f[f'gaps/{gap}']
                for attr_key in ['tension', 'void_depth']:
                    if attr_key in node.attrs:
                        val = node.attrs[attr_key]
                        if abs(val) > 100.0:
                            node.attrs[attr_key] = 100.0 if val > 0 else -100.0
                            print(f"Capped {attr_key} in {gap}")

    print("Healing complete.")

if __name__ == "__main__":
    heal_h5()
