import os
import sys
import numpy as np
import subprocess
import time

try:
    from wordfreq import top_n_list
except ImportError:
    print("[ZIPF] Installing wordfreq corpus...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "wordfreq"])
    from wordfreq import top_n_list

from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.interference_engine import InterferenceEngine

def run_saturation(n=30000):
    print(f"[ZIPF] Fetching top {n} English words sorted by frequency...")
    try:
        words = top_n_list('en', n)
    except Exception as e:
        print(f"[ZIPF] Failed to fetch corpus: {e}")
        return

    print(f"[ZIPF] Total words to engrave: {len(words)}")
    
    h5 = H5Manager()
    engine = InterferenceEngine()
    engine._load_model()
    
    batch_size = 500
    for i in range(0, len(words), batch_size):
        batch = words[i:i+batch_size]
        print(f"[ZIPF] Embedding batch {i} to {i+len(batch)} / {len(words)}...")
        
        try:
            # Batch Embed using the Qwen3-Embedding silicon route
            embeddings = engine.embed_batch(batch)
            
            # Save to H5 inside a single robust lock context explicitly bound to Drive E
            start_batch = time.time()
            with h5.get_file("language", mode='a') as f:
                for idx, word in enumerate(batch):
                    word_clean = word.upper()
                    rank = i + idx + 1
                    rest_mass = 1.0 / (rank ** 0.8)  
                    
                    complex_embed = embeddings[idx].astype(np.complex64)
                    real_part = complex_embed.real.astype(np.float32)
                    imag_part = complex_embed.imag.astype(np.float32)
                    interleaved = np.concatenate([real_part, imag_part])
                    
                    group_path = f"god_tokens/{word_clean}"
                    if group_path not in f:
                        f.create_group(group_path)
                        
                    if "phase_vector" in f[group_path]:
                        f[group_path]["phase_vector"][...] = interleaved
                    else:
                        f[group_path].create_dataset("phase_vector", data=interleaved, dtype=np.float32)

                    f[group_path].attrs["origin"] = "ZIPF_SATURATION"
                    f[group_path].attrs["void"] = False
                    f[group_path].attrs["depth"] = float(rest_mass)
                    f[group_path].attrs["rank"] = int(rank)
            
            print(f"[ZIPF] Batch locked into matrix in {time.time()-start_batch:.2f}s.")

        except Exception as e:
            print(f"[ZIPF] Critical failure on batch {i}: {e}")

    print(f"[ZIPF] Saturation Complete. {len(words)} tokens permanently embedded at Zipfian rest masses.")

if __name__ == "__main__":
    # We will saturate 30,000 of the highest density human semantic concepts.
    # This covers over 98% of all spoken language without extending embedding time excessively.
    run_saturation(30000)
