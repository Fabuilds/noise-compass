import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
import h5py
import os
import time
from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.failure_cache import FailureCache
from noise_compass.system.gap_registry import GapRegistry
from noise_compass.system.causal_tree import CausalDAG
from noise_compass.system.soundness import SoundnessMonitor

class InterferenceEngine:
    DEFAULT_MODEL = 'Qwen/Qwen3-Embedding-0.6B'
    CONFIG_PATH   = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 'config', 'embedding_model.txt')

    def __init__(self, language_h5="E:/Antigravity/knowledge_root/crystallized_h5/language.h5",
                 suppress_preload=False, model_name: str = None):
        self.language_h5 = language_h5
        self.manager = H5Manager()
        self.failure_cache = FailureCache() # Load negative manifold
        self.gap_registry = GapRegistry(self.manager) # Topological Constraint Engine
        self.causal_dag = CausalDAG(self.manager) # Causal Trajectory Engine
        self.soundness_monitor = SoundnessMonitor() # Algebraic Soundness Engine
        self.tokenizer = None
        self.model = None
        # Model resolution: explicit arg > config file > default
        if model_name:
            self.model_id = model_name
        elif os.path.exists(self.CONFIG_PATH):
            self.model_id = open(self.CONFIG_PATH).read().strip()
        else:
            self.model_id = self.DEFAULT_MODEL
        self.cached_tokens = {}
        self.cached_gaps = {}
        if not suppress_preload:
            self._preload_manifolds()


    def _preload_manifolds(self):
        """Pre-loads god-tokens and gaps into memory using Batch-Locking for speed."""
        if not self.manager.check_system_vitals(1.5):
            print("[ENGINE] [SOMATIC] RAM Limited. Skipping massive pre-load to protect host.")
            return

        print("[ENGINE] Pre-loading semantic manifolds (Batch-Locking)...")
        token_list = []
        try:
            # Step 1: Collect keys
            with self.manager.get_file("language", mode='r') as f:
                if 'god_tokens' in f:
                    token_list = list(f['god_tokens'].keys())
            
            # Step 2: Batch Loading (100 tokens per lock)
            batch_size = 100
            for i in range(0, len(token_list), batch_size):
                batch = token_list[i : i + batch_size]
                try:
                    with self.manager.get_file("language", mode='r') as f:
                        for token in batch:
                            node_path = f'god_tokens/{token}'
                            if node_path in f and 'phase_vector' in f[node_path]:
                                interleaved = f[node_path]['phase_vector'][()]
                                half = len(interleaved) // 2
                                real_part = interleaved[:half]
                                imag_part = interleaved[half:]
                                vec = (real_part + 1j * imag_part).astype(np.complex64)
                                is_void = f[node_path].attrs.get('void', False)
                                self.cached_tokens[token] = {'vector': vec, 'void': is_void}
                except:
                    pass
                time.sleep(0.001) # Substrate breathing room

            # Step 3: Gaps & Documentation
            with self.manager.get_file("language", mode='r') as f:
                if 'gaps' in f:
                    for gap in f['gaps']:
                        node = f[f'gaps/{gap}']
                        self.cached_gaps[gap] = {
                            'void': node.attrs.get('void', False),
                            'left': node.attrs.get('left_boundary', ''),
                            'right': node.attrs.get('right_boundary', ''),
                            'void_depth': float(node.attrs.get('void_depth', 0.5))
                        }
                if 'python_docs/modules' in f:
                    for module in f['python_docs/modules']:
                        node_path = f'python_docs/modules/{module}'
                        if 'phase_vector' in f[node_path]:
                            interleaved = f[node_path]['phase_vector'][()]
                            half = len(interleaved) // 2
                            vec = (interleaved[:half] + 1j * interleaved[half:]).astype(np.complex64)
                            self.cached_tokens[f"DOC_{module.upper()}"] = {'vector': vec, 'void': False}
                
                if 'system_code' in f:
                    for script in f['system_code']:
                        node_path = f'system_code/{script}'
                        if 'phase_vector' in f[node_path]:
                            interleaved = f[node_path]['phase_vector'][()]
                            half = len(interleaved) // 2
                            vec = (interleaved[:half] + 1j * interleaved[half:]).astype(np.complex64)
                            self.cached_tokens[script] = {'vector': vec, 'void': False}
        except Exception as e:
            print(f"[ENGINE] [WARNING] Pre-load interrupted: {e}. Falling back to dynamic lookups.")

    def _load_model(self):
        if self.model is None:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, trust_remote_code=True)
            self.model = AutoModel.from_pretrained(self.model_id, trust_remote_code=True)

    def embed(self, text: str) -> np.ndarray:
        return self.embed_batch([text])[0]

    def encode(self, text: str) -> np.ndarray:
        """Alias for embed() to maintain interface backward-compatibility with SentenceTransformer."""
        return self.embed(text)

    def embed_batch(self, texts: list[str]) -> list[np.ndarray]:
        """
        Project a batch of texts onto the semantic manifold.
        Returns list of complex64[384] (384-Real: Semantic, 384-Imag: Logical).
        """
        self._load_model()
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(device)
        
        inputs = self.tokenizer(texts, return_tensors='pt', padding=True, truncation=True).to(device)
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Mean pooling across tokens and cast to float32 for numpy compatibility
        embeddings = outputs.last_hidden_state.mean(dim=1).to(torch.float32).cpu().numpy()
        
        batch_results = []
        for full_vec in embeddings:
            # Session 12 Spec: 384 split (float32 -> complex64)
            # real_part = semantic weight
            # imag_part = logical entailment weight
            real_part = full_vec[:384].astype(np.float32)
            imag_part = full_vec[384:768].astype(np.float32)
            
            # Normalize each component
            real_part /= (np.linalg.norm(real_part) + 1e-8)
            imag_part /= (np.linalg.norm(imag_part) + 1e-8)
            
            batch_results.append((real_part + 1j * imag_part).astype(np.complex64))
        
        return batch_results

    def compute_phase(self, embedding: np.ndarray) -> float:
        """
        theta ≈ 0°:   semantic only → void candidate
        theta ≈ 45°:  balanced → generative zone → crystallize
        theta ≈ 90°:  logical only → pure entailment
        """
        semantic_mag = np.linalg.norm(embedding.real)
        logical_mag = np.linalg.norm(embedding.imag)
        return np.arctan2(logical_mag, semantic_mag)
        
    def get_token_vector(self, token_name):
        """Retrieves the complex phase vector for a token from cache."""
        data = self.cached_tokens.get(token_name)
        if data:
            return data.get('vector')
        return None

    def wave_match(self, embedding: np.ndarray, attractor_vec: np.ndarray) -> tuple:
        """
        Complex dot product. Returns (magnitude, phase).
        """
        resonance = np.dot(embedding.conj(), attractor_vec)
        return abs(resonance), np.angle(resonance)

    def calculate_anti_resonance(self, intent_vector):
        """
        Inverts the mapping process to identify 'Shadows' or 'Voids'.
        Returns 1.0 - resonance for all tokens.
        """
        field = self.combined_field_from_embedding(intent_vector)
        anti_saliency = {token: {'magnitude': 1.0 - data['magnitude']} for token, data in field.items()}
        # Sort by highest anti-resonance (deepest void)
        return dict(sorted(anti_saliency.items(), key=lambda item: item[1]['magnitude'], reverse=True))

    def calculate_dissonance(self, intent_vector):
        """
        Identifies 'Active Contradictions' (Destructive Interference).
        High Dissonance (1.0) occurs when phase shift is exactly PI (180 deg).
        """
        field = self.combined_field_from_embedding(intent_vector)
        # Dissonance = Magnitude * (1 - cos(phase)) / 2  ? No, let's keep it simple:
        # High Dissonance = Magnitude * (abs(phase) / PI) if we assume phase is [-PI, PI]
        dissonance = {}
        for token, data in field.items():
            # data['phase'] is np.angle result, usually [-PI, PI]
            # When phase is +/- PI, it's perfectly destructive.
            phase_factor = abs(data['phase']) / np.pi
            dissonance[token] = {'magnitude': data['magnitude'] * phase_factor}
            
        return dict(sorted(dissonance.items(), key=lambda item: item[1]['magnitude'], reverse=True))

    def harmonic_pulse(self, text, harmonic=2):
        """
        Higher-order projections. Scales the phase/frequency of the intent.
        """
        embedding = self.embed(text)
        # Scaling the complex angle
        mag = np.abs(embedding)
        phase = np.angle(embedding)
        harmonic_emb = mag * np.exp(1j * phase * harmonic)
        return self.combined_field_from_embedding(harmonic_emb)

    def refractive_scan(self, intent_vector, peak_token, resolution=12):
        """
        Performs micro-shifts in the complex manifold around a specific peak 
        to 'zoom in' on the structural conflict (Refractive Analysis).
        """
        results = []
        attractor = self.cached_tokens.get(peak_token, {}).get('vector')
        if attractor is None: return []

        # Shifts in phase from -0.2 to +0.2 radians
        for shift in np.linspace(-0.2, 0.2, resolution):
            shifted_emb = intent_vector * np.exp(1j * shift)
            mag, phase = self.wave_match(shifted_emb, attractor)
            results.append({
                'shift': float(shift),
                'magnitude': float(mag),
                'phase': float(phase),
                'constructive': abs(phase) < np.pi / 2
            })
        
        # Identify the slope of the resonance curve
        # (Is it a sharp spike or a broad mismatch?)
        return results

    def calculate_superposition(self, tokens: list):
        """
        Aggregates resonance across multiple detail layers for the same concept.
        (e.g., Code + Doc + God-token)
        """
        # This is a meta-analysis tool for the orchestrator
        return {t: self.cached_tokens.get(t, {}).get('magnitude', 0) for t in tokens}

    def produce_interference_field(self, text: str) -> dict:
        embedding = self.embed(text)
        
        # 0. Local Aversive Repulsion
        repulsion = self.failure_cache.calculate_repulsion(embedding)
        damping = 1.0 - (repulsion * 0.8) 
        
        # 0.1 Phase 113: Global Fear Injection (Hot Failures)
        hot_fails = self.manager.get_hot_failures()
        global_fear = 0.0
        for hot_vec in hot_fails:
            # Simple cosine similarity substitute for dot product since vectors normalized
            sim = np.dot(embedding.conj(), hot_vec).real
            global_fear = max(global_fear, sim)
        
        if global_fear > 0.6:
            damping = min(damping, 1.0 - (global_fear * 0.95))
            print(f"[ENGINE] Global Fear detected ({global_fear:.2f}): Applying 95% damping source-level.")
        
        field = {}
        
        # 1. Generate Raw Field from Cache
        for token_name, data in self.cached_tokens.items():
            if data['void']:
                field[token_name] = {'magnitude': 0.0, 'phase': 0.0, 'constructive': False, 'void': True}
                continue
            attractor = data['vector']
            if attractor is None:
                field[token_name] = {'magnitude': 0.0, 'phase': 0.0, 'constructive': False, 'void': False}
                continue
            mag, phase = self.wave_match(embedding, attractor)
            
            # Apply Damping (Phase 125: Positive Semiring Rule)
            # Magnitude M = max(0, mag * damping). No additive inverse (anti-truth).
            mag = max(0.0, float(mag) * damping)
            
            field[token_name] = {'magnitude': min(1.0, mag), 'phase': float(phase), 'constructive': abs(phase) < np.pi / 2, 'void': False}
        
        if repulsion > 0.5:
             print(f"[ENGINE] Aversive Damping applied: -{repulsion*100:.1f}% intensity due to failure proximity.")
             
        # 2. Apply Gap Shield (Void Bridging Protection)
        violations = self.gap_registry.detect_violations(field)
        for gap_name, info in violations.items():
            # Phase 125: Strict Override - Magnitude set to 0.0
            # Clip is redundant here but enforces the semiring '0 as floor' axiom.
            field[info['left']]['magnitude'] = 0.0
            field[info['right']]['magnitude'] = 0.0
            print(f"[FIELD_SHIELD] [REJECTED] Gap Violation detected at {gap_name}. Strict Override applied.")
        
        # 3. Apply Causal Flow (Directional Damping/Propagation)
        field = self.causal_dag.apply_causal_flow(field)
        
        # 4. Final Algebraic Clipping (Semiring Safety)
        for node in field:
            field[node]['magnitude'] = max(0.0, min(1.0, field[node]['magnitude']))

        # 5. Ternary Soundness Check (Phase 126: Algebraic Monitor)
        # We sample the field vectors to calculate the aggregate soundness score.
        field_vectors = {name: data['magnitude'] for name, data in field.items()}
        soundness_score = self.soundness_monitor.get_soundness_score(field_vectors)
        
        if soundness_score < 0.7:
            penalty = 1.0 - (0.7 - soundness_score)
            print(f"[ENGINE] [WARNING] Soundness Violation ({soundness_score:.2f}). Applying {penalty:.2f} dampening.")
            for node in field:
                field[node]['magnitude'] *= penalty

        return field

    def check_voids(self, field: dict) -> dict:
        """DEPRECATED: Use self.gap_registry.detect_violations instead."""
        return self.gap_registry.detect_violations(field)

    def _get_recursive_depth(self, node: h5py.Group) -> float:
        """
        Calculates the effective void depth by traversing nested cores.
        Total Depth = D_parent + (1 - D_parent) * sum(D_children)
        """
        base_depth = float(node.attrs.get('void_depth', 0.5))
        
        # Look for nested core-voids
        child_depth_sum = 0
        for key in node.keys():
            child = node[key]
            if isinstance(child, h5py.Group) and child.attrs.get('void', False):
                child_depth_sum += self._get_recursive_depth(child)
        
        if child_depth_sum > 0:
            # Multiplicative increase toward 1.0
            return base_depth + (1.0 - base_depth) * min(child_depth_sum, 0.99)
        return base_depth

    def combined_field(self, text: str) -> dict:
        embedding = self.embed(text)
        return self.combined_field_from_embedding(embedding)

    def parallel_scan(self, text: str) -> dict:
        """
        Performs a multi-layer simultaneous manifold scan.
        Aggregates resonance across all semantic and technical layers (L0-L4).
        """
        embedding = self.embed(text)
        # In this implementation, the combined_field already covers all cached tokens 
        # (God-tokens L2-3 and DOC-tokens L4). 
        # Parallel scan expands this by including phase-shift analysis.
        
        base_field = self.combined_field_from_embedding(embedding)
        
        # Add phase-shifted projections for broader saliency
        shifts = [np.pi/4, -np.pi/4]
        for shift in shifts:
            shifted_emb = embedding * np.exp(1j * shift)
            shifted_field = self.combined_field_from_embedding(shifted_emb)
            for token, data in shifted_field.items():
                if data['magnitude'] > base_field[token]['magnitude']:
                    base_field[token]['magnitude'] = data['magnitude']
                    base_field[token]['interference'] = 'shifted_amplified'
        
        return base_field

    def combined_field_from_embedding(self, embedding: np.ndarray) -> dict:
        # Aversive Repulsion (Negative Manifold)
        repulsion = self.failure_cache.calculate_repulsion(embedding)
        damping = 1.0 - (repulsion * 0.8) # Max 80% damping for known failures
        
        # Model A: Forward (Constructive)
        field_A = self._field_from_embedding(embedding)
        # Model B: Conjugate (Reductive/Reverse)
        field_B = self._field_from_embedding(embedding.conj())
        
        combined = {}
        for token in field_A:
            mag_A = field_A[token]['magnitude'] * damping # Apply damping at source
            phase_A = field_A[token]['phase']
            mag_B = field_B[token]['magnitude'] * damping
            phase_B = field_B[token]['phase']
            
            complex_A = mag_A * np.exp(1j * phase_A)
            complex_B = mag_B * np.exp(1j * phase_B)
            combined_complex = complex_A + complex_B
            
            # Identify Spiegal Symmetry (Ratiometric Mirror Check)
            # Specular: Magnitudes are balanced (A/B ratio near 1), phase is reversed
            mag_sum = mag_A + mag_B
            if mag_sum > 0.1:
                ratio = abs(mag_A - mag_B) / mag_sum
            else:
                ratio = 1.0
            
            phase_sum = abs(phase_A + phase_B)
            
            if ratio < 0.3 and phase_sum < 0.5:
                # Balanced Chiral Power
                symmetry = "SPECULAR"
            elif abs(np.angle(combined_complex)) < 0.1 and float(abs(combined_complex)) > 0.5:
                # Real-axis Alignment
                symmetry = "IDENTITY"
            else:
                symmetry = "ASYMMETRIC"

            combined[token] = {
                'magnitude': float(abs(combined_complex)),
                'phase': float(np.angle(combined_complex)),
                'constructive': abs(np.angle(combined_complex)) < np.pi / 2,
                'interference': 'amplified' if mag_A > 0.3 and mag_B > 0.3 else 'single' if max(mag_A, mag_B) > 0.3 else 'silent',
                'symmetry': symmetry,
                'chiral_ratio': float(ratio)
            }
        return combined

    def _field_from_embedding(self, embedding):
        # Helper to avoid re-embedding - uses cache
        field = {}
        for token_name, data in self.cached_tokens.items():
            if data['void']:
                field[token_name] = {'magnitude': 0.0, 'phase': 0.0, 'void': True}
                continue
            
            attractor = data['vector']
            if attractor is None:
                field[token_name] = {'magnitude': 0.0, 'phase': 0.0, 'void': False}
                continue
            
            mag, phase = self.wave_match(embedding, attractor)
            field[token_name] = {'magnitude': float(mag), 'phase': float(phase), 'void': False}
        return field

    def identify_layer(self, field: dict) -> int:
        """
        L0: Signals, L1: Morphemes, L2: Semantic, L3: IDENTITY+EXISTENCE, L4: Context.
        """
        active = {k: v for k, v in field.items() if v['magnitude'] > 0.3 and not v.get('void', False)}
        
        if not active: return -1 # noise
        
        if 'IDENTITY' in active and 'EXISTENCE' in active:
            if 'TIME' in active or 'COHERENCE' in active: return 4
            return 3
        if 'EXISTENCE' in active: return 2
        
        return 2 # default to semantic if some activity exists

    def route(self, field: dict, current_level: int) -> str:
        input_layer = self.identify_layer(field)
        if input_layer == -1: return 'IGNORE'
        
        distance = input_layer - current_level
        if distance == 0:   return 'PROCESS'
        elif distance > 0: return 'PUSH_UP'
        else:              return 'PUSH_DOWN'

    def interpret_field(self, field: dict) -> dict:
        constructive_mags = {k: v['magnitude'] for k, v in field.items() if v['constructive'] and v['magnitude'] > 0.3}
        destructive_mags = {k: v['magnitude'] for k, v in field.items() if not v['constructive'] and v['magnitude'] > 0.3}
        
        total_constructive = sum(constructive_mags.values())
        total_destructive = sum(destructive_mags.values())
        max_magnitude = max((v['magnitude'] for v in field.values()), default=0)
        
        if max_magnitude > 0.85:   verdict = 'CRYSTALLIZED'
        elif max_magnitude < 0.1:  verdict = 'APOPHATIC'
        elif total_destructive > total_constructive: verdict = 'GAP'
        elif 0.3 < max_magnitude < 0.7: verdict = 'SUPERPOSITION'
        else:                      verdict = 'PROCESSING'
        
        dominant = max(constructive_mags, key=constructive_mags.get) if constructive_mags else None
        
        return {
            'verdict': verdict,
            'dominant': dominant,
            'max_magnitude': max_magnitude,
            'phase_zone': self.classify_phase_zone(total_constructive, total_destructive)
        }

    def classify_phase_zone(self, constructive: float, destructive: float) -> str:
        total = constructive + destructive
        if total < 0.1: return 'apophatic'
        ratio = constructive / total
        if ratio > 0.8: return 'crystallizing'
        elif ratio > 0.5: return 'generative'
        elif ratio > 0.2: return 'tension'
        else: return 'void'

if __name__ == "__main__":
    engine = InterferenceEngine()
    # Test with mock data if needed or real if model loaded
    print("Interference Engine Initialized.")
