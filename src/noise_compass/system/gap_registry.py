import h5py
import numpy as np
import os
from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.gap_constants import EXTENDED_GOD_TOKEN_SEEDS, INSTANCE_GOD_TOKEN_SEEDS, GAP_VIOLATION_CONSEQUENCES

class GapRegistry:
    """
    Topological Constraint Engine (The Ghost Dictionary).
    Enforces 'Structural Integrity' by identifying missing semantic nodes.
    """
    def __init__(self, manager: H5Manager = None):
        self.manager = manager or H5Manager()
        self.cached_gaps = {}
        self.load_gaps()

    def load_gaps(self):
        """Pre-caches gap definitions from the H5 substrate."""
        try:
            with self.manager.get_file("language", mode='r') as f:
                if f is not None and 'gaps' in f:
                    for gap_name in f['gaps'].keys():
                        node = f[f'gaps/{gap_name}']
                        self.cached_gaps[gap_name] = {
                            'left': node.attrs.get('left_boundary', ''),
                            'right': node.attrs.get('right_boundary', ''),
                            'void_depth': float(node.attrs.get('void_depth', 0.5)),
                            'void': node.attrs.get('void', False),
                            'tension_threshold': float(node.attrs.get('tension_threshold', 0.1)),
                            'binder_depth': int(node.attrs.get('binder_depth', 0)) # Phase 125: De Bruijn Index
                        }
        except Exception as e:
            print(f"[GAP_REGISTRY] [WARNING] Failed to load gaps from H5: {e}")

    def detect_violations(self, field: dict, threshold: float = 0.3, current_depth: int = 0) -> dict:
        """
        Identifies 'Logic Decompression' events.
        Phase 125: Filters by binder_depth (De Bruijn logic) to isolate nested reasoning levels.
        """
        violations = {}
        for gap_name, config in self.cached_gaps.items():
            # Only enforce gaps that match the current reasoning depth
            if config.get('binder_depth', 0) != current_depth:
                continue

            left = config['left']
            right = config['right']
            
            # Skip if we don't have these tokens in the field
            if left not in field or right not in field:
                continue

            def get_val(node):
                v = field.get(node, 0)
                if isinstance(v, dict):
                    return v.get('magnitude', 0)
                return float(v)

            left_res = get_val(left)
            right_res = get_val(right)

            # A violation occurs if one is active (>threshold) and the other is dark (<0.1)
            is_violation = False
            if left_res > threshold and right_res < 0.1:
                is_violation = True
                missing = right
            elif right_res > threshold and left_res < 0.1:
                is_violation = True
                missing = left
            
            if is_violation:
                tension = self.calculate_tension(gap_name, field)
                violation_info = {
                    'missing': missing,
                    'tension': tension,
                    'void_depth': config['void_depth'],
                    'left': left,
                    'right': right
                }
                # Phase 125: Enriched Rejection - Log for future analysis
                self.log_violation(gap_name, violation_info)
                violations[gap_name] = violation_info
        return violations

    def calculate_tension(self, gap_name, field: dict) -> float:
        """
        Calculates the Apophatic Tension: T = |Res(A) - Res(B)| * VoidDepth.
        Handles both interference fields (dict of dicts) and neural states (dict of floats).
        """
        config = self.cached_gaps.get(gap_name)
        if not config: return 0.0

        def get_val(node):
            v = field.get(node, 0)
            if isinstance(v, dict):
                return v.get('magnitude', 0)
            return float(v)

        left_res = get_val(config['left'])
        right_res = get_val(config['right'])

        # Tension is the imbalance scaled by the depth of the void
        imbalance = abs(left_res - right_res)
        return float(imbalance * config['void_depth'])

    def register_gap(self, gap_name, left, right, void_depth=0.5, void=True,
                     binder_depth=0, classification: str = None,
                     alignment: float = None, gradient: float = None):
        """Crystallizes a new gap into the H5 substrate.

        Phase 8c extension: accepts compositor-derived metadata:
            classification — 'primitive', 'frontier', etc.
            alignment      — 0.0-1.0 (1.0 = fully resolved)
            gradient       — CW_mean - CCW_mean (positive = CW dominant)
        """
        metadata = {
            'left_boundary':  left,
            'right_boundary': right if right else left,
            'void_depth':     void_depth,
            'void':           void,
            'tension':        0.0,
            'binder_depth':   binder_depth,
        }
        # Phase 8c: compositor-derived attrs (optional)
        if classification is not None:
            metadata['classification'] = classification
        if alignment is not None:
            metadata['alignment'] = float(alignment)
        if gradient is not None:
            metadata['gradient'] = float(gradient)

        # Save to H5 via manager
        for key, val in metadata.items():
            self.manager.set_attr("language", f"gaps/{gap_name}", key, val)

        # Update in-memory cache
        self.cached_gaps[gap_name] = {
            'left':              left,
            'right':             right if right else left,
            'void_depth':        void_depth,
            'void':              void,
            'tension_threshold': 0.1,
            'classification':    classification or 'unknown',
            'alignment':         alignment if alignment is not None else 0.5,
            'gradient':          gradient if gradient is not None else 0.0,
        }
        print(f"[GAP_REGISTRY] Gap '{gap_name}' → {left} ↔ {right}  "
              f"[{classification or 'structural'}  depth={void_depth:.2f}]")


    def log_violation(self, gap_name, info):
        """Records the gap violation as an enriched dissonance object."""
        context = {
            'event': 'GAP_VIOLATION',
            'gap': gap_name,
            'missing_node': info['missing'],
            'tension': info['tension'],
            'boundaries': f"{info['left']} <-> {info['right']}",
            'verdict': 'REJECTED'
        }
        self.manager.record_dissonance_context(f"GAP_{gap_name}", context)

    def get_void_report(self, field: dict) -> dict:
        """Aggregates all active gaps and their current tension levels."""
        report = {}
        for gap_name in self.cached_gaps:
            tension = self.calculate_tension(gap_name, field)
            if tension > 0.05: # Report anything with visible tension
                report[gap_name] = tension
        return report
