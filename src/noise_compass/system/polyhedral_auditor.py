"""
polyhedral_auditor.py — Structural Audit & Repair for the H5 Substrate.
Ensures 4-connection connectivity and identifies placeholder nodes.
"""

import os
import sys
import json
import time
import numpy as np
import networkx as nx

# Ensure package is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.lattice_graph import LatticeGraph
from noise_compass.system.core import Scout
from noise_compass.system.dictionary import Dictionary
from noise_compass.system.causal_tree import CausalDAG

class PolyhedralAuditor:
    """
    Scans the LatticeGraph for structural violations.
    - Connectivity Check: min(out_degree) >= 4.
    - Placeholder Audit: Identify nodes with redundant or empty content.
    - Automatic Repair: Use Scout/Dictionary to bridge low-info nodes.
    """
    def __init__(self, h5=None, graph=None):
        self.h5 = h5 or H5Manager()
        self.graph = graph or LatticeGraph(h5=self.h5)
        self.causal_dag = CausalDAG(manager=self.h5)
        self.dictionary = Dictionary(self.h5)
        self.scout = Scout(self.dictionary)

    def run_audit(self):
        """Performs a full structural audit of the substrate."""
        print("[AUDITOR] Starting Polyhedral Substrate Audit...")
        self.graph.sync_with_substrate(self.scout)
        nx_graph = self.graph.graph
        
        violations = []
        placeholders = []
        
        # 1. Structural Checks
        for node, data in nx_graph.nodes(data=True):
            if node == "EGO_CURSOR": continue
            
            # Connection Check
            out_degree = nx_graph.out_degree(node)
            if out_degree < 4:
                violations.append((node, "LOW_CONNECTIVITY", out_degree))
            
            # Placeholder Check
            meta = data.get('metadata', {})
            if meta.get('type') == 'PLACEHOLDER' or data.get('mass', 1.0) < 0.1:
                placeholders.append(node)
                
        print(f"  [AUDITOR] Found {len(violations)} connectivity violations.")
        print(f"  [AUDITOR] Found {len(placeholders)} placeholder nodes.")
        
        # 2. Automated Repair Loop
        if violations:
            self.repair_connectivity(violations)
            
        print("[AUDITOR] Audit Complete.")
        return violations, placeholders

    def stamp_node(self, node_id):
        """
        Synchronous Hook: Stamping a new node with its 4 resonant paths.
        Used at the moment of projection.
        """
        print(f"  [STAMPER] Stamping new node '{node_id}'...")
        emb_a, meta_a = self.h5.get_projection(node_id)
        if emb_a is None: return
        
        # Calculate resonances across the manifold
        all_ids = self.h5.get_all_projections()
        candidates = []
        for other_id in all_ids:
            if other_id == node_id: continue
            emb_b, _ = self.h5.get_projection(other_id)
            if emb_b is None: continue
            
            sim = np.dot(emb_a, emb_b) / (np.linalg.norm(emb_a) * np.linalg.norm(emb_b) + 1e-9)
            candidates.append((other_id, sim))
        
        # Add God-Tokens to candidates too
        for gt in self.dictionary.god_tokens.keys():
            emb_gt = self.dictionary.god_tokens[gt].embedding
            if emb_gt is None: continue
            sim = np.dot(emb_a, emb_gt) / (np.linalg.norm(emb_a) * np.linalg.norm(emb_gt) + 1e-9)
            candidates.append((gt, sim))

        candidates.sort(key=lambda x: -x[1])
        
        # Stamp the top 4
        for i in range(min(4, len(candidates))):
            target, sim = candidates[i]
            rel_info = f"Phase 139: Informed path to '{target}' (resonance: {sim:.3f})."
            self.causal_dag.add_relation(node_id, target, rel_type="INFORMED", weight=float(sim), info=rel_info)

    def repair_connectivity(self, violations):
        """Forces informational links to resolve connectivity violations."""
        print(f"[AUDITOR] Repairing {len(violations)} structural holes...")
        
        for node, reason, current_deg in violations:
            needed = 4 - current_deg
            print(f"  [AUDITOR] Node '{node}' needs {needed} more connections.")
            
            # Calculate all resonances to find best candidates
            emb_a = self.graph.graph.nodes[node].get('embedding')
            if emb_a is None: continue
            
            candidates = []
            for n_target, data_target in self.graph.graph.nodes(data=True):
                if n_target == node or n_target == "EGO_CURSOR" or self.graph.graph.has_edge(node, n_target):
                    continue
                
                emb_b = data_target.get('embedding')
                if emb_b is None: continue
                
                sim = np.dot(emb_a, emb_b) / (np.linalg.norm(emb_a) * np.linalg.norm(emb_b) + 1e-9)
                candidates.append((n_target, sim))
            
            # Sort by resonance
            candidates.sort(key=lambda x: -x[1])
            
            # Bridge the gap
            for i in range(min(needed, len(candidates))):
                target, sim = candidates[i]
                # Revise the link: Add specific 'Information' metadata
                rel_info = f"Structural integrity bridge from '{node}' to '{target}' based on {sim:.3f} resonance."
                print(f"    -> Adding Informational Link: {node} -> {target}")
                self.causal_dag.add_relation(node, target, rel_type="BRIDGE", weight=float(sim), info=rel_info)

if __name__ == "__main__":
    auditor = PolyhedralAuditor()
    auditor.run_audit()
