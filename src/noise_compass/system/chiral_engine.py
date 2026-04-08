import os
import json
import time
import random
import glob
from noise_compass.system.knowledge_lattice import KnowledgeLattice

# Default path where compositor outputs are written
COMPOSITOR_OUTPUT_DIR = "E:/Claude Input/Claude04062026"

class ChiralEngine:
    def __init__(self, lattice: KnowledgeLattice, compositor_dir: str = None):
        self.lattice = lattice
        self.sanity_depth = lattice.sanity_depth
        self.compositor_dir = compositor_dir or COMPOSITOR_OUTPUT_DIR
        self._compositor_report = None   # cached on first load
        
    def _load_compositor_report(self) -> dict:
        """Finds the most-recent compositor report in compositor_dir.
        Returns {} if no report exists (triggers random-walk fallback)."""
        if self._compositor_report is not None:
            return self._compositor_report
        pattern = os.path.join(self.compositor_dir, "compositor*.json")
        matches = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
        if not matches:
            return {}
        try:
            with open(matches[0], encoding='utf-8') as f:
                self._compositor_report = json.load(f)
            print(f"[CHIRAL] Loaded compositor report: {os.path.basename(matches[0])}")
            return self._compositor_report
        except Exception as e:
            print(f"[CHIRAL] Failed to load compositor report: {e}")
            return {}

    def _concepts_by_direction(self, cw: bool) -> list:
        """Returns concept_ids filtered by gradient sign.
        gradient > 0 = CW dominant, gradient < 0 = CCW dominant."""
        report   = self._load_compositor_report()
        concepts = report.get('concepts', [])
        if isinstance(report, list):
            concepts = report
        sign = (lambda g: g > 0) if cw else (lambda g: g < 0)
        return [c.get('concept_id', c.get('id', '?'))
                for c in concepts
                if sign(float(c.get('gradient', 0.0)))]

    def run_model_a(self, seed_node):
        """Model A: Constructive Traversal (CW / Forward).
        Uses compositor gradient > 0 nodes when a report is available;
        falls back to random walk simulation otherwise."""
        path = [seed_node]
        self.lattice.record_traversal("A", path, "forward", "start")

        cw_concepts = self._concepts_by_direction(cw=True)
        if cw_concepts:
            # Use compositor-derived path (CW-dominant concepts)
            for concept_id in cw_concepts[:self.sanity_depth]:
                path.append(concept_id)
                if self.lattice.is_void(self.lattice.get_path(concept_id, "concept_nodes")):
                    self.lattice.record_traversal("A", path, "forward", "void")
                    return path
            self.lattice.record_traversal("A", path, "forward", "compositor_end")
            return path

        # Fallback: random walk simulation (original Phase 34 logic)
        current_folder = self.lattice.get_path(seed_node)
        for depth in range(2, self.sanity_depth + 1):
            if self.lattice.is_void(current_folder):
                self.lattice.record_traversal("A", path, "forward", "void")
                return path
            next_nodes = ["EXISTENCE", "IDENTITY", "INFORMATION", "COHERENCE"]
            next_node  = random.choice(next_nodes)
            path.append(next_node)
            current_folder = self.lattice.get_path(next_node)
            if depth >= self.sanity_depth:
                self.lattice.record_traversal("A", path, "forward", "depth_limit")
                return path
        return path

    def run_model_b(self, seed_node):
        """Model B: Reductive Traversal (CCW / Backward).
        Uses compositor gradient < 0 nodes when a report is available;
        falls back to reductive anchor simulation otherwise."""
        path = [seed_node]
        self.lattice.record_traversal("B", path, "backward", "start")

        ccw_concepts = self._concepts_by_direction(cw=False)
        if ccw_concepts:
            for concept_id in ccw_concepts[:self.sanity_depth]:
                path.append(concept_id)
                if self.lattice.is_void(self.lattice.get_path(concept_id, "concept_nodes")):
                    self.lattice.record_traversal("B", path, "backward", "void")
                    return path
            self.lattice.record_traversal("B", path, "backward", "compositor_end")
            return path

        # Fallback: reductive anchor simulation
        current_folder = self.lattice.get_path(seed_node)
        for depth in range(self.lattice.get_depth(current_folder), 0, -1):
            if self.lattice.is_void(current_folder):
                self.lattice.record_traversal("B", path, "backward", "void")
                return path
            path.append("SELF")   # Reductive anchor
            if depth <= 1:
                self.lattice.record_traversal("B", path, "backward", "root")
                return path
        return path

class ApexObserver:
    def __init__(self, lattice: KnowledgeLattice):
        self.lattice = lattice

    def observe(self, model_a_record, model_b_record):
        """
        Apex: Identifies 'The Fold' and computes phase angle.
        """
        path_a = model_a_record["path"]
        path_b = model_b_record["path"]
        
        # Find intersection (The Fold)
        intersection = list(set(path_a) & set(path_b))
        
        # Phase Angle computation (heuristic for Phase 34)
        # 0.0 (Apophatic) to 3.14 (Crystallized)
        if not intersection:
            phase = 0.2 # Near apophatic
        else:
            # More intersection = higher phase
            phase = min(3.14, len(intersection) * 0.5)
            
        verdict = "SUPERPOSITION"
        if phase > 2.5: verdict = "CRYSTALLIZED"
        elif phase < 0.5: verdict = "APOPHATIC"
        
        return {
            "phase_angle": phase,
            "fold_positions": intersection,
            "verdict": verdict
        }
