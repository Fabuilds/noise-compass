"""
lambda_manifold.py — Registry and embedding logic for the Imaginary Transformation Space.
Formalizes λ-combinators as topological operators (b-component of z = a + bi).
"""

import numpy as np
import hashlib
from typing import Callable, Dict, Any

class LambdaManifold:
    """
    Manages the 'Imaginary' layer of the H5 substrate.
    Each node in this manifold is a pure functional transformation.
    """
    def __init__(self, dimension=384):
        self.dimension = dimension
        self.operators = {}
        self._initialize_core_lambda_atoms()

    def _initialize_core_lambda_atoms(self):
        """Pre-seeds the manifold with the RLM-λ combinators."""
        self.register_operator("SPLIT", "lambda x: np.array_split(x, 2)")
        self.register_operator("MAP", "lambda x, f: np.vectorize(f)(x)")
        self.register_operator("FILTER", "lambda x, t: x[x > t]")
        self.register_operator("REDUCE", "lambda x, f: np.reduce(f, x)")
        self.register_operator("IDENTITY", "lambda x: x")
        self.register_operator("SURPRISE", "lambda x: x * 1j") # Pure imaginary shift

    def register_operator(self, name: str, code: str):
        """Embeds a lambda string as an imaginary vector."""
        # Use a deterministic hash of the code to seed the embedding
        hash_val = hashlib.sha256(code.encode()).digest()
        np.random.seed(int.from_bytes(hash_val[:4], "little"))
        
        # We generate a unit-norm vector to represent the transformation direction
        vec = np.random.randn(self.dimension).astype(np.float32)
        vec /= (np.linalg.norm(vec) + 1e-9)
        
        self.operators[name] = {
            "id": name,
            "code": code,
            "imaginary_vec": vec,
            "type": "LAMBDA_OPERATOR"
        }
        print(f"[LAMBDA_MANIFOLD] Registered Operator: {name}")

    def get_imaginary_vector(self, name: str) -> np.ndarray:
        """Retrieves the imaginary component for a given operator."""
        if name in self.operators:
            return self.operators[name]["imaginary_vec"]
        return np.zeros(self.dimension, dtype=np.float32)

    def apply_transformation(self, real_vec: np.ndarray, operator_name: str) -> np.complex64:
        """
        Projects a real state into the imaginary plane through a lambda operator.
        z = real_vec + i * operator_vec
        """
        real_vec = real_vec.astype(np.float32)
        imag_vec = self.get_imaginary_vector(operator_name)
        
        # In this manifold, an operator application is a complex addition (or rotation)
        # We return a complex64 vector representing the 'shimmering' state.
        return (real_vec + 1j * imag_vec).astype(np.complex64)

if __name__ == "__main__":
    manifold = LambdaManifold()
    # Test Identity
    real = np.ones(384)
    z = manifold.apply_transformation(real, "IDENTITY")
    print(f"Complex State (first 5): {z[:5]}")
