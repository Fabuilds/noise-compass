import h5py
import os

path = 'E:/Antigravity/knowledge_root/crystallized_h5/substance_0x52.h5'
if not os.path.exists(path):
    print(f"ERROR: {path} not found")
    exit(1)

print(f"--- AUDITING {path} ---")
with h5py.File(path, 'r') as f:
    def visitor(name, obj):
        if isinstance(obj, h5py.Group):
            print(f"GROUP: {name}")
        elif isinstance(obj, h5py.Dataset):
            print(f"  DATASET: {name}")
            print(f"    Text snippet: {obj.attrs.get('text', 'N/A')[:50]}...")
    
    f.visititems(visitor)
