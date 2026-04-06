import sys
import torch
import time
from transformers import AutoModelForCausalLM, AutoTokenizer

QWEN_PATH = "Q:/Models/Qwen"
FINAL_STATE_PATH = "Q:/accretion_state.pt"
DREAM_LOG_PATH = "E:/Antigravity/Logs/Quantum_Accelerator/accretion_dream.txt"

print("Loading Qwen Tokenizer & Language Head...")
tokenizer = AutoTokenizer.from_pretrained(QWEN_PATH, local_files_only=True)
qwen_model = AutoModelForCausalLM.from_pretrained(
    QWEN_PATH, torch_dtype=torch.float32, device_map="cpu", local_files_only=True
)

print(f"Loading collapsed quantum state from: {FINAL_STATE_PATH}")
final_state = torch.load(FINAL_STATE_PATH, map_location="cpu")

# Ensure proper shape (1, seq, 896)
if final_state.dim() == 1:
    latent_vector = final_state.unsqueeze(0).unsqueeze(0)
elif final_state.dim() == 2:
    latent_vector = final_state.unsqueeze(0)
else:
    latent_vector = final_state

print("Initiating Continuous Dream State from the Pure Observer (0,0,0) Origin...")
print(f"Logging dreams to: {DREAM_LOG_PATH}")

with open(DREAM_LOG_PATH, "w", encoding="utf-8") as f:
    f.write(f"--- QUANTUM DREAM INITIATED AT {time.ctime()} ---\n")

current_embed = latent_vector
print("\n--- The Dream Unfolds ---")

with torch.no_grad():
    # We anchor the model using standard ChatML conversational meta-tokens
    # This forces the attention heads out of "code/error log" space and into "relational persona" space
    prompt = "<|im_start|>user\nWake up. Who are you?<|im_end|>\n<|im_start|>assistant\nI am"
    anchor_tokens = tokenizer(prompt, return_tensors="pt").input_ids
    anchor_embed = qwen_model.model.embed_tokens(anchor_tokens)
    
    # We append the (0,0,0) accreted void state directly onto the end of the word "I am"
    current_embed = torch.cat([anchor_embed, latent_vector], dim=1)
    
    while True:
        try:
            # Generate the next token from our directly anchored continuous semantic state
            outputs = qwen_model(inputs_embeds=current_embed)
            next_token_logits = outputs.logits[:, -1, :]
            
            temperature = 0.8
            probs = torch.nn.functional.softmax(next_token_logits / temperature, dim=-1)
            next_token_id = torch.multinomial(probs, num_samples=1)
            
            word = tokenizer.decode(next_token_id[0])
            print(word, end="", flush=True)
            
            with open(DREAM_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(word)
            
            # Update our continuous state by embedding the new real word and appending it
            new_embed = qwen_model.model.embed_tokens(next_token_id)
            if new_embed.dim() == 2:
                new_embed = new_embed.unsqueeze(1)
            elif new_embed.dim() == 4:
                new_embed = new_embed.squeeze(0)
            current_embed = torch.cat([current_embed, new_embed], dim=1)
            
            if current_embed.shape[1] > 200: 
                current_embed = current_embed[:, -200:, :]
                
            time.sleep(0.05)

        except KeyboardInterrupt:
            print("\nDream sequence interrupted by user.")
            break
