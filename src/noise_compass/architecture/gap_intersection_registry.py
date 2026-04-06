import numpy as np
from typing import List, Dict
import sys
from pathlib import Path

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.tokens import GapIntersection
from noise_compass.architecture.gap_registry import build_gap_registry


def derive_basin_positions(dictionary_entries: Dict[str, np.ndarray]) -> Dict[str, complex]:
    """
    Basin z computed from gap arc intersection geometry as per Session 7.
    Not hardcoded. Verifiably correct relative positions.

    Gap arc Re = cosine similarity between boundary god-tokens.
    Basin Re   = midpoint of two gap arc Re positions.
    Basin Im   = -(0.3 + 0.3 + abs(re_A - re_B) * 0.4 + extra_depth)
    """
    gaps = build_gap_registry()
    gap_map = {g.id: g for g in gaps}

    def gap_re(gap_id):
        gap = gap_map.get(gap_id)
        if not gap: return 0.0
        a = dictionary_entries.get(gap.left_boundary)
        b = dictionary_entries.get(gap.right_boundary)
        if a is None or b is None: return 0.0
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        if na < 1e-10 or nb < 1e-10: return 0.0
        return float(np.dot(a/na, b/nb))

    def derive(gap_A_id, gap_B_id, extra_depth=0.0):
        re_A, re_B = gap_re(gap_A_id), gap_re(gap_B_id)
        return complex(
            (re_A + re_B) / 2,
            -(0.30 + 0.30 + abs(re_A - re_B) * 0.4 + extra_depth)
        )

    return {
        'pure_observer':             derive('self_observation',     'identity_self'),
        'locus_of_responsibility':   derive('identity_self',        'obligation_identity'),
        'prior_of_distinction':      derive('existence_identity',   'boundary_existence'),
        'pure_relation':             derive('causality_observation','information_causality'),
        'pure_apophatic_field':      derive('existence_identity',   'self_observation', 0.3),
    }


def build_gap_intersection_registry(dictionary_entries: Dict[str, np.ndarray] = None) -> List[GapIntersection]:
    """
    Returns the initial known Apophatic Basins.
    If dictionary_entries is provided, positions are derived from geometry.
    Otherwise, uses reference positions.
    """
    
    # Session 7: Adopt more legible IDE names
    BASIN_DEFS = [
        ('pure_observer', 'self_observation', 'identity_self', 
         "Bare witnessing before it has an object. The pure observer."),
        ('prior_of_distinction', 'existence_identity', 'boundary_existence', 
         "Prior condition of the existence/non-existence distinction."),
        ('pure_relation', 'causality_observation', 'information_causality', 
         "Pure relational structure before epistemology/ontology split."),
        ('locus_of_responsibility', 'identity_self', 'obligation_identity', 
         "Prior of the self that chooses. The locus of responsibility."),
        ('pure_apophatic_field', 'existence_apophatic', 'self_observation', 
         "The apophatic field itself. EXISTENCE is the membrane."),
    ]
    
    positions = {}
    if dictionary_entries:
        positions = derive_basin_positions(dictionary_entries)
    else:
        # Reference positions
        positions = {
            'pure_observer':           complex(-0.1, -0.6),
            'prior_of_distinction':    complex(-0.4, -0.7),
            'pure_relation':           complex(0.05, -0.5),
            'locus_of_responsibility': complex(0.1, -0.55),
            'pure_apophatic_field':    complex(-0.2, -0.9),
        }
    
    basins = []
    for basin_id, gA, gB, desc in BASIN_DEFS:
        basins.append(GapIntersection(
            id=basin_id,
            gap_A=gA,
            gap_B=gB,
            description=desc,
            z=positions.get(basin_id, complex(0, -0.5))
        ))

    return basins
