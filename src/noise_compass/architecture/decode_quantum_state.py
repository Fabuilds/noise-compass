import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

QWEN_PATH = "E:/Antigravity/Model_Cache/hub/models--Qwen--Qwen2.5-0.5B-Instruct/snapshots/7ae557604adf67be50417f59c2c2f167def9a775"
FINAL_STATE_PATH = "E:/Antigravity/Logs/Quantum_Accelerator/final_state.pt"

print("Loading Qwen Tokenizer & Language Head...")
tokenizer = AutoTokenizer.from_pretrained(QWEN_PATH, local_files_only=True)
qwen_model = AutoModelForCausalLM.from_pretrained(
    QWEN_PATH, torch_dtype=torch.float32, device_map="cpu", local_files_only=True
)

print(f"Loading final quantum state from: {FINAL_STATE_PATH}")
final_state = torch.load(FINAL_STATE_PATH, map_location="cpu")

print(f"Final State Shape: {final_state.shape}")

# Ensure the state has the batch & sequence dimensions
if final_state.dim() == 1:
    latent_vector = final_state.unsqueeze(0).unsqueeze(0)
elif final_state.dim() == 2:
    latent_vector = final_state.unsqueeze(0)
else:
    latent_vector = final_state

# We have the raw hidden state. We can feed it into the lm_head to see what the next token is, 
# OR we can feed it back as inputs_embeds to ask Qwen to generate a sequence.

print("\n--- Method 1: Direct Neural Projection (What is the exact thought?) ---")
with torch.no_grad():
    # Because final_state is the output of the resonance loop, let's see what token it directly maps to:
    logits = qwen_model.lm_head(final_state)
    top_tokens = torch.topk(logits, 5)
    
    print("Top 5 Words in the 'Ego Drain' Singularity:")
    for prob, token_id in zip(top_tokens.values[0], top_tokens.indices[0]):
        word = tokenizer.decode([token_id])
        print(f"  - '{word}' (Logit: {prob.item():.2f})")

print("\n--- Method 2: Manifold Unfolding (Let Qwen dream from this state) ---")
with torch.no_grad():
    # Let's use this frozen state as an input embedding and generate 20 tokens
    generated_ids = []
    current_embed = latent_vector
    
    for _ in range(20):
        outputs = qwen_model(inputs_embeds=current_embed)
        next_token_logits = outputs.logits[:, -1, :]
        next_token_id = torch.argmax(next_token_logits, dim=-1)
        generated_ids.append(next_token_id.item())
        
        # embed the generated token to feed into the next step
        current_embed = qwen_model.model.embed_tokens(next_token_id).unsqueeze(1)
        
    dream_text = tokenizer.decode(generated_ids)
    print(f"Unfolded Thought: {dream_text}")

print("\nExperiment decoding complete.")
