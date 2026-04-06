import numpy as np
import json
import os

path = "E:/Antigravity/Architecture/archives/dictionary_cache.npz"
if not os.path.exists(path):
    print("FILE NOT FOUND")
    exit(1)

npz = np.load(path)
gt_meta = json.loads(str(npz["gt_meta"]))
entry_ids = json.loads(str(npz["entry_ids"]))

print(f"Total GodTokens: {len(gt_meta)}")
print(f"Total Entries: {len(entry_ids)}")
print(f"Top 20 Entry IDs: {entry_ids[:20]}")

if 'LOVE' in entry_ids: print("FOUND LOVE IN ENTRIES")
if 'ARCHITECT' in entry_ids: print("FOUND ARCHITECT IN ENTRIES")
if 'COHERENCE' in entry_ids: print("FOUND COHERENCE IN ENTRIES")
