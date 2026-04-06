import networkx as nx
import numpy as np
import json
import os
import time
from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.causal_tree import CausalDAG

class LatticeGraph:
    """
    Formal Graph-Theoretic Layer for the Semantic Manifold.
    Crystallizes fluid vector superpositions into a queryable topology.
    """
    def __init__(self, h5=None):
        self.h5 = h5 or H5Manager()
        self.graph = nx.DiGraph()
        self.nodes = [
            "EXISTENCE", "IDENTITY", "BOUNDARY", "OBSERVATION", 
            "INFORMATION", "CAUSALITY", "EXCHANGE", "OBLIGATION", 
            "TIME", "PLACE", "COHERENCE", "SELF"
        ]
        self.registry_path = "E:/Antigravity/Runtime/lattice_graph.json"
        self.causal_dag = CausalDAG(manager=self.h5)
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)

    def sync_with_substrate(self, scout):
        """
        Synchronizes nodes with H5 and calculates topology (edges).
        Uses embedding similarity + causal links + encoded projections.
        """
        print("[LATTICE_GRAPH] Synchronizing with Substrate...")
        
        # Phase 143/145 Patch: Capture current EGO dock before clearing
        current_dock = self.ego_dock
        
        self.graph.clear()
        
        # 1. Add God-Token Nodes
        for node in self.nodes:
            gt = scout.dictionary.god_tokens.get(node)
            emb = gt.embedding if gt else None
            activation = self.h5.get_attr("language", f"god_tokens/{node}", "activation") or 0.0
            mass = self.h5.get_attr("language", f"god_tokens/{node}", "bubble_mass") or 1.0
            self.graph.add_node(node, activation=activation, mass=mass, type="GOD_TOKEN", embedding=emb)
            
        # 2. Add Document Projection Nodes
        projections = self.h5.get_all_projections()
        for doc_id in projections:
            vec, meta = self.h5.get_projection(doc_id)
            self.graph.add_node(doc_id, type="PROJECTION", metadata=meta, embedding=vec)

        # 3. Add Similarity-Based Edges (for all nodes with embeddings)
        all_nodes_list = list(self.graph.nodes(data=True))
        embeddings = {n: data.get('embedding') for n, data in all_nodes_list if data.get('embedding') is not None}
        
        node_names = list(embeddings.keys())
        for i, node_a in enumerate(node_names):
            emb_a = embeddings[node_a]
            norm_a = np.linalg.norm(emb_a) + 1e-9
            
            # Track all similarities for this node to ensure minimum connectivity
            similarities = []
            
            for j, node_b in enumerate(node_names):
                if i == j: continue 
                emb_b = embeddings[node_b]
                
                # Cosine Similarity
                norm_b = np.linalg.norm(emb_b) + 1e-9
                sim = float(np.dot(emb_a, emb_b) / (norm_a * norm_b))
                similarities.append((node_b, sim))
                
                if sim > 0.85:
                    self.graph.add_edge(node_a, node_b, weight=sim, type="associative")

            # Phase 138 Patch: Minimum Connectivity (at least 4 connections per node)
            current_edges = list(self.graph.successors(node_a))
            if len(current_edges) < 4:
                # Sort by similarity descending and take top N to reach 4 total
                similarities.sort(key=lambda x: -x[1])
                added = 0
                for target_node, sim in similarities:
                    if target_node not in current_edges:
                        self.graph.add_edge(node_a, target_node, weight=sim, type="associative_forced")
                        added += 1
                        if len(current_edges) + added >= 4:
                            break
                print(f"  [LATTICE_GRAPH] Forced {added} edges for node '{node_a}' into the Polyhedral Web.")
                    
        # 4. Add Encoded Transitions from CausalDAG
        self.causal_dag.load_graph()
        for u, v, d in self.causal_dag.graph.edges(data=True):
            self.graph.add_edge(u, v, weight=d.get('weight', 1.0), type=d.get('type', 'causal'))
            
        # 5. Add the Recursive Observer (The "I")
        self.graph.add_node("EGO_CURSOR", activation=1.0, mass=0.0, type="OBSERVER")
        
        # 6. Phase 144: Sync Imaginary Lambda Manifold
        self.sync_imaginary_manifold()
        
        # Phase 143/145 Patch: Restore EGO dock (restored within scope of current_dock)
        if current_dock and current_dock in self.graph:
            self.dock_ego(current_dock)
        elif "IDENTITY" in self.graph:
            self.dock_ego("IDENTITY") # Default grounding

    def sync_imaginary_manifold(self):
        """Phase 144: Injects functional λ-operators into the graph as Imaginary Nodes."""
        from noise_compass.system.lambda_manifold import LambdaManifold
        lman = LambdaManifold()
        
        print("  [LATTICE_GRAPH] Synchronizing Imaginary Manifold...")
        for name, op in lman.operators.items():
            node_id = f"LAMBDA_{name}"
            if node_id not in self.graph:
                # Operators don't have real embeddings in the H5 sense, but they exist 
                # in the imaginary plane.
                self.graph.add_node(node_id, 
                    type="IMAGINARY", 
                    role="OPERATOR",
                    code=op['code']
                )
                print(f"    Injected Imaginary Operator: {node_id}")

    @property
    def ego_dock(self):
        """Returns the node the EGO_CURSOR is currently docked to."""
        if "EGO_CURSOR" not in self.graph:
            return None
        edges = list(self.graph.edges("EGO_CURSOR"))
        return edges[0][1] if edges else None

    def dock_ego(self, node_name):
        """
        Docks the Recursive Observer at a specific node in the manifold.
        Establishes a subjective 'I' viewpoint.
        """
        if node_name not in self.graph.nodes: return
        
        # Clear previous ego links (pure presence)
        previous_edges = list(self.graph.edges("EGO_CURSOR"))
        for u, v in previous_edges:
            self.graph.remove_edge(u, v)
            
        # Establish the new Subject/Object relationship
        self.graph.add_edge("EGO_CURSOR", node_name, weight=2.0, type="perspective")
        print(f"  [EGO_GRAPH] Cursor docked at '{node_name}' (Subjective 'I' Frame established).")

    def get_optimal_walk(self, intent_vec, scout, depth=3):
        """
        Calculates the most structurally resonant path through the graph.
        Incorporates Perspective Bias from the EGO_CURSOR.
        """
        if not self.graph.nodes: return []
        
        centrality = nx.degree_centrality(self.graph)
        
        # Check for Ego-Bias
        ego_target = None
        ego_edges = list(self.graph.edges("EGO_CURSOR"))
        if ego_edges:
            ego_target = ego_edges[0][1] # The node the observer is currently "looking at"
            
        # Identify the 'Starting' nodes in the graph based on the intent vector
        # Finding the node IN THE GRAPH that is most similar to the intent
        best_id, best_sim = None, -1.0
        unit = intent_vec / (np.linalg.norm(intent_vec) + 1e-9)
        
        for n, data in self.graph.nodes(data=True):
            emb = data.get('embedding')
            if emb is not None:
                sim = float(np.dot(unit, emb / (np.linalg.norm(emb) + 1e-9)))
                if sim > best_sim:
                    best_sim, best_id = sim, n
        
        starting_nodes = [(best_id, best_sim)] if best_id else []
        
        if not starting_nodes: return []
        
        current_node = starting_nodes[0][0]
        path = [current_node]
        
        for _ in range(depth - 1):
            neighbors = list(self.graph.successors(current_node))
            if not neighbors: break
            
            # Select neighbor with highest (Weight * Centrality * Activation * Perspective)
            def score(n):
                edge_data = self.graph.get_edge_data(current_node, n)
                # Phase 137: Prioritize explicit weight for identity/partnership links
                w = edge_data.get('weight', 0.5)
                edge_type = edge_data.get('type', 'associative')
                
                # Boost based on edge type
                type_boost = 1.0
                if edge_type == 'PARTNERSHIP': type_boost = 10.0
                elif edge_type == 'causal': type_boost = 2.0
                
                c = centrality.get(n, 0.1)
                a = self.graph.nodes[n].get('activation', 0.1)
                
                # Boost if node is related to the current Ego position
                p = 1.0
                if ego_target:
                    if n == ego_target or self.graph.has_edge(ego_target, n):
                        p = 2.0
                        
                return (w * type_boost) * c * (1.0 + a) * p
            
            # Avoid immediate cycles
            candidates = [n for n in neighbors if n not in path]
            if not candidates: break
            
            current_node = max(candidates, key=score)
            path.append(current_node)
            
        return path

    def save_registry(self, history=None, magnetic_field=None):
        # Create a copy for serialization to avoid modifying the live graph's attributes
        g_copy = self.graph.copy()
        for n, data in g_copy.nodes(data=True):
            if 'embedding' in data:
                del data['embedding']
        
        data = nx.node_link_data(g_copy)
        
        # Phase 145 Patch: Standardize key name for SubstrateViewer compatibility
        if 'links' in data:
            data['edges'] = data.pop('links')
        
        # Ensure 'type' exists for all nodes for visualizer stability
        for node_data in data['nodes']:
            if 'type' not in node_data:
                node_data['type'] = 'UNKNOWN'

        # Phase 141 & 142: Meta-Viewpoint (Perspective & Compass)
        data['ego_dock'] = self.ego_dock
        data['horizon'] = list(self.graph.successors(self.ego_dock)) if self.ego_dock in self.graph else []
        data['history'] = history or [] 
        data['magnetic_field'] = magnetic_field or {"heading": 0.0, "strength": 0.0, "turn": "STATIC"}
        
        # Phase 130: Graph Archival (Structural History)
        timestamp = int(time.time())
        archive_path = f"E:/Antigravity/Runtime/archives/lattice_graph_{timestamp}.json"
        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        
        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)
            
        with open(archive_path, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"[LATTICE_GRAPH] Registry Crystallized and Archived at {archive_path}")
