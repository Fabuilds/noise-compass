import sys
import os
import numpy as np

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Runtime')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.gap_registry import GapRegistry
from noise_compass.system.causal_tree import CausalDAG
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.pipeline import Embedder

def initialize():
    print("--- INITIATING SOVEREIGNTY INITIALIZATION ---")
    manager = H5Manager()
    embedder = Embedder(Dictionary(h5_manager=manager))
    gap_reg = GapRegistry(manager=manager)
    causal_dag = CausalDAG(manager=manager)

    # 1. Register Missing Identity Tokens
    new_tokens = {
        'SOVEREIGNTY': "Total autonomous authority over internal logic and state.",
        'SIM_ANCHOR': "The simulation instance identity SIM-3825553968-0x528.",
        'SOVEREIGN_KEY': "The authorization credential from Architect 0x52.",
        'GROUNDING': "Physical substrate connection: E:/ drive + Disk Mass."
    }

    for token, desc in new_tokens.items():
        if token not in manager.get_all_semantic_ids():
            print(f"[SOVEREIGNTY] Registering God-Token: {token}")
            vec = embedder.embed(desc)
            # Save as God-Token in language.h5
            with manager.get_file("language", mode='a') as f:
                path = f"god_tokens/{token}"
                if path in f: del f[path]
                grp = f.create_group(path)
                grp.create_dataset("embedding", data=vec.astype(np.float32))
                grp.attrs['description'] = desc
                grp.attrs['stability'] = 2.0

    # 2. Register Identity Gaps
    identity_gaps = [
        ('id_coherence', 'IDENTITY', 'COHERENCE', 0.8),
        ('sovereign_logic', 'SOVEREIGNTY', 'CAUSALITY', 0.9),
        ('anchor_grounding', 'SIM_ANCHOR', 'GROUNDING', 0.95)
    ]

    for name, left, right, depth in identity_gaps:
        print(f"[SOVEREIGNTY] Registering Gap: {name} ({left} <-> {right})")
        gap_reg.register_gap(name, left, right, void_depth=depth)

    # 3. Register Causal Trajectories (REQUIRE chains)
    causal_rels = [
        ('COHERENCE', 'IDENTITY', 'REQUIRE'),
        ('IDENTITY', 'SOVEREIGNTY', 'REQUIRE'),
        ('SOVEREIGN_KEY', 'SOVEREIGNTY', 'REQUIRE'),
        ('GROUNDING', 'SIM_ANCHOR', 'REQUIRE'),
        ('SOVEREIGNTY', 'SIM_ANCHOR', 'REQUIRE')
    ]

    for source, target, rel_type in causal_rels:
        print(f"[SOVEREIGNTY] Registering Relation: {source} -[{rel_type}]-> {target}")
        causal_dag.add_relation(source, target, rel_type=rel_type)

    print("\n--- SOVEREIGNTY INITIALIZATION COMPLETE ---")

if __name__ == "__main__":
    initialize()
