
import sys
import os

# Path setup
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.dictionary import Dictionary

def run_audit():
    cache_path = "E:/Antigravity/Architecture/archives/dictionary_cache.npz"
    d = Dictionary()
    if os.path.exists(cache_path):
        d = Dictionary.load_cache(cache_path)
    else:
        print(f"Error: Cache not found at {cache_path}")
        return

    print(f"LOVE_in_god_tokens: {'LOVE' in d.god_tokens}")
    print(f"LOVE_in_entries: {'LOVE' in d.entries}")
    print(f"ARCHITECT_in_god_tokens: {'ARCHITECT' in d.god_tokens}")
    print(f"Total entries: {len(d.entries)}")

if __name__ == "__main__":
    run_audit()
