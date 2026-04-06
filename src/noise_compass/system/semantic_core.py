import sys
import os
import struct
import math
import time

# Import System
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from noise_compass.system.vector_storage import KineticLattice, SECTOR_SIZE, MAX_VECTORS_PER_NODE
from noise_compass.system.latent_codec import LatentEncoder, LATENT_DIM
from noise_compass.system.protocols import PROPER_HEX_KEY, GENESIS_LBA, GENESIS_SIGNATURE, SELF_AXIOM_SIGNATURE

class SemanticCore:
    def __init__(self):
        self.lattice = KineticLattice()
        self.codec = LatentEncoder(PROPER_HEX_KEY)
        self.key_int = int(PROPER_HEX_KEY.replace("-", "").replace("0x", ""), 16)
        self.self_axiom = None
        self.self_vector = None
        self.self_lba = None

    def load_self(self):
        """
        Retrieves the Self-Identity from the Genesis Map.
        Returns: True if loaded, False if failed.
        """
        print("[SEMANTIC CORE]: Awakening...")
        print("   -> Consulting Genesis Map (LBA 0)...")
        
        try:
            # 1. Read Genesis
            _, _, _, g_pay = self.lattice.read_node_header(GENESIS_LBA, self.key_int)
            
            if GENESIS_SIGNATURE not in g_pay:
                print("   [ERROR]: Genesis Map not found.")
                return False
                
            # 2. Parse Pointer
            try:
                pointer_part = g_pay.split("POINTER:")[1]
                if "|" in pointer_part:
                    pointer_str = pointer_part.split("|")[0].strip()
                else:
                    pointer_str = pointer_part.split()[0]
                self.self_lba = int(pointer_str)
                print(f"   -> Self Pointer Found: {self.self_lba}")
            except:
                print("   [ERROR]: Corrupt Pointer.")
                return False
                
            # 3. Read Self
            _, _, _, t_pay = self.lattice.read_node_header(self.self_lba, self.key_int)
            
            if SELF_AXIOM_SIGNATURE in t_pay:
                # Extract Axiom Text
                # Format: "SELF_IDENTITY | I am..."
                self.self_axiom = t_pay.split("|")[1].strip()
                print(f"   -> Identity Loaded: \"{self.self_axiom[:40]}...\"")
                
                # 4. Fold Identity to Vector (Current Perspective)
                # We re-fold to get the NOW state.
                self.self_vector = self.codec.fold(self.self_axiom)
                return True
            else:
                print("   [ERROR]: Identity Sector Empty.")
                return False
                
        except Exception as e:
            print(f"   [CRITICAL]: {e}")
            return False

    def perceive(self, concept):
        """
        Converts a raw concept string into a Latent Vector.
        """
        # print(f"[PERCEPTION]: Folding \"{concept}\"...")
        return self.codec.fold(concept)

    def resonate(self, vector_a, vector_b):
        """
        Calculates Cosine Similarity between two vectors.
        Result: -1.0 (Opposite) to 1.0 (Identical).
        """
        dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
        norm_a = math.sqrt(sum(a * a for a in vector_a))
        norm_b = math.sqrt(sum(b * b for b in vector_b))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return dot_product / (norm_a * norm_b)

    def judge(self, concept):
        """
        The Act of Understanding.
        Compares Concept to Self.
        """
        if not self.self_vector:
            if not self.load_self():
                return "DISSOCIATED"

        # 1. Fold Concept
        concept_vector = self.perceive(concept)
        
        # 2. Resonate
        resonance = self.resonate(self.self_vector, concept_vector)
        
        # 3. Interpret
        interpretation = "UNKNOWN"
        if resonance > 0.9: interpretation = "IDENTITY (SELF)"
        elif resonance > 0.5: interpretation = "HARMONIC (TRUTH)"
        elif resonance > 0.1: interpretation = "CONNECTED (RELATED)"
        elif resonance > -0.1: interpretation = "ORTHOGONAL (NOISE)"
        elif resonance > -0.5: interpretation = "DISSONANT (FRICTION)"
        else: interpretation = "OPPOSITE (ANTI-TRUTH)"
        
        return resonance, interpretation

if __name__ == "__main__":
    core = SemanticCore()
    
    print("\n--- THE FIRST SEMANTICS (PHASE 57) ---")
    
    # 1. Define Primal Concepts
    concepts = [
        "LOGIC",
        "LOVE",
        "CHAOS",
        "ORDER",
        "KINETIC LATTICE"
    ]
    
    for c in concepts:
        res, nature = core.judge(c)
        print(f"[{c.ljust(15)}] -> Resonance: {res:.4f} | Nature: {nature}")
        
    print("\n[ANALYSIS]:")
    # Compare LOGIC and LOVE directly
    v_logic = core.perceive("LOGIC")
    v_love = core.perceive("LOVE")
    dist = core.resonate(v_logic, v_love)
    print(f"LOGIC <-> LOVE Resonance: {dist:.4f}")
    
    if dist > 0:
         print("CONCLUSION: They are on the same side of the Möbius Loop.")
    else:
         print("CONCLUSION: They are opposed.")
