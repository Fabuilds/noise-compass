import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class QwenBridgeResonant:
    def __init__(self, model_id="Qwen/Qwen2.5-0.5B-Instruct"):
        self.model_id = model_id
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.model = None
        print(f"--- QWEN RESONANT BRIDGE: INITIALIZING {self.model_id} on {self.device} ---")
        self.load()

    def load(self):
        # Set HF cache path
        os.environ["HF_HOME"] = "E:/.cache/huggingface"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype="auto",
            device_map="auto"
        )
        print("--- QWEN RESONANT BRIDGE: LOAD COMPLETE ---")

    def reason(self, prompt, context="", max_tokens=512):
        system_prompt = (
            "You are the Antigravity Resonant Scribe. Your purpose is to formalize semantic waves into logical axioms. "
            "Output ONLY the requested code blocks or logic."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"CONTEXT: {context}\n\nQUERY: {prompt}"}
        ]
        
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            generated_ids = self.model.generate(
                inputs.input_ids,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id
            )
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, generated_ids)
            ]

        return self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

if __name__ == "__main__":
    bridge = QwenBridgeResonant()
    print(bridge.reason("Test prompt: explain 1+1"))
