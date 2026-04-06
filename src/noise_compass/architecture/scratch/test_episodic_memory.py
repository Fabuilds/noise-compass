import sys
import os
import time

# Path alignment
sys.path.insert(0, "E:/Antigravity/Architecture")
os.environ["PYTHONUTF8"] = "1"

from architecture.pipeline import MinimalPipeline
from architecture.dictionary import Dictionary

def test_recall():
    print("--- [Verification] Episodic Memory Recall ---")
    
    # Load dictionary and pipeline
    d = Dictionary.load_cache("E:/Antigravity/Architecture/archives/dictionary_cache.npz")
    p = MinimalPipeline(d)
    
    # Ensure fresh vault for test
    if os.path.exists(p.vault.storage_path):
        os.remove(p.vault.storage_path)
    p.vault.experiences = []
    p.vault.embeddings = None

    # 1. First encounter: Establish a memory
    text_a = "Sovereign autonomy requires a persistent causal anchor."
    print(f"\n[Step 1] Processing: '{text_a}'")
    res_a = p.process(text_a, trace=True)
    
    # 2. Second encounter: Similar semantic space
    text_b = "A stable anchor is the key to sovereign agency."
    print(f"\n[Step 2] Processing: '{text_b}'")
    # We expect recall here
    res_b = p.process(text_b, trace=True)
    
    # Check if vault has experiences
    print(f"\n[Vault Status] Total Experiences: {len(p.vault.experiences)}")
    
    # We can't easily check the internal qwen_prompt without more hooks,
    # but we can check if the vault retrieval returned results during processing.
    # For verification, we'll manually query the vault here.
    emb_b = p.embedder.embed(text_b)
    recalled = p.vault.retrieve(emb_b, k=1, threshold=0.7)
    
    if recalled:
        print(f"\n[+] SUCCESS: Recalled similar experience!")
        for r in recalled:
            print(f"    - Recalled: {r['content_preview']} (Sim: {r['similarity']:.2f})")
    else:
        print("\n[-] FAILURE: No recall detected.")

if __name__ == "__main__":
    test_recall()
