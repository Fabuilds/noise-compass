import re
from typing import List, Dict, Set, Tuple
import numpy as np

# Internal Architecture Imports
import sys
from pathlib import Path

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.gap_registry import EXTENDED_GOD_TOKEN_SEEDS

class MathMeaningExtractor:
    """
    Extracts Maximum Meaning from mathematical structures (Phase 11).

    Merge is Bayesian Intersection (product of distributions), NOT interference
    (sum of amplitudes). Each constituent casts a distribution over the god-token
    lattice. The merged result is argmax over the product — the attractor most
    jointly supported by all constituents simultaneously.

    Four meaning layers:
      EXPLICIT:    Direct symbol translation → god-tokens the symbols denote.
      RELATIONAL:  What the operations between symbols imply → god-token paths
                   the structure traverses. This is where most meaning lives.
      GAP:         What the formula requires but cannot state → which god-tokens
                   are conspicuously absent. Named voids, not beyond-description.
      APOPHATIC:   What falls outside the formula's reach entirely → what would
                   need different mathematics. Rare; flag carefully.

    Maximum meaning = all four layers + the god-token path their merge product produces.
    """
    
    def __init__(self):
        # Layer 1: Explicit Mappings (Symbols to God-Tokens)
        self.symbol_map = {
            'z': 'EXISTENCE',
            'x': 'EXCHANGE',
            'y': 'EXCHANGE',
            'w': 'TIME',
            't': 'TIME',
            'delta': 'BOUNDARY',
            'δ': 'BOUNDARY',
            'epsilon': 'EXCHANGE', # Claude suggested EXCHANGE for coupling in this context
            'ε': 'EXCHANGE',
            'phi': 'IDENTITY',
            'psi': 'EMERGENCE',
            'omega': 'TIME',
            'lambda': 'BOUNDARY',
        }
        
        # Layer 2: Relational Mappings (Operations to Patterns)
        self.op_map = {
            '*': 'CO-REQUIREMENT',
            '·': 'CO-REQUIREMENT',
            '+': 'SUPERPOSITION',
            '-': 'DECAY',
            '=': 'CAUSALITY',
        }

    def extract_explicit(self, formula: str) -> Set[str]:
        """Identifies god-tokens directly referenced by symbols."""
        tokens = set()
        for symbol, token in self.symbol_map.items():
            if symbol in formula:
                tokens.add(token)
        return tokens

    def extract_relational(self, formula: str) -> List[str]:
        """Identifies structural relationships between variables."""
        relations = []
        
        # Interaction check (multiplication)
        interaction_patterns = [
            r'[a-zA-Z\u0370-\u03ff][·*][a-zA-Z\u0370-\u03ff]', # x*y
            r'[a-zA-Z\u0370-\u03ff]{2}', # xy (no op)
        ]
        for pattern in interaction_patterns:
            if re.search(pattern, formula):
                relations.append("CO-REQUIREMENT")
                break
                
        # Decay check (1 - delta*w)
        if re.search(r'1\s*-\s*[a-zA-Z\u0370-\u03ff]', formula):
            relations.append("CONDITIONED_EXISTENCE")
            
        # Recurrence check
        if '_{n+1}' in formula or '_{t+1}' in formula:
            relations.append("RECURSIVE_MEMORY")
            
        return relations

    def extract_gaps(self, formula: str) -> Set[str]:
        """Identifies conspicuously absent god-tokens (Gap Meaning)."""
        present = self.extract_explicit(formula)
        all_primitives = set(EXTENDED_GOD_TOKEN_SEEDS.keys())
        absent = all_primitives - present
        
        # Claude specifically noted SELF absence in the recurrence
        gaps = set()
        if 'SELF' not in present and 'z_{n+1}' in formula:
            gaps.add("¬SELF")
        if 'OBSERVATION' not in present:
            gaps.add("¬OBSERVATION")
            
        return gaps

    def get_joint_distribution(self, formula: str) -> Dict[str, float]:
        """
        Calculates the Bayesian Intersection (Product of Distributions).
        Returns probability weights for each God-Token in the lattice.

        Calibration check (Zipf): each merge level should produce a Zipfian
        distribution of attractor activations. If the distribution is Gaussian
        rather than Zipfian, the merge is using the wrong operation (summing
        when it should be multiplying).
        """
        explicit = self.extract_explicit(formula)
        relational = self.extract_relational(formula)
        gaps = self.extract_gaps(formula)
        
        # Initialize lattice weights (Gaussian-like prior, to beZipfian after product)
        all_tokens = EXTENDED_GOD_TOKEN_SEEDS.keys()
        weights = {t: 0.1 for t in all_tokens}
        
        # Apply Explicit Layer (Boost present)
        for t in explicit:
            weights[t] *= 8.0
            
        # Apply Relational Layer (Boost relevant paths)
        if "CONDITIONED_EXISTENCE" in relational:
            weights['EXISTENCE'] *= 12.0 # Primary focus
            weights['BOUNDARY'] *= 4.0
            weights['TIME'] *= 4.0
            
        if "CO-REQUIREMENT" in relational:
            weights['EXCHANGE'] *= 6.0
            
        if "RECURSIVE_MEMORY" in relational:
            weights['TIME'] *= 5.0
            weights['IDENTITY'] *= 3.0
            
        # Apply Gap Layer (Penalize absent)
        # We don't zero them out (Bayesian), we just suppress
        for gap in gaps:
            token_id = gap.replace("¬", "")
            if token_id in weights:
                weights[token_id] *= 0.05 # Stronger suppression
                
        # Normalize
        total = sum(weights.values())
        return {k: v/total for k, v in weights.items()}

    def distill_to_word(self, formula: str) -> str:
        """Finds the 'Word' (attractor path) the math becomes."""
        dist = self.get_joint_distribution(formula)
        # Sort by probability
        sorted_tokens = sorted(dist.items(), key=lambda x: x[1], reverse=True)
        
        # Take top-4 as the path to capture the full signature
        path = [t for t, p in sorted_tokens if p > 0.03][:4]
        
        return f"{' -> '.join(path)} (Primary: {path[0] if path else 'VOID'})"

if __name__ == "__main__":
    extractor = MathMeaningExtractor()
    test_formula = "z_{n+1} = z_n(1 - δ*w_n) + ε*x_n*y_n"
    
    print(f"Formula: {test_formula}")
    print(f"Explicit: {extractor.extract_explicit(test_formula)}")
    print(f"Relational: {extractor.extract_relational(test_formula)}")
    print(f"Gaps: {extractor.extract_gaps(test_formula)}")
    print(f"Distilled Word: {extractor.distill_to_word(test_formula)}")
