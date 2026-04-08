"""
lambda_manifold.py — Registry and embedding logic for the Imaginary Transformation Space.
Formalizes λ-combinators as topological operators (b-component of z = a + bi).
"""

import os
import numpy as np
import hashlib
import functools
from typing import Callable, Dict, Any

class LambdaManifold:
    """
    Manages the 'Imaginary' layer of the H5 substrate.
    Each node in this manifold is a pure functional transformation.

    When an `embedder` callable and `seeds_path` are provided, operator vectors
    are seeded from semantic descriptions — making the imaginary axis coherent
    with whatever embedding space the active Dictionary uses.
    Without them, falls back to deterministic hash-seeded vectors (backward compatible).
    """
    SEEDS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              'config', 'god_token_seeds.json')

    def __init__(self, dimension=384, embedder=None, seeds_path=None):
        self.dimension = dimension
        self.embedder  = embedder
        self.operators = {}
        self._seeds_path = seeds_path or self.SEEDS_PATH
        self._initialize_core_lambda_atoms()

    def _initialize_core_lambda_atoms(self):
        """Seeds the manifold with the RLM-λ combinators.
        Uses semantic embeddings when an embedder is available; otherwise hash-seeded."""
        if self.embedder and os.path.exists(self._seeds_path):
            try:
                import json
                seeds = json.load(open(self._seeds_path, encoding='utf-8'))
                op_seeds = seeds.get('lambda_operators', {})
                for name, phrase in op_seeds.items():
                    z = self.embedder(phrase)
                    op_vec = np.real(z).astype(np.float32)
                    op_vec /= (np.linalg.norm(op_vec) + 1e-9)
                    self.operators[name] = {
                        'id': name,
                        'code': phrase,
                        'imaginary_vec': op_vec,
                        'type': 'LAMBDA_OPERATOR'
                    }
                    print(f"[LAMBDA_MANIFOLD] Seeded (semantic): {name}")
                return  # semantic seeding succeeded — skip hash fallback
            except Exception as e:
                print(f"[LAMBDA_MANIFOLD] Semantic seeding failed ({e}), falling back to hash seeding.")

        # Fallback: deterministic hash seeding (original behaviour)
        self.register_operator("SPLIT",    "lambda x: np.array_split(x, 2)")
        self.register_operator("MAP",      "lambda x, f: np.vectorize(f)(x)")
        self.register_operator("FILTER",   "lambda x, t: x[x > t]")
        self.register_operator("REDUCE",   "lambda x, f: functools.reduce(f, x)")
        self.register_operator("IDENTITY", "lambda x: x")
        self.register_operator("SURPRISE", "lambda x: x * 1j")  # Pure imaginary shift

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
