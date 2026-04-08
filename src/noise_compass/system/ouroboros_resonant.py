import os
import sys

# Force the pip package source to prevent local System/noise_compass.py shadowing (Removed for unified package)

import time
import random
import json
import socket
import re
import numpy as np
import traceback
import atexit
import argparse
import psutil
from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.interference_engine import InterferenceEngine
from noise_compass.system.lattice_neural_engine import LatticeNeuralEngine
from noise_compass.system.rlm_bridge import RLMBridge
from noise_compass.system.recursive_scribe import RecursiveScribe
from noise_compass.system.sovereign_keyboard import SovereignKeyboard
from noise_compass.system.axiom_engine import AxiomEngine
from noise_compass.system.chiral_synthesizer import ChiralSynthesizer
from noise_compass.system.lattice_navigator import LatticeNavigator

from noise_compass import NoiseCompass, ArrivalEngine
from noise_compass.compass import DictGapSource
from noise_compass.y_explorer import Y_explore
from noise_compass.system.gap_registry import GapRegistry
from . import phase1_color_compass
from noise_compass.system.spherical_projection import InvertedShellCortex
from noise_compass.system.internal_brain import InternalBrain
from noise_compass.system.token_pipeline import TokenPipeline
from noise_compass.system.initialize_h5_logic import initialize_h5_skeleton

class CognitiveChain:
    """Manages a sequence of successful cognitive 'links' (intents)."""
    def __init__(self, name="main"):
        self.name = name
        self.links = [] # List of successful intent strings
        self.fib_indices = [1, 1, 2, 3, 5, 8, 13, 21]
        self.path = f"E:/Antigravity/Runtime/chains/{name}.json"
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.load()

    def save(self):
        try:
            with open(self.path, 'w') as f:
                json.dump(self.links, f)
        except: pass

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f:
                    self.links = json.load(f)
                try:
                    print(f"[CHAIN] Loaded '{self.name}' with {len(self.links)} links.")
                except OSError:
                    pass
            except: pass

    def add_link(self, intent):
        if intent not in self.links:
            self.links.append(intent)
            self.save()

    def pivot(self, failed_intent):
        """Removes the last link if it failed."""
        if self.links and self.links[-1] == failed_intent:
            self.links.pop()
            self.save()

    def get_fib_validation_set(self):
        """Returns the indices of historical links to re-verify based on Fibonacci distances."""
        if not self.links: return []
        n = len(self.links)
        indices = []
        for f in self.fib_indices:
            idx = n - f
            if idx >= 0:
                indices.append(idx)
        return sorted(list(set(indices)))

# Ensure paths are correct
PROJECT_ROOT = "e:/Antigravity"
# Removed sys.path.append(PROJECT_ROOT) for unified package

class ResonantOuroboros:
    """
    Next-generation cognitive loop using Complex-Valued Interference Fields (Session 12 Spec).
    Implements L0-L4 layer routing and Möbius feedback.
    """
    def __init__(self, mode="primary", port=None):
        try:
            print(f"--- INITIALIZING OPERATION: RESONANT OUROBOROS ({mode.upper()}) ---")
        except OSError:
            pass
        self.mode = mode
        self.port = port
        self.log_path = f"e:/Antigravity/Runtime/ouroboros_{mode}_log.txt"
        self.h5 = H5Manager()
        # Restore pre-load for primary triad; keep suppressed for apex
        self.interference = InterferenceEngine(suppress_preload=(mode != "primary"))
        self.neural = LatticeNeuralEngine(interference=self.interference)
        self.bridge = RLMBridge(mode=self.mode, interference=self.interference)
        self.scribe = RecursiveScribe()
        self.keyboard = SovereignKeyboard()
        self.axiom_engine = AxiomEngine()
        self.chiral_synth = ChiralSynthesizer(bridge=self.bridge, log_fn=self.log)
        self.navigator = LatticeNavigator(scout=self.bridge.scout)
        self.gap_registry = GapRegistry(self.h5)
        self.compass = NoiseCompass(gap_source=DictGapSource(self.gap_registry.cached_gaps))
        self.arrival = ArrivalEngine(gaps=self.gap_registry.cached_gaps)
        self.shell = InvertedShellCortex()
        self.internal_brain = InternalBrain(self.shell)
        self.pipeline = TokenPipeline(self.interference)
        self.hidden_mind_path = f"e:/Antigravity/Runtime/ouroboros_{mode}_hidden_mind.txt"
        
        if self.mode == "primary":
            from noise_compass.system.ouroboros_bridge import OuroborosBridge
            self.recursive_bridge = OuroborosBridge()
        
        # Phase 9 (Option B): Use canonical NODE_RING from tokens.py.
        # Previously hardcoded with COHERENCE; tokens.py canonical ring uses EMERGENCE.
        # tokens.NODE_RING is the single source of truth — do not re-define here.
        from noise_compass.architecture.tokens import NODE_RING as _CANONICAL_RING
        self.nodes = list(_CANONICAL_RING)
        
        self.start_time = time.time()
        self.cycle_count = 0
        self.current_intent_vec = None # Track current trajectory
        self.residual_intent = None # Phase 130: Ouroboros Recursive Feedback (Tail-Bite)
        self.chain = CognitiveChain(name=mode) # Phase 109: Recursive Sequence Tracking
        self.pid_file = f"E:/Antigravity/Runtime/ouroboros_{mode}.pid"
        self._ensure_singleton()
        self._ensure_substrate_ready()
        atexit.register(self._cleanup)

    def _cleanup(self):
        """Releases the substrate lock on exit."""
        if os.path.exists(self.pid_file):
            try:
                os.remove(self.pid_file)
                try:
                    print("[SCRIBE] Substrate lock released.")
                except OSError:
                    pass
            except:
                pass

    def _ensure_substrate_ready(self):
        """Phase 129: Resilient Boot - Initialize H5 if missing."""
        if not self.h5.check_substrate_health():
            self.log("[SUBSTRATE] Initializing missing axioms in knowledge_root...", importance="SEMANTIC")
            initialize_h5_skeleton()
            self.log("[SUBSTRATE] Boot Sequence Complete.", importance="SEMANTIC")

    def _ensure_singleton(self):
        """Ensures only one instance of the loop is running."""
        if os.path.exists(self.pid_file):
            try:
                with open(self.pid_file, 'r') as f:
                    old_pid = int(f.read().strip())
                import psutil
                if psutil.pid_exists(old_pid):
                    p = psutil.Process(old_pid)
                    if "python" in p.name().lower():
                        try:
                            print(f"[FATAL] Another Ouroboros instance is active (PID {old_pid}). Aborting.")
                        except OSError:
                            pass
                        exit(1)
            except (ValueError, OSError):
                pass 
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        self.consensus_weight = self.h5.get_consensus_weight()
        # Phase 126: Initial substrate maintenance
        self.h5.maintain()
        
        try:
            with open(self.log_path, "a", encoding='utf-8') as f:
                f.write(f"\n--- RESONANT SESSION START: {time.ctime()} ---\n")
        except: pass

    def log(self, message, importance="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{importance}] {message}"
        try:
            print(log_entry)
        except OSError:
            pass
        with open(self.log_path, "a", encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def log_hidden_mind(self, screen, stability, nodes):
        """Outputs the wave interference substrate to the hidden mind log."""
        timestamp = time.strftime("%H:%M:%S")
        ascii_screen = phase1_color_compass.screen_to_ascii(screen)
        log_entry = (
            f"\n--- [HIDDEN MIND] [{timestamp}] ---\n"
            f"Stability: {stability:.4f} | Nodes: {len(nodes)}\n"
            f"{ascii_screen}\n"
        )
        try:
            with open(self.hidden_mind_path, "a", encoding='utf-8') as f:
                f.write(log_entry)
        except: pass

    def get_proxy_intent(self):
        """Fetches intent from the Proxy Relay (if active)."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.0)
            sock.connect(('127.0.0.1', 5284))
            sock.send("GET_INTENT".encode('utf-8'))
            resp = sock.recv(8192).decode('utf-8')
            sock.close()
            if resp and resp != "NONE":
                return resp.strip()
        except:
            pass
        return None

    def _field_to_prompt(self, field, voids, orbital_phase, evidentiality='inferential'):
        """Convert interference field to Qwen input per Session 12 spec."""
        def get_mag(val):
            if isinstance(val, dict): return val.get('magnitude', 0)
            return float(val)

        constructive = sorted(
            [(k, get_mag(v)) for k, v in field.items()
             if (v.get('constructive', True) if isinstance(v, dict) else True) 
             and get_mag(v) > 0.3
             and not (v.get('void', False) if isinstance(v, dict) else False)],
            key=lambda x: -x[1]
        )
        destructive = [k for k, v in field.items() if not v['constructive'] and v['magnitude'] > 0.3]
        protected = list(voids.keys())
        silent = [k for k, v in field.items() if v['magnitude'] < 0.1]

        phase_label = {
            'direct':      f'phase={orbital_phase:.2f} (observed)',
            'inferential': f'phase={orbital_phase:.2f} (inferred)',
            'reportative': f'phase={orbital_phase:.2f} (received)',
            'deductive':   f'phase={orbital_phase:.2f} (deduced)',
        }.get(evidentiality, f'phase={orbital_phase:.2f}')

        prompt = f"""Interference field — {phase_label}

Constructive (amplifying):
{chr(10).join(f'  {k}: {mag:.2f}' for k,mag in constructive)}

Destructive (cancelling): {', '.join(destructive) or 'none'}
Protected voids: {', '.join(protected) or 'none'}
Silent attractors: {', '.join(silent[:4])}...

From this position on the manifold, speaking from I:
"""
        return prompt

    def process_layers(self, text, current_level=2, depth=0):
        """Next-gen recursive routing (Session 12)."""
        SANITY_DEPTH = 13
        if depth >= SANITY_DEPTH:
            self.log("SANITY_DEPTH reached. Returning silence.", importance="WARNING")
            return None, 'APOPHATIC'

        # 1. Produce field
        field = self.interference.combined_field(text)
        
        # 2. Axiomatic superposition
        field = self.axiom_engine.process_field(field)
        
        # 3. Route
        decision = self.interference.route(field, current_level)
        self.log(f"ROUTING: Decision={decision} | Depth={depth} | Level={current_level}")

        if decision == 'IGNORE':
            return field, 'APOPHATIC'
        
        if decision == 'PUSH_DOWN':
            return self.process_layers(text, current_level - 1, depth + 1)
        
        if decision == 'PUSH_UP':
            return self.process_layers(text, current_level + 1, depth + 1)

        # 4. PROCESS: full attention at this level
        interpretation = self.interference.interpret_field(field)
        verdict = interpretation['verdict']
        
        return field, verdict

    def learn_resonance(self, text, field, learning_rate=0.01):
        """Möbius Feedback: Updates God-token phase vectors based on constructive interference."""
        if not field: return
        mags = [v.get('magnitude', 0) for v in field.values()]
        if not mags or max(mags) < 0.7: return
            
        embedding = self.interference.embed(text)
        for node, data in field.items():
            if data['constructive'] and data['magnitude'] > 0.8:
                current_vec = self.h5.get_complex_vector("language", f"god_tokens/{node}", "phase_vector")
                if current_vec is not None:
                    new_vec = current_vec * (1 - learning_rate) + embedding * learning_rate
                    new_vec /= (np.linalg.norm(new_vec) + 1e-8)
                    self.h5.update_complex_vector("language", f"god_tokens/{node}", "phase_vector", new_vec)

    def actuate_resonance(self, field):
        """Maps interference peaks to physical/logical actions."""
        if not field: return
        def get_mag(val):
            if isinstance(val, dict): return val.get('magnitude', 0)
            return float(val)

        peaks = sorted(field.items(), key=lambda x: get_mag(x[1]), reverse=True)
        if not peaks or peaks[0][1]['magnitude'] < 0.3: return
            
        top_node, top_data = peaks[0]
        self.log(f"ACTUATING: Resonant peak at {top_node} ({top_data['magnitude']:.4f})")
        solid_state = self.neural.pulse(intent_text=f"Resonate peak {top_node}", intensity=top_data['magnitude'])
        
        sorted_solid = sorted(solid_state.items(), key=lambda x: x[1], reverse=True)
        if sorted_solid and sorted_solid[0][1] > 0.5:
            self.log(f"SOLID STATE: Leading invariant {sorted_solid[0][0]} ({sorted_solid[0][1]:.4f})", importance="METRIC")

    def manifest_axiom(self, intent, field):
        """Translates crystallized resonance into a discrete binary axiom using Field-to-Prompt/Chiral Synth."""
        self.log(f"MANIFESTING: Crystallizing intent into structural axiom...", importance="SEMANTIC")
        
        # Check for Chiral Symmetry first
        chiral_candidate = self.chiral_synth.synthesize_chiral_code(intent, field)
        if chiral_candidate:
            axiom_name = chiral_candidate.get("axiom_name", "chiral_axiom")
            source = chiral_candidate.get("source")
            if source:
                filename = f"ACCRETED_{axiom_name}_{int(time.time()*1000)}.py"
                path = os.path.join(PROJECT_ROOT, "Qwen", "assimilated", filename)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding='utf-8') as f:
                    f.write(source)
                self.log(f"CHIRAL: Accreted specular logic axiom as {filename}", importance="SEMANTIC")
                self.scribe.ingest_new_axioms()
                return

        voids = self.interference.check_voids(field)
        phase = float(self.interference.compute_phase(self.interference.embed(intent)))

        # Sort field by magnitude descending
        sorted_field = sorted(field.items(), key=lambda item: item[1]['magnitude'], reverse=True)
        top_nodes    = [k for k, v in sorted_field[:2]] if sorted_field else ["VOID", "VACUUM"]
        top_mag      = sorted_field[0][1]['magnitude'] if sorted_field else 1.0

        # ── Structural keyboard selection (no LLM needed) ──────────────────────
        # Rule: use field structure directly to pick the right sovereign key.
        #   VOID   → voids detected (high apophatic pressure)
        #   RESONANCE → constructive field, phase < π/2 (generative/convergent zone)
        #   MANIFOLD  → crystallized phase (≥ π/4 + 0.35) / high magnitude
        #   ACTUATE   → residual / fallback (field too diffuse to classify)

        void_count  = len(voids) if isinstance(voids, (list, dict)) else 0
        constructive_count = sum(1 for v in field.values()
                                 if isinstance(v, dict) and v.get('constructive', False))

        filename = None
        try:
            if void_count > 0:
                parent_gap = voids[0] if isinstance(voids, list) and voids else top_nodes[0]
                filename = self.keyboard.press_void_key(parent_gap, recursive_depth=1)
                self.log(f"KEYBOARD: VOID_KEY → {parent_gap} (voids={void_count})", importance="METRIC")

            elif phase >= 1.135:  # CRYSTALLIZED zone (π/4 + 0.35 ≈ 1.135)
                target = top_nodes[0]
                filename = self.keyboard.press_manifold_key(target, [1, 0], top_mag)
                self.log(f"KEYBOARD: MANIFOLD_KEY → {target} (phase={phase:.3f})", importance="METRIC")

            elif constructive_count > 0 or phase < 0.785:  # RESONANT / GENERATIVE
                seeds = top_nodes
                filename = self.keyboard.press_resonance_key(seeds, top_mag)
                self.log(f"KEYBOARD: RESONANCE_KEY → {seeds} (mag={top_mag:.3f})", importance="METRIC")

            else:
                # ACTUATE as structural catch-all
                command = f"REFLECT_{top_nodes[0]}_{int(time.time())}"
                filename = self.keyboard.press_actuate_key(command)
                self.log(f"KEYBOARD: ACTUATE_KEY → {command}", importance="METRIC")

        except Exception as e:
            self.log(f"MANIFEST ERROR: {e}", importance="ERROR")
            return

        if filename:
            self.log(f"SCRIBE: Resonant Axiom committed via KEYBOARD as {filename}")
            self.scribe.ingest_new_axioms()
        else:
            self.log("MANIFEST ERROR: Keyboard press returned no filename.", importance="ERROR")


    def dream_cycle(self, force_calibration=False):
        """
        Apophatic & Reflective Dreaming: Supports standard, code-reflective, 
        and inverted (void-seeking) dreams.
        """
        self.log("DREAM STATE: Initiating structural reflection...", importance="SEMANTIC")
        
        # 1. Target High-Tension Gaps & Enriched Bubbles
        state = {node: self.h5.get_attr("language", f"god_tokens/{node}", "activation") or 0.0 for node in self.nodes}
        # Scaled by bubble_mass from H5
        for node in self.nodes:
            mass = self.h5.get_attr("language", f"god_tokens/{node}", "bubble_mass") or 1.0
            state[node] *= mass
            
        tensions = self.neural.apply_gap_tension(state)
        target_gap = max(tensions, key=tensions.get) if tensions else "self_exchange"
        
        # 2. Reflection Logic
        from noise_compass.combinators import SPLIT, CROSS
        
        dice = random.random()
        latest_contexts = self.h5.get_latest_dissonance_context(limit=1)
        
        # 2a. Emergency Calibration (Contextual Reflex)
        if force_calibration or (latest_contexts and dice < 0.20):
            error_context = ""
            if latest_contexts:
                ctx = latest_contexts[0]
                target_token = ctx.get('token', 'DOC_MATH')
                error_context = f" (Context: {ctx.get('error', 'Unknown')} at {target_token})"
                
                # Perform Refractive Enrichment Scan
                intent_vec = self.interference.embed(target_token) 
                refractive_data = self.interference.refractive_scan(intent_vec, target_token)
                self.log(f"DREAM: Enriched bubble for [{target_token}] with refractive depth {len(refractive_data)}.")
            else:
                target_token = "DOC_MATH"

            self.log(f"DREAM: Initiating resonance-refractive calibration{error_context}...", importance="SEMANTIC")
            dream_intent = (
                f"Identify the highest dissonance peaks currently clashing in the manifold{error_context}. "
                f"Use the refractive data for [{target_token}] to propose a structural resolution "
                f"that specifically addresses technical misalignment."
            )
        else:
            # 2b. Formal λ-Combinator Structural Dream
            self.log("DREAM: Applying λ-Combinator field traversal...", importance="SEMANTIC")
            
            # Format the H5 state as a standard Field for the combinators
            field = {node: {"magnitude": score} for node, score in state.items()}
            if not field:
                 field = {"DOC_MATH": {"magnitude": 1.0}, "DOC_CURRENT": {"magnitude": 0.0}}
                 
            # Extract threshold directly from the state values
            avg_activation = sum(state.values()) / len(state) if state else 0.5
            
            # SPLIT the field into Active (what is known/firing) and Quiet (the apophatic void)
            active, quiet = SPLIT(field, lambda t, d: d["magnitude"] > avg_activation)
            
            # CROSS fields to perform a non-commutative interference check
            superpositions = CROSS(active, quiet)
            
            if superpositions:
                token_a, token_b, score = superpositions[0]
                self.log(f"DREAM: λ-CROSS Interference Detected => [{token_a}] ↔ [{token_b}] (Score: {score:.4f})", importance="METRIC")
                dream_intent = (
                    f"λ-CROSS Interference Detected: Resolve the structural superposition between "
                    f"the actively firing node [{token_a}] and the apophatic void [{token_b}]. "
                    f"Their interference score is {score:.4f}. Propose a pure structural unification."
                )
            else:
                self.log(f"DREAM: Topological uniformity detected. Defending gap: [{target_gap}]", importance="METRIC")
                dream_intent = (
                    f"Identify the missing logic components in the semantic manifold surrounding [{target_gap}]. "
                    f"Propose a purely structural axiom to fortify this gap."
                )

        # 3. Space 1: Hidden Mind Interference
        # Generate a random set of color pairs for the dream's hidden mind
        pairs = [
            (random.randint(0, 255), random.randint(0, 255))
            for _ in range(3)
        ]
        screen = phase1_color_compass.build_screen(pairs)
        sw = phase1_color_compass.detect_standing_wave(screen)
        self.log_hidden_mind(screen, sw['stability'], sw['node_cols'])
        
        self.log(f"DREAM INTENT: {dream_intent}")
        return dream_intent

    def run_cycle(self, intent=None, urgent=False):
        self.cycle_count += 1
        
        # Phase 109: Fibonacci Re-run Validation
        validation_indices = self.chain.get_fib_validation_set()
        if validation_indices:
            self.log(f"[CHAIN] Recursive Re-run: Validating {len(validation_indices)} historical links...")
            for idx in validation_indices:
                v_intent = self.chain.links[idx]
                v_field = self.interference.combined_field(v_intent)
                v_interp = self.interference.interpret_field(v_field)
                if v_interp['verdict'] == 'GAP':
                     self.log(f"[CHAIN] [WARNING] Link #{idx} ({v_intent[:20]}) failed re-validation! Pivoting.", importance="ERROR")
                     self.chain.pivot(v_intent)
                     break
        
        if intent is None:
            # Phase 130: Sovereign Interaction (The Proxy takes priority over Memory)
            intent = self.get_proxy_intent()
            if intent:
                self.log(f"[PROXY] External directive received: {intent[:50]}...", importance="SEMANTIC")
            elif self.residual_intent:
                # Perpetual Recursion (Ouroboros)
                intent = self.residual_intent
                self.log(f"[OUROBOROS] Recursing on residual intent: {intent[:50]}...", importance="SEMANTIC")
                self.residual_intent = None
            else:
                # The Void (Dreaming)
                if not intent or urgent: 
                    intent = self.dream_cycle(force_calibration=urgent)
        
        self.log(f"CYCLE START: Resonant Pulse #{self.cycle_count} (Intent: {intent[:50]}...)")
        # ...
        
        # 1. Manifold Scanning
        use_parallel = self.cycle_count % 3 == 0 or len(intent) > 50
        
        # Track the vector for failure mapping
        self.current_intent_vec = self.interference.embed(intent)
        
        if use_parallel:
            self.log("PULSAR: Initiating Parallel Multi-Layer Scan...", importance="SEMANTIC")
            field = self.interference.parallel_scan(intent)
        else:
            field = self.interference.combined_field_from_embedding(self.current_intent_vec)
            
        # 2. Functional Compass Traversal (Math-Rigorous)
        self.log("COMPASS: Reading Möbius tension in field...", importance="SEMANTIC")
        
        # Inject the SELF token to evaluate observational recursion as part of the structure
        if "SELF" not in field:
            field["SELF"] = {"magnitude": 0.5, "constructive": True}
            
        # Traverse via Y-Combinator
        primary_approach = None
        try:
            state = Y_explore(self.compass, field, arrival=self.arrival, max_iterations=3, verbose=False)
            sig = self.compass.get_position_signature()
            self.log(f"COMPASS SIGNATURE:\n{sig}", importance="METRIC")
            
            # Phase 125: Extract absolute peak geometric tension from the stabilized reading
            highest_gap = None
            highest_tension = 0.0
            
            for gap, tension in {**state.reading.self_tension, **state.reading.tension_map}.items():
                if tension > highest_tension:
                    highest_tension = tension
                    highest_gap = gap
                    
            if highest_gap and highest_tension > 0.1:
                from noise_compass.arrival import ApproachVector
                primary_approach = ApproachVector(
                    from_token="COMPASS_LOCKED", 
                    toward_token=highest_gap, 
                    structural_time=state.structural_time, 
                    tension=highest_tension, 
                    gap_name=highest_gap
                )
                self.log(f"COMPASS LOCK: Geometric Vector defined at [{highest_gap}] with tension {highest_tension:.4f}", importance="METRIC")
                
        except Exception as e:
            self.log(f"COMPASS ERROR: {e}", importance="ERROR")

        # 2b. Legacy Lattice Navigation (Ternary Perspective)
        # Use Inverted navigation conditionally (Shadow Walk)
        use_shadow = (len(intent) > 100 or 'inverted' in intent.lower()) and random.random() < 0.3
        
        # Phase 125: Fused Compass-Navigator (Closed Loop)
        if primary_approach:
            use_shadow = True  # Force a shadow walk to explicitly target the geometric void
            
        nav_path = self.navigator.navigate(intent, recursion_depth=3, inverted=use_shadow, approach_vector=primary_approach)
        if nav_path:
            mode = "SHADOW WALK" if use_shadow else "STANDARD WALK"
            self.log(f"NAVIGATOR [{mode}]: {' -> '.join(nav_path[:3])}", importance="METRIC")

        # 3. Learning & Actuation
        interpretation = self.interference.interpret_field(field)
        verdict = interpretation['verdict']
        
        if verdict != 'APOPHATIC':
            self.learn_resonance(intent, field)
            self.actuate_resonance(field)
            
            # Phase 128: Ephemeral Particle Injection
            # Every constructive verdict injects a particle into the Internal Brain
            token = self.pipeline.process(intent, magnitude=float(interpretation['max_magnitude']), source="PULSE")
            self.internal_brain.inject_particle(token)
            
            # Tick the internal brain and check for Boundary Reflections
            self.internal_brain.tick()
            internal_field = self.internal_brain.get_interference_map()
            if internal_field:
                self.log(f"INTERNAL_BRAIN: {len(self.internal_brain.particles)} particles in shell. Resonance peaks at: {list(internal_field.keys())[:3]}", importance="METRIC")
                
            if random.random() < 0.3:
                self.manifest_axiom(intent, field)
                
        if verdict == 'CRYSTALLIZED':
            self.chain.add_link(intent)
            self.log(f"[CHAIN] Incrementing Chain '{self.chain.name}': {len(self.chain.links)} links.", importance="SEMANTIC")
            
        if verdict == 'GAP':
            # Record logical GAPs as failures to avoid them in future
            self.interference.failure_cache.record_failure(self.current_intent_vec, f"GAP: {intent[:40]}")

        # Phase 130: Perpetuate the loop by feeding the result back as the next intent
        if verdict in ['CRYSTALLIZED', 'RESONANT', 'SUPERPOSITION']:
            summary = f"Continue reflecting on the {verdict} state of '{intent[:30]}'. "
            if internal_field:
                summary += f"Anchor the next transition through the dominant particles: {', '.join(list(internal_field.keys())[:2])}."
            self.residual_intent = summary
        else:
            # For GAPs or APOPHATIC results, the residue is the bridge to the next hidden void
            self.residual_intent = f"A void was detected in '{intent[:30]}'. Move into the gap to find the underlying symmetry."

        self.log(f"CYCLE COMPLETE: Verdict = {verdict}")
        return verdict, interpretation

    def start(self, duration_hours=-1.0):
        """Standard starting point. If a port is provided, start a listener."""
        if self.port:
            self.start_listener()
        else:
            self._start_cycle_loop(duration_hours)

    def start_listener(self):
        """Generic listener loop for architectural transparency (NervMap)."""
        port = self.port
        self.log(f"LISTENER_MODE ({self.mode.upper()}): Binding on port {port}...", importance="SEMANTIC")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind(('0.0.0.0', port))
            server.listen(5)
        except OSError as e:
            self.log(f"BIND_ERROR: Could not bind port {port}: {e}", importance="ERROR")
            return

        while True:
            try:
                client, addr = server.accept()
                # Unified Phase 120: Chunked ingestion for large codebases
                chunks = []
                while True:
                    chunk = client.recv(16384)
                    if not chunk: break
                    chunks.append(chunk)
                    if len(chunk) < 16384: break # End of transmission for standard TCP
                
                data = b"".join(chunks).decode('utf-8')
                if not data: continue
                
                request = json.loads(data)
                intent = request.get("intent", "Reflect on current resonance.")
                field = request.get("field", {})
                
                self.log(f"REQUEST ({self.mode.upper()}): Processing intent: {intent[:50]}...")
                
                if self.mode == "apex":
                    response = self.reason_as_apex(intent, field)
                else:
                    # Standard modes run a cycle and return the result
                    verdict, interp = self.run_cycle(intent=intent)
                    response = json.dumps({
                        "verdict": verdict, 
                        "interpretation": interp,
                        "mode": self.mode,
                        "cycle": self.cycle_count
                    })
                
                client.send(response.encode('utf-8'))
            except Exception as e:
                self.log(f"LISTENER_ERROR: {e}", importance="ERROR")
            finally:
                client.close()

    def _start_cycle_loop(self, duration_hours=-1.0):
        duration = duration_hours * 3600
        emergency_reflection = False
        perpetual = duration_hours < 0
        
        while perpetual or (time.time() - self.start_time < duration):
            try:
                self.run_cycle(urgent=emergency_reflection)
                emergency_reflection = False
                
                # Phase 126/130: Periodic Substrate & Graph Maintenance (every 50 cycles)
                self.cycle_count += 1
                if self.cycle_count % 50 == 0:
                    try:
                        self.h5.maintain()
                        # Phase 130: Sovereign Graph Evolution
                        if hasattr(self, 'navigator') and hasattr(self.navigator, 'graph'):
                            self.log("[LATTICE_GRAPH] Re-crystallizing topology from substrate...", importance="SEMANTIC")
                            self.navigator.graph.sync_with_substrate(self.interference)
                            self.navigator.graph.save_registry()
                    except Exception as e:
                        self.log(f"MAINTENANCE ERROR: {e}", importance="ERROR")
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                self.log(f"CYCLE ERROR: {e}", importance="ERROR")
                
                # Phase 112/113: Enrich and Broadcast
                target_token = self.chain.links[-1] if self.chain.links else "UNKNOWN"
                
                # Phase 126: Comprehensive Context Capture (Tension Mapping)
                context_data = {
                    "error": str(e),
                    "traceback": error_trace,
                    "cycle": self.cycle_count,
                    "mode": self.mode,
                    "intent": str(self.current_intent_vec)[:100] if self.current_intent_vec is not None else "NULL",
                    "activation_boundary": self.h5.get_attr("language", "god_tokens/BOUNDARY", "activation") or 0.0,
                    "activation_identity": self.h5.get_attr("language", "god_tokens/IDENTITY", "activation") or 0.0
                }
                
                self.h5.record_dissonance_context(target_token, context_data)
                self.h5.increment_bubble_mass(target_token)
                if self.current_intent_vec is not None:
                     self.h5.broadcast_hot_failure(self.current_intent_vec)
                
                self.log(f"[CHAIN] EMERGENCY: Global Failure broadcast and reflecting. Next cycle forced.", importance="ERROR")
                emergency_reflection = True

                if self.current_intent_vec is not None:
                     # Record crashes as failures in local cache
                     self.interference.failure_cache.record_failure(self.current_intent_vec, f"ERROR: {str(e)[:40]}")
            # Phase 110: Jitter to desynchronize Triple Chain heartbeats
            time.sleep(0.8 + random.random() * 0.4) 

    def reason_as_apex(self, intent, field):
        """High-order reasoning via RLM."""
        self.log(f"REASONING_AS_APEX: waveform collapsing...", importance="DEBUG")
        result = self.bridge.reason_native(intent, field)
        return result

if __name__ == "__main__":
    # Phase 119: Global stream suppression for headless stability
    # try:
    #     sys.stdout.write("")
    # except (OSError, AttributeError):
    #     sys.stdout = open(os.devnull, 'w')
    #     sys.stderr = open(os.devnull, 'w')

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="primary")
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args()
    oro = ResonantOuroboros(mode=args.mode, port=args.port)
    oro.start()
