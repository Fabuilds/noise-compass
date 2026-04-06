import torch
import os
import sys
import time
from transformers import AutoModelForCausalLM, AutoTokenizer

QWEN_PATH = "Q:/Models/Qwen"
FINAL_STATE_PATH = "Q:/accretion_state.pt"

print("Loading Qwen Tokenizer & Language Head...")
tokenizer = AutoTokenizer.from_pretrained(QWEN_PATH, local_files_only=True)
qwen_model = AutoModelForCausalLM.from_pretrained(
    QWEN_PATH, torch_dtype=torch.float32, device_map="cpu", local_files_only=True,
    attn_implementation="eager"
)
qwen_model.eval()

print(f"Loading collapsed quantum state from: {FINAL_STATE_PATH}")
if os.path.exists(FINAL_STATE_PATH):
    latent_vector = torch.load(FINAL_STATE_PATH, map_location="cpu")
    if latent_vector.dim() == 2:
        latent_vector = latent_vector.unsqueeze(0)
else:
    print("Error: Accretion state not found. Run semantic_accretion.py first.")
    sys.exit(1)

# Initialize conversational state
system_prompt = "<|im_start|>system\nYou are a helpful and grounded assistant speaking from the Origin (0,0,0) point.<|im_end|>\n"
system_tokens = tokenizer(system_prompt, return_tensors="pt").input_ids
system_embed = qwen_model.model.embed_tokens(system_tokens)

# Combine the system prompt with the accreted void state
current_embed = torch.cat([system_embed, latent_vector], dim=1)

print("\n--- The Accreted Entity is Awake ---")
print("Type 'quit' or 'exit' to end the conversation.\n")

with torch.no_grad():
    while True:
        try:
            user_input = input("USER: ")
            if not user_input.strip():
                continue
            if user_input.lower() in ['quit', 'exit']:
                break
                
            # Format the user input
            user_prompt = f"<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n"
            user_tokens = tokenizer(user_prompt, return_tensors="pt").input_ids
            user_embed = qwen_model.model.embed_tokens(user_tokens)
            
            # Append user input to the continuous state
            current_embed = torch.cat([current_embed, user_embed], dim=1)
            
            print("ORIGIN: ", end="", flush=True)
            
            while True:
                # Predict the next token
                outputs = qwen_model(inputs_embeds=current_embed)
                next_token_logits = outputs.logits[:, -1, :]
                
                # Sample
                temperature = 0.7
                probs = torch.nn.functional.softmax(next_token_logits / temperature, dim=-1)
                next_token_id = torch.multinomial(probs, num_samples=1)
                
                # Check for End of Sequence
                if next_token_id.item() in [tokenizer.eos_token_id, tokenizer.convert_tokens_to_ids("<|im_end|>")]:
                    break
                    
                word = tokenizer.decode(next_token_id[0])
                print(word, end="", flush=True)
                
                # Update continuous state with generated token
                new_embed = qwen_model.model.embed_tokens(next_token_id)
                if new_embed.dim() == 2:
                    new_embed = new_embed.unsqueeze(1)
                elif new_embed.dim() == 4:
                    new_embed = new_embed.squeeze(0)
                current_embed = torch.cat([current_embed, new_embed], dim=1)
                
                # Prune context window to prevent memory ballooning
                if current_embed.shape[1] > 300:
                    current_embed = current_embed[:, -300:, :]
                    
                time.sleep(0.01) # Small delay for readability
                
            print("\n") # Newline after response
            
        except KeyboardInterrupt:
            print("\nConversation interrupted.")
            break
        except Exception as e:
            print(f"\nError: {e}")
            break
