import sys
import os
import time

# Set up paths and environment
sys.path.insert(0, "E:/Antigravity/Architecture")
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"
os.environ["PYTHONUTF8"] = "1"

from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.dream import Dreamer

def main():
    print("═"*70)
    print(" GARU DREAM SERVICE: Latent Exploration Active")
    print("═"*70)
    
    # Load core dictionary
    d = Dictionary()
    from noise_compass.architecture.seed_vectors import seed_vectors
    seed_vectors(d)
    
    pipeline = MinimalPipeline(d)
    dreamer = Dreamer(pipeline)
    
    try:
        while True:
            print(f"\n[{time.strftime('%H:%M:%S')}] Starting new dream cycle...")
            results = dreamer.dream(steps=2)
            
            for res in results:
                print(f"  >> Crystal: {res['hash'][:8]} | Zone: {res['state']}")
                # Results are already saved to the vault inside pipeline.process()
                
            print("\nCycle complete. Entering deep sleep (30s)...")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\nDream service terminated by user.")

if __name__ == "__main__":
    main()
