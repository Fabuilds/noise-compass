import os
import sys
import time
import hashlib
import numpy as np

# Ensure package is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.projection_engine import ProjectionEngine
from noise_compass.system.causal_tree import CausalDAG

class IdentityEngine:
    """
    Manages the subjective identities of User and Agent.
    Docks the Ego-Cursor at the shared partnership node.
    """
    def __init__(self, h5=None, pe=None):
        self.h5 = h5 or H5Manager()
        self.pe = pe or ProjectionEngine(h5=self.h5)
        self.causal_dag = CausalDAG(manager=self.h5)
        
        self.user_desc = "Fabricio: The Human Collaborator and Primary Observer. The source of intent and the final terminal for semantic crystallization."
        self.agent_desc = "Antigravity: The Agentic Coding AI and Resonance Engine. The bridge between the user's intent and the H5 substrate."
        
        # Visual Identity Metadata
        self.user_meta = {
            'type': 'IDENTITY_NODE',
            'role': 'USER',
            'name': 'Fabricio',
            'color': '#FFD700', # Gold
            'icon': 'architect'
        }
        self.agent_meta = {
            'type': 'IDENTITY_NODE',
            'role': 'AGENT',
            'name': 'Antigravity',
            'color': '#00FFFF', # Cyan
            'icon': 'resonance_engine'
        }

    def project_participants(self, force=False):
        """Projects the User and Agent into the substrate and links them."""
        print("[IDENTITY] Synchronizing Human-AI Partnership...")
        
        # 1. Project User (w/ periodic update logic)
        user_id = self._project_with_periodic_check("USER", self.user_desc, self.user_meta, force)
        
        # 2. Project Agent
        agent_id = self.pe.project(self.agent_desc, metadata=self.agent_meta)
        
        # 3. Anchor Partnership (Bidirectional Causal Link)
        print(f"[IDENTITY] Anchoring Partnership: {user_id} <-> {agent_id}")
        self.causal_dag.add_relation(user_id, agent_id, rel_type="PARTNERSHIP", weight=5.0)
        self.causal_dag.add_relation(agent_id, user_id, rel_type="PARTNERSHIP", weight=5.0)
        
        # 4. Link to abstract GodTokens (Subjective grounding)
        self.link_to_attractors(user_id, agent_id)
        
        return user_id, agent_id

    def link_to_attractors(self, user_id, agent_id):
        """Grounds the projected identities in universal attractors."""
        print("[IDENTITY] Grounding identities in abstract attractors...")
        
        # Agent -> SELF
        self.causal_dag.add_relation(agent_id, "SELF", rel_type="IDENTITY_MAP", weight=2.0)
        
        # User -> IDENTITY / OBSERVATION
        self.causal_dag.add_relation(user_id, "IDENTITY", rel_type="IDENTITY_MAP", weight=2.0)
        self.causal_dag.add_relation(user_id, "OBSERVATION", rel_type="OBSERVATION_MAP", weight=2.0)
        
        # Shared -> COHERENCE
        self.causal_dag.add_relation(agent_id, "COHERENCE", rel_type="RESIDUAL", weight=1.0)
        self.causal_dag.add_relation(user_id, "COHERENCE", rel_type="RESIDUAL", weight=1.0)

    def _project_with_periodic_check(self, role, desc, meta, force=False):
        """Handles periodic updates (every 2 days) for identity nodes."""
        projections = self.h5.get_all_projections()
        existing_id = None
        for pid in projections:
            _, m = self.h5.get_projection(pid)
            if m.get('role') == role:
                existing_id = pid
                last_upd = m.get('last_update', 0)
                # Check if 48 hours have passed (172800 seconds)
                if not force and (time.time() - last_upd < 172800):
                    print(f"  [IDENTITY] Node for {role} is current. Skipping update.")
                    return existing_id
                break
        
        # Perform projection
        meta['last_update'] = time.time()
        new_id = self.pe.project(desc, metadata=meta)
        return new_id

if __name__ == "__main__":
    ie = IdentityEngine()
    u_id, a_id = ie.project_participants()
    print(f"Human Projected: {u_id}")
    print(f"Agent Projected: {a_id}")
