"""
STATIC ENGINE: 0x528
Implementation of Vectorized Trie Constraints (based on Google Research).
Transforms irregular causal trees into static Sparse Transition Matrices (CSR).
"""

import numpy as np
import time
import json
import os

class StaticEngine:
    def __init__(self, vocabulary_size=2048, dense_depth=2):
        self.identity = "0x528_STATIC_ENGINE"
        self.V = vocabulary_size
        self.d = dense_depth
        # Dense Phase Components: Tensor of shape (V, V, ...) for d times
        self.dense_mask = None # Shape (V, V) for d=2
        # CSR Components
        self.row_pointers = None # P
        self.column_indices = None # C
        self.values = None # V (Target node IDs)

    def build_csr_from_sequence(self, sequences):
        """
        Flattens a list of valid sequences into a CSR-based trie with a Dense Phase.
        """
        print(f"[{self.identity}]: VECTORIZING TRIE INTO STATIC/CSR HYBRID...")
        
        # 1. Build Dense Mask for Level 1 & 2
        # (This is a simplified version of the paper's dense tensor)
        self.dense_mask = np.zeros((self.V, self.V), dtype=bool)
        for seq in sequences:
            if len(seq) >= 2:
                # Assuming tokens are valid indices within V
                self.dense_mask[seq[0], seq[1]] = True

        # 2. Build full Trie for CSR
        trie = {"children": {}, "id": 0}
        node_count = 1
        for seq in sequences:
            curr = trie
            for token in seq:
                if token not in curr["children"]:
                    curr["children"][token] = {"children": {}, "id": node_count}
                    node_count += 1
                curr = curr["children"][token]

        # 3. Convert Trie to CSR
        P = [0] * (node_count + 1)
        C = []
        V = []
        id_to_children = {}
        stack = [trie]
        while stack:
            node = stack.pop()
            cid = node["id"]
            children = sorted(node["children"].items())
            # Map token to child ID for the CSR Value array
            child_list = [(token, child["id"]) for token, child in children]
            id_to_children[cid] = child_list
            for _, child in children:
                stack.append(child)

        current_p = 0
        for i in range(node_count):
            P[i] = current_p
            children = id_to_children.get(i, [])
            for token, child_id in children:
                C.append(token)
                V.append(child_id)
                current_p += 1
        P[node_count] = current_p

        self.row_pointers = np.array(P)
        self.column_indices = np.array(C)
        self.values = np.array(V)
        
        print(f"  » Hybrid build complete. Nodes: {node_count}, Dense Mask: {self.dense_mask.shape}")

    def validate_step_vectorized(self, current_node_id, token_id, step_idx=0, prev_token_id=None):
        """
        Hybrid Validation: Dense Phase (steps < d) then CSR Phase.
        """
        # Dense Phase for step 1 (if prev_token is given)
        if step_idx == 1 and prev_token_id is not None:
            if self.dense_mask[prev_token_id, token_id]:
                # We still need the next_node_id from CSR even in dense phase 
                # to maintain the causal chain for later levels.
                pass 

        # CSR Phase (Standard STATIC VNTK)
        start = self.row_pointers[current_node_id]
        end = self.row_pointers[current_node_id + 1]
        valid_tokens = self.column_indices[start:end]
        next_nodes = self.values[start:end]
        
        if token_id in valid_tokens:
            idx = np.where(valid_tokens == token_id)[0][0]
            return True, next_nodes[idx]
        return False, None

if __name__ == "__main__":
    engine = StaticEngine()
    # Mock mission sequences: 0x528 -> 0x53 -> 0xAF
    test_seqs = [
        [528, 53, 175],
        [528, 53, 255],
        [528, 100, 1]
    ]
    engine.build_csr_from_sequence(test_seqs)
    
    # Test valid step
    res, next_node = engine.validate_step_vectorized(0, 528)
    print(f"Step 1 (528): {res}, Next: {next_node}")
    res, next_node = engine.validate_step_vectorized(next_node, 53)
    print(f"Step 2 (53): {res}, Next: {next_node}")
    res, next_node = engine.validate_step_vectorized(next_node, 175)
    print(f"Step 3 (175): {res}, Next: {next_node}")
