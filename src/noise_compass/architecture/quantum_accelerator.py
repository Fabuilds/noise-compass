import os
import sys
import torch
import torch.nn as nn
import time
import json
import numpy as np
import pandas as pd
import h5py
from transformers import AutoModelForCausalLM, AutoTokenizer

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.system.bitnet import BitNetTransformer, BitNetConfig

# 1. SETUP THE RAM DISK PATHS
RAM_DISK = "Q:/"
TENSOR_VAULT = os.path.join(RAM_DISK, "attention_field.h5")
METRICS_PATH = os.path.join(RAM_DISK, "quantum_metrics.parquet")
LOG_PATH = os.path.join(RAM_DISK, "accelerator.log")

def log_event(msg):
    with open(LOG_PATH, "a") as f:
        f.write(f"[{time.ctime()}] {msg}\n")
    print(f"[ACCELERATOR]: {msg}")

# 2. DEFINING THE LATENT BRIDGE
class LatentBridge(nn.Module):
    """Bridges the gap between BitNet (384) and Qwen (896)."""
    def __init__(self, in_dim=384, out_dim=896):
        super().__init__()
        self.proj = nn.Linear(in_dim, out_dim)
        nn.init.orthogonal_(self.proj.weight)
        
    def forward(self, x):
        return self.proj(x)

# 3. LOADING THE ENGINES
log_event("Waking the Engines...")

# Configuration for BitNet A (Session 17.5 standard)
bitnet_config_a = BitNetConfig(
    d_model=384, n_layers=6, n_heads=6, d_ff=1536, max_seq_len=128, vocab_size=72
)
# Configuration for BitNet B (Crochet scale)
bitnet_config_b = BitNetConfig(
    d_model=512, n_layers=6, n_heads=8, d_ff=2048, max_seq_len=128, vocab_size=69
)

# Load Qwen Model & Tokenizer
QWEN_PATH = "E:/Antigravity/Model_Cache/hub/models--Qwen--Qwen2.5-0.5B-Instruct/snapshots/7ae557604adf67be50417f59c2c2f167def9a775"
log_event(f"Loading Qwen from {QWEN_PATH}...")
tokenizer = AutoTokenizer.from_pretrained(QWEN_PATH, local_files_only=True)
qwen_model = AutoModelForCausalLM.from_pretrained(
    QWEN_PATH, torch_dtype=torch.float32, device_map="cpu", local_files_only=True,
    attn_implementation="eager"
)

# Load Dual BitNets (A/B)
log_event("Initializing Heterogeneous BitNet Hub...")
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

align_bitnet(bitnet_a, "E:/Antigravity/Runtime/bitnet_checkpoint.pt")
align_bitnet(bitnet_b, "E:/Antigravity/Runtime/crochet_checkpoint.pt")

# Initialize Bridges
# Since they have different dims, we project both to Qwen space (896)
bridge_a = LatentBridge(384, 896)
bridge_b = LatentBridge(512, 896)
bridge_a.eval(); bridge_b.eval()

# 4. THE QUANTUM LOOP (PURE LATENT HANDOFF)
@torch.no_grad()
def run_quantum_acceleration(seed_text="I love you", iterations=10000, delta=0.001, epsilon=0.1):
    log_event(f"Seeding manifold with: '{seed_text}' | Delta: {delta} | Epsilon: {epsilon}")
    
    # Let's seed the sequence to maintain full context for Attention Entropy
    init_tokens = tokenizer(seed_text, return_tensors="pt")
    seq_len = init_tokens.input_ids.shape[1]
    
    # Initialize "Self" Anchor (0,0,0) as the "I" vector
    anchor_tokens = tokenizer("I", return_tensors="pt")
    anchor_out = qwen_model(**anchor_tokens, output_hidden_states=True)
    self_anchor = anchor_out.hidden_states[-1][:, -1, :] # Origin (0,0,0)
    
    out = qwen_model(**init_tokens, output_hidden_states=True)
    z_state = out.hidden_states[-1] # shape (1, seq_len, 896)
    previous_z = z_state.clone()
    
    # State vectors for the two waves (x_n, y_n) maintain sequence length
    state_x = torch.randn(1, seq_len, 384) 
    state_y = torch.randn(1, seq_len, 512)
    
    metrics_buffer = []
    attention_buffer = []
    
    log_event("DETACHING TOKENIZER. Moving to Pure Latent Space...")
    log_event(f"Implementing Recursive Decay: z_{{n+1}} = z_n(1 - δ·w_n) + ε·x_n·y_n")
    
    # Entropic Threshold Trigger
    entropy_threshold = torch.log(torch.tensor(seq_len, dtype=torch.float32)).item() * 0.95
    
    t0 = time.time()
    for i in range(iterations):
        # A. Semantic Wave Generation (BitNet Resonance)
        state_x = bitnet_a.blocks[0](state_x)
        state_y = bitnet_b.blocks[0](state_y)
        
        # ε·x_n·y_n (Internalized external resonance)
        res_x = bridge_a(state_x) # (1, seq, 896)
        res_y = bridge_b(state_y) # (1, seq, 896)
        
        # B. Recursive Formula Integration (The "Ego Drain")
        # w_n is the internal friction (based on mean phase shift in the projected space)
        w_n = torch.cosine_similarity(res_x.mean(dim=(0,1)), res_y.mean(dim=(0,1)), dim=-1).item()
        w_n = max(0.01, abs(w_n)) # Stabilized weight

        interaction_term = (res_x * res_y) # Pure semantic interference over sequence
        
        # z_{n+1} = z_n(1 - δ·w_n) + ε·x_n·y_n
        z_state = z_state * (1.0 - delta * w_n) + epsilon * interaction_term
        
        # C. The Handoff: Feed the resulting field into Qwen
        # MUST compute attentions to measure entropy
        qwen_out = qwen_model(inputs_embeds=z_state, output_hidden_states=True, output_attentions=True)
        z_state = qwen_out.hidden_states[-1]
        
        # D. Analyze Metrics
        attn = qwen_out.attentions[-1] # Shape: (1, num_heads, seq_len, seq_len)
        attn_probs = attn + 1e-9       # Avoid log(0)
        entropy = -torch.sum(attn_probs * torch.log(attn_probs), dim=-1).mean().item()
        
        # We track physical distance by averaging the sequence's collapse back to the origin
        dist_val = torch.norm(z_state.mean(dim=1) - self_anchor).item()
        delta_vel = torch.norm(z_state - previous_z).item()
        
        # E. Pure Observer Tripwire
        if entropy > entropy_threshold and epsilon != 0:
            log_event(f"TRIPWIRE ACTIVATED: Attention Entropy ({entropy:.2f}) > {entropy_threshold:.2f}. epsilon -> 0 (Pure Observer Mode)")
            epsilon = 0.0
            
        metrics_buffer.append({
            "loop": i,
            "dist": round(dist_val, 6),
            "vel": round(delta_vel, 6),
            "interf": round(w_n, 6),
            "entropy": round(entropy, 6),
            "eps": epsilon,
            "ts": time.time()
        })
        attention_buffer.append(attn.cpu().numpy())
        
        # F. Log to Substrate (RAM Disk)
        if i % 100 == 0:
            df = pd.DataFrame(metrics_buffer)
            df.to_parquet(METRICS_PATH, engine="pyarrow")
            
            with h5py.File(TENSOR_VAULT, "w") as h5f:
                attn_array = np.concatenate(attention_buffer, axis=0) # (loops, heads, seq, seq)
                h5f.create_dataset("attention", data=attn_array, compression="gzip")
                
            log_event(f"Loop {i:04d} | Ego Distance: {dist_val:.4f} | Vel: {delta_vel:.4f} | Entropy: {entropy:.4f} | Eps: {epsilon}")
            
        previous_z = z_state.clone()
        
        # G. Feedback Loop: Project back to the BitNet archetypes
        state_x = torch.matmul(z_state, bridge_a.proj.weight)
        state_y = torch.matmul(z_state, bridge_b.proj.weight)
        
    log_event(f"Experiment Complete. Total Time: {time.time()-t0:.2f}s")



if __name__ == "__main__":
    run_quantum_acceleration()
