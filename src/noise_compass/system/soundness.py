"""
soundness.py — Ternary Γ-Semiring Soundness Monitor.
Following Theorem 3.1: "Ternary Γ-Semirings as a Novel Algebraic Framework 
for Learnable Symbolic Reasoning" (Nov 2025).

Calculates Algebraic Regularization (Associativity and Distributivity) 
to ensure the reasoning engine remains sound.
"""

import numpy as np

class SoundnessMonitor:
    def __init__(self, tolerance=0.1):
        self.tolerance = tolerance
        self.history = []

    def calculate_ternary_op(self, x, y, z, gamma=1.0):
        """
        Simplified Ternary Operator implementation for soundness checking.
        In the RLM, this represents the resonance between three semantic nodes.
        [x, y, z]_gamma = (x * y * z) modulated by gamma (context/semiring).
        """
        # Linear-Algebraic Lambda Calculus: Ternary resonance is the element-wise 
        # product of three vectors modulated by the semiring dampening (gamma).
        # We use sqrt/magnitudes to maintain Positive Semiring [0, 1] range.
        return np.clip(x * y * z * gamma, 0, 1)

    def check_associativity(self, x, y, z, w, v, gamma=1.0):
        """
        Theorem 3.1: [[x, y, z], w, v] == [x, [y, z, w], v]
        Returns the L2 distance (violation score). 0.0 is perfect soundness.
        """
        # Left-nested composition
        lhs_inner = self.calculate_ternary_op(x, y, z, gamma)
        lhs = self.calculate_ternary_op(lhs_inner, w, v, gamma)
        
        # Right-nested composition
        rhs_inner = self.calculate_ternary_op(y, z, w, gamma)
        rhs = self.calculate_ternary_op(x, rhs_inner, v, gamma)
        
        violation = np.linalg.norm(lhs - rhs)
        return float(violation)

    def check_distributivity(self, x, y, z, w, gamma=1.0):
        """
        Theorem 3.1: [x + y, z, w] == [x, z, w] + [y, z, w]
        Note: '+' here is the additive monoid operation (semantic superposition).
        """
        # Superposition (A + B)
        sum_xy = np.clip(x + y, 0, 1)
        lhs = self.calculate_ternary_op(sum_xy, z, w, gamma)
        
        # Individual resonance summation
        rhs_1 = self.calculate_ternary_op(x, z, w, gamma)
        rhs_2 = self.calculate_ternary_op(y, z, w, gamma)
        rhs = np.clip(rhs_1 + rhs_2, 0, 1)
        
        violation = np.linalg.norm(lhs - rhs)
        return float(violation)

    def get_soundness_score(self, field_vectors, gamma=1.0, samples=5):
        """
        Performs a batch soundness check on the current interference field.
        Returns a score from 0.0 (Chaotic) to 1.0 (Sound).
        """
        if len(field_vectors) < 5:
            return 1.0 # Insufficient data to detect warping
            
        violations = []
        vec_list = list(field_vectors.values())
        
        for _ in range(samples):
            # Sample 5 random vectors for associativity check
            if len(vec_list) >= 5:
                s = random_sample = [vec_list[i] for i in np.random.choice(len(vec_list), 5, replace=False)]
                v_assoc = self.check_associativity(s[0], s[1], s[2], s[3], s[4], gamma)
                v_dist = self.check_distributivity(s[0], s[1], s[2], s[3], gamma)
                violations.append((v_assoc + v_dist) / 2.0)
        
        avg_violation = np.mean(violations) if violations else 0.0
        # Normalizing to 0-1 score (Exponential decay of soundness)
        score = np.exp(-avg_violation * 2.0)
        
        self.history.append(score)
        if len(self.history) > 100: self.history.pop(0)
        
        return float(score)

if __name__ == "__main__":
    # Self-test
    monitor = SoundnessMonitor()
    x = np.random.rand(1024)
    y = np.random.rand(1024)
    z = np.random.rand(1024)
    w = np.random.rand(1024)
    v = np.random.rand(1024)
    
    score = monitor.get_soundness_score({"a":x, "b":y, "c":z, "d":w, "e":v})
    print(f"[TEST] Ternary Soundness Score: {score:.4f}")
