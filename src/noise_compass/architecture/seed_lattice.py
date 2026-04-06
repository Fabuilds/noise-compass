"""
Iterative Seed Lattice (v1.0)
Defines the minimal valid seed set for the Antigravity manifold.
Tokens evolved from existing gap analyses.
"""

SEED_SET = {
    "SELF",
    "EXCHANGE",
    "OBLIGATION",
    "CAUSALITY",
    "EXISTENCE",
    "BODY",
    "OBSERVATION"
}

def is_seed(token_id: str) -> bool:
    """Checks if a token is part of the provisional seed lattice."""
    return token_id.upper() in SEED_SET

def get_seed_set() -> set:
    """Returns the current seed lattice set."""
    return SEED_SET.copy()
