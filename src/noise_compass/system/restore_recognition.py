import h5py
import numpy as np
import os

h5_path = "E:/Antigravity/knowledge_root/crystallized_h5/history.h5"

def restore_file(group, key, dest_path):
    with h5py.File(h5_path, 'r') as f:
        if group in f and key in f[group]:
            dataset = f[group][key]
            content = dataset[()]
            if isinstance(content, np.void):
                content = content.tobytes()
            elif hasattr(content, 'tobytes'):
                 content = content.tobytes()
            elif isinstance(content, str):
                content = content.encode('utf-8')
                
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, 'wb') as dest:
                dest.write(content)
            print(f"Restored: {group}/{key} -> {dest_path}")
        else:
            print(f"Error: {group}/{key} not found in {h5_path}")

if __name__ == "__main__":
    restore_file("scripts", "qwen_bridge.py", "e:/Antigravity/Runtime/qwen_bridge.py")
    restore_file("scripts", "self_recognition.py", "e:/Antigravity/Runtime/self_recognition.py")
