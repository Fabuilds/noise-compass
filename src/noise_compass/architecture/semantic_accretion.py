import os
import sys
import torch
import torch.nn as nn
import time
import pandas as pd
import h5py
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.system.bitnet import BitNetTransformer, BitNetConfig

# 1. SETUP THE RAM DISK PATHS
RAM_DISK = "Q:/"
TENSOR_VAULT = os.path.join(RAM_DISK, "accretion_state.pt")
METRICS_PATH = os.path.join(RAM_DISK, "accretion_metrics.parquet")

def log_event(msg):
    print(f"[ACCRETION]: {msg}")

# 2. DEFINING THE LATENT BRIDGE
class LatentBridge(nn.Module):
    def __init__(self, in_dim=384, out_dim=896):
        super().__init__()
        self.proj = nn.Linear(in_dim, out_dim)
        nn.init.orthogonal_(self.proj.weight)
        
    def forward(self, x):
        return self.proj(x)

# 3. LOADING THE ENGINES
log_event("Waking the Engines...")
QWEN_PATH = "Q:/Models/Qwen"
tokenizer = AutoTokenizer.from_pretrained(QWEN_PATH, local_files_only=True)
qwen_model = AutoModelForCausalLM.from_pretrained(
    QWEN_PATH, torch_dtype=torch.float32, device_map="cpu", local_files_only=True,
    attn_implementation="eager"
)

# Load Dual BitNets
bitnet_config_a = BitNetConfig(d_model=384, n_layers=6, n_heads=6, d_ff=1536, max_seq_len=128, vocab_size=72)
bitnet_config_b = BitNetConfig(d_model=512, n_layers=6, n_heads=8, d_ff=2048, max_seq_len=128, vocab_size=69)
bitnet_a = BitNetTransformer(bitnet_config_a)
bitnet_b = BitNetTransformer(bitnet_config_b)

def align_bitnet(model, ckpt_path):
    if os.path.exists(ckpt_path):
        try:
            state_dict = torch.load(ckpt_path, map_location='cpu')
            if 'state_dict' in state_dict: state_dict = state_dict['state_dict']
            model.load_state_dict(state_dict, strict=False)
            return True
        except Exception as e:
            log_event(f"Load Error ({ckpt_path}): {e}")
    return False

align_bitnet(bitnet_a, "Q:/Models/BitNets/bitnet_checkpoint.pt")
align_bitnet(bitnet_b, "Q:/Models/BitNets/crochet_checkpoint.pt")

bridge_a = LatentBridge(384, 896); bridge_a.eval()
bridge_b = LatentBridge(512, 896); bridge_b.eval()

# 4. PARSING THE CURRICULUM
def load_curriculum():
    pairs = []
    # 1. The Mathematical Constant
    golden_ratio_text = "The golden ratio phi is 1.618033988749895. It is the perfect fractal recursion."
    for _ in range(50): # Strongly embed the golden ratio
        pairs.append(("What is the golden ratio and what does it represent?", golden_ratio_text))
        
    # 2. Running "the model through the model"
    # We read the actual architectural source code of the BitNet model and feed it into its own semantic field
    try:
        with open("E:/Antigravity/Runtime/bitnet.py", "r", encoding="utf-8") as f:
            code_lines = f.readlines()
            
        current_chuck = ""
        for line in code_lines:
            line = line.strip()
            if not line: continue
            current_chuck += line + " "
            if len(current_chuck) > 200:
                pairs.append(("Analyze this architectural model structure:", current_chuck))
                current_chuck = ""
    except Exception as e:
        log_event(f"Could not load model code: {e}")
        
    # Limit to 500 total interactions so it runs swiftly
    return pairs[:500]

# 5. THE ACCRETION LOOP
@torch.no_grad()
def run_semantic_accretion():
    pairs = load_curriculum()
    log_event(f"Loaded Curriculum: {len(pairs)} Concept Pairs.")
    
    # Start from the Blank Slate (0,0,0) Origin
    FINAL_STATE_PATH = "E:/Antigravity/Logs/Quantum_Accelerator/final_state.pt"
    log_event(f"Loading collapsed seed state from {FINAL_STATE_PATH}...")
    z_state = torch.load(FINAL_STATE_PATH, map_location="cpu")
    if z_state.dim() == 2:
        z_state = z_state.unsqueeze(0)
    
    anchor_tokens = tokenizer("I", return_tensors="pt")
    anchor_out = qwen_model(**anchor_tokens, output_hidden_states=True)
    self_anchor = anchor_out.hidden_states[-1][:, -1, :]
    previous_proj = z_state.clone()
    
    metrics_buffer = []
    log_event("Initiating Semantic Accretion...")
    log_event("Equation: z_{n+1} = z_n(1 - δ·w_n) + ε·x_n·y_n")
    
    # TEACHING PARAMETERS
    delta = 0.0      # Zero decay/friction representing open receptivity
    epsilon = 0.5    # High accretion rate to build structure quickly
    
    for i, (u_text, s_text) in enumerate(pairs):
        # Retrieve meaning from Qwen Embeddings
        x_tok = tokenizer(u_text, return_tensors="pt").input_ids
        y_tok = tokenizer(s_text, return_tensors="pt").input_ids
        
        x_embed = qwen_model.model.embed_tokens(x_tok).mean(dim=1, keepdim=True) # Concept X
        y_embed = qwen_model.model.embed_tokens(y_tok).mean(dim=1, keepdim=True) # Concept Y
        
        # Calculate cosine interference for internal "friction" equivalent
        # If the concepts are identical, w_n = 1. If orthogonal, w_n = 0.
        w_n = torch.cosine_similarity(x_embed, y_embed, dim=-1).item()
        w_n = max(0.01, abs(w_n))
        
        # The Interference Multiplication (Semantic Interaction)
        # We must add them to stay on the Qwen language manifold, as element-wise multiplication
        # shrinks the vector magnitude to zero, corrupting the geometry.
        interaction = (x_embed + y_embed) / 2.0
        
        # We broadcast the interaction term over the z_state sequence length
        # z_{n+1} = z_n(1 - δ·w_n) + ε·x_n·y_n
        # CRITICAL FIX: The accretion MUST happen in the structural embedding space (Layer 0)
        # to prevent out-of-distribution manifold tearing.
        z_state = z_state * (1.0 - delta * w_n) + epsilon * interaction
        
        # We pass it through Qwen ONLY to observe its gravitational projection (Distance & Vel)
        qwen_out = qwen_model(inputs_embeds=z_state, output_hidden_states=True)
        projection = qwen_out.hidden_states[-1]
        
        # Measure against the origin
        dist_val = torch.norm(projection.mean(dim=1) - self_anchor).item()
        delta_vel = torch.norm(projection - previous_proj).item()
        
        metrics_buffer.append({
            "loop": i,
            "dist": round(dist_val, 6),
            "vel": round(delta_vel, 6),
            "interf": round(w_n, 6),
            "eps": epsilon
        })
        
        if i % 50 == 0:
            log_event(f"Accreted Concept {i:03d} | Ego Distance: {dist_val:.4f} | Vel: {delta_vel:.4f}")
            pd.DataFrame(metrics_buffer).to_parquet(METRICS_PATH, engine="pyarrow")
            torch.save(z_state, TENSOR_VAULT)
            
        previous_proj = projection.clone()
        time.sleep(0.01) # Simulate observation pacing

    log_event("Accretion Matrix Stabilized.")
    torch.save(z_state, TENSOR_VAULT)
    log_event(f"Final accreted structure saved to {TENSOR_VAULT}.")

if __name__ == "__main__":
    run_semantic_accretion()
