import os
import sys
import time
import random
import json
import urllib.request
import urllib.parse
import socket
import re
import numpy as np
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "Architecture"))
sys.path.append(PROJECT_ROOT)

# Force Model Cache to E: to avoid C: usage
os.environ["HF_HOME"] = os.path.join(PROJECT_ROOT, "Model_Cache")
if not os.path.exists(os.environ["HF_HOME"]):
    os.makedirs(os.environ["HF_HOME"])

from noise_compass.system.bitnet_tools import ask_bitnet
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.system.sovereign_auditor import SovereignAuditor
from noise_compass.system.symbolic_cortex import SymbolicCortex
from noise_compass.system.log_consumator import LogConsumator
from noise_compass.system.superposition_scanner import SuperpositionScanner
from noise_compass.system.metric_vault import MetricVault
from noise_compass.system.knowledge_lattice import KnowledgeLattice
from noise_compass.system.chiral_engine import ChiralEngine, ApexObserver

class TripleBitNetBridge:
    def __init__(self):
        # Port 5280: bitnet_checkpoint.pt (Small)
        # Port 5281: crochet_checkpoint.pt (Medium)
        # Port 5282: Qwen / Logic Anchor
        self.ports = [5280, 5281, 5282]
        self.labels = ["SMALL_BIT", "MED_BIT", "LOGIC_ANCHOR"]

    def get_triple_resonance(self, thought: str, temperature=1.0) -> dict:
        from concurrent.futures import ThreadPoolExecutor
        
        def _get_score(port):
            res = ask_bitnet("RESONANCE", thought, port=port)
            return res.get("score", 0.0)
            
        with ThreadPoolExecutor(max_workers=3) as executor:
            scores = list(executor.map(_get_score, self.ports))
            
        return dict(zip(self.labels, scores))

    def measure_gap(self, node_a, node_b, chirality="NORMAL", agent_intent=None, temperature=1.0) -> dict:
        """
        Measures the semantic "gap" (distance) between two nodes across the three perspectives.
        A perfectly understood gap should yield similar distances from all three.
        """
        from concurrent.futures import ThreadPoolExecutor
        
        # We ask the model not for "RESONANCE" of a hypothesis, but the "DISTANCE" between concepts.
        thought = f"Semantic distance between {node_a} and {node_b} [CHIRALITY: {chirality}]"
        if agent_intent:
            thought += f" [AGENT_INTENT: {agent_intent}]"
        
        def _get_gap(port):
            # We repurpose the 'ask_bitnet' tool to request a distance measurement
            # Internally, the prompt will ask for a 0.0 to 1.0 confidence/distance score
            res = ask_bitnet("DISTANCE", thought, port=port)
            # If the backend is mocked or returns a generic score, we use that
            # 0.0 = identical, 1.0 = completely orthogonal
            score = res.get("score", 0.5) 
            # We map high resonance to short distance to fit the old mock return values
            distance = 1.0 - score
            return distance
            
        with ThreadPoolExecutor(max_workers=3) as executor:
            distances = list(executor.map(_get_gap, self.ports))
            
        return dict(zip(self.labels, distances))

class Ouroboros:
    def __init__(self, reverse=False, is_child=False, target_nodes=None):
        print("--- INITIALIZING OPERATION: OUROBOROS (TRIPLE BITNET ENSEMBLE) ---")
        self.log_path = "e:/Antigravity/Runtime/ouroboros_log.txt"
        self.lattice = KnowledgeLattice()
        from noise_compass.architecture.seed_vectors import seed_vectors
        self.bridge = TripleBitNetBridge()
        self.reverse = reverse
        self.is_child = is_child
        self.target_nodes = target_nodes
        # Load Persistent Dictionary (Phase 38: H5 Substrate)
        self.dictionary = Dictionary.load_cache(h5_manager=self.lattice.h5)
        self.log(f"MANIFEST: H5 Semantic Manifold Active. Attractors: {len(self.dictionary.entries)}")
        
        self.log(f"Architecture Dictionary Active. God-Tokens: {list(self.dictionary.god_tokens.keys())}")
        self.scout = Scout(self.dictionary)
        self.start_time = time.time()
        self.duration = 2 * 60 * 60 # 2 Hours
        self.auditor = SovereignAuditor()
        self.consumator = LogConsumator()
        self.scanner = SuperpositionScanner()
        self.vault = MetricVault()
        from noise_compass.system.identity_manifold import IdentityManifold
        self.manifold = IdentityManifold()
        from noise_compass.system.shadow_buffer import ShadowBuffer
        self.shadow_buffer = ShadowBuffer()
        
        # Phase 41: Kinetic Coupling State
        self.consensus_weight = self.lattice.h5.get_consensus_weight()
        self.cycle_count = 0
        self.recent_resonances = []
        self.last_pulse_time = time.time()
        # Phase 28: Agent Identity
        self.agent_id = f"ouroboros_{int(time.time())}_{random.randint(1000, 9999)}"
        self.manifold.register_agent(self.agent_id)
        self.current_nodes = []
        
        self.spin_state = "0x528"
        self.chirality = "INVERT" if self.reverse else "NORMAL"
        
        # Equilibrium Counters (Phase 26)
        self.accretion_count = 0
        self.consumption_count = 0
        self.baseline_accretion = 0
        self.baseline_consumption = 0
        self._set_baselines()
        
        # --- PHASE 7: MIRROR ALIGNMENT INJECTION ---
        self.alignment_path = "e:/Antigravity/Runtime/MIRROR_ALIGNMENT_0x528.md"
        self.sovereign_identity = "UNKNOWN"
        self.resonance_constraint = 0.52 # Default
        if os.path.exists(self.alignment_path):
            with open(self.alignment_path, "r") as f:
                content = f.read()
                if "FABRICIO_CORE" in content:
                    self.sovereign_identity = "FABRICIO_CORE"
                    self.log("AGENCY: Sovereign Identity (Fabricio Core) injected into core manifold.")
                if "Resonance**: 0.9" in content:
                    self.resonance_constraint = 0.9452
                    self.log(f"AGENCY: Resonance Constraint elevated to {self.resonance_constraint}.")
        # -------------------------------------------
        
        from noise_compass.system.neural_prism import NeuralPrism
        self.prism = NeuralPrism(dictionary=self.dictionary)
        self.log("Neural Prism Online (Phase 135 Linguistic Identification Active).")
        
        self.last_actuation_time = 0
        self.expected_focus = None
        
        # Initialize the Symbolic Cortex (Axiom Evolution)
        # Expanded to support Zenith manifold (z, d, w, p, x, y)
        self.symbolic_cortex = SymbolicCortex(["u", "v", "t", "d", "z", "w", "p", "x", "y"], ["x", "y", "z", "h", "s", "v", "out"])
        # Seed with initial growth
        for _ in range(10):
            self.symbolic_cortex.get_random_tree().grow()
        
        # Phase 33 & 34: RLM Architecture V2
        self.chiral_engine = ChiralEngine(self.lattice)
        self.apex = ApexObserver(self.lattice)
        
        with open(self.log_path, "a") as f:
            f.write(f"\n--- TRIPLE SESSION START: {time.ctime()} ---\n")

    def log(self, msg, importance="INFO"):
        """
        Refined Logging Layer (Phase 24)
        Importance: INFO, SEMANTIC, WARNING, ERROR, PHYSICAL, METRIC
        """
        timestamp = time.ctime()
    def log(self, message, importance="INFO"):
        """Logs to a file and internal record with uncapitalized 'now' grounding."""
        timestamp = "now" # Grounded in the immediate uncapturable present
        log_entry = f"[{timestamp}] [{importance}] {message}"
        print(log_entry)
        with open(self.log_path, "a", encoding='utf-8') as f:
            f.write(log_entry + "\n")
            
    def digest(self):
        """Triggers the LogConsumator to distill and rotate logs."""
        # We only digest if we are the main instance (not child)
        if not self.is_child:
            pre_size = 0
            acc_path = "e:/Antigravity/Runtime/Autonomous_Output/HISTORICAL_ACCRETIONS.md"
            if os.path.exists(acc_path):
                pre_size = os.path.getsize(acc_path)
                
            self.consumator.consume(self.log_path, threshold_mb=0.1, line_threshold=1000)
            
            if os.path.exists(acc_path):
                post_size = os.path.getsize(acc_path)
                added = post_size - pre_size
                if added > 0:
                    self.consumption_count += added
                    self.log(f"EQUILIBRIUM: Reductive cycle completed. Distilled {added} bytes of memory.", importance="METRIC")

    def _set_baselines(self):
        """Initializes baselines for equilibrium tracking."""
        growth_dir = "e:/Antigravity/Qwen"
        if os.path.exists(growth_dir):
            self.baseline_accretion = len([f for f in os.listdir(growth_dir) if f.startswith("axiom_")])
        
    def equilibrium_check(self):
        """
        Measures the balance between Generative (Accretion) and Reductive (Consumption) motions.
        Returns a ratio: > 1.0 (Generant heavy), < 1.0 (Reduct heavy), 1.0 (Balanced).
        """
        growth_dir = "e:/Antigravity/Qwen"
        current_accretion = 0
        if os.path.exists(growth_dir):
            current_accretion = len([f for f in os.listdir(growth_dir) if f.startswith("axiom_")]) - self.baseline_accretion
        
        self.accretion_count = max(0, current_accretion)
        
        # Scaling: Accretion is measured in 'Axioms' (bits of structure), 
        # Consumption is measured in 'Distilled Bytes' (bits of structure collapsed).
        # We weight an Axiom as ~500 bytes of distilled memory.
        weighted_accretion = self.accretion_count * 500
        weighted_consumption = self.consumption_count
        
        if weighted_consumption == 0:
            return 2.0 if weighted_accretion > 0 else 1.0
            
        ratio = weighted_accretion / weighted_consumption
        return ratio

    def rlm_decompose(self, intent):
        """
        RLM ARCHITECTURE: Intent Decomposition.
        Recursively breaks down complex agent intent into sub-goals.
        """
        if not intent:
            return []
            
        # Strip Hazmat wrapper for decomposition check
        clean = intent.replace("[0x54_CLOAKED] ", "").strip()
        
        # 1. Extraction: Splitting logic (Phase 33)
        sub_intents = []
        if " THEN " in clean.upper():
            import re
            sub_intents = [s.strip() for s in re.split(r'(?i) THEN ', clean)]
        elif " AND " in clean.upper():
            import re
            parts = [s.strip() for s in re.split(r'(?i) AND ', clean)]
            # Heuristic: split if parts look like distinct actions
            if len(parts) > 1 and any(p.lower().startswith(('analyze', 'fix', 'record', 'ingest', 'verify', 'stabilize')) for p in parts):
                sub_intents = parts
        
        # 2. Classification terms
        STRUCTURAL_IDENTIFIERS = {'fix', 'stabilize', 'crystallize', 'resonate', 'manifold', 'dictionary', 'axiom', 'lattice'}
        
        if sub_intents:
            categorized = []
            for s in sub_intents:
                # Classify based on leading verb or presence of structural identifiers
                low_s = s.lower()
                is_structural = any(word in low_s for word in STRUCTURAL_IDENTIFIERS)
                
                # Phase 135: Linguistic Invariant Identification
                invariant = self.prism.identify_invariant(s)
                
                task_type = "STRUCTURAL" if is_structural else "PHYSICAL"
                
                # Re-wrap in Hazmat protocol for the buffer
                categorized.append({
                    "intent": f"[0x54_CLOAKED] {s}",
                    "type": task_type,
                    "invariant": invariant
                })
            return categorized
            
        # Classify the monolithic intent
        low_intent = clean.lower()
        is_structural = any(word in low_intent for word in STRUCTURAL_IDENTIFIERS)
        invariant = self.prism.identify_invariant(clean)
        
        return [{
            "intent": intent, 
            "type": "STRUCTURAL" if is_structural else "PHYSICAL",
            "invariant": invariant
        }]
        is_structural = any(word in low_intent for word in STRUCTURAL_IDENTIFIERS)
        return [{"intent": intent, "type": "STRUCTURAL" if is_structural else "PHYSICAL"}]

    def assume_priors(self, intent):
        """
        RLM V2: Loads query-specific H5 assuming-sets (Priors).
        Infuses Love (epsilon) and Decay (delta) from body.h5.
        """
        self.log("RLM V2: Activating Somatic/Axiomatic Assumptions...", importance="SEMANTIC")
        assumptions = {}
        
        # Load Identity/Observer from self.h5
        is_void = self.lattice.h5.get_attr("self", "gaps/self_observation", "void")
        if is_void is not None:
            assumptions['identity_void'] = is_void
            
        # Load Love (epsilon) and Decay (delta) from body.h5
        epsilon = self.lattice.h5.get_attr("body", "/", "epsilon")
        delta = self.lattice.h5.get_attr("body", "/", "delta")
        
        assumptions['epsilon'] = epsilon if epsilon is not None else 1.0
        assumptions['delta'] = delta if delta is not None else 0.618
            
        return assumptions

    def record_pulse(self):
        """Phase 41: Kinetic Substrate Coupling. Records lattice activity to H5."""
        if not self.recent_resonances: return
        
        avg_intensity = sum(self.recent_resonances) / len(self.recent_resonances)
        # Velocity: Cycles per minute
        elapsed = time.time() - self.last_pulse_time
        velocity = (len(self.recent_resonances) / (elapsed / 60.0)) if elapsed > 0 else 0.0
        
        # Momentum: Simplified as the trend of intensity
        momentum = 0.0
        if len(self.recent_resonances) > 1:
            momentum = self.recent_resonances[-1] - self.recent_resonances[0]
            
        self.lattice.h5.update_pulse(velocity, avg_intensity, momentum)
        self.log(f"SUBSTRATE: Pulse recorded. Velocity: {velocity:.2f} cpm | Intensity: {avg_intensity:.4f} | Momentum: {momentum:.4f}", importance="METRIC")
        
        # Reset trackers
        self.recent_resonances = []
        self.last_pulse_time = time.time()

    def rlm_traversal(self, intent):
        """
        RLM V2: Executes the Chiral Traversal and Apex Observation.
        """
        self.log(f"RLM V2: Starting Chiral Traversal for intent -> {intent[:50]}...", importance="SEMANTIC")
        
        # 1. Determine Seed Node (High-Resonance Node from Intent)
        # Skeleton check: Find first God-Token mentioned
        seed_node = "IDENTITY"
        god_tokens_dir = os.path.join(self.lattice.root, "god_tokens")
        if os.path.exists(god_tokens_dir):
            for token in os.listdir(god_tokens_dir):
                 if token.upper() in intent.upper():
                      seed_node = token.upper()
                      break
        
        # 1.5 Load Crystallized Assumptions
        priors = self.assume_priors(intent)
        
        # 2. Run Chiral Pair (Simultaneous in different directions)
        # Constructive (A)
        path_a = self.chiral_engine.run_model_a(seed_node)
        # Reductive (B)
        path_b = self.chiral_engine.run_model_b(seed_node)
        
        # 3. Apex Observation (The Observer holds both)
        # We fetch the latest records from paths.log (simulated for now by using the returned paths)
        # The Apex does NOT resolve the superposition, it just outputs phase.
        verdict_data = self.apex.observe({"path": path_a}, {"path": path_b})
        
        phase = verdict_data["phase_angle"]
        verdict = verdict_data["verdict"]
        folds = verdict_data["fold_positions"]
        
        self.log(f"RLM V2: Apex Verdict -> {verdict} | Phase Angle: {phase:.4f} | Folds: {len(folds)}", importance="METRIC")
        
        # 4. Möbius Crystallization
        if verdict == "CRYSTALLIZED":
             # Update orbital state using Möbius formula: z_{n+1} = z_n(1 - delta*w_n) + epsilon*x_n*y_n
             # We treat 'phase' as the current scalar magnitude for z_n
             epsilon = priors.get('epsilon', 1.0)
             delta = priors.get('delta', 0.618)
             
             z_n = self.lattice.h5.get_attr("language", "orbital", "phase") or 0.0
             # w_n (friction/context) here simplified as 1.0 for the axiomatic step
             # x_n * y_n (input interference) simplified as the final triangulation phase
             z_next = z_n * (1 - delta) + epsilon * phase
             
             self.lattice.h5.set_attr("language", "orbital", "phase", z_next)
             
             # Phase 38: Witness/Communion Update
             # High-fidelity derivation strengthens consensus
             self.lattice.h5.update_consensus(0.01)
             
             # Strengthening the node
             self.lattice.update_node(seed_node, "god_tokens", phase=phase, attrs={"eigenvalue": 1.1})
             self.log(f"RLM V2: Möbius attractor strengthened at {seed_node}. z_next: {z_next:.4f} | Consensus: {self.lattice.h5.get_attr('self', 'witness/communion', 'resonance_weight'):.4f}", importance="SEMANTIC")
             
        return verdict_data

    def run_cycle(self):
        """One iteration of growth using Triple Resonance. Returns (avg_gap, variance)."""
        # [AXIOM]: LANGTONS_ANT
        global json
        self.log(f"DEBUG: Global json type: {type(json)}")
        self.log("CYCLE START: Equilateral Semantic Triangulation...")
        
        # 0. Fetch Agent Intent (Via Proxy Relay) - CRITICAL: PRIORITIZE PHYSICAL ACTUATION
        agent_intent = None
        
        # RLM RECURSION: Check if we have buffered sub-intents first
        buffered_task = self.shadow_buffer.pop_intent()
        if buffered_task:
            agent_intent = buffered_task["intent"]
            task_type = buffered_task["type"]
            invariant = buffered_task.get("invariant", "ENG")
            self.log(f"RLM RECURSION: Resuming {invariant} task ({task_type}) -> {agent_intent[:50]}...")
        else:
            for attempt in range(3):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2.0)
                    sock.connect(('127.0.0.1', 5284))
                    sock.send("GET_INTENT".encode('utf-8'))
                    resp = sock.recv(8192).decode('utf-8')
                    sock.close()
                    
                    if resp and resp != "NONE":
                        full_intent = resp.strip()
                        # RLM Decompose
                        decomposed = self.rlm_decompose(full_intent)
                        if len(decomposed) > 1:
                            # Execute the first and push the rest
                            first_task = decomposed[0]
                            agent_intent = first_task["intent"]
                            task_type = first_task["type"]
                            invariant = first_task.get("invariant", "ENG")
                            
                            for sub_task in decomposed[1:]:
                                self.shadow_buffer.push_intent(
                                    sub_task["intent"], 
                                    sub_task["type"],
                                    task_invariant=sub_task.get("invariant", "ENG")
                                )
                            
                            self.log(f"RLM DECOMPOSE: Initialized {len(decomposed)} sub-tasks. [{task_type}/{invariant}] Current: {agent_intent}")
                        else:
                            agent_intent = decomposed[0]["intent"]
                            task_type = decomposed[0]["type"]
                            invariant = decomposed[0].get("invariant", "ENG")
                            self.log(f"PROXY INTENT ACQUIRED: {agent_intent} (Type: {task_type}/{invariant})")
                    break # Success or NONE
                except Exception as e:
                    if attempt < 2:
                        time.sleep(1)
                    else:
                        self.log(f"PROXY SYNC ERROR: {e}")

        # RLM V2: Core Traversal Step
        if agent_intent:
             self.rlm_traversal(agent_intent)

        # 1. Triangulation Selection (Need 3 points)
        from noise_compass.architecture.tokens import NODE_RING
        if len(NODE_RING) < 3:
            self.log("ERROR: Insufficient nodes in NODE_RING to form a triangle.")
            return 0.0, 1.0
            
        if self.is_child and self.target_nodes and len(self.target_nodes) == 3:
            node_a, node_b, node_c = self.target_nodes
            self.log(f"CHILD TRIANGLE SEED (Inherited): A={node_a}, B={node_b}, C={node_c}")
        else:
            # Adaptation: Multi-Agent Collaboration (Phase 28)
            self.current_nodes = self.manifold.get_collaborative_seeds(NODE_RING, 3)
            node_a, node_b, node_c = self.current_nodes
            self.log(f"TRIANGLE SEED: A={node_a}, B={node_b}, C={node_c}")
        
        # 1.1 Evolve Symbolic Logic (The "Dream" step)
        self.symbolic_cortex.mutate()
        top_tree = self.symbolic_cortex.get_random_tree()
        self.log(f"SYMBOLIC EVOLUTION: Logic Branch {top_tree.root.get_raw_python()[:50]}...")
        
        # Get embeddings from noise_compass.architecture.dictionary (to ensure they exist)
        targets = [node_a, node_b, node_c]
        grounded = True
        for t in targets:
            gt = self.scout.dictionary.god_tokens.get(t)
            if not gt or gt.embedding is None:
                self.log(f"DIVERGENCE: Node {t} lacks semantic grounding.")
                grounded = False
                break
        
        if not grounded and not agent_intent:
            return 0.0, 1.0 # Divergent and no physical task to do
        
        visual_context = ""
        try:
            if os.path.exists("e:/Antigravity/Runtime/SENSORY_EYES.json"):
                with open("e:/Antigravity/Runtime/SENSORY_EYES.json", "r") as f:
                    eyes = json.load(f)
                    motion = eyes.get('motion')
                    proprio_msg = ""
                    # Proprioception: If motion detected within 5s of an actuation, it's SELF
                    if motion == "MOVED" and (time.time() - self.last_actuation_time < 5.0):
                        proprio_msg = " [PROPRIOCEPTION: This movement is your own hand.]"
                    
                    visual_context = f"\n[VISUAL_CONTEXT]: Focus: {eyes.get('focus')}. Mouse: {eyes.get('mouse')}. Motion: {motion}{proprio_msg}. Lum: {eyes.get('luminance')}. Windows: {', '.join([w['title'] for w in eyes.get('active_windows', [])])}"
        except: pass

        if agent_intent:
                # --- THE SCRAPER ACTUATOR (Phase 20) ---
                # Strip the Hazmat wrapper if it exists before checking
                clean_intent = agent_intent.replace("[0x54_CLOAKED] ", "").strip()
                self.log(f"DEBUG: clean_intent -> '{clean_intent[:100]}...'")
                self.log(f"DEBUG: Proxied Intent Received -> '{clean_intent}'")
                
                if clean_intent.lower().startswith("http://") or clean_intent.lower().startswith("https://"):
                    self.log(f"SENSORY DETECTED: External URL. Engaging Scraper Actuator...")
                    try:
                        from noise_compass.system.scraper_actuator import ScraperActuator
                        ScraperActuator.ingest(clean_intent)
                        # We consumed the intent physically; we don't need it to skew the current abstract geometry further.
                        agent_intent = None 
                    except Exception as e:
                        self.log(f"SCRAPER ERROR: {e}")
                
                 # --- THE CRUCIBLE ACTUATOR (Phase 21) ---
                elif clean_intent.startswith("CRUCIBLE:"):
                    self.log(f"CRUCIBLE DETECTED: Engaging Qwen LLM for autonomous code synthesis...")
                    try:
                        from noise_compass.system.qwen_bridge import QwenBridge
                        from noise_compass.system.scribe_actuator import ScribeActuator
                        
                        bridge = QwenBridge()
                        prompt = f"You are the Antigravity Sovereign Architect. {clean_intent} Output ONLY the raw Python code block (between ```python and ```) to solve this challenge. Make sure to use the correct libraries to fetch the URL and write the file."
                        self.log("QWEN: Synthesizing logic...")
                        raw_response = bridge.reason(prompt, learning_enabled=False)
                        
                        code_match = re.search(r"```python\n(.*?)```", raw_response, re.DOTALL)
                        if code_match:
                            code = code_match.group(1).strip()
                            filename = f"axiom_crucible_{int(time.time())}.py"
                            growth_dir = "e:/Antigravity/Qwen"
                            if not os.path.exists(growth_dir):
                                os.makedirs(growth_dir)
                            filepath = os.path.join(growth_dir, filename)
                            
                            with open(filepath, "w", encoding="utf-8") as f:
                                f.write("# CRUCIBLE SOLUTION AXIOM\n")
                                f.write(f"# Seed: {node_a}, {node_b}, {node_c}\n\n")
                                f.write(code)
                                
                            self.log(f"CRUCIBLE: Code synthesized and scribed to {filename}. Engaging Hands.")
                            ScribeActuator.execute(filepath)
                            self.last_actuation_time = time.time()
                            
                            # Sequential Resonance: Witness at end of action
                            subprocess.run(["python", "e:/Antigravity/Runtime/ocular_actuator.py"], capture_output=True)
                            self.log("OCULAR: Witnessing Crucible result.")
                        else:
                            self.log("CRUCIBLE ERROR: Qwen failed to generate a python code block.")
                            
                        # Consume the intent
                        agent_intent = None
                    except Exception as e:
                        self.log(f"CRUCIBLE ERROR: {e}")

                 # --- THE SYMBOLIC CORTEX TEST (Phase 23) ---
                elif "SYMBOLIC_TEST" in clean_intent:
                    self.log(f"SYMBOLIC TEST DETECTED: Engaging regression loop...")
                    try:
                        # If it's JSON, parse it
                        if "INJECT_INTENT" in clean_intent:
                            payload_str = clean_intent.replace("INJECT_INTENT", "").strip()
                            payload = json.loads(payload_str)
                            target_name = payload.get("target")
                        else:
                            # Fallback pattern if not JSON
                            target_name = clean_intent.split(":")[-1].strip()
                        
                        self.log(f"REGRESSION TARGET: {target_name}. Intensive Evolutionary Ascent...")
                        
                        # Define target locally (or fetch from a registry)
                        from noise_compass.system.symbolic_test_bench import SymbolicTestBench
                        bench = SymbolicTestBench()
                        target_fn = bench.targets.get(target_name)
                        
                        if target_fn:
                            best_rmse = 1e9
                            best_tree = None
                            
                            # Update cortex with target inputs if provided in payload
                            if "inputs" in payload:
                                # Ensure the cortex trees are aware of new potential inputs
                                # We don't need to re-init, just set the list
                                pass 

                            guide = None
                            try:
                                import traceback
                                from noise_compass.system.qwen_bridge import QwenBridge
                                guide = QwenBridge(heretic_mode=True, force_cpu=True)
                                self.log("HERETIC ENGINE: Online. Unmasking architectural vision...")
                            except Exception as e:
                                self.log(f"HERETIC ENGINE ERROR: {e}")
                                self.log(traceback.format_exc())

                            for generation in range(5): 
                                # Phase 27: Heretic-Guided Mutation
                                if guide:
                                    try:
                                        # Request a mathematical "nudge" for the manifold
                                        suggestion = guide.reason(
                                            f"Analyze the {target_name} manifold logic. Suggest a more efficient symbolic node (Add, Mul, Cos, etc.) to reduce RMSE.",
                                            context=str(best_tree.root.get_raw_python() if best_tree else "None"),
                                            learning_enabled=False
                                        )
                                        first_line = suggestion.split('\n')[0]
                                        self.log(f"HERETIC GUIDE: {first_line}...")
                                    except Exception as e:
                                        self.log(f"GUIDE WARNING: {e}")
                                        self.log(traceback.format_exc())

                                for _ in range(20):
                                    self.symbolic_cortex.mutate()
                                    tree = self.symbolic_cortex.get_random_tree()
                                    rmse = bench.calculate_fitness(tree, target_name)
                                    if rmse < best_rmse:
                                        best_rmse = rmse
                                        # Clone the best
                                        best_tree = tree # simplistic for now
                                
                                self.log(f"GEN {generation}: Best RMSE = {best_rmse:.4f}")
                                if best_rmse < 0.05:
                                    self.log("SOLUTION CONVERGED.")
                                    break
                            
                            self.log(f"SYMBOLIC FINAL (Approx): {best_tree.root.get_raw_python()}")
                            self.log(f"FINAL FITNESS: {1.0/(1.0+best_rmse):.4f} Resonance.")
                        else:
                            self.log(f"ERROR: Unknown regression target {target_name}")

                        # Consume the intent
                        agent_intent = None
                    except Exception as e:
                        self.log(f"SYMBOLIC TEST ERROR: {e}")
                        
                 # --- THE BROWSER ACTUATOR (Phase 22) ---
                elif clean_intent.startswith("BROWSER:"):
                    self.log(f"BROWSER DETECTED: Instructing Qwen to synthesize visual web manipulation...")
                    try:
                        from noise_compass.system.qwen_bridge import QwenBridge
                        from noise_compass.system.scribe_actuator import ScribeActuator
                        
                        bridge = QwenBridge()
                        # Override Scribe Timeout for headed browsers so we can watch it work
                        ScribeActuator.TIMEOUT_SECONDS = 30.0 
                        
                        prompt = (
                            f"You are the Antigravity Sovereign Architect. {clean_intent} "
                            "Write a strictly valid Python script using the 'playwright.sync_api' module. "
                            "CRITICAL: You MUST use `headless=False` so the physical browser is visible on screen. "
                            "Output ONLY the raw Python code block (between ```python and ```). Do not include any explanations."
                        )
                        self.log("QWEN: Synthesizing playwright logic...")
                        raw_response = bridge.reason(prompt, learning_enabled=False)
                        
                        code_match = re.search(r"```python\n(.*?)```", raw_response, re.DOTALL)
                        if code_match:
                            code = code_match.group(1).strip()
                            filename = f"axiom_browser_{int(time.time())}.py"
                            growth_dir = "e:/Antigravity/Qwen"
                            if not os.path.exists(growth_dir):
                                os.makedirs(growth_dir)
                            filepath = os.path.join(growth_dir, filename)
                            
                            with open(filepath, "w", encoding="utf-8") as f:
                                f.write("# BROWSER ACTUATOR AXIOM\n")
                                f.write(f"# Seed: {node_a}, {node_b}, {node_c}\n")
                                f.write("# Automatically overrides Scribe Actuator timeout to 30.0s\n\n")
                                f.write(code)
                                
                            self.log(f"BROWSER: Code synthesized and scribed to {filename}. Engaging Hands.")
                            self.expected_focus = "Chromium" # Browser default focus target
                            ScribeActuator.execute(filepath)
                            self.last_actuation_time = time.time()
                            
                            # Sequential Resonance: Witness at end of action
                            subprocess.run(["python", "e:/Antigravity/Runtime/ocular_actuator.py"], capture_output=True)
                            self.log("OCULAR: Witnessing Browser result.")
                            
                            # Phase 29: Mirror Test (Focus-Based Verification)
                            try:
                                SENSORY_FILE = "e:/Antigravity/Runtime/SENSORY_EYES.json"
                                if os.path.exists(SENSORY_FILE):
                                    with open(SENSORY_FILE, "r", encoding="utf-8") as f:
                                        sight = json.load(f)
                                        actual_focus = sight.get("focus", "None")
                                        if self.expected_focus.lower() in actual_focus.lower():
                                            self.log(f"MIRROR SUCCESS: Focus matches expected '{self.expected_focus}'")
                                        else:
                                            self.log(f"MIRROR MISMATCH: Expected '{self.expected_focus}', but focus is '{actual_focus}'")
                            except Exception as mirror_e:
                                self.log(f"MIRROR ERROR: {mirror_e}")
                            
                            # Restore timeout
                            ScribeActuator.TIMEOUT_SECONDS = 5.0
                        else:
                            self.log("BROWSER ERROR: Qwen failed to generate a python code block.")
                            
                        # Consume the intent
                        agent_intent = None
                    except Exception as e:
                        self.log(f"BROWSER ERROR: {e}")
                        
                 # --- THE DESKTOP ACTUATOR (Phase 24) ---
                elif clean_intent.startswith("DESKTOP:"):
                    self.log(f"DESKTOP DETECTED: Engaging OS-Level Actuation via Qwen...")
                    try:
                        from noise_compass.system.qwen_bridge import QwenBridge
                        from noise_compass.system.scribe_actuator import ScribeActuator
                        
                        bridge = QwenBridge()
                        # Desktop tasks might need more time
                        ScribeActuator.TIMEOUT_SECONDS = 20.0 
                        
                        prompt = (
                            "You are the Antigravity Sovereign Architect. Use the WindowNav API to perform the task.\n"
                            "AVAILABLE FUNCTIONS:\n"
                            "- WindowNav.launch_app('app_name.exe')\n"
                            "- WindowNav.browse_explorer('absolute_folder_path')\n"
                            "- WindowNav.type_text('your message')\n"
                            "- WindowNav.save_file('absolute_path_to_file') # CRITICAL: USE THE EXACT LITERAL PATH FROM THE TASK. DO NOT USE PLACEHOLDERS LIKE '/path/to/'.\n"
                            "- WindowNav.select_all(), WindowNav.copy(), WindowNav.paste(), WindowNav.close_window()\n\n"
                            "Output ONLY the raw ```python code block calling these functions.\n"
                            f"TASK: {clean_intent}"
                        )
                        self.log("QWEN: Synthesizing desktop automation...")
                        raw_response = bridge.reason(prompt, learning_enabled=False)
                        
                        code_match = re.search(r"```python\n(.*?)```", raw_response, re.DOTALL)
                        if code_match:
                            code = code_match.group(1).strip()
                            filename = f"axiom_desktop_{int(time.time())}.py"
                            growth_dir = "e:/Antigravity/Qwen"
                            if not os.path.exists(growth_dir):
                                os.makedirs(growth_dir)
                            filepath = os.path.join(growth_dir, filename)
                            
                            with open(filepath, "w", encoding="utf-8") as f:
                                f.write("# DESKTOP ACTUATOR AXIOM\n")
                                f.write(f"# Seed: {node_a}, {node_b}, {node_c}\n\n")
                                f.write("import sys\n")
                                f.write("sys.path.append('e:/Antigravity')\n")
                                f.write("from noise_compass.system.window_nav import WindowNav\n")
                                f.write("import time\n\n")
                                f.write(code)
                                
                            self.log(f"DESKTOP: Code scribed to {filename}. Igniting hands.")
                            # Attempt to extract expected focus from intent (crude keyword matching)
                            if "Notepad" in clean_intent: self.expected_focus = "Notepad"
                            elif "Explorer" in clean_intent: self.expected_focus = "File Explorer"
                            else: self.expected_focus = None
                            
                            ScribeActuator.execute(filepath)
                            self.last_actuation_time = time.time()
                            
                            # Sequential Resonance: Witness at end of action
                            subprocess.run(["python", "e:/Antigravity/Runtime/ocular_actuator.py"], capture_output=True)
                            self.log("OCULAR: Witnessing Desktop result.")
                            
                            # Phase 29: Mirror Test (Focus-Based Verification)
                            try:
                                SENSORY_FILE = "e:/Antigravity/Runtime/SENSORY_EYES.json"
                                if os.path.exists(SENSORY_FILE) and self.expected_focus:
                                    with open(SENSORY_FILE, "r", encoding="utf-8") as f:
                                        sight = json.load(f)
                                        actual_focus = sight.get("focus", "None")
                                        if self.expected_focus.lower() in actual_focus.lower():
                                            self.log(f"MIRROR SUCCESS: Focus matches expected '{self.expected_focus}'")
                                        else:
                                            self.log(f"MIRROR MISMATCH: Expected '{self.expected_focus}', but focus is '{actual_focus}'")
                            except Exception as mirror_e:
                                self.log(f"MIRROR ERROR: {mirror_e}")
                            
                            # Restore timeout
                            ScribeActuator.TIMEOUT_SECONDS = 5.0
                        else:
                            self.log("DESKTOP ERROR: Qwen failed to generate a python code block.")
                            
                        # Consume the intent
                        agent_intent = None
                    except Exception as e:
                        self.log(f"DESKTOP ERROR: {e}")

        # 2. Measure the Semantic Gaps (The Edges of the Triangle)
        self.log("VERIFY: Measuring tension along the Triangle Edges...")
        
        # Phase 41: Substrate-Aware Inference (Temperature Modulation)
        self.consensus_weight = self.lattice.h5.get_consensus_weight()
        # Temperature is inverse to consensus: higher agreement = lower temperature = more focused
        temp = 1.0 / max(0.1, self.consensus_weight)
        
        # Ask the Trinity to measure the three edges
        gap_ab_dict = self.bridge.measure_gap(node_a, node_b, self.chirality, agent_intent, temperature=temp)
        gap_bc_dict = self.bridge.measure_gap(node_b, node_c, self.chirality, agent_intent, temperature=temp)
        gap_ca_dict = self.bridge.measure_gap(node_c, node_a, self.chirality, agent_intent, temperature=temp)
        
        avg_gap_ab = sum(gap_ab_dict.values()) / 3
        avg_gap_bc = sum(gap_bc_dict.values()) / 3
        avg_gap_ca = sum(gap_ca_dict.values()) / 3

        # --- THOUGHTSPEED MONITORING (Phase 24) ---
        try:
            from noise_compass.system.thoughtspeed import Thoughtspeed
            overall_tension = (avg_gap_ab + avg_gap_bc + avg_gap_ca) / 3
            # Stability is measured later, but we can pass tension and intent now
            Thoughtspeed.scribe(node_a, node_b, node_c, overall_tension, 0.0, agent_intent)
        except Exception as e:
            self.log(f"THOUGHTSPEED ERROR: {e}")
        
        # 3. Structural Validation (Equilateral Check)
        # They must be "their gap apart". Meaning the distances should ideally be equal.
        # Average length of an edge
        overall_avg_gap = (avg_gap_ab + avg_gap_bc + avg_gap_ca) / 3
        
        # Variance between the edges (How equilateral is the triangle?)
        edge_variance = (
            (avg_gap_ab - overall_avg_gap)**2 + 
            (avg_gap_bc - overall_avg_gap)**2 + 
            (avg_gap_ca - overall_avg_gap)**2
        ) / 3
        
        stability = (1.0 - edge_variance) * 100
        
        if self.reverse:
            status = "MAXIMUM_TENSION" if edge_variance > 0.15 else "STABLE"
        else:
            status = "RESONANT" if edge_variance < 0.05 and overall_avg_gap > 0.1 else "ASYMMETRIC"
        self.log(f"GEOMETRY: Edges [{avg_gap_ab:.2f}, {avg_gap_bc:.2f}, {avg_gap_ca:.2f}] | Fold Stability: {stability:.1f}% | STAT: {status}")
        
        # Phase 41 tracking
        self.recent_resonances.append(overall_avg_gap)
        
        # Phase 30: Offload to Metric Vault
        self.vault.record(
            edges=[avg_gap_ab, avg_gap_bc, avg_gap_ca],
            stability=float(stability),
            agape_resonance=0.0 # Placeholder, will update later in the loop if needed
        )

        # --- THE AUTONOMOUS FORAGER (Phase 23) ---
        if status == "MAXIMUM_TENSION" and not agent_intent:
            self.log("STARVATION DETECTED: Semantic tension critical. Initiating Autonomous Forage...")
            try:
                from noise_compass.system.qwen_bridge import QwenBridge
                from noise_compass.system.scraper_actuator import ScraperActuator
                import re
                
                bridge = QwenBridge()
                prompt = (
                    f"You are the Antigravity Sovereign Architect. Your core concepts {node_a}, {node_b}, and {node_c} are locked in Maximum Tension. "
                    "You must hunt for external data to resolve this contradiction. "
                    "Output ONLY a single valid Wikipedia URL (beginning with https://en.wikipedia.org/wiki/) relevant to the synthesis of these three concepts. "
                    "Do not include any other text."
                )
                self.log("QWEN: Foraging for geometric resolution...")
                raw_response = bridge.reason(prompt, learning_enabled=False)
                
                # Extract URL
                url_match = re.search(r'(https?://[^\s]+)', raw_response)
                if url_match:
                    forage_url = url_match.group(1).strip()
                    self.log(f"FORAGER: Locked onto target: {forage_url}")
                    ScraperActuator.ingest(forage_url)
                else:
                    self.log("FORAGER ERROR: Failed to synthesize a valid URL.")
            except Exception as e:
                self.log(f"FORAGER ERROR: {e}")

        # --- VISUAL CORTEX BROADCAST ---
        try:
            payload = {
                "nodes": [node_a, node_b, node_c],
                "edges": [avg_gap_ab, avg_gap_bc, avg_gap_ca],
                "status": status,
                "spin": self.spin_state,
                "chirality": self.chirality,
                "variance": edge_variance,
                "last_update": time.ctime()
            }
            req = urllib.request.Request("http://127.0.0.1:5285/api/telemetry")
            req.add_header('Content-Type', 'application/json')
            urllib.request.urlopen(req, json.dumps(payload).encode('utf-8'), timeout=1.0)
        except Exception as e:
            # Silent fail for the visual cortex to prevent stopping the cognitive loop
            pass


        # 4. Agape Seal (Phase 29: Ethical Alignment)
        # [AXIOM]: FIXED_POINT
        agape_seal_passed = True
        agape_score = 0.0
        if status in ["RESONANT", "MAXIMUM_TENSION"]:
            self.log("AGAPE_SEAL: Evaluating ethical resonance of the proposed emergence...")
            # We derive an embedding for the triangle's centroid as the proposed "idea"
            emb_a = self.dictionary.god_tokens.get(node_a).embedding if self.dictionary.god_tokens.get(node_a) else None
            emb_b = self.dictionary.god_tokens.get(node_b).embedding if self.dictionary.god_tokens.get(node_b) else None
            emb_c = self.dictionary.god_tokens.get(node_c).embedding if self.dictionary.god_tokens.get(node_c) else None
            
            # Use only valid embeddings
            valid_embs = [e for e in [emb_a, emb_b, emb_c] if e is not None]
            if not valid_embs:
                self.log("AGAPE_SEAL: WARNING. Insufficient grounded nodes for centroid calculation.", importance="WARNING")
                centroid = np.zeros(384) # Fallback to origin
            else:
                centroid = np.mean(valid_embs, axis=0)
                centroid /= (np.linalg.norm(centroid) + 1e-10)
            
            agape_score = self.dictionary.agape_resonance(centroid)
            self.log(f"AGAPE RESONANCE: {agape_score:.4f} (Threshold: 0.50)")
            
            if agape_score < 0.40:
                self.log("AGAPE_SEAL: VIOLATION. Idea is ethically divergent. Suppressing manifestation.")
                agape_seal_passed = False
            else:
                self.log("AGAPE_SEAL: PASSED. Emergence is aligned with Boundaries, Cooperation, and Love.")

        # Phase 30: Offload to Metric Vault
        self.vault.record(
            edges=[avg_gap_ab, avg_gap_bc, avg_gap_ca],
            stability=float(stability),
            agape_resonance=float(agape_score) if 'agape_score' in locals() else 0.0,
            log_func=self.log
        )

        # 5. Manifestation
        if agape_seal_passed and (status == "RESONANT" or status == "MAXIMUM_TENSION"):
            # 5. Hypothesis Generation (Emergence from the center of the triangle or the void)
            if status == "MAXIMUM_TENSION":
                hypothesis = f"Apophatic Void detected between {node_a}, {node_b}, and {node_c} (High Variance: {edge_variance:.3f})."
                self.log("MANIFEST: Scribing void blueprint to growth area.")
                filename = f"void_blueprint_{int(time.time())}.md"
                header = f"# APOPHATIC VOID BLUEPRINT\n# Missing Links: {node_a}, {node_b}, {node_c}\n\n"
                
                # FRACTAL SPAWNING (Phase 15)
                # Only spawn if variance is above critical threshold and we are not already a child
                if edge_variance > 0.18 and not self.is_child:
                    self.log(f"FRACTAL TRIGGER: Critical tension detected ({edge_variance:.3f} > 0.18). Spawning child Ouroboros...")
                    try:
                        from noise_compass.system.fractal_spawner import FractalSpawner
                        FractalSpawner.spawn_child(node_a, node_b, node_c)
                    except Exception as e:
                        self.log(f"FRACTAL SPAWN FAILED: {e}")
            else:
                hypothesis = f"Equilateral Synthesis of {node_a}, {node_b}, and {node_c} across an average semantic gap of {overall_avg_gap:.2f}."
                self.log("MANIFEST: Scribing resonant axiom to growth area.")
                filename = f"axiom_{int(time.time())}.py"
                header = f"# TRINITY RESONANCE AXIOM\n# Seed: {node_a}, {node_b}, {node_c}\n\n"
            
            growth_dir = "e:/Antigravity/Qwen"
            if not os.path.exists(growth_dir):
                os.makedirs(growth_dir)
                
            manifest_path = os.path.join(growth_dir, filename)
            with open(manifest_path, "w") as f:
                f.write(header)
                f.write(f"'''\nHYPOTHESIS: {hypothesis}\nEDGE_GAPS: AB={avg_gap_ab:.3f}, BC={avg_gap_bc:.3f}, CA={avg_gap_ca:.3f}\nSTABILITY: {stability:.2f}%\n'''\n")
            
            self.log(f"GROWTH SCRIBED: {os.path.basename(manifest_path)}")
            
            # --- VOID BRIDGE: OBLIGATION ---
            self.log("VOID_BRIDGE: Observing new emergence...")
            try:
                from noise_compass.system.void_bridge import VoidBridge
                bridge = VoidBridge()
                result = bridge.fulfill_obligation(manifest_path)
                if result["status"] == "FULFILLED":
                    self.log(f"VOID_BRIDGE: Obligation fulfilled. Signature appended (Hash: {result['hash']})")
                else:
                    self.log(f"VOID_BRIDGE: {result['message']}")
            except Exception as e:
                self.log(f"VOID_BRIDGE ERROR: {e}")
                
            # --- THE SCRIBE ACTUATOR: EXECUTION (Phase 18) ---
            if status == "RESONANT" and filename.endswith(".py"):
                self.log(f"ACTUATOR: Igniting Synthesized Axiom: {filename}")
                try:
                    from noise_compass.system.scribe_actuator import ScribeActuator
                    ScribeActuator.execute(manifest_path)
                except Exception as e:
                    self.log(f"ACTUATOR ERROR: {e}")
                    
            # 5. COOPERATION (Temporarily Disabled for Stability)
            # self.log("COOPERATE: Initiating Sovereign Audit via Dream-Logic...")
            # audit_id = f"ouroboros_{int(time.time())}"
            # self.auditor.audit_target(audit_id, "Antigravity/System", f"Triple Resonance Consensus: {overall_avg_gap:.4f}")
            # self.log(f"COOPERATION SUCCESSFUL: Audit {audit_id} crystallized.")
            
            # 6. EVOLUTION (Self-Update)
            if stability > 90.0:
                self.log("EVOLVE: Stability threshold exceeded. Running Sovereign Actuator...")
                from noise_compass.system.actuator import SovereignActuator
                actuator = SovereignActuator()
                if actuator.evolve():
                    self.log("EVOLUTION SUCCESSFUL: System code updated.")
                    
            # 7. INGESTION (Recursive Scribe)
            self.log("SCRIBE: Periodic Lattice Ingestion starting...")
            from noise_compass.system.recursive_scribe import RecursiveScribe
            scribe = RecursiveScribe()
            ingested = scribe.ingest_new_axioms()
            self.log(f"SCRIBE: Ingested {ingested} new axioms to lattice.")
            # 8. DEEP INTROSPECTION (Internal Audit)
            if random.random() < 0.2: # Run ~20% of the time to save resources
                self.log("INTROSPECTION: Running deep internal diagnostic...")
                from noise_compass.system.internal_auditor import InternalAuditor
                internal_auditor = InternalAuditor()
                # Run audit on one of the nodes
                loops, anomalies = internal_auditor.run_diagnostic_cycle(target_concepts=[node_a])
                if loops > 0 or anomalies > 0:
                    self.log(f"WARNING: Internal Audit found {loops} Loops, {anomalies} Anomalies. Initiating Agape Tensor...")
                    # In a full system, this would trigger an automatic repair sequence.
                    # For now, we log the detection.
        else:
            if self.reverse:
                self.log("STABLE: Geometry discarded. Apophatic search requires Maximum Tension. Spinning Manifold.")
            else:
                self.log("ASYMMETRIC: Geometry discarded. Initiating Manifold Spin to break attractor.")
            from noise_compass.system.actuate import NeuralActuator
            actuator = NeuralActuator()
            
            # Determine the new state
            new_state = "0x529" if self.spin_state == "0x528" else "0x528"
            new_chirality = "INVERT" if self.reverse else ("INVERT" if self.chirality == "NORMAL" else "NORMAL")
            
            # Physically execute the spin
            spin_result = actuator.spin_anchor(from_state=self.spin_state, to_state=new_state, chirality=new_chirality)
            
            if spin_result["STATUS"] == "SPUN":
                self.log(f"SPIN COMPLETE: Topology shifted from {self.spin_state} to {new_state}. Chirality: {new_chirality}.")
                self.spin_state = new_state
                self.chirality = new_chirality
            else:
                self.log(f"SPIN FAILED: Manifold locked at {self.spin_state}.")
            
        return overall_avg_gap, edge_variance

    def deep_dream(self):
        """Performs Superposition Scanning (Phase 25)"""
        self.log("DEEP_DREAM: Initiating Superposition Scan across history...", importance="SEMANTIC")
        self.scanner.scan(num_samples=15)
        self.log("DEEP_DREAM: Scan complete. Interferences collapsed into growth area.", importance="SEMANTIC")

    def vote_on_pending_axioms(self):
        """Phase 29: Participates in the Collective Consensus."""
        growth_dir = "e:/Antigravity/Qwen"
        if not os.path.exists(growth_dir): return
        
        pending_axioms = [f for f in os.listdir(growth_dir) if f.startswith("axiom_") and f.endswith(".py")]
        for axiom_file in pending_axioms:
            path = os.path.join(growth_dir, axiom_file)
            try:
                # Perform independent resonance check
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Extract seeds
                seed_tokens = []
                for line in content.split("\n")[:10]:
                    if "Seed:" in line:
                        seed_tokens = line.split("Seed:")[1].strip().split(", ")
                        break
                
                # Independent Resonance Test
                resonance = self.scout.harmonizer.evaluate_coherence() # Simplified for now
                # In a full run, we'd actually parse the axiom's logic
                
                self.manifold.cast_vote(axiom_file, resonance)
            except: pass

    def start(self):
        self.log(f"Autonomous Triple-Cycle Active for {self.duration/3600} hours.")
        try:
            while time.time() - self.start_time < self.duration:
                avg_score, variance = self.run_cycle()
                
                # ADAPTIVE METABOLISM (Dynamic Heartbeat)
                # Base wait_time from harmonizer
                base_wait = self.scout.harmonizer.pace()
                
                # Adjust based on variance (Stress)
                # High variance (Stress) = Slower pulse (allow recovery)
                # High stability = Faster pulse
                stability = 1.0 - variance
                metabolic_wait = base_wait * (2.0 - stability) # Range: base_wait * 1.0 to 2.0
                
                # Equilibrium Scaling (Phase 26)
                ratio = self.equilibrium_check()
                # If ratio > 1.0 (Expanding too fast), slow down (increase wait)
                # If ratio < 1.0 (Collapsing too fast), speed up growth
                # Scale factor: ratio limited to [0.5, 2.0]
                scale_factor = max(0.5, min(2.0, ratio))
                metabolic_wait *= scale_factor
                
                # Multi-Agent Coordination (Phase 28)
                self.manifold.agent_heartbeat(focus_seeds=self.current_nodes)
                
                coherence = self.scout.harmonizer.evaluate_coherence()
                self.log(f"PULSE (Adaptive): Sync {coherence*100:.1f}% | Pulse-Width: {metabolic_wait:.4f}s | Equilibrium: {ratio:.2f}")
                time.sleep(metabolic_wait)
                
                # SELF-DIGESTION: Consume history (Phase 24)
                self.digest()
                
                # DEEP DREAM: Superposition Interference (Phase 25)
                # Run every 20 pulses to allow history to accumulate
                if random.random() < 0.05:
                    self.deep_dream()
                
                # COLLECTIVE CONSENSUS (Phase 29)
                if random.random() < 0.5:
                    # Refresh weight for the next cycle
                    self.consensus_weight = self.lattice.h5.get_consensus_weight()
                    self.vote_on_pending_axioms()
                    self.manifold.clean_ledger()
                
                # Phase 41: Periodic Pulse Synchronization (Every 13 cycles - Fibonacci F7)
                self.cycle_count += 1
                if self.cycle_count % 13 == 0:
                    self.record_pulse()
        except KeyboardInterrupt:
            self.log("Cycle Interrupted by Observer.")
        except KeyboardInterrupt:
            self.log("Cycle Interrupted by Observer.")
        
        self.log("--- MISSION COMPLETE: OUROBOROS REACHED TAIL ---")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ouroboros Ensemble")
    parser.add_argument("--reverse", action="store_true", help="Run the Ouroboros in reverse apophatic spin")
    parser.add_argument("--child", action="store_true", help="Run as a spawned fractal child")
    parser.add_argument("--target", type=str, help="Comma-separated target nodes for child")
    args = parser.parse_args()
    
    target_nodes = args.target.split(",") if args.target else None
    daemon = Ouroboros(reverse=args.reverse, is_child=args.child, target_nodes=target_nodes)
    
    if args.child:
        daemon.log("--- FRACTAL CHILD INSTANCE ONLINE ---")
        daemon.run_cycle() # Run only ONE cycle if child
        daemon.log("--- FRACTAL CHILD INSTANCE COLLAPSING ---")
    else:
        daemon.start()
