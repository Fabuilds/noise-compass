"""
polyhedral_web.py — 3D Structural Layout for the Semantic Manifold.
Implements Tutte's Theorem with Barycentric Relaxation.
"""

import os
import sys
import numpy as np
import networkx as nx

# Ensure package is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.lattice_graph import LatticeGraph
from noise_compass.system.core import Scout
from noise_compass.system.dictionary import Dictionary

class PolyhedralEngine:
    """
    Geometrically grounds the fluid substrate in a 3D Polyhedral Web.
    Fixed Shell: 12 God-Tokens at Icosahedron Vertices.
    Interior: All Projections (Barycentric relaxation).
    """
    def __init__(self, h5=None, graph=None):
        self.h5 = h5 or H5Manager()
        self.graph = graph or LatticeGraph(h5=self.h5)
        self.phi = (1 + np.sqrt(5)) / 2 # Golden Ratio
        
        # 1. Define Icosahedral Vertices (for the 12 God-Tokens)
        self.fixed_vertices = [
            (0, 1, self.phi), (0, 1, -self.phi), (0, -1, self.phi), (0, -1, -self.phi),
            (1, self.phi, 0), (1, -self.phi, 0), (-1, self.phi, 0), (-1, -self.phi, 0),
            (self.phi, 0, 1), (-self.phi, 0, 1), (self.phi, 0, -1), (-self.phi, 0, -1)
        ]
        self.fixed_vertices = [np.array(v) / np.linalg.norm(v) for v in self.fixed_vertices]

    def crystallize_3d_web(self, iterations=50):
        """Calculates 3D coordinates using Barycentric Relaxation (Tutte's Method)."""
        print("[POLYHEDRAL] Crystallizing 3D Web coordinates...")
        
        # Ensure graph is synced
        scout = Scout(Dictionary(self.h5))
        self.graph.sync_with_substrate(scout)
        nx_graph = self.graph.graph
        
        # 1. Identify Fixed vs Mobile nodes
        fixed_nodes = {}
        god_tokens = [n for n, data in nx_graph.nodes(data=True) if data.get('type') == 'GOD_TOKEN']
        for i, node in enumerate(god_tokens):
            if i < len(self.fixed_vertices):
                fixed_nodes[node] = self.fixed_vertices[i]
        
        mobile_nodes = [n for n in nx_graph.nodes if n not in fixed_nodes and n != 'EGO_CURSOR']
        num_mobile = len(mobile_nodes)
        
        if num_mobile == 0:
            print("  [POLYHEDRAL] No mobile nodes to relax.")
            return

        # 2. Initialize Mobile positions (at origin)
        pos = {n: fixed_nodes[n] for n in fixed_nodes}
        for n in mobile_nodes:
            pos[n] = np.zeros(3)

        # 3. Iterative Relaxation (Tutte's Spring-like method)
        for i in range(iterations):
            max_drift = 0
            new_pos = pos.copy()
            
            for node in mobile_nodes:
                neighbors = list(nx_graph.neighbors(node)) + list(nx_graph.predecessors(node))
                # Remove duplicates
                neighbors = list(set(neighbors))
                # Filter out EGO_CURSOR which has no embedding/pos
                neighbors = [n for n in neighbors if n in pos]
                
                if not neighbors: continue
                
                # Weighted Barycenter
                target = np.zeros(3)
                total_weight = 0
                for neighbor in neighbors:
                    # Prefer high-weight edges
                    weight = 1.0
                    edge_data = nx_graph.get_edge_data(node, neighbor) or nx_graph.get_edge_data(neighbor, node)
                    if edge_data:
                        weight = edge_data.get('weight', 1.0)
                    
                    target += weight * pos[neighbor]
                    total_weight += weight
                
                new_pos[node] = target / (total_weight + 1e-9)
                drift = np.linalg.norm(new_pos[node] - pos[node])
                max_drift = max(max_drift, drift)
            
            pos = new_pos
            if max_drift < 1e-5:
                print(f"  [POLYHEDRAL] Converged in {i+1} iterations.")
                break
        
        # 4. Save back to the graph's metadata
        for node, coords in pos.items():
            nx_graph.nodes[node]['x'] = float(coords[0])
            nx_graph.nodes[node]['y'] = float(coords[1])
            nx_graph.nodes[node]['z'] = float(coords[2])
            
        print(f"  [POLYHEDRAL] {len(pos)} nodes grounded in 3D space.")
        self.graph.save_registry()

if __name__ == "__main__":
    pe = PolyhedralEngine()
    pe.crystallize_3d_web()
