"""
gap_registry.py (Architecture Wrapper)
Phase 125: Forwarding Module.
Proxies all gap-related requests to the System Substrate (E:/Antigravity/Runtime).
This maintains backward compatibility for the Architecture layer while 
ensuring a single source of truth for the Algebraic Lambda Calculus logic.
"""

import sys
import os

# Ensure project root is available for absolute imports
ROOT_PATH = 'E:/Antigravity'
if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH)

# Forwarding imports for Constants
from noise_compass.system.gap_constants import (
    EXTENDED_GOD_TOKEN_SEEDS,
    INSTANCE_GOD_TOKEN_SEEDS,
    GAP_VIOLATION_CONSEQUENCES
)

# Forwarding imports for Logic
from noise_compass.system.gap_registry import GapRegistry

# Re-implementing functional interfaces for backward compatibility
from noise_compass.architecture.tokens import GapToken

def build_universal_gaps() -> list:
    """
    Returns the list of universal structural voids.
    Note: These are now managed by the System.GapRegistry in H5.
    This function remains as a legacy seeder interface.
    """
    gaps = []
    # Simplified legacy definitions (Scout now queries H5)
    # We populate some defaults if needed for offline boot.
    return gaps

def build_instance_gaps() -> list:
    return []

def build_gap_registry() -> list:
    """Wrapper to maintain backward compatibility for seeders."""
    return build_universal_gaps() + build_instance_gaps()

def get_gap_by_id(gap_id: str, registry: list) -> GapToken:
    for gap in registry:
        if gap.id == gap_id:
            return gap
    return None

def gaps_containing(god_token_id: str, registry: list) -> list:
    return [g for g in registry
            if g.left_boundary == god_token_id
            or g.right_boundary == god_token_id]

def gaps_between(gt_a: str, gt_b: str, registry: list) -> list:
    return [g for g in registry
            if set([g.left_boundary, g.right_boundary]) == set([gt_a, gt_b])]

# If this is called directly, verify the forwarding
if __name__ == "__main__":
    print("[SYSTEM] Architecture Gap Registry Wrapper Active.")
    print(f"[SYSTEM] Centralized God Tokens: {len(EXTENDED_GOD_TOKEN_SEEDS)}")
