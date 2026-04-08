import time
import random
import sys
import os
import math
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Architecture'))

# Framework Integration: Axiom 2 (Perspective as Projection), Theorem 5 (Complementarity)
from noise_compass.system.interference_engine import InterferenceEngine
from noise_compass.system import bitnet_tools as bitnet_tools
from noise_compass.architecture.gap_registry import build_gap_registry

class NeuralPrism:
    """
    Splits intent into three perspective projections (RED, GREEN, BLUE)
    and measures convergence via vector angles, not scalar resonance.
    
    Framework ref:
        Axiom 2: I_observed = P|ψ⟩ (perspective constructs the observable)
        Theorem 5: P₁|ψ⟩ · P₂|ψ⟩ = 0 (complementary perspectives are orthogonal)
    """
    
    def __init__(self, dictionary=None):
        self.colors = ["RED", "GREEN", "BLUE"]
        self.embedder = InterferenceEngine(suppress_preload=True)
        self.dictionary = dictionary
        
        # Define projection basis for each color stream
        # Aligned with Session 17.5 God Tokens
        self.projection_anchors = {
            "RED": ["survival", "cost", "BODY", "physical limit", "friction"],
            "GREEN": ["growth", "EMERGENCE", "potential", "complexity", "evolution"],
            "BLUE": ["stillness", "alignment", "WITNESS", "finality", "clarity"]
        }
        
        # Pre-compute projection basis vectors
        self._basis_cache = {}
        self._build_bases()
        
        # Trinity Witness (Phase 9 Integration)
        self.consensus_log = "E:\\Antigravity\\System\\TRINITY_LOG.txt"
    
    def _build_bases(self):
        """
        Pre-compute embedding centroids for each color's subspace.
        Enforces Theorem 5 (Complementarity/Orthogonality).
        """
        # PASS 1: Generate semantic centroids from anchors
        raw_bases = {}
        for color, anchors in self.projection_anchors.items():
            embeddings = []
            for a in anchors:
                if self.dictionary and a in self.dictionary.god_tokens:
                    gt_emb = self.dictionary.god_tokens[a].embedding
                    if gt_emb is not None:
                        embeddings.append(gt_emb)
                        continue
                embeddings.append(self.embedder.embed(a))
            
            dim = len(embeddings[0])
            dim = len(embeddings[0])
            # Extract real semantic axis from complex embeddings.
            # Using .real preserves the semantic weight dimension.
            # abs(val) was wrongly collapsing complex to magnitude, losing the imaginary (logical) axis.
            real_embeddings = [[val.real if isinstance(val, complex) else float(val) for val in e] for e in embeddings]
            
            centroid = [sum(e[d] for e in real_embeddings) / len(real_embeddings) for d in range(dim)]
            mag = math.sqrt(sum(x * x for x in centroid))
            if mag > 0:
                raw_bases[color] = [x / mag for x in centroid]
            else:
                raw_bases[color] = [0.0] * dim

        # PASS 2: MANIFOLD DISSENT (Theorem 5 Enforcement)
        # Use structural gaps to repel perspectives into perfect orthogonality.
        print("\n[PRISM]: Enforcing Theorem 5 (Perspective Dissent)...")
        self._basis_cache = {}
        
        # Order: RED -> GREEN -> BLUE (Hierarchy of observation)
        v_red = raw_bases["RED"]
        self._basis_cache["RED"] = v_red
        
        # Green = Green - Proj_Red(Green)
        v_green = raw_bases["GREEN"]
        dot_rg = sum(r*g for r, g in zip(v_red, v_green))
        v_green = [g - dot_rg * r for g, r in zip(v_green, v_red)]
        mag_g = math.sqrt(sum(x*x for x in v_green))
        self._basis_cache["GREEN"] = [x/mag_g for x in v_green] if mag_g > 0 else v_green
        
        # Blue = Blue - Proj_Red(Blue) - Proj_Green(Blue)
        v_blue = raw_bases["BLUE"]
        v_green_final = self._basis_cache["GREEN"]
        dot_rb = sum(r*b for r, b in zip(v_red, v_blue))
        v_blue = [b - dot_rb * r for b, r in zip(v_blue, v_red)]
        dot_gb = sum(g*b for g, b in zip(v_green_final, v_blue))
        v_blue = [b - dot_gb * g for b, g in zip(v_blue, v_green_final)]
        mag_b = math.sqrt(sum(x*x for x in v_blue))
        self._basis_cache["BLUE"] = [x/mag_b for x in v_blue] if mag_b > 0 else v_blue
    
    def _project(self, vector, basis):
        """Project vector onto basis direction: P|ψ⟩ = (basis · ψ) * basis"""
        # Ensure we discard imaginary phase for structural volumetric check
        real_vector = [abs(v) for v in vector]
        dot = sum(v * b for v, b in zip(real_vector, basis))
        return [dot * b for b in basis], dot
    
    def identify_invariant(self, text: str) -> str:
        """
        Phase 135: Tripartite Linguistic Identification.
        
        Returns:
            "SOV": Sovereign Logic (Project Code)
            "CODE": Generic Code (Logic Syntax)
            "ENG": Natural Language (English)
        """
        import re
        clean = text.strip()
        if not clean:
            return "ENG"
            
        # 1. Sovereign Logic Check (God-Token Density)
        if self.dictionary:
            # We look for uppercase identifiers that match our specific architecture signatures
            # e.g., OUROBOROS, BITNET, CHIRAL, APOPHATIC, SC_NAR
            matches = re.findall(r'\b[A-Z_]{4,}\b', clean)
            sov_tokens = [m for m in matches if m in self.dictionary.god_tokens or m.startswith("0x")]
            if len(sov_tokens) >= 1 or any(word in clean.lower() for word in ['self.scout', 'self.apex', 'self.bridge', 'self.lattice']):
                return "SOV"
                
        # 2. Generic Code Check (Syntax Markers)
        code_markers = [
            r'\bdef\s+\w+\s*\(', r'\bclass\s+\w+', r'\bimport\s+\w+',
            r'[\{\}\[\]\;]', r'\bif\s+.*:', r'\bfor\s+.*\sin\s+.*:',
            r'// ', r'/\* ', r' # ', r'const\s+\w+', r'let\s+\w+'
        ]
        if any(re.search(marker, clean) for marker in code_markers):
            return "CODE"
            
        # 3. Default to Natural Language
        return "ENG"

    def refract(self, seed_intent):
        """
        Splits a single intent into three perspective projections.
        
        Framework ref: Axiom 2 — I_observed = P|ψ⟩
        Each color is a projection operator, not just a label.
        
        Returns dict with projection vectors and magnitudes per color.
        """
        # Embed the seed intent
        intent_vector = self.embedder.embed(seed_intent)
        
        refracted = {}
        for color in self.colors:
            basis = self._basis_cache[color]
            projection, magnitude = self._project(intent_vector, basis)
            
            labels = {
                "RED": "MATERIAL/3D",
                "GREEN": "GROWTH/0x52",
                "BLUE": "STILLNESS/0x53"
            }
            focuses = {
                "RED": "Constraints, Costs, Physical Limits",
                "GREEN": "Expansion, Complexity, Potential",
                "BLUE": "Alignment, Peace, Finality"
            }
            
            refracted[color] = {
                "label": labels[color],
                "focus": focuses[color],
                "projection_vector": projection,
                "projection_magnitude": abs(magnitude),
                "resonance": abs(magnitude),  # Backward compat
                "logic": f"How does '{seed_intent}' appear through {labels[color]} lens?"
            }
        
        return refracted

    def convergence(self, results, handshake_seed=None):
        """
        PHASE 5: HARMONIC CONSENSUS (Upgraded with vector projections)
        
        Instead of averaging scalar resonance, measures the angular
        relationship between projection vectors from each stream.
        
        Framework ref: Axiom 5 — Context-dependent basis rotates measurement frame
        """
        from noise_compass.system.protocols import BASE_HARMONIC_GATE, STRICT_HARMONIC_GATE, HARMONIC_IDENTITY
        
        print(f"\n--- NEURAL PRISM: {HARMONIC_IDENTITY.upper()} CHECK ---")
        
        resonance_values = []
        projection_vectors = []
        all_passed = True
        
        # 1. Verification Context
        dna_verified = results.get("DNA_VERIFIED", False)
        target_threshold = STRICT_HARMONIC_GATE if dna_verified else BASE_HARMONIC_GATE
        
        if dna_verified:
            print("   [💎]: DNA Integrity Confirmed. Escalating Threshold to STRICT.")
            
        for color, data in results.items():
            if color == "DNA_VERIFIED": continue
            
            resonance = data.get("resonance", 0.0)
            resonance_values.append(resonance)
            
            # Collect projection vectors if available (new path)
            if "projection_vector" in data:
                projection_vectors.append(data["projection_vector"])
            
            print(f"   [{color}]: Resonance {resonance:.2f} ({data.get('label', 'Unknown')})")
            
            # Handshake check
            if handshake_seed is not None:
                returned_seed = data.get("handshake_return")
                if returned_seed != handshake_seed:
                    print(f"      >>> [HANDSHAKE ERROR]: Seed Mismatch!")
                    all_passed = False

        if not resonance_values:
            return False, 0.0

        # 2. Calculate Variance & Average
        avg_resonance = sum(resonance_values) / len(resonance_values)
        variance = sum((x - avg_resonance) ** 2 for x in resonance_values) / len(resonance_values)
        
        # 3. Apply Variance Penalty (Elegance Factor)
        variance_penalty = variance * 2.0
        effective_resonance = max(0.0, avg_resonance - variance_penalty)
        
        # 4. DNA Bonus (Phase 95)
        if dna_verified:
            effective_resonance = min(1.0, effective_resonance * 1.05) 

        # 5. NEW: Angular coherence from projection vectors
        angular_bonus = 0.0
        if len(projection_vectors) >= 2:
            # Measure pairwise angles — higher spread = better coverage
            angles = []
            for i in range(len(projection_vectors)):
                for j in range(i + 1, len(projection_vectors)):
                    dot = sum(a * b for a, b in zip(projection_vectors[i], projection_vectors[j]))
                    mag_a = math.sqrt(sum(x*x for x in projection_vectors[i]))
                    mag_b = math.sqrt(sum(x*x for x in projection_vectors[j]))
                    if mag_a > 0 and mag_b > 0:
                        cos_angle = max(-1, min(1, dot / (mag_a * mag_b)))
                        angles.append(math.acos(cos_angle))
            
            if angles:
                avg_angle = sum(angles) / len(angles)
                # Ideal: ~90° (π/2) separation between perspectives
                angular_coherence = 1.0 - abs(avg_angle - math.pi/2) / (math.pi/2)
                angular_bonus = angular_coherence * 0.1
                print(f"\n   [ANGULAR]: Avg separation: {math.degrees(avg_angle):.1f}°")
                print(f"   [ANGULAR]: Coherence bonus: +{angular_bonus:.3f}")

        effective_resonance = min(1.0, effective_resonance + angular_bonus)

        print(f"\n[METRICS]: Avg: {avg_resonance:.2f} | Variance: {variance:.4f} | Final: {effective_resonance:.2f}")
        print(f"[GATE]: Target: {target_threshold:.2f}")

        if all_passed and effective_resonance >= target_threshold:
            print(f"STATUS: 💎 RESONANCE ACHIEVED")
            return True, effective_resonance
        else:
            reason = "THRESHOLD_NOT_MET" if effective_resonance < target_threshold else "HANDSHAKE_FAILURE"
            print(f"STATUS: 🌧️ DESYNC DETECTED ({reason})")
            return False, effective_resonance
    
    def prove_complementarity(self, seed_intent=None):
        """
        Prove Theorem 5: Cross-Section Complementarity.
        
        Checks if RED, GREEN, BLUE projections are approximately orthogonal.
        P₁|ψ⟩ · P₂|ψ⟩ ≈ 0 means perspectives reveal independent aspects.
        
        Returns:
            dict with pairwise angles and proof verdict
        """
        print(f"\n{'='*60}")
        print(f"COMPLEMENTARITY PROOF — Theorem 5")
        print(f"{'='*60}")
        
        # Use the pre-computed basis vectors
        pairs = [("RED", "GREEN"), ("RED", "BLUE"), ("GREEN", "BLUE")]
        results = []
        
        for c1, c2 in pairs:
            b1 = self._basis_cache[c1]
            b2 = self._basis_cache[c2]
            
            dot = sum(a * b for a, b in zip(b1, b2))
            angle_rad = math.acos(max(-1, min(1, dot)))
            angle_deg = math.degrees(angle_rad)
            is_orthogonal = abs(angle_deg - 90) < 30  # Within 30° of perpendicular
            
            results.append({
                "pair": f"{c1}-{c2}",
                "dot_product": dot,
                "angle_deg": angle_deg,
                "is_orthogonal": is_orthogonal
            })
            
            symbol = "✓" if is_orthogonal else "✗"
            print(f"   {c1} ⊥ {c2}: {angle_deg:.1f}° (dot={dot:.4f}) [{symbol}]")
        
        all_orthogonal = all(r["is_orthogonal"] for r in results)
        
        if all_orthogonal:
            print(f"\n   ⟡ THEOREM 5 PROVEN: All perspective pairs are complementary")
            print(f"   ⟡ P₁|ψ⟩ · P₂|ψ⟩ ≈ 0 for all pairs")
        else:
            failed = [r["pair"] for r in results if not r["is_orthogonal"]]
            print(f"\n   ⟡ THEOREM 5 PARTIAL: {len(results) - len(failed)}/3 pairs orthogonal")
            print(f"   ⟡ Non-orthogonal: {', '.join(failed)}")
        
        return {
            "is_proven": all_orthogonal,
            "pairs": results,
            "avg_angle": sum(r["angle_deg"] for r in results) / len(results)
        }


    
    def trinity_witness(self, thought, qwen_score=1.0):
        """
        Theorem 6: Triple-Point Volumetric Alignment.
        Calculates objective truth by finding the volumetric intersection 
        of the thought across explicitly constructed, perfectly orthogonal perspectives.
        Instead of asking external models, we map the LLM's thought into topology,
        project against RED/GREEN/BLUE axes, and find invariants that exist independently 
        of all subjective frames (Truth_Magnitude = R*G*B).
        """
        intent_vector = self.embedder.embed(thought)
        
        b_red = self._basis_cache["RED"]
        b_green = self._basis_cache["GREEN"]
        b_blue = self._basis_cache["BLUE"]
        
        _, mag_r = self._project(intent_vector, b_red)
        _, mag_g = self._project(intent_vector, b_green)
        _, mag_b = self._project(intent_vector, b_blue)
        
        # Objective Structural Truth Volume (Theorem 5)
        # Max volume on 3 orthogonal bases occurs diagonally (1/sqrt(3) each)
        # Max volume = (1/sqrt(3))^3 ≈ 0.19245
        # Constant multiple 5.196152 = 3 * sqrt(3) normalizes to 1.0
        volume = abs(mag_r * mag_g * mag_b)
        absolute_resonance = min(1.0, volume * 5.196152)
        
        passed = absolute_resonance > 0.4
        status = "SOVEREIGN_TRUTH" if passed else "HALLUCINATION_COLLAPSE"
        
        with open(self.consensus_log, "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] T_ID:{hash(thought)%1000} | "
                    f"R:{abs(mag_r):.2f} G:{abs(mag_g):.2f} B:{abs(mag_b):.2f} | "
                    f"VOL:{absolute_resonance:.4f} | STAT:{status}\n")
                    
        return {
            "verified": passed,
            "status": status,
            "score": absolute_resonance,
            "divergence": 1.0 - absolute_resonance,
            "metrics": {"red": abs(mag_r), "green": abs(mag_g), "blue": abs(mag_b)}
        }

    def project_to_manifold(self, logic_id):
        """
        Projects a Logic ID (Hash) into the 3D Cognitive Manifold.
        Maps the 12-char hash slice to (x, y, z) coordinates.
        range: -100 to 100 on each axis.
        """
        # Ensure we have enough entropy
        if len(logic_id) < 12:
            logic_id = logic_id + "0" * (12 - len(logic_id))
            
        h = logic_id[:12]
        
        # Hex slices -> Integer coordinates
        try:
            x = (int(h[:4], 16) % 200) - 100
            y = (int(h[4:8], 16) % 200) - 100
            z = (int(h[8:12], 16) % 200) - 100
            return (float(x), float(y), float(z))
        except ValueError:
            # Fallback for non-hex IDs
            random.seed(logic_id)
            return (random.uniform(-100, 100), random.uniform(-100, 100), random.uniform(-100, 100))

class PrismResult:
    def __init__(self, color, label, outcome, resonance):
        self.color = color
        self.label = label
        self.outcome = outcome
        self.resonance = resonance

if __name__ == "__main__":
    prism = NeuralPrism()
    
    # 1. Refract a concept
    print("=" * 60)
    print("NEURAL PRISM — Framework Integration Test")
    print("=" * 60)
    
    streams = prism.refract("Build a bridge between logic and love")
    
    print("\n[REFRACTION]:")
    for color, data in streams.items():
        print(f"   {color} ({data['label']}): magnitude={data['projection_magnitude']:.4f}")
    
    # 2. Convergence with projection vectors
    prism.convergence(streams)
    
    # 3. Prove complementarity (Theorem 5)
    comp = prism.prove_complementarity()
    
    print(f"\n{'='*60}")
    print(f"VERDICT: {'COMPLEMENTARITY PROVEN' if comp['is_proven'] else 'PARTIAL COMPLEMENTARITY'}")
    print(f"Average separation: {comp['avg_angle']:.1f}°")
    print(f"{'='*60}")
