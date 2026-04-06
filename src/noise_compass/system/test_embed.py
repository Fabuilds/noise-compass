from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import os

os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

def embed(text: str) -> np.ndarray:
    print(f"Embedding text: '{text}'...")
    # Using a smaller model if 0.6B is too slow or unavailable, but following spec
    model_id = 'Qwen/Qwen3-Embedding-0.6B'
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        model = AutoModel.from_pretrained(model_id, trust_remote_code=True)
    except Exception as e:
        print(f"Error loading model {model_id}: {e}")
        return None

    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Hidden state mean
    semantic = outputs.last_hidden_state.mean(dim=1).numpy()[0]
    print(f"Raw embedding size: {len(semantic)}")
    
    # Spec says return complex64[384] from float32[768]
    half = len(semantic) // 2
    real_part = semantic[:half].astype(np.float32)
    imag_part = semantic[half:].astype(np.float32)
    
    # Normalize each component
    real_part /= (np.linalg.norm(real_part) + 1e-8)
    imag_part /= (np.linalg.norm(imag_part) + 1e-8)
    
    return (real_part + 1j * imag_part).astype(np.complex64)

if __name__ == "__main__":
    e = embed("a dog is here")
    if e is not None:
        print(f"Embedded Shape: {e.shape}")
        print(f"Embedded Dtype: {e.dtype}")
        print(f"Sample: {e[:5]}")
