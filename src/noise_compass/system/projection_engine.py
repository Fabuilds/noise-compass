"""
projection_engine.py — Orchestrates the projection of documents into the H5 substrate.
Bridges Scout reasoning with topological H5 persistence.
"""

import os
import time
import hashlib
import numpy as np
from sentence_transformers import SentenceTransformer
from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.core import Scout
from noise_compass.system.dictionary import Dictionary
from noise_compass.system.causal_tree import CausalDAG

class ProjectionEngine:
    """
    Projector of information onto the H5 substrate.
    Turns documents into non-linear, traversable nodes.
    """
    def __init__(self, h5=None, encoder=None):
        self.h5 = h5 or H5Manager()
        self.dictionary = Dictionary(self.h5)
        self.encoder = encoder or SentenceTransformer("all-MiniLM-L6-v2")
        self.scout = Scout(self.dictionary, encoder=self.encoder)
        self.causal_dag = CausalDAG(manager=self.h5)

    def project(self, text, metadata=None):
        """
        Embeds text into the manifold and saves it as a projection node in H5.
        Returns the doc_id (hash of content).
        """
        if not text: return None
        
        # 1. Generate unique projection ID
        doc_id = hashlib.sha256(text.encode('utf-8')).hexdigest()[:16].upper()
        
        # 2. Embed using the system's current standard (384D)
        embedding = self.encoder.encode(text)
        
        # 3. Augment metadata
        meta = metadata or {}
        meta.update({
            'len': len(text),
            'timestamp': time.time(),
            'source': 'PROJECTION_ENGINE_V1'
        })
        
        # 4. Save to H5 Substrate
        self.h5.save_projection(doc_id, embedding, metadata=meta)
        
        # 5. Optional: Map to nearest GodTokens for semantic grounding
        msg, wf = self.scout.process(embedding, content=text[:200])
        self.h5.set_attr("language", f"projections/{doc_id}", "primary_zone", msg.zone)
        self.h5.set_attr("language", f"projections/{doc_id}", "energy_level", msg.energy_level)

        # Phase 139: Synchronous Stamping & Polyhedral Crystallization
        from noise_compass.system.polyhedral_auditor import PolyhedralAuditor
        from noise_compass.system.polyhedral_web import PolyhedralEngine
        auditor = PolyhedralAuditor(h5=self.h5)
        auditor.stamp_node(doc_id)
        
        engine = PolyhedralEngine(h5=self.h5)
        engine.crystallize_3d_web(iterations=10) # Quick relaxation
        
        print(f"[PROJECTION] Document '{doc_id}' projected and STAMPED. Zone: {msg.zone}")
        return doc_id

    def link(self, source_id, target_id, weight=1.0):
        """Encodes a traversable topological link between two projections."""
        self.causal_dag.add_transition(source_id, target_id, weight=weight)
        print(f"[TOPOLOGY] Transition encoded: {source_id} -> {target_id} (w={weight})")

    def batch_project(self, documents):
        """Projects multiple documents and identifies their sequential transitions."""
        ids = []
        for doc in documents:
            doc_id = self.project(doc['text'], metadata=doc.get('metadata'))
            if doc_id:
                if ids:
                    # Automatically link sequential documents as a default trajectory
                    self.link(ids[-1], doc_id, weight=0.8)
                ids.append(doc_id)
        return ids

if __name__ == "__main__":
    pe = ProjectionEngine()
    # Test projection
    doc1 = pe.project("The semantic manifold is a high-dimensional space of meaning.")
    doc2 = pe.project("Navigation through the manifold requires a topological graph.")
    pe.link(doc1, doc2)
