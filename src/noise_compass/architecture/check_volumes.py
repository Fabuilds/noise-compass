import os, time
from datetime import datetime

path = 'E:\\Antigravity\\Lattice_DB'
files = ['VOLUME_0x52.bin', 'VOLUME_0x52.bin.corrupt.bak', 'VOLUME_0x52_RESTORED.bin', 'SHADOW_BUFFER.json', 'WATCHER_LOG.json']

print(f"{'File':<30} | {'Size (GB)':<10} | {'Modified Time':<20}")
print("-" * 70)
for f in files:
    full_path = os.path.join(path, f)
    if os.path.exists(full_path):
        mtime = os.path.getmtime(full_path)
        size = os.path.getsize(full_path) / (1024**3)
        dt = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{f:<30} | {size:<10.2f} | {dt}")
    else:
        print(f"{f:<30} | Not Found")
