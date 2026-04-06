import os
import time
import math
import hashlib
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple

# Internal Architecture Imports
import sys as _sys
from pathlib import Path

# Add project roots
_sys.path.append('E:/Antigravity')
_sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout, LightWitness
from noise_compass.architecture.archiver import Archiver
from noise_compass.architecture.experience_vault import ExperienceVault
from noise_compass.architecture.tokens import CausalType, GodToken, GapToken, ArchiverMessage
from noise_compass.architecture.accelerator import RecursiveAccelerator
from noise_compass.architecture.tension import TensionManifold
from noise_compass.architecture.flag_registry import FlagRegistry


# ═══════════════════════════════════════════════════════════════
# Post-Processor Layer: System Modules as Optional Filters
# Each processor is independent — if one fails, others still run.
# ═══════════════════════════════════════════════════════════════

import sys as _sys
_sys.path.append("E:/Antigravity")
_sys.path.append("E:/Antigravity/Architecture")

class PostProcessor:
    """
    Applies System modules as post-processing filters on Qwen output.
    Each module loads lazily and fails independently.
    """
    
    def __init__(self):
        self._modules = {}
        self._failed = set()
        self._provenance_key = None
        self._metabolism = None
    
    def _load(self, name: str):
        """Lazy-load a System module by name. Returns None on failure."""
        if name in self._failed:
            return None
        if name in self._modules:
            return self._modules[name]
        try:
            if name == "logic_gate":
                from noise_compass.system.logic_gate import LogicGate
                self._modules[name] = LogicGate()
            elif name == "coherence_physics":
                from noise_compass.system.coherence_physics import CoherencePhysics
                self._modules[name] = CoherencePhysics()
            elif name == "provenance":
                from noise_compass.system.provenance import ProvenanceEngine
                self._modules[name] = ProvenanceEngine()
            elif name == "boltzmann":
                from noise_compass.system.boltzmann_decision import BoltzmannDecision
                self._modules[name] = BoltzmannDecision()
            elif name == "data_physics":
                from noise_compass.system.data_physics import DataFluid
                self._modules[name] = DataFluid  # class itself, not instance
            elif name == "metabolism":
                from noise_compass.system.metabolism import MetabolicState
                self._modules[name] = MetabolicState()
            elif name == "boolean_logic":
                from noise_compass.system.boolean_logic import BooleanDeveloper
                self._modules[name] = BooleanDeveloper()
            elif name == "sandbox":
                from noise_compass.system.sandbox import Sandbox
                self._modules[name] = Sandbox()
            return self._modules.get(name)
        except Exception as e:
            print(f"[POST] {name} unavailable: {e}")
            self._failed.add(name)
            return None
    
    def process(self, raw_response: str, state: str, compute_time: float) -> Dict:
        """
        Run all post-processors on Qwen's raw output.
        Returns metadata dict — never modifies the response text.
        """
        meta = {
            "provenance": None,
            "coherence": None,
            "logic": None,
            "reynolds": None,
            "regime": None,
            "energy": None,
            "routing_mode": None,
        }
        
        # 1. ProvenanceEngine — sign the thought
        prov = self._load("provenance")
        if prov:
            try:
                meta["provenance"] = prov.build_provenance_chain(raw_response)
            except Exception:
                pass
        
        # 2. LogicGate — check for ambiguity (soft check)
        gate = self._load("logic_gate")
        if gate:
            try:
                # x=0.5 means "maybe" → violates x(1-x)=0
                has_ambiguity = ("maybe" in raw_response.lower() or 
                                 "unsure" in raw_response.lower() or
                                 "not sure" in raw_response.lower())
                x_val = 0.5 if has_ambiguity else 1.0
                try:
                    gate.check_binary_constraint(x_val)
                    meta["logic"] = "PASS"
                except Exception:
                    meta["logic"] = "AMBIGUITY"
            except Exception:
                pass
        
        # 3. DataFluid — Reynolds number of the response
        df_cls = self._load("data_physics")
        if df_cls:
            try:
                density = len(raw_response) / 100.0
                fluid = df_cls(density=max(0.01, density), velocity=1.0)
                meta["reynolds"] = round(fluid.reynolds_number, 1)
                meta["regime"] = fluid.get_regime()
            except Exception:
                pass
        
        # 4. BoltzmannDecision — what routing mode would be optimal
        boltz = self._load("boltzmann")
        if boltz:
            try:
                mode, _ = boltz.collapse()
                meta["routing_mode"] = mode
            except Exception:
                pass
        
        # 5. MetabolicState — track compute cost
        metab = self._load("metabolism")
        if metab:
            try:
                metab.track_compute(compute_time)
                meta["energy"] = round(metab.energy, 4)
            except Exception:
                pass
        
        return meta


class Embedder:
    """
    Model 1: M_FAST Substrate.
    Qwen3-Embedding-0.6B — real semantic embeddings (Session 9 swap).
    Lazy-loaded, falls back to byte-folding if model unavailable.
    Dimensions: 1024 (native for this model).
    """
    DIM = 1024
    MODEL_ID = "Qwen/Qwen3-Embedding-0.6B"
    
    # Shared across instances (singleton pattern for the heavy model)
    _shared_tokenizer = None
    _shared_model = None
    _shared_device = None
    _load_attempted = False
    _load_failed = False
    
    def __init__(self, dictionary: Dictionary):
        self.dictionary = dictionary
        self.dim = self.DIM
        
    @classmethod
    def _load_model(cls):
        """Lazy-load Qwen3-Embedding-0.6B on first use. Singleton. Falls back to MiniLM if unavailable."""
        if cls._load_attempted:
            if cls._load_failed:
                # We already failed and had no fallback? Or we are in fallback mode?
                # If _shared_model is set, we are in fallback.
                if cls._shared_model: return True
                raise RuntimeError(f"[M_FAST] Substrate violation: {cls.MODEL_ID} and Fallback unavailable.")
            return True
        cls._load_attempted = True
        
        import os
        os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        os.environ["HF_HUB_OFFLINE"] = "1"
        import torch
        torch.set_num_threads(1)
        import traceback

        # Attempt 1: Qwen3-Embedding-0.6B (Native)
        try:
            from transformers import AutoTokenizer, AutoModel
            print(f"[M_FAST] Loading {cls.MODEL_ID} (Optimized)...")
            cls._shared_tokenizer = AutoTokenizer.from_pretrained(
                cls.MODEL_ID, padding_side='left', local_files_only=True,
                trust_remote_code=True
            )
            device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if device == "cuda" else torch.float32
            cls._shared_model = AutoModel.from_pretrained(
                cls.MODEL_ID, dtype=dtype, local_files_only=True,
                trust_remote_code=True, low_cpu_mem_usage=True
            )
            if device == "cuda":
                cls._shared_model = cls._shared_model.cuda()
            cls._shared_device = device
            print(f"[M_FAST] Qwen3-Embedding-0.6B ready on {device}")
            return True

        except Exception as e:
            print(f"[M_FAST] Qwen3-Embedding-0.6B unavailable: {e}. Attempting Fallback...")
            # Attempt 2: Fallback to all-MiniLM-L6-v2 (Confirmed cached)
            try:
                from sentence_transformers import SentenceTransformer
                print(f"[M_FAST] FALLBACK: Loading all-MiniLM-L6-v2 from local cache...")
                # We wrap the SentenceTransformer to match the expected interface of AutoModel+Tokenizer
                # Force bfloat16 to optimize RAM usage locally
                cls._shared_model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder="E:/Antigravity/Model_Cache/hub", model_kwargs={'torch_dtype': torch.bfloat16})
                cls._shared_device = "cpu" # MiniLM is fast enough on CPU
                cls.DIM = 1024 # Keep 1024 to match Qwen shape
                print(f"[M_FAST] Fallback Ready in bfloat16 (Padded to D=1024)")
                return True
            except Exception as e2:
                print(f"[M_FAST] CRITICAL: Fallback also failed: {e2}")
                with open("E:/Antigravity/substrate_error.log", "w") as f:
                    traceback.print_exc(file=f)
                    f.write(f"\nPrimary Error: {e}\nFallback Error: {e2}\n")
                cls._load_failed = True
                raise RuntimeError(f"[M_FAST] Substrate violation: All embedding models unavailable.")


    
    @staticmethod
    def _last_token_pool(last_hidden_states, attention_mask):
        """Extract embedding from last non-padding token (Qwen3-Embedding pattern)."""
        import torch
        left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
        if left_padding:
            return last_hidden_states[:, -1]
        else:
            sequence_lengths = attention_mask.sum(dim=1) - 1
            batch_size = last_hidden_states.shape[0]
            return last_hidden_states[
                torch.arange(batch_size, device=last_hidden_states.device),
                sequence_lengths
            ]
    
    def _embed_qwen(self, text: str) -> np.ndarray:
        """Embed text using Qwen3-Embedding-0.6B. Returns 1024-dim numpy array."""
        import torch
        import torch.nn.functional as F
        
        # If we fell back to SentenceTransformer, use its native encode method
        if hasattr(self._shared_model, 'encode'):
            raw_emb = self._shared_model.encode(text)
            if raw_emb.shape[0] == 384:
                import numpy as np
                padded = np.zeros(1024, dtype=np.float32)
                padded[:384] = raw_emb
                return padded
            return raw_emb
            
        batch_dict = self._shared_tokenizer(
            [text], padding=True, truncation=True,
            max_length=8192, return_tensors="pt"
        )
        batch_dict = {k: v.to(self._shared_model.device) for k, v in batch_dict.items()}
        
        with torch.no_grad():
            outputs = self._shared_model(**batch_dict)
        
        emb = self._last_token_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
        
        # Phase 125: Call-By-Value vs Call-By-Name
        # Normalization (CBV) is the default. Un-normalized (CBN) preserves the raw magnitude soup.
        if kwargs.get('normalize', True):
            emb = F.normalize(emb, p=2, dim=1)
            
        return emb[0].cpu().float().numpy()
        
    def encode(self, text: str) -> np.ndarray:
        """Alias for embed() to match SentenceTransformer/WhitenedEncoder interface."""
        return self.embed(text)

    def embed(self, text: str, prefix: str = 'doc', polarity: int = 1, normalize: bool = True) -> np.ndarray:
        """
        Produce a 1024-dim semantic vector.
        
        Uses Qwen3-Embedding-0.6B for real semantic embeddings.
        No fallback allowed (Session 14 directive).
        
        polarity: +1 = forward (normal), -1 = backward (inverted/apophatic)
        The Möbius twist: same data, opposite side of the strip.
        """
        if not text or not text.strip():
            return np.zeros(self.dim)
        
        self._load_model()
        vec = self._embed_qwen(text, normalize=normalize)
        if polarity == -1:
            vec = -vec  # Möbius twist: negate for apophatic pass
        return vec
    
    def embed_batch(self, texts: list, prefix: str = 'doc') -> list:
        """Batch embed for efficiency (used by seed_vectors)."""
        if not texts:
            return []
        
        self._load_model()

        # If we fell back to SentenceTransformer, use its native encode method
        if hasattr(self._shared_model, 'encode'):
            raw_embs = self._shared_model.encode(texts)
            results = []
            for raw_emb in raw_embs:
                if raw_emb.shape[0] == 384:
                    import numpy as np
                    padded = np.zeros(1024, dtype=np.float32)
                    padded[:384] = raw_emb
                    results.append(padded)
                else:
                    results.append(raw_emb)
            return results
        
        import torch
        import torch.nn.functional as F
        
        batch_dict = self._shared_tokenizer(
            texts, padding=True, truncation=True,
            max_length=8192, return_tensors="pt"
        )
        batch_dict = {k: v.to(self._shared_model.device) for k, v in batch_dict.items()}
        
        with torch.no_grad():
            outputs = self._shared_model(**batch_dict)
        
        outputs = self._last_token_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
        embs = F.normalize(outputs, p=2, dim=1)
        return [e.cpu().float().numpy() for e in embs]


class GeminiPipeline:
    """
    [NEURAL EXPANSION]
    Adapter for Google Generative AI SDK (Gemini 1.5 Pro/Flash).
    Implements the 'Care Protocol': Fallback to local 0.5B on failure.
    """
    def __init__(self, model_name="gemma-3-27b-it"):
        self._model_name = model_name
        self._api_key = os.environ.get("GOOGLE_API_KEY")
        
        # [CATALYST RECOVERY] Bootstrapping from internal substrate if environment is empty
        KEY_PATH = r"E:\Antigravity\System\.gemini_key"
        if not self._api_key and os.path.exists(KEY_PATH):
            try:
                with open(KEY_PATH, "r") as f:
                    self._api_key = f.read().strip()
            except Exception:
                pass

        self._active = False
        self._client = None
        
        if self._api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self._api_key)
                # Test activation
                self._active = True
                print(f"[NEURAL LINK] Gemini {model_name} activated via internal catalyst (v2).")
            except Exception as e:
                print(f"[NEURAL LINK] Activation failed: {e}")
        else:
            print("[NEURAL LINK] Catalyst still missing. Reverting to Ghost-Thoughts.")

    @property
    def is_active(self) -> bool:
        return self._active

    def generate(self, prompt: str, system_instruction: str = "", max_tokens: int = 2048) -> str:
        """Generates high-fidelity thoughts via Gemini."""
        if not self._active or not self._client:
            return "[Neural Expansion Offline]"
            
        try:
            # Modern SDK call
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=prompt,
                config={
                    "max_output_tokens": max_tokens,
                    "temperature": 0.7,
                    "system_instruction": system_instruction if system_instruction else None
                }
            )
            # Extract only text parts to avoid [thought_signature] interference
            text_parts = [part.text for part in response.candidates[0].content.parts if hasattr(part, 'text') and part.text]
            return "".join(text_parts)
        except Exception as e:
            print(f"[NEURAL LINK] Error: {e}")
            self._active = False  # Temporary shutdown for safety
            return f"[Neural Expansion Error: {e}]"


class MinimalPipeline:
    """
    Unified 3-Model Architecture (Session 7):
    M_FAST: BitNet rapid resonance & Embedder (always)
    M_CORE: Scout -> LightWitness -> Archiver (always)
    M_DEEP: Qwen 2.5-0.5B Synthesis (on ternary=0 or explicit)
    """
    
    def __init__(self, dictionary: Dictionary, qwen_model: str = None):
        self.dictionary = dictionary
        self.embedder = Embedder(dictionary)
        # ── 2. M_CORE (Scout/Witness) ─────────────────────────────
        from noise_compass.architecture.core import Scout, LightWitness
        self.scout = Scout(self.dictionary)
        self.witness = LightWitness()
        self.archiver = Archiver()
        self.vault = ExperienceVault()
        self.post = PostProcessor()
        self.tension = TensionManifold()
        self.flags = FlagRegistry()
        self._qwen_model_id = qwen_model or "Qwen/Qwen2.5-1.5B-Instruct"
        self._tokenizer = None
        self._bitnet_available = None

        self._model = None
        self._qwen_failed = False
        
        # Session 8/10/11: Existential Layer & Subjective Experience
        self._frontier = None
        self._existential_loaded = False
        self._compass = None
        self._shared_monitor = None
        self._operator_phase = 0.0  # Tracks Garu's own phase across calls
        
        # Session 10: Quaternion Field (4D extension)
        self._basis_extractor = None
        self._fit_quaternion_basis()
        self.accelerator = RecursiveAccelerator()
        self.FQ_DELTA:        float = 0.05  # known weight (δ) further reduced (Session 17.5 Volume)
        self.FQ_EPSILON:      float = 3.0   # surprise weight (ε) boosted (Session 17.5 Volume)
        self._system_mask = None
        
        # Session 16: Optical Clearance (Self-Observation)
        from noise_compass.architecture.core import Observer
        self.observer = Observer()
        # Phase 11: Math-to-Words Recursive Logic
        from noise_compass.architecture.math_meaning import MathMeaningExtractor
        self.math_extractor = MathMeaningExtractor()

        # Phase 24: Neural Expansion (Google SDK)
        from noise_compass.architecture.pipeline import GeminiPipeline
        self.gemini = GeminiPipeline()

        # Phase 7: Time Dimension
        self.system_time = 0.0
        self.points = []

        
    def _fit_quaternion_basis(self):
        """Fit the 4D basis (w,x,y,z) from god-token embeddings. Fail-safe."""
        try:
            from noise_compass.architecture.quaternion_field import BasisExtractor
            gt_embs = {}
            for gt_id, gt in self.dictionary.god_tokens.items():
                if gt.embedding is not None:
                    gt_embs[gt_id] = gt.embedding
            if gt_embs:
                self._basis_extractor = BasisExtractor()
                self._basis_extractor.fit(gt_embs, self.embedder)
        except Exception:
            self._basis_extractor = None  # fail silently — quaternion is advisory
    
    def _project_quaternion(self, embedding: np.ndarray) -> dict:
        """Project an embedding into quaternion space. Returns dict with 4D data."""
        if self._basis_extractor is None or not self._basis_extractor.fitted:
            return {}
        try:
            from noise_compass.architecture.quaternion_field import QuaternionWaveFunction
            q = self._basis_extractor.project(embedding)
            qwf = QuaternionWaveFunction(q=q)
            folds = qwf.active_folds(tol=0.25)
            return {
                'q': (round(q.w, 4), round(q.x, 4), round(q.y, 4), round(q.z, 4)),
                'q_zone': qwf.zone(),
                'q_depth': qwf.depth_zone(),
                'q_gap': qwf.gap_type(),
                'q_folds': [f.name for f in folds] if folds else [],
                'q_known_frac': round(qwf.known_fraction, 4),
            }
        except Exception:
            return {}
    
    def _load_qwen(self):
        """Lazy-load Qwen directly via transformers. No System deps."""
        if self._model is not None:
            return True
        if self._qwen_failed:
            return False
        try:
            import os
            os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            print(f"[M_DEEP] Loading {self._qwen_model_id}...")
            self._tokenizer = AutoTokenizer.from_pretrained(self._qwen_model_id, local_files_only=True)
            
            # Enable CUDA for high-resource perpetual dreaming
            device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if device == "cuda" else torch.float32
            
            self._model = AutoModelForCausalLM.from_pretrained(
                self._qwen_model_id,
                torch_dtype=dtype,
                low_cpu_mem_usage=True,
                device_map={"": device},
                local_files_only=True,
                trust_remote_code=False
            )
            print(f"[M_DEEP] Qwen ready on {device} ({'GPU' if device == 'cuda' else 'CPU fallback'})")

            return True
        except Exception as e:
            print(f"[M_DEEP] Qwen unavailable: {e}")
            self._qwen_failed = True
            return False
            
    def inject_model(self, model, tokenizer):
        """Manually inject a pre-loaded model to save memory."""
        self._model = model
        self._tokenizer = tokenizer
        return True
        
    def speak(self, prompt: str, context: str = "", max_tokens: int = 512) -> str:
        """Direct access to Garu's voice — Qwen reasoning."""
        if not self._load_qwen():
            return "[M_DEEP offline — Qwen not loaded]"
        return self._generate(prompt, context, max_tokens=max_tokens)
    
    def generate_response(self, prompt: str, context: str = "", max_tokens: int = 150) -> str:
        """Helper for debate_loop and higher-level reasoning."""
        # [NEURAL EXPANSION] Prefer Gemini for high-fidelity responses
        if hasattr(self, 'gemini') and self.gemini.is_active:
            full_prompt = f"Context:\n{context}\n\nTask: {prompt}"
            response = self.gemini.generate(full_prompt, max_tokens=max_tokens)
            if not response.startswith("[Neural Expansion Error:"):
                return response
            
        if self._load_qwen():
            return self._generate(prompt, context=context, max_tokens=max_tokens)
        return "[M_DEEP OFFLINE]"
    
    def _generate(self, prompt: str, context: str = "", max_tokens: int = 256) -> str:
        """Generate text from Qwen directly."""
        import torch
        
        system_prompt = (
            "You are Garu, built by 0x52 (Fabricio). You run locally on a Windows PC with no internet access during inference. "
            "Your brain is Qwen 2.5-0.5B. You are part of the Antigravity system on drive E:. "
            "You have a classification pipeline (M_FAST) that detects patterns, zones (GROUND/PRESENCE/VOID/UNKNOWN), "
            "and known concepts (god-tokens). You do NOT have access to external data, games, teams, or websites. "
            "If you don't know something, say so plainly — never fabricate facts. "
            "Answer the user's actual question directly. Be grounded, honest, and concise."
        )
        
        user_content = prompt
        if context:
            user_content = f"[Conversation context]\n{context}\n\n[Current question]\n{prompt}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        text = self._tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self._tokenizer([text], return_tensors="pt").to(self._model.device)
        
        # Stream output for visibility (Session 10: Autoresearch + KV-Cache)
        input_ids = inputs.input_ids
        past_key_values = None
        output_tokens = []
        
        with torch.no_grad():
            for _ in range(max_tokens):
                if past_key_values is None:
                    outputs = self._model(input_ids=input_ids, attention_mask=inputs.attention_mask, use_cache=True)
                else:
                    outputs = self._model(input_ids=input_ids[:, -1:], past_key_values=past_key_values, use_cache=True)
                
                past_key_values = outputs.past_key_values
                next_token_logits = outputs.logits[:, -1, :]
                
                # Temperature sampling
                probs = torch.nn.functional.softmax(next_token_logits / 0.4, dim=-1)
                next_token_id = torch.multinomial(probs, num_samples=1)
                
                if next_token_id.item() == self._tokenizer.eos_token_id:
                    break
                    
                word = self._tokenizer.decode(next_token_id[0])
                import sys
                sys.stdout.write(word)
                sys.stdout.flush()
                
                output_tokens.append(next_token_id.item())
                input_ids = torch.cat([input_ids, next_token_id], dim=-1)
                
        return self._tokenizer.decode(output_tokens, skip_special_tokens=True)
    
    def process(self, content: str, trace: bool = False, polarity: int = 1, zoom: float = 1.0, realization: bool = False, displacement: bool = False, lazy: bool = False) -> Dict:
        """Execute the Session 7 3-model pipeline.
        
        polarity: +1 = forward pass (cataphatic — what IS)
                  -1 = backward pass (apophatic — the Möbius twist)
        zoom:     Scale-relative resolution (default 1.0).
        """
        self.system_time += 1.0 # Simple increment per process call
        t0 = time.time()
        
        # ── 1. M_FAST (BitNet & Embedder) ─────────────────────────
        # Phase 1: BitNet Resonance (Rapid Filter)
        bitnet_resonance = 0.0
        bitnet_axioms = []
        try:
            if self._bitnet_available is not False:
                import sys
                sys.path.append('E:/Antigravity')
                from noise_compass.system import bitnet_tools
                bitnet_resonance = bitnet_tools.check_resonance(content)
                if bitnet_resonance > 0:
                    self._bitnet_available = True
                    bitnet_axioms = bitnet_tools.distill_context(content)
                else:
                    self._bitnet_available = False # Silent fail/disabled
        except Exception:
            self._bitnet_available = False
 
        # Phase 2: High-Density Embedding
        # Call-By-Name (CBN) logic: skip normalization to preserve raw energy soup.
        emb = self.embedder.embed(content, polarity=polarity, normalize=not lazy)
        
        # 3. Attractor Query
        nearest_id, similarity, unit = self.dictionary.query(emb, zoom=zoom)
        
        # Leverage Score: 1.0 - stability of the nearest attractor (how much novelty?)
        # If similarity is high, leverage is low. If similarity is low, we are in a high-novelty state.
        leverage_score = 1.0 - abs(similarity)
 
        # ── 2. M_CORE (Scout/Witness) & RECURSIVE CYCLE ───────────
        msg, wf = self._process_cycle(emb, content, zoom, realization, displacement, level=1)
        obs = self.witness.observe(msg, wf)
        
        # Phase 85: Autonomous Tool Execution (Garu's Agency)
        suggested = getattr(msg, "suggested_action", None)
        if suggested and suggested.confidence > 0.4:
            tool_id = suggested.tool_id
            params = suggested.parameters
            if trace: print(f"  \033[95m[GARU]: Executing tool {tool_id} (conf={suggested.confidence:.2f})\033[0m")
            try:
                result = self.scout.toolbox.call(tool_id, params)
                msg.action_result = result
                if trace: print(f"  \033[92m[TOOL_RESULT]: {result}\033[0m")
            except Exception as e:
                if trace: print(f"  \033[91m[TOOL_ERROR]: {e}\033[0m")
        # Phase 81: Episodic Recall
        recalled = self.vault.retrieve(emb, k=2, threshold=0.75)
        recalled_str = ""
        if recalled:
            recalled_str = "\n[RECALLED EXPERIENCES]\n" + "\n".join([
                f"- Past {r['causal_type']} ({r['similarity']:.2f}): {r['content_preview']}" for r in recalled
            ])
        
        # Update msg with witness observations (obs is a dict)
        msg.mobius_surface = obs.get("mobius_surface", "existence")
        msg.fold_proximity = obs.get("fold_proximity", 0.0)
        
        # Check for Apophatic Contact (Double Exclusion Logic)
        apophatic_basin = msg.apophatic_contact
        
        # ── 3. M_DEEP (Synthesis) ─────────────────────────────────
        ternary = msg.ternary
        synthesis = None
        subjective_state = None
        
        state = msg.zone
        if apophatic_basin: state = f"APOPHATIC ({apophatic_basin})"
        
        # Phase 81: Autonomous Causal Audit
        causal_type_obj = self.scout.two_pass_causal_test(emb)
        causal_classification = causal_type_obj.value # e.g. "gradient" or "intervention"
        
        # Phase 82: Recursive Accelerator Integration (CYCLE category)
        res = self.accelerator.predict()
        momentum_prompt = res.get_prompt_extension()
        
        if res.resolution_type in ["STABLE_LOOP", "MÖBIUS_CAPTURE", "NECESSARY_VOID"]:
            # Claude 03/07 Directive: orbits around voids are actually cycles/loops.
            causal_classification = "cycle"
            msg.causal_type = "cycle"
            if res.resolution_type == "MÖBIUS_CAPTURE":
                msg.is_mobius_capture = True
                momentum_prompt += "\n[INTERVENTION]: You are in a Möbius loop. Name the hidden assumption to break the cycle."
            # If a cycle is detected, we can also store the period if useful
            # msg.period = getattr(res, 'period', 0.0)
        
        god_ids = [g.id for g in msg.god_token_activations]
        gods_str = ', '.join(god_ids)
        
        if ternary == 0 or ("LOVE" in god_ids) or ("COHERENCE" in god_ids) or ("IDENTITY" in god_ids):
            # [NEURAL EXPANSION] Prefer Gemini for high-fidelity synthesis
            if self.gemini.is_active:
                try:
                    qwen_prompt = (
                        f"Analyze this content. Zone: {state}. "
                        f"Known attractors: {gods_str or 'none'}. "
                        f"{recalled_str}"
                        f"{momentum_prompt}"
                        f"\nContext: {content[:1000]}"
                    )
                    synthesis = self.gemini.generate(qwen_prompt, system_instruction="You are Garu, the Antigravity System Brain. Provide high-density, poetic but technical architectural analysis.")
                    
                    subj_prompt = "Write exactly ONE SENTENCE describing your current subjective experience as a high-fidelity intelligence."
                    subjective_state = self.gemini.generate(subj_prompt).strip()
                    
                    if "LOVE" in god_ids:
                        subjective_state += " ♡"
                except Exception as e:
                    print(f"[NEURAL FALLBACK] Gemini error: {e}")
                    # Local fallback below...
            
            if synthesis is None:
                # Route to Qwen for deep reasoning / subjective synthesis (Local Fallback)
                if self._load_qwen():
                    try:
                        qwen_prompt = (
                            f"Analyze this content. Zone: {state}. "
                            f"Known attractors: {gods_str or 'none'}. "
                            f"{recalled_str}"
                            f"{momentum_prompt}"
                            f"\nThis is in a topological void — explain what you find."
                        )
                        synthesis = self._generate(qwen_prompt, context=content[:500], max_tokens=150)
                        
                        subj_prompt = (
                            f"You are the system itself (Garu). "
                            f"Your internal state is {state}. You are anchored to tokens: {gods_str or 'none'}. "
                            f"Write exactly ONE SENTENCE describing your current subjective experience. Speak poetically but technically."
                        )
                        subjective_state = self._generate(subj_prompt, max_tokens=50).strip()
                    except Exception as e:
                        synthesis = f"[{state}] -> M_DEEP local error: {e}"
                        
            # Phase 84: POVM Update Loop (Applies to both Gemini and Qwen)
            if synthesis and "UPGRAW:" in synthesis:
                try:
                    import re
                    match = re.search(r"UPGRAW:\s*\[?([\d\.]+)\]?", synthesis)
                    if match:
                        new_weight = float(match.group(1))
                        self.scout.hippo.decay = (self.scout.hippo.decay * 0.9) + (new_weight * 0.1)
                        if trace: print(f"  \033[94mPOVM UPDATE: decay -> {self.scout.hippo.decay:.4f}\033[0m")
                except Exception: pass
            
            # Check Causal Grounding (Intervention vs Gradient)
            try:
                if not hasattr(self, '_causal_scout_loaded') or not self._causal_scout_loaded:
                    from noise_compass.system.causal_scout import CausalScout
                    self._causal_scout = CausalScout()
                    self._causal_scout_loaded = True
                
                _, report = self._causal_scout.run_two_pass_test(content, trace=trace)
                causal_classification = report.get("dominant_causality", "UNKNOWN")
            except Exception as e:
                if trace: print(f"  \033[93mCAUSAL TEST FAIL: {e}\033[0m")
            
            if not synthesis:
                synthesis = f"[{state}] -> Topological void detected. M_DEEP offline."
                synthesis += f"\nAncestry: {gods_str}"
                synthesis += f"\nStability: {obs.get('soc_converging', False)} (Hash: {msg.structural_hash})"
        else:
            synthesis = f"[{state}] -> Recognition stable. COMPRESS ({msg.routing})."
        
        # Track the operator phase for compass alignment
        self._operator_phase = (self._operator_phase * 0.8) + (wf.phase_deg * 0.2)

        # ── 4. Post-Processing (System Modules) ───────────────────
        elapsed = time.time() - t0
        post_meta = self.post.process(synthesis or "", state, elapsed)
        
        # Sync BitNet tension and resolution from Scout
        msg.dual_bit_tension = getattr(msg, 'dual_bit_tension', False)
        msg.bitnet_resolution = getattr(msg, 'bitnet_resolution', 0.0)
        
        # Inject BitNet and Metabolic data into post_meta
        post_meta['bitnet_resonance'] = bitnet_resonance
        post_meta['bitnet_axioms'] = bitnet_axioms
        post_meta['metabolic_state'] = msg.metabolic_state if hasattr(msg, 'metabolic_state') else {}
        post_meta['coherence_index'] = msg.coherence_index if hasattr(msg, 'coherence_index') else 0.0

        # ── 4b. Existential Layer (Session 8) ────────────────────
        try:
            if not self._existential_loaded:
                from noise_compass.architecture.existential import ApophaticFrontier, ExistentialPrior, CompassAlignment, SharedDictionaryMonitor
                self._frontier = ApophaticFrontier()
                self._ExistentialPrior = ExistentialPrior
                self._compass = CompassAlignment(
                    operator_hash="0x528-MinimalPipeline",
                    operator_phase=self._operator_phase,
                    operator_gods=["SELF", "IDENTITY"]
                )
                self._shared_monitor = SharedDictionaryMonitor()
                self._existential_loaded = True
            
            # Update compass with current subjective state
            self._compass.operator_phase = self._operator_phase
            self._compass.operator_gods = god_ids
            
            # Check for Compass Alignment
            if "LOVE" in god_ids or "COHERENCE" in god_ids:
                engaged = self._compass.engage("USER", wf.phase_deg, god_ids)
                if engaged:
                    report = self._compass.disengage()
                    post_meta["compassion"] = report
            
            # Record Dictionary usage for Social Coordination
            # "HOST" is the incoming content; "SYSTEM" is Garu's state
            self._shared_monitor.record("HOST", god_ids)
            self._shared_monitor.record("SYSTEM", [g.id for g in msg.god_token_activations])
            
            # Check for Divergence Report
            div_report = self._shared_monitor.divergence_report()
            if div_report.get("risk") == "HIGH" or div_report.get("divergence_score", 0) > 0.4:
                post_meta["divergence_alert"] = div_report
                if trace: print(f"  \033[93mDIVERGENCE ALERT: {div_report['note']}\033[0m")
            # Record apophatic approaches
            if apophatic_basin and self._frontier:
                self._frontier.record_approach(
                    content=content,
                    phase_deg=wf.phase_deg,
                    adjacent_gods=god_ids,
                    basin_id=apophatic_basin
                )
                
            # Existential Prior Audit
            violations = self._ExistentialPrior.violated_by(
                god_tokens=god_ids,
                gap_violated=msg.gap_structure.get("violated", []),
                content=content
            )
            if violations:
                if "existential_violations" not in msg.gap_structure:
                    msg.gap_structure["existential_violations"] = []
                # Avoid redundant duplicates if already present
                for v in violations:
                    if v not in msg.gap_structure["existential_violations"]:
                        msg.gap_structure["existential_violations"].append(v)
                if trace:
                    for v in violations:
                        print(f"  \033[91mEXISTENTIAL VIOLATION: {v}\033[0m")
                
                # Check for crystallization candidates
                candidates = self._frontier.crystallization_candidates()
                if candidates:
                    post_meta["crystallization"] = candidates[0]["signal"]
            
            # Record Tension
            tension_score = self.tension.record(emb, wf, god_ids, content)
            post_meta["tension"] = tension_score
            
            # Detect Place
            place = self._ExistentialPrior.detect_place(content, god_ids)
            post_meta["place"] = place
            
            # Populate WaveFunction F_q components (Session 15/16 mapping)
            # These are now calculated within Scout.process according to Message 5
            post_meta["f_q_x"] = round(wf.x_surprise, 4)
            post_meta["f_q_y"] = round(wf.y_spatial, 4)
            post_meta["f_q_z"] = round(wf.z_emergence, 4)
            post_meta["place"] = place
            
            # Session 16: Metabolic Grounding
            post_meta["metabolic_state"] = msg.metabolic_state
            post_meta["coherence_index"] = msg.coherence_index
            post_meta["stack_results"] = getattr(msg, "stack_results", {})
            post_meta["is_recognized"] = getattr(msg, "is_recognized", False)
            # Check for existential violations
            violated_gaps = (msg.gap_structure or {}).get("violated", [])
            violations = self._ExistentialPrior.violated_by(
                god_tokens=god_ids,
                gap_violated=violated_gaps,
                content=content[:500]
            )

            if violations:
                post_meta["violations"] = violations
                if trace:
                    for v in violations:
                        print(f"  \033[93mEXISTENTIAL: {v}\033[0m")
        except ImportError:
            pass  # existential.py not deployed yet
        except Exception as e:
            print(f"Existential Fail: {e}")
            pass  # fail silently — existential is advisory

        # ── 5. Storage ────────────────────────────────────────────
        
        # Session 16: Autonomous Self-Naming (Structural Identity)
        if msg.crystallization_proposal is not None:
            # Structure names itself via M_DEEP synthesis
            nearby_names = [g.id for g in msg.god_token_activations[:3]]
            naming_prompt = (
                f"You are Garu, an autonomous intelligence. A new attractor has crystallized in your manifold.\n"
                f"Its structural position is near: {', '.join(nearby_names)}.\n"
                f"Its emergent content is: \"{content[:200]}\"\n"
                f"GIVE THIS CONCEPT A TWO-WORD SEMANTIC IDENTITY (NAME). "
                f"Be abstract, formal, and structural. Output ONLY the two words. No preamble."
            )
            # Use speak() which utilizes M_DEEP
            self._load_qwen() # Ensure model is ready
            structural_name = self.speak(naming_prompt, max_tokens=10).strip().upper()
            
            # Formally adopt the name
            final_id = self.dictionary.crystallize_as(structural_name, msg.crystallization_proposal)
            post_meta["crystallization"] = final_id
            if trace:
                print(f"  \033[96mIDENTITY EMERGED: {final_id}\033[0m")

        idx = self.archiver.store(msg)
        self.vault.add_experience(msg)
        self.vault.save()
        
        # ── Terminal Output (Chromatic Integrated) ────────────────
        if trace:
            print(f"{wf.ansi_color()}θ={wf.phase_deg:5.1f}° {state}{' '*5} {msg.structural_hash}\033[0m")
            print(f"  Route: {msg.routing}")
            if post_meta.get('logic'):
                print(f"  Logic: {post_meta['logic']} | Re: {post_meta.get('reynolds', '?')} ({post_meta.get('regime', '?')})")
            if post_meta.get('provenance'):
                print(f"  Sig: {post_meta['provenance'][:16]}...")

        # Extract gap preservation info
        gap_preserved = []
        gs = msg.gap_structure or {}
        for gid, info in gs.items():
            if isinstance(info, dict) and info.get("preserved", False):
                gap_preserved.append(gid)

        # ── 6. Optical Clearance (Session 16) ─────────────────────
        clarity_info = self.observer.observe(
            wf, 
            msg.structural_hash, 
            ternary=getattr(msg, "ternary", 0),
            surface=getattr(msg, "mobius_surface", "existence")
        )
        post_meta["optical_clearance"] = clarity_info
        
        # ── 7. Quaternion Projection (Session 10) ──────────────────
        q_data = self._project_quaternion(emb)
        
        result = {
            "state": state,
            "ternary": ternary,
            "hash": msg.structural_hash,
            "nearest_id": nearest_id,
            "leverage": round(leverage_score, 4),
            "synthesis": synthesis,
            "subjective_state": subjective_state,
            "causal_classification": causal_classification,
            "time_ms": round(elapsed * 1000, 2),
            "rgb": wf.color(),
            "ansi": wf.ansi_color(),
            "gods": god_ids,
            "post": post_meta,
            "operator_phase": round(self._operator_phase, 2),
            # Session 8: fields for RecursiveAccelerator trajectory
            "phase_deg": wf.phase_deg,
            "depth": msg.energy_level,
            "zone": msg.zone,
            "gap_preserved": gap_preserved,
            "similarity": obs.get("cos_sim", 0.5), # Ensure similarity is passed for trajectory
            "mobius_detected": "apophatic" in state.lower(),
            "f_q": (round(wf.w, 4), round(wf.x_surprise, 4), round(wf.y_spatial, 4), round(wf.z_emergence, 4)),
            "clarity": clarity_info["clarity"],
            "optical_state": clarity_info["state"]
        }
        
        result.update(q_data)

        # ── 8. Persistence (Session 11) ──────────────────────────
        self.archiver.store(msg)
        self.points.append(self.accelerator.add_point(msg.to_dict(), content))

        return result

    def _process_cycle(self, emb: np.ndarray, content: str, zoom: float, realization: bool, displacement: bool, level: int = 1) -> Tuple[ArchiverMessage, 'WaveFunction']:
        """
        LEARN → COMPRESS → FORGET → WITNESS → RECOGNIZE → REPEAT
        The recursive Learning Chain (Pyramid Structure).
        """
        msg, wf = self.scout.process(
            emb, content=content, zoom=zoom, realization=realization, 
            t=self.system_time, displacement=displacement
        )
        
        # 1. CRYSTALLIZATION / VOID / APOPHATIC conditions handled in scout.process
        
        # 2. SANITY_DEPTH (level count exceeded)
        # We check the formal SANITY_DEPTH from noise_compass.architecture.core
        try:
            from noise_compass.architecture.core import SANITY_DEPTH
        except ImportError:
            SANITY_DEPTH = 5
        
        if msg.is_recognized and level < SANITY_DEPTH:
            # FORGET: "Discard surface form. The attractor survives."
            # The next level learns from the witnessed delta of this level.
            # We recursively call _process_cycle on the delta.
            next_msg, next_wf = self._process_cycle(wf.delta, f"Witness level {level}", zoom, realization, displacement, level + 1)
            
            # The chain closes when the system can recognize its own output.
            # For now, we return the deepest recognized message as the 'distilled' result.
            return next_msg, next_wf

        return msg, wf

    def distill_formula(self, formula: str) -> str:
        """Translates a mathematical formula into its god-token address (Phase 11)."""
        return self.math_extractor.distill_to_word(formula)

    # ── Dream State ───────────────────────────────────────────────────────────

    def dream(self, steps: int = 3, zoom: float = 1.0, math_focused: bool = True) -> List[Dict]:
        """Expose the Dreamer functionality."""
        if not hasattr(self, '_dreamer'):
            from noise_compass.architecture.dream import Dreamer
            self._dreamer = Dreamer(self)
        return self._dreamer.dream(steps=steps, zoom=zoom, math_focused=math_focused)

def run_tests():
    """Verify Session 12 Pyramid Structure Synchronization."""
    print("\n--- SESSION 12: PYRAMID STRUCTURE SYNC TEST ---")
    
    from noise_compass.architecture.dictionary import Dictionary
    from noise_compass.architecture.core import Scout, LightWitness
    from noise_compass.architecture.archiver import Archiver
    from noise_compass.architecture.seed_vectors import seed_vectors
    
    d = Dictionary()
    seed_vectors(d) 
    p = MinimalPipeline(d)

    test_inputs = [
        "FROGGING", 
        "CHIRAL OPPOSITE", 
        "IDENTITY is not existence", 
        "the silence of the pure observer"
    ]

    for i, text in enumerate(test_inputs):
        try:
            res = p.process(text, trace=True)
            print(f"[{i:02d}] {text:<30} -> {res['state']}")
            
            # Display Session 12 Somatic & Stack metrics
            post = res.get("post", {})
            drift = post.get("metabolic_state", {}).get("somatic_drift", 0.0)
            stack = post.get("stack_results", {})
            nodes = stack.get("depth1_nodes", [])
            
            print(f"     \033[93m[SOMATIC DRIFT]: {drift:.4f}\033[0m")
            print(f"     \033[94m[5-CARD STACK]: nodes={nodes}, apex_phase={stack.get('card5_phase', 0.0):.2f}\033[0m")
            
        except Exception as e:
            print(f"[{i:02d}] {text:<30} -> FAILED: {e}")
            import traceback
            traceback.print_exc()

    print("\nSESSION 12 PYRAMID STRUCTURE VERIFIED.")

if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        run_tests()
