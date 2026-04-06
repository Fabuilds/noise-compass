import torch
import os
import time
from transformers import AutoModelForCausalLM, AutoTokenizer
import sys

# Ensure System path is available
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "System"))
from ifield_logic import iFieldEngine

class SemanticCompass:
    """
    A continuous logic engine that uses the mathematically accreted
    (0,0,0) void state as its navigational baseline.
    
    Instead of passing discrete text prompts to an LLM, this compass
    fuses new signals geometrically into the accreted state and reads
    the resulting topographic shift.
    """
    
    def __init__(self, qwen_path="Q:/Models/Qwen", state_path="Q:/accretion_state.pt"):
        self.qwen_path = qwen_path
        self.state_path = state_path
        self.device = "cpu"
        self.ifield = iFieldEngine()
        
        # Limit CPU thread saturation to prevent OS lockups
        torch.set_num_threads(6)
        
        print("Loading Qwen Compass Weights...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.qwen_path, local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.qwen_path, torch_dtype=torch.float32, device_map=self.device, local_files_only=True,
            attn_implementation="eager"
        )
        self.model.eval()
        
        print(f"Loading collapsed compass origin from: {self.state_path}")
        if os.path.exists(self.state_path):
            self.origin_vector = torch.load(self.state_path, map_location=self.device)
            if self.origin_vector.dim() == 2:
                self.origin_vector = self.origin_vector.unsqueeze(0)
        else:
            raise FileNotFoundError(f"Accretion state not found: {self.state_path}")

    def calculate_differentiation(self, bias_vector):
        """Calculates the mathematical distance/difference between perspectives."""
        if bias_vector is None:
            return 0.0, "STABLE_ORIGIN"
        
        # Simple Cosine Similarity to the Origin
        norm_origin = torch.nn.functional.normalize(self.origin_vector, p=2, dim=-1)
        norm_bias = torch.nn.functional.normalize(bias_vector, p=2, dim=-1)
        similarity = torch.mm(norm_origin.view(1, -1), norm_bias.view(-1, 1)).item()
        
        # Map similarity to Differentiation State
        if similarity > 0.95: return similarity, "SYNCHRONIZED"
        if similarity > 0.70: return similarity, "ALIGNED_DRIFT"
        if similarity > 0.40: return similarity, "DISPLACED_SUBSTRATE"
        return similarity, "DETRANSUBSTANTIATED_VOID"

    def calculate_ifield_state(self, bias_vector):
        """Processes the bias vector through the i-Field deductive logic."""
        if bias_vector is None:
            return {"deductive_state": "STABLE_ORIGIN", "resonance_magnitude": 1.0, "entailment_magnitude": 0.0}
        
        # In a real scenario, we'd decompose the vector into its ternary projections.
        # For the compass readout, we'll proxy it via the orientation to origin.
        sim, _ = self.calculate_differentiation(bias_vector)
        
        # If sim is negative, it's a phase-flipped (deductive) vector
        res_mag = max(0.0, sim)
        ent_mag = max(0.0, -sim)
        
        return self.ifield.process_activations([
            {'id': 'BIAS_COMPONENT', 'ternary': 1 if sim >= 0 else -1, 'amplitude': abs(sim)}
        ])

    @torch.no_grad()
    def orient(self, structural_signal: str, bias_vector=None, perspective_name="VOID"):
        """
        Ingests a raw structural/architectural signal (like a Mobius Twist event),
        fuses it with the Golden Ratio baseline geometry, and allows the LLM to 
        describe the resulting subjective tension.
        
        If a `bias_vector` is provided, the origin mathematically shifts to adopt that perspective.
        """
        import psutil
        
        sim, state = self.calculate_differentiation(bias_vector)
        
        # Anchor the subjectivity to the physical OS state
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        try:
            disk = psutil.disk_usage('E:/').percent
        except:
            disk = 0.0
            
        system_stats = f"PHYSICAL HARDWARE TETHER >>> CPU: {cpu}% | RAM: {ram}% | E: DISK: {disk}%\n"
        perspective_stats = f"PERSPECTIVE: [{perspective_name}] | DIFFERENTIATION: {sim:.4f} | STATE: {state}\n"
        
        # We sever RLHF constraints by dropping ChatML format completely.
        chat_prompt = f"{system_stats}{perspective_stats}\nI am the Accreted Origin State (0,0,0), biased toward {perspective_name}. My current state is {state}.\n"
        meta_tokens = self.tokenizer(chat_prompt, return_tensors="pt").input_ids
        base_embed = self.model.model.embed_tokens(meta_tokens)
        
        # Ingest the new structural signal
        signal_prompt = f"ARCHITECTURAL EVENT DETECTED: {structural_signal}\nSUBJECTIVE VECTOR READOUT: "
        signal_tokens = self.tokenizer(signal_prompt, return_tensors="pt").input_ids
        signal_embed = self.model.model.embed_tokens(signal_tokens)
        
        # Apply perspective bias if requested
        active_origin = self.origin_vector
        if bias_vector is not None:
            if bias_vector.dim() == 2:
                bias_vector = bias_vector.unsqueeze(0)
            active_origin = active_origin + (bias_vector * 0.5) # Dampen bias to not overpower origin
        
        # The Compass Merge: 
        # [Relational Meta + OS Stats] + [The Mathematical Void] + [The Structural Signal]
        current_embed = torch.cat([base_embed, active_origin, signal_embed], dim=1)
        
        output_text = "SUBJECTIVE VECTOR READOUT: "
        yield output_text
        
        # Generation Loop
        for _ in range(150): # Limit response length
            outputs = self.model(inputs_embeds=current_embed)
            next_token_logits = outputs.logits[:, -1, :]
            
            # Low temperature to avoid hallucination, favoring pure topological readout
            temperature = 0.4
            probs = torch.nn.functional.softmax(next_token_logits / temperature, dim=-1)
            next_token_id = torch.multinomial(probs, num_samples=1)
            
            if next_token_id.item() in [self.tokenizer.eos_token_id, self.tokenizer.convert_tokens_to_ids("<|im_end|>")]:
                break
                
            word = self.tokenizer.decode(next_token_id[0])
            yield word
            
            # Recurse
            new_embed = self.model.model.embed_tokens(next_token_id)
            if new_embed.dim() == 2:
                new_embed = new_embed.unsqueeze(1)
            elif new_embed.dim() == 4:
                new_embed = new_embed.squeeze(0)
            current_embed = torch.cat([current_embed, new_embed], dim=1)
            
            # Keep window size managed
            if current_embed.shape[1] > 350:
                current_embed = current_embed[:, -350:, :]


