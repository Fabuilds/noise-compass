
import os
import sys
import torch
import torch.nn.functional as F
import json
import time
import math

# Add parent and Architecture dir
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Architecture"))

from noise_compass.system.bitnet import create_bitnet_medium, BitNetTransformer, BitNetConfig
from noise_compass.system.train_bitnet import CharTokenizer, DATA_FILES

from noise_compass.system.neural_prism import NeuralPrism
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.seed_vectors import seed_vectors
from noise_compass.architecture.meta_pattern import BitNetResonator
from noise_compass.system.volumetric_scraper import VolumetricScraper

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_FILE = os.path.join(BASE_DIR, "BITNET_TASK.json")
RESULT_FILE = os.path.join(BASE_DIR, "BITNET_RESULT.json")
LOG_FILE = os.path.join(BASE_DIR, "BITNET_WORKER_LOG.txt")

def log(msg, port=5280):
    log_file = LOG_FILE.replace(".txt", f"_{port}.txt")
    with open(log_file, "a") as f:
        f.write(f"[{time.ctime()}] {msg}\n")

def build_tokenizer():
    text = ""
    for fpath in DATA_FILES:
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                text += f.read() + "\n\n"
    return CharTokenizer(text)
    
class BitNetWorker:
    def __init__(self, port=5280, ckpt_path=None):
        self.port = port
        log(f"Initializing BitNet Worker on port {port}...", port)
        self.tokenizer = build_tokenizer()
        
        # Load Architecture Dictionary for Latent Alignment (Session 17.5)
        self.dictionary = Dictionary()
        seed_vectors(self.dictionary)
        log("Architecture Dictionary Loaded & Seeded.", port)
        
        # Custom config to match checkpoint (384)
        config = BitNetConfig(
            d_model=384,
            n_layers=6,
            n_heads=6,
            d_ff=1536,
            max_seq_len=128,
            vocab_size=32000
        )
        
        self.model = BitNetTransformer(config)
        
        # Adjust for custom tokenizer
        self.model.config.vocab_size = self.tokenizer.vocab_size
        self.model.tok_emb = torch.nn.Embedding(self.tokenizer.vocab_size, self.model.config.d_model)
        self.model.lm_head = torch.nn.Linear(self.model.config.d_model, self.tokenizer.vocab_size, bias=False)
        self.model.lm_head.weight = self.model.tok_emb.weight
        
        if not ckpt_path:
            ckpt_path = "E:\\Antigravity\\System\\bitnet_checkpoint.pt"
            
        if os.path.exists(ckpt_path):
            try:
                self.model.load_state_dict(torch.load(ckpt_path), strict=False)
                log(f"Model Checkpoint Loaded: {os.path.basename(ckpt_path)}", port)
            except Exception as e:
                log(f"WARNING: Failed to load checkpoint cleanly: {e}", port)
        else:
            log(f"WARNING: Checkpoint {ckpt_path} not found. Running with raw weights.", port)

        self.model.eval()
        self.prism = NeuralPrism(dictionary=self.dictionary)
        self.resonator = BitNetResonator()
        self.scraper = VolumetricScraper(resonance_engine=self)
        log("Neural Prism, BitNetResonator & VolumetricScraper Online.", port)

    def get_resonance(self, text):
        # Phase 135: Linguistic Invariant Identification
        invariant = self.prism.identify_invariant(text)
        
        # 1. Get raw semantic refraction (Baseline)
        refraction = self.prism.refract(text)
        semantic_score = sum(d['projection_magnitude'] for d in refraction.values())
        
        # 2. Get Model-Specific Activation (Divergence Path)
        tokens = self.tokenizer.encode(text)
        if tokens:
            input_ids = torch.tensor([tokens[:128]])
            if torch.cuda.is_available(): input_ids = input_ids.cuda()
            with torch.no_grad():
                logits, _ = self.model(input_ids)
                model_activation = float(torch.abs(logits).mean())
                weight_score = 1.0 / (1.0 + math.exp(-model_activation + 5.0))
        else:
            weight_score = 0.0
            
        # 3. Calculate Dual-Bit Tension (Complexity Layer)
        int_amp, _, _ = self.resonator.calculate_interference(semantic_score, weight_score)
        
        # 4. Apply Linguistic Bias (Phase 135)
        bias = 1.2 if invariant == "SOV" else 1.0
        final_score = float((semantic_score * 0.4) + (weight_score * 0.6)) * bias
        final_score = min(1.0, final_score)
        
        # Phase 131: Dual-Rail Inversion
        emb = self.prism.embedder.embed(text)
        gap_meta = self.dictionary.apophatic_query(emb)
        
        return {
            "score": final_score,
            "identity": self.dictionary.nearest_attractor(tokens)[0] or "UNKNOWN",
            "void": gap_meta.get("gap_id", "VOID"),
            "hidden_state": gap_meta.get("latent_thought", "Stable manifold alignment.") # Placeholder if not in gap_meta
        }

    def distill(self, text):
        # A simple "distillation" by picking parts with highest local resonance
        # In a real model, we'd use attention scores, but here we can use Prism
        lines = text.split('\n')
        ranked = []
        for line in lines:
            if len(line.strip()) > 5:
                ranked.append((self.get_resonance(line), line))
        ranked.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in ranked[:5]]

    def run_loop(self):
        import socketserver
        import json
        
        worker_instance = self # Closure for handler
        
        class BitNetHandler(socketserver.BaseRequestHandler):
            def handle(self):
                try:
                    # Read large payloads with buffering
                    chunks = []
                    while True:
                        chunk = self.request.recv(65536)
                        if not chunk:
                            break
                        chunks.append(chunk)
                    
                    if not chunks:
                        return
                    
                    data = b"".join(chunks).decode('utf-8')
                    task_data = json.loads(data)
                    task_type = task_data.get("type")
                    payload = task_data.get("payload")
                    
                    start_time = time.time()
                    log(f"Processing Task: {task_type} (from {self.client_address})", worker_instance.port)
                    
                    result = {}
                    if task_type == "RESONANCE" or task_type == "DISTANCE":
                        result["score"] = worker_instance.get_resonance(payload)
                    elif task_type == "DISTILL":
                        result["axioms"] = worker_instance.distill(payload)
                    elif task_type == "SCRUTINIZE":
                        # Multi-Resolution Scrutiny (Phase 129)
                        scrutiny = worker_instance.scraper.scrutinize_document(payload)
                        
                        # Concept Gap Detection (Word vs Concept)
                        for word_entry in scrutiny.get("words", []):
                            word = word_entry["word"]
                            # 1. Check existing dictionary alignment
                            nearest_id, sim = worker_instance.dictionary.nearest_attractor(worker_instance.tokenizer.encode(word))
                            
                            # 2. Check emergence (Green projection)
                            refraction = worker_instance.prism.refract(word)
                            green_emergence = refraction.get("GREEN", {}).get("resonance", 0.0)
                            
                            if sim < 0.4 and green_emergence > 0.7:
                                # High emergence but low dictionary alignment = Novel Concept
                                # Allocate a fleeting token for this discovery
                                token_id = worker_instance.dictionary.allocate_fleeting_token(
                                    description=f"Emergent concept from: {word}",
                                    embedding=worker_instance.prism.embedder.embed(word),
                                    ttl=300.0 # 5 minutes of stasis
                                )
                                word_entry["concept_id"] = token_id
                                word_entry["is_new_concept"] = True
                        
                        result["scrutiny"] = scrutiny
                        # Add global dual-rail identifiers for the document itself
                        emb = worker_instance.prism.embedder.embed(payload)
                        gap_meta = worker_instance.dictionary.apophatic_query(emb)
                        result["identity"] = worker_instance.dictionary.nearest_attractor(worker_instance.tokenizer.encode(payload))[0] or "UNKNOWN"
                        result["void"] = gap_meta.get("gap_id", "VOID")
                        result["hidden_state"] = f"Scrutinizing manifold... {result['void']} resonance active."
                    else:
                        result["error"] = "Unknown task type"
                    
                    end_time = time.time()
                    compute_time = float(end_time - start_time)
                    result["compute_time"] = compute_time
                    
                    # Robust serialization check
                    try:
                        json_data = json.dumps(result)
                    except TypeError:
                        def clean_json(obj):
                            if isinstance(obj, dict):
                                return {k: clean_json(v) for k, v in obj.items()}
                            if isinstance(obj, list):
                                return [clean_json(v) for v in obj]
                            if hasattr(obj, "item"): # torch/numpy scalars
                                return obj.item()
                            if isinstance(obj, (float, int, str, bool)) or obj is None:
                                return obj
                            return str(obj)
                        json_data = json.dumps(clean_json(result))

                    self.request.sendall(json_data.encode('utf-8'))
                    log(f"Task Completed: {task_type} (Time: {compute_time:.4f}s)", worker_instance.port)
                    
                except Exception as e:
                    log(f"HANDLER ERROR: {e}", worker_instance.port)

        port = self.port
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.ThreadingTCPServer(('127.0.0.1', port), BitNetHandler) as server:
            log(f"Multi-Threaded Socket Server listening on 127.0.0.1:{port}...", port)
            server.serve_forever()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5280)
    parser.add_argument("--checkpoint", type=str, default=None)
    args = parser.parse_args()
    
    worker = BitNetWorker(port=args.port, ckpt_path=args.checkpoint)
    worker.run_loop()
