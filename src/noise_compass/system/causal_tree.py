import networkx as nx
import numpy as np
from noise_compass.system.h5_manager import H5Manager

class CausalDAG:
    """
    Directed Acyclic Graph for Semantic Trajectories.
    Moves from Correlation (Resonance) to Causality (Flow).
    """
    def __init__(self, manager: H5Manager = None):
        self.manager = manager or H5Manager()
        self.graph = nx.DiGraph()
        self.load_graph()

    def load_graph(self):
        """Pre-loads the causal skeleton from H5."""
        try:
            relations = self.manager.get_all_causal_relations()
            for rel in relations:
                self.graph.add_edge(
                    rel['source'], 
                    rel['target'], 
                    type=rel['type'], 
                    weight=rel['weight']
                )
            if relations:
                print(f"[CAUSAL_TREE] Loaded {len(relations)} directed relations from substrate.")
        except Exception as e:
            print(f"[CAUSAL_TREE] [WARNING] Failed to load causal graph: {e}")

    def add_relation(self, source, target, rel_type="TRIGGER", weight=1.0, info: str = ""):
        """Adds a directed edge and crystallizes it to H5 with optional info."""
        self.graph.add_edge(source, target, type=rel_type, weight=weight, info=info)
        self.manager.save_causal_relation(source, target, rel_type, weight, info=info)
        print(f"[CAUSAL_TREE] Crystallized relation: {source} -[{rel_type}]-> {target}")

    def add_transition(self, source, target, weight=1.0):
        """Encodes a traversable path between two projections in the substrate."""
        self.add_relation(source, target, rel_type="NAVIGATE", weight=weight)

    def apply_causal_flow(self, field: dict, damp_factor: float = 0.8) -> dict:
        """
        Refines an interference field based on causal pre-conditions.
        - REQUIRE: If parent is dark (<0.2), dampen child by damp_factor.
        - TRIGGER: If parent is high (>0.7), boost child expectation (future saliency).
        """
        modified_field = field.copy()
        
        # 1. REQUIRE Check (Pre-condition Validation)
        for node in self.graph.nodes:
            if node not in field:
                continue
            
            # Find all nodes that this node REQUIRES
            requirements = [
                u for u, v, d in self.graph.in_edges(node, data=True) 
                if d['type'] == 'REQUIRE'
            ]
            
            def get_mag(val):
                if isinstance(val, dict): return val.get('magnitude', 0)
                return float(val)

            for req in requirements:
                req_res = get_mag(field.get(req, 0))
                if req_res < 0.2: # Pre-condition not satisfied
                    # Phase 125: Strict Override - Magnitude set to 0.0
                    modified_field[node]['magnitude'] = 0.0
                    modified_field[node]['causal_status'] = 'REJECTED_BY_CAUSAL_PARENT'
                    self.log_violation(node, req)
                    print(f"[CAUSAL_TREE] [REJECTED] Node {node} zeroed due to missing parent {req}")
        
        # 2. TRIGGER Detection (Future Saliency)
        # This highlights what *should* come next based on current high-resolution peaks
        for u, v, d in self.graph.edges(data=True):
            if d['type'] == 'TRIGGER':
                source_res = field.get(u, {}).get('magnitude', 0)
                if source_res > 0.7:
                    if v in modified_field:
                        modified_field[v]['causal_boost'] = True
                        # We don't artificially increase magnitude here to avoid hallucination, 
                        # but we mark it for the Archiver to prioritize.
        
        return modified_field

    def log_violation(self, node, missing_parent):
        """Records the causal failure for future analysis."""
        context = {
            'event': 'CAUSAL_VIOLATION',
            'effect': node,
            'missing_cause': missing_parent,
            'verdict': 'REJECTED'
        }
        self.manager.record_dissonance_context(f"CAUSAL_{node}", context)

    def get_trajectories(self, active_nodes: list):
        """Returns ordered paths through the DAG based on active nodes."""
        # Simple implementation: Return all successors of active nodes
        trajectories = {}
        for node in active_nodes:
            if node in self.graph:
                successors = [
                    (v, self.graph[node][v].get('type', 'NAVIGATE'), self.graph[node][v].get('weight', 1.0))
                    for v in self.graph.successors(node)
                ]
                if successors:
                    trajectories[node] = successors
        return trajectories
