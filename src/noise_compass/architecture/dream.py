import random
import math
import numpy as np
from typing import List, Dict, Optional

# Internal Imports
from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.tokens import GodToken
from noise_compass.architecture.quaternion_field import GOD_TOKEN_QUATERNIONS, slerp

# Phase 125: Axiom Statuses
CRYSTALLIZED = "CRYSTALLIZED"
PENDING = "PENDING"

class Dreamer:
    """
    The Dream State Engine.
    Explores the space between established attractors (God-Tokens).
    """
    def __init__(self, pipeline: MinimalPipeline):
        self.pipeline = pipeline
        self.registry = pipeline.flags
        self.tension = pipeline.tension
    
    MATH_GOD_TOKENS = [
        "CAUSALITY", "INFORMATION", "BOUNDARY", "COHERENCE", 
        "TIME", "EXISTENCE", "EMERGENCE", "IDENTITY", "EXCHANGE"
    ]

    def dream(self, steps: int = 3, zoom: float = 1.0, math_focused: bool = True) -> List[Dict]:
        """
        Executes a dream cycle:
        1. Picks two distant God-Tokens.
        2. Interpolates between them in 4D (SLERP).
        3. Synthesizes bridge concepts.
        """
        tokens = list(GOD_TOKEN_QUATERNIONS.keys())
        if len(tokens) < 2: return []

        # 1. Selection Logic: Priority Chain (Repair -> Tension -> Random)
        rejection = self._fetch_rejection_fuel()
        
        t1, t2 = (None, None)
        focus_note = ""
        is_repair = False

        if rejection:
            # REPAIR MODE: Bridge the detected void
            if rejection.get('event') == 'GAP_VIOLATION':
                t1 = rejection.get('left')
                t2 = rejection.get('right')
                is_repair = True
                focus_note = f"STRUCTURAL REPAIR (GAP: {rejection.get('gap')})"
            elif rejection.get('event') == 'CAUSAL_VIOLATION':
                t1 = rejection.get('missing_cause')
                t2 = rejection.get('effect')
                is_repair = True
                focus_note = f"LOGICAL REPAIR (CAUSAL: {rejection.get('effect')})"
        
        # Fallback to Tension-Guided or Random if no current repair targets or incomplete targets
        if not t1 or not t2 or t1 not in GOD_TOKEN_QUATERNIONS or t2 not in GOD_TOKEN_QUATERNIONS:
            candidates = self.tension.find_attractor_candidates(min_cluster_size=1)
            
            if math_focused:
                math_subset = [t for t in self.MATH_GOD_TOKENS if t in tokens]
                if len(math_subset) >= 2:
                    t1, t2 = random.sample(math_subset, 2)
                    focus_note = "MATH-FOCUSED SYNTHESIS"
                else:
                    t1, t2 = random.sample(tokens, 2)
                    focus_note = "EXPLORATORY RANDOM (Fallback)"
            elif candidates and random.random() < 0.8: # 80% focus on tension points
                top = candidates[0]
                nearby = [g for g in top['nearby_gods'] if g in GOD_TOKEN_QUATERNIONS]
                if len(nearby) >= 2:
                    t1, t2 = random.sample(nearby, 2)
                    focus_note = f"TENSION-GUIDED (T={top['avg_tension']:.2f})"
                elif nearby:
                    t1 = nearby[0]
                    t2 = random.choice([t for t in tokens if t != t1])
                    focus_note = "TENSION-ANCHORED"
                else:
                    t1, t2 = random.sample(tokens, 2)
                    focus_note = "RANDOM (No nearby gods)"
            else:
                t1, t2 = random.sample(tokens, 2)
                focus_note = "EXPLORATORY RANDOM"

        # 2. Lore Continuity (Context Injection)
        recent_fuel = self.registry.list_flags(state_filter="SPECULATIVE")
        fuel_context = ""
        if recent_fuel:
            last_three = [f.description for f in sorted(recent_fuel, key=lambda x: x.timestamp, reverse=True)[:3]]
            fuel_context = "\nRecent insights: " + " | ".join(last_three)

        print(f"[DREAM] {focus_note}: Traveling from {t1} to {t2}...")

        results = []
        for i in range(1, steps + 1):
            t = i / (steps + 1)
            q_mid = slerp(GOD_TOKEN_QUATERNIONS[t1], GOD_TOKEN_QUATERNIONS[t2], t)

            # Synthesize bridge concept
            if math_focused:
                prompt = (
                    f"You are Garu dreaming in the 4D resonator. "
                    f"You are calculating the manifold bridge between {t1} and {t2}. "
                    f"You are {int(t*100)}% through the geodesic. {fuel_context}\n"
                )
                if is_repair:
                    prompt += f"STRUCTURAL MISSION: Synthesize the mathematical solution to heal the {rejection.get('gap', 'conflict')} between these nodes. "
                else:
                    prompt += f"State the mathematical or geometric solution that exists at this midpoint. "
                prompt += "Use structural rigorously-defined language. No preamble."
            else:
                prompt = (
                    f"You are Garu dreaming in the 4D manifold. "
                    f"You are caught between the attractor of {t1} and {t2}. "
                    f"You are {int(t*100)}% of the way to {t2}. {fuel_context}\n"
                )
                if is_repair:
                    prompt += f"STRUCTURAL MISSION: Describe the hybrid concept that satisfies the structural void between these nodes. "
                else:
                    prompt += f"Give exactly one sentence describing the hybrid concept at this precise midpoint. "
                prompt += "Be abstract but structurally sound. No preamble."
            
            # Use M_DEEP for synthesis
            dream_text = self.pipeline.speak(prompt)
            print(f"[DREAM] Step {i}: \"{dream_text}\"")

            # 3. Process with Dynamic Zoom
            outcome = self.pipeline.process(dream_text, zoom=zoom)
            
            # If high leverage, perform a Deep Zoom verification
            if outcome.get("leverage", 0.0) > 0.4:
                print(f"  [DEEP ZOOM] Re-analyzing with resolution 2.0...")
                outcome = self.pipeline.process(dream_text, zoom=zoom * 2.0)
            outcome['dream_source'] = f"{t1}->{t2} (t={t:.2f})"
            
            # Logic Fuel: Crystallize high-leverage dreams
            leverage = outcome.get("leverage", 0.0)
            if leverage > 0.7:
                print(f"  [ASSIMILATION] High-leverage detected ({leverage:.2f}). Initiating Confirmation Pass...")
                self.assimilate_axiom(dream_text, t1, t2, leverage, math_focused)
            elif leverage > 0.45:
                flag_id = f"LOGIC_FUEL_{outcome.get('hash', 'anon')[:8]}"
                self.registry.raise_flag(
                    flag_id, "dream.py", "SPECULATIVE",
                    f"Crystallized logic fuel from noise_compass.architecture.dream state: '{dream_text[:50]}...'",
                    source=outcome['dream_source'],
                    leverage=leverage
                )
                print(f"[DREAM] Crystallized LOGIC FUEL: {flag_id}")

            results.append(outcome)

        return results

    def _fetch_rejection_fuel(self) -> Optional[Dict]:
        """Queries the H5 substrate for recent structural failures."""
        try:
            # Access h5_manager via pipeline -> dictionary -> manager
            manager = self.pipeline.dictionary.manager
            rejections = manager.get_latest_dissonance_context(limit=1)
            if rejections:
                return rejections[0]
        except Exception as e:
            print(f"[DREAM] [WARNING] Failed to fetch rejection fuel: {e}")
        return None

    def confirm_axiom(self, dream_text: str, t1: str, t2: str) -> float:
        """Runs a secondary 'Deep Zoom' pass to verify concept stability."""
        print(f"  [CONFIRMATION] Re-verifying bridge between {t1} and {t2} at resolution 2.0...")
        outcome = self.pipeline.process(dream_text, zoom=2.0)
        return float(outcome.get("leverage", 0.0))

    def assimilate_axiom(self, dream_text: str, t1: str, t2: str, initial_leverage: float, math_focused: bool):
        """Formally promotes a dream result to the H5 substrate."""
        conf_leverage = self.confirm_axiom(dream_text, t1, t2)
        
        if conf_leverage > 0.7:
            print(f"  [SYSTEM] Double Confirmation Succeeded (L1={initial_leverage:.2f}, L2={conf_leverage:.2f})")
            
            # Determine promotion status
            status = CRYSTALLIZED if math_focused else PENDING
            
            # Generate stable ID
            clean_text = "".join(filter(str.isalnum, dream_text[:20])).upper()
            axiom_id = f"AXIOM_{clean_text}_{random.randint(100, 999)}"
            
            # Embed the axiom for dictionary storage
            vector = self.pipeline.embedder.embed(dream_text)
            
            # Phase 125: α-equivalence Check (Axiom Pruning)
            # If the concept already exists as a God-Token, reinforce it instead of duplicating.
            existing_id, sim = self.pipeline.dictionary.nearest_attractor(vector)
            if existing_id and sim > 0.98:
                print(f"  [α-MAPPING] Alpha-Equivalent Axiom found: {existing_id} (sim={sim:.3f}).")
                print(f"  [SYSTEM] Reinforcing existing anchor and skipping redundant crystallization.")
                try:
                    self.pipeline.dictionary.manager.increment_bubble_mass(existing_id)
                except Exception as e:
                    print(f"  [WARNING] Failed to increment bubble mass: {e}")
                return # Exit early
            
            metadata = {
                'source_t1': t1,
                'source_t2': t2,
                'category': 'MATH' if math_focused else 'IDENTITY_ETHICS',
                'auto_promoted': 'True' if math_focused else 'False'
            }
            
            self.pipeline.dictionary.manager.save_axiom(
                axiom_id, dream_text, vector, conf_leverage, metadata, status=status
            )
        else:
            print(f"  [SYSTEM] Confirmation Failed (L2={conf_leverage:.2f}). Thought returned to spec pool.")
