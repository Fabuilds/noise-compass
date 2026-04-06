"""
hyper_ingestor.py — Ingests the E:\\hyperdimensions directory into the H5 substrate.
Formalizes evolutionary art experiments as situational attractors.
"""

import os
import sys
import time
import numpy as np

# Ensure package is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.projection_engine import ProjectionEngine
from noise_compass.system.lattice_graph import LatticeGraph

class HyperIngestor:
    def __init__(self, target_dir="E:\\hyperdimensions"):
        self.target_dir = os.path.normpath(target_dir)
        self.h5 = H5Manager()
        self.pe = ProjectionEngine(h5=self.h5)
        self.graph = LatticeGraph(h5=self.h5)
        self.root_node_id = "HYPERDIMENSIONS_ROOT"

    def ingest(self):
        print(f"--- [HYPER] Starting Ingestion of {self.target_dir} ---")
        
        # 1. Ensure Root Node
        root_desc = f"Hyperdimensions: A collection of evolutionary art and genetic logic located at {self.target_dir}."
        root_meta = {
            'role': 'SYSTEM_ROOT',
            'type': 'HYPERDIMENSIONAL',
            'path': self.target_dir
        }
        root_id = self.pe.project(root_desc, metadata=root_meta)
        print(f"  [HYPER] Root crystallized: {root_id}")

        # 2. Iterate Files
        ingested_count = 0
        for root, dirs, files in os.walk(self.target_dir):
            if '.git' in root: continue
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.target_dir)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if not content.strip(): continue
                    
                    # Truncate content for embedding if too large, but keep semantic essence
                    # The pe.project handles the core encoding
                    file_meta = {
                        'filename': file,
                        'rel_path': rel_path,
                        'parent_system': root_id,
                        'type': 'HYPER_COMPONENT',
                        'ext': os.path.splitext(file)[1]
                    }
                    
                    doc_id = self.pe.project(content[:5000], metadata=file_meta)
                    if doc_id:
                        # Link to root
                        self.pe.link(root_id, doc_id, weight=0.9)
                        ingested_count += 1
                        print(f"    -> Ingested: {rel_path} ({doc_id})")
                        
                except Exception as e:
                    print(f"    [ERROR] Failed to ingest {file}: {e}")

        # 3. Synchronize Graph & Ensure connectivity
        print(f"--- [HYPER] Ingestion complete. Synchronizing {ingested_count} nodes... ---")
        self.graph.sync_with_substrate(self.pe.scout)
        self.graph.save_registry()
        
        return ingested_count

if __name__ == "__main__":
    ingestor = HyperIngestor()
    count = ingestor.ingest()
    print(f"Successfully crystallized {count} hyperdimensional attractors into the H5 manifold.")
