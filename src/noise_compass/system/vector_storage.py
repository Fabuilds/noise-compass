import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
import struct
import random
import math
import time
import hashlib

from noise_compass.system.protocols import PROPER_HEX_KEY

try:
    print("STARTING KINETIC LATTICE ENGINE (V3)...", flush=True)
except OSError:
    pass

# 0x52 KINETIC CONFIGURATION
VOLUME_PATH = os.path.join(BASE_DIR, 'Lattice_DB', 'VOLUME_0x52_RESTORED.bin')
SECTOR_SIZE = 8192        # High Density Sub-Sector (v4.1)
VECTOR_SIZE = 8          # 64-bit Signed Integer
MAX_VECTORS_PER_NODE = 800 # Reduced for Phase 88 metadata support
HEADER_SIZE = 4 + 8 + (MAX_VECTORS_PER_NODE * VECTOR_SIZE) # 4B count + 8B next_ptr + vectors
METADATA_SIZE = SECTOR_SIZE - HEADER_SIZE # Reclaims ~1.7KB for DNA/ROAD metadata
VOLUME_SIZE = 1024 * 1024 * 1024 # 1GB Simulated Volume

class Void:
    """Regions where data cannot go — shape constraints."""
    def __init__(self, center, radius):
        self.center = center  # LBA position
        self.radius = radius  # Size of forbidden zone
    
    def repel(self, point):
        """Force pushing data away from void."""
        dist = abs(point - self.center)
        if dist < self.radius:
            return (self.radius - dist) / self.radius
        return 0

class KineticLattice:
    def __init__(self):
        self.path = VOLUME_PATH
        self.ensure_volume()
        # Seed voids
        self.voids = [Void(1024*1024*512, 1024*1024*50)] # Seed in middle

    def ensure_volume(self):
        if not os.path.exists(os.path.dirname(self.path)):
            os.makedirs(os.path.dirname(self.path))
        
        if not os.path.exists(self.path) or os.path.getsize(self.path) < VOLUME_SIZE:
             with open(self.path, "ab") as f:
                current_size = f.tell()
                if current_size < VOLUME_SIZE:
                    f.write(b'\x00' * (VOLUME_SIZE - current_size))

    def _write_sector(self, lba, data):
        if lba < 0 or lba >= VOLUME_SIZE:
            print(f"[ERROR]: Invalid LBA {lba} (Max: {VOLUME_SIZE})")
            return
            
        if len(data) > SECTOR_SIZE:
            data = data[:SECTOR_SIZE]
        if len(data) < SECTOR_SIZE:
            data = data + b'\x00' * (SECTOR_SIZE - len(data))
            
        try:
            with open(self.path, "r+b") as f:
                f.seek(lba)
                f.write(data)
                f.flush()
        except OSError as e:
            # [Errno 22] Invalid argument is common on Windows with some file flags
            if e.errno != 22:
                raise e
            else:
                print(f"[WARNING]: Suppressed Errno 22 during seek/write/flush at LBA {lba}")

    def find_free_sector(self, start_lba):
        """Linear Probe to find the nearest free sector. Wraps around if necessary."""
        limit = (VOLUME_SIZE // SECTOR_SIZE) * SECTOR_SIZE
        # Start probing from next sector
        probe_lba = (start_lba + SECTOR_SIZE) % limit
        initial_probe = probe_lba
        
        while True:
            data = self._read_sector(probe_lba)
            if not data or all(b == 0 for b in data):
                return probe_lba
            
            probe_lba = (probe_lba + SECTOR_SIZE) % limit
            if probe_lba == initial_probe:
                # We've circled the entire volume and found nothing
                return -1

    def _read_sector(self, lba):
        if lba < 0 or lba >= VOLUME_SIZE: return None
        try:
            with open(self.path, "rb") as f:
                f.seek(lba)
                return f.read(SECTOR_SIZE)
        except:
            return None

    def dimensional_collapse(self, key_int):
        mask_48 = (1 << 48) - 1
        chunk1 = key_int & mask_48
        chunk2 = (key_int >> 48) & mask_48
        chunk3 = (key_int >> 96) & mask_48
        chunk4 = (key_int >> 144)
        collapsed = chunk1 ^ (chunk2 << 1) ^ (chunk3 << 2) ^ (chunk4 << 3)
        final_lba = (collapsed & mask_48) % (VOLUME_SIZE // SECTOR_SIZE) * SECTOR_SIZE 
        return final_lba

    def projection_filter(self, data, key_int):
        key_bytes = key_int.to_bytes(20, 'big')
        mask = key_bytes * (len(data) // len(key_bytes) + 1)
        mask = mask[:len(data)]
        encrypted = bytes(a ^ b for a, b in zip(data, mask))
        return encrypted

    def _get_centers(self, key_int):
        centers = []
        limit = VOLUME_SIZE // SECTOR_SIZE
        key_bytes = key_int.to_bytes(20, 'big') 
        for i, byte_val in enumerate(key_bytes):
            projected_val = (byte_val * (i + 1) * 997) 
            lba = (projected_val % limit) * SECTOR_SIZE
            centers.append(lba)
        return centers

    def agape_tensor(self, current_lba, key_int):
        centers = self._get_centers(key_int)
        max_weighted_influence = 0
        best_center = None
        sigma = 1024 * 1024 * 5
        for i, center in enumerate(centers):
            distance = abs(current_lba - center)
            phi = math.exp(-(distance**2) / (2 * sigma**2))
            weight = 1.0 / (i + 1)
            repulsion = sum(v.repel(current_lba) for v in self.voids)
            weighted_influence = (phi * weight) - (repulsion * 0.5)
            if weighted_influence > max_weighted_influence:
                max_weighted_influence = weighted_influence
                best_center = center
        if max_weighted_influence > 0.0001:
            return best_center, max_weighted_influence
        return None, 0.0

    def parse_origin(self, key):
        clean = key.replace("-", "").replace("0x", "")
        key_int = int(clean, 16)
        lba = self.dimensional_collapse(key_int)
        return lba, key_int

    def read_node_header(self, lba, key_int=0):
        """Returns (num_vectors, next_lba, [vectors], payload)"""
        data = self._read_sector(lba)
        if not data:
            return 0, 0, [], ""
            
        # DE-MASK (Apply Projection Filter)
        if key_int != 0:
            data = self.projection_filter(data, key_int)
        
        # Check if it looks valid
        if len(data) < 12: return 0, 0, [], ""

        # Unpack Header: Count (4B), NextPtr (8B)
        num_vectors = struct.unpack(">I", data[0:4])[0]
        next_lba = struct.unpack(">Q", data[4:12])[0]
        
        if num_vectors > MAX_VECTORS_PER_NODE:
             # Likely junk/uninitialized if we read random noise
             return 0, 0, [], ""

        vectors = []
        offset = 12 # 4 + 8
        for _ in range(num_vectors):
            v_data = data[offset : offset+8]
            vec = struct.unpack(">q", v_data)[0]
            vectors.append(vec)
            offset += 8
            
        payload = data[offset:].split(b'\x00')[0].decode('utf-8', errors='ignore')
        return num_vectors, next_lba, vectors, payload

    def read_chain(self, start_lba, key_int):
        """
        Generator that yields all payloads in the chain starting at lba.
        Yields: (lba, payload)
        """
        current_lba = start_lba
        visited = set()
        
        while current_lba != 0 and current_lba not in visited:
            visited.add(current_lba)
            num, next_lba, vecs, payload = self.read_node_header(current_lba, key_int)
            
            if payload:
                yield (current_lba, payload)
            
            current_lba = next_lba

    def append_vector(self, node_lba, new_vector, key_int):
        """
        Adds a vector to an existing node.
        """
        num, next_lba, vectors, payload = self.read_node_header(node_lba, key_int)
        
        if num >= MAX_VECTORS_PER_NODE:
            # print(f"   [FULL]: Node {node_lba} is full.")
            return False
            
        vectors.append(new_vector)
        
        # Repack
        self._write_node_to_disk(node_lba, vectors, payload, key_int, next_lba)
        return True

    def write_payload(self, lba, payload, key_int):
        """
        Public method to write a Payload (Content) to a specific LBA.
        Handles COLISSIONS via CHAINING (Linked List).
        """
        # 1. Read what's currently there
        num, next_lba, vectors, current_payload = self.read_node_header(lba, key_int)
        
        # Case A: Empty Slot
        if num == 0 and current_payload == "":
            # Just write it
            self._write_node_to_disk(lba, [], payload, key_int, next_lba=0)
            return True
            
        # Case B: Occupied Slot (Collision or Update)
        # Check if content matches (Idempotent Update)
        # We assume payload format "FILE: {name} | ..."
        # If headers match, we overwrite/update.
        
        current_header = current_payload.split('|')[0].strip() if '|' in current_payload else current_payload
        new_header = payload.split('|')[0].strip() if '|' in payload else payload
        
        if current_header == new_header:
            # Update existing node (keep Next Ptr!)
            self._write_node_to_disk(lba, vectors, payload, key_int, next_lba)
            print(f"   [UPDATE]: Overwriting {lba} (Matched Content)")
            return True
            
        # Case C: True Collision (Hash Clash) -> CHAIN IT
        # 1. Traverse to Tail
        tail_lba = lba
        while next_lba != 0:
            tail_lba = next_lba
            # Read tail
            _, next_lba, _, _ = self.read_node_header(tail_lba, key_int)
            
        # 2. Allocate New Sector
        new_lba = self.find_free_sector(tail_lba)
        if new_lba == -1:
            print(f"   [FATAL]: Volume Full. Cannot chain collision at {lba}.")
            return False
            
        print(f"   [COLLISION]: {lba} Occupied. Chaining -> {new_lba}")
        
        # 3. Write New Node to New LBA (Next=0)
        self._write_node_to_disk(new_lba, [], payload, key_int, next_lba=0)
        
        # 4. Link Tail to New LBA
        # Re-read tail full data to preserve it
        t_num, t_next, t_vecs, t_pay = self.read_node_header(tail_lba, key_int)
        # Update Tail's Next Ptr
        self._write_node_to_disk(tail_lba, t_vecs, t_pay, key_int, next_lba=new_lba)
        
        return True

    def map_semantic_trajectory(self, base_concept, key_int, max_depth=50):
        """
        Traces the evolution of a concept across the lattice chain.
        Returns a list of LBAs and payloads representing the trajectory.
        """
        # First, find the root LBA using the standard dimensional collapse
        # We simulate the concept as a "seed" to find its starting LBA
        # To do this correctly, we use the same hashing as in RecursiveScribe
        dna_raw = f"|{base_concept}|{PROPER_HEX_KEY}" 
        dna = hashlib.sha256(dna_raw.encode()).hexdigest()[:16]
        start_lba = self.dimensional_collapse(int(dna, 16))
        
        trajectory = []
        current_lba = start_lba
        depth = 0
        visited = set()
        
        while current_lba != 0 and depth < max_depth and current_lba not in visited:
            visited.add(current_lba)
            num, next_lba, _, payload = self.read_node_header(current_lba, key_int)
            
            if payload:
                trajectory.append((current_lba, payload))
                
            current_lba = next_lba
            depth += 1
            
        return trajectory

    def scribe_tree(self, origin_key, tree_structure, append=True):
        """
        Writes Recursive Tree.
        V4.0: Applies Dimensional Collapse and Projection Filter.
        """
        origin_lba, key_int = self.parse_origin(origin_key)
        print(f"[SCRIBE V4.0]: Collapsed LBA {origin_lba} (0x{origin_lba:X})")
        
        # Check Origin
        current_num, _, _, current_payload = self.read_node_header(origin_lba, key_int)
        
        payload, children = tree_structure
        child_vectors = []
        
        for child in children:
            # AGAPE TENSOR (Empathy Layer): Deterministic Displacement
            # jump = (hash(payload) % 2000) * direction
            child_payload = child[0] # Tuple (Payload, Children)
            
            # Simple Stable Hash (MD5)
            h = hashlib.md5(child_payload.encode('utf-8', errors='ignore')).digest()
            # Use first 4 bytes as int
            h_int = struct.unpack(">I", h[:4])[0]
            
            # Jump Logic: 10 to 5000 sectors
            jump = (h_int % 4990) + 10
            
            # Direction: Use next bit
            direction = 1 if (h_int % 2) == 0 else -1
            
            displacement = jump * direction * SECTOR_SIZE
            child_lba = origin_lba + displacement
            
            self._scribe_node_recursive(child_lba, child, key_int)
            child_vectors.append(displacement)

        # Update Origin
        if append and current_num > 0:
            print(f"   [APPEND]: Adding {len(child_vectors)} vectors (Masked)...")
            for v in child_vectors:
                self.append_vector(origin_lba, v, key_int)
        else:
            print(f"   [INIT]: Initializing Root (Masked)...")
            # Write Root with proper logic
            self._write_node_to_disk(origin_lba, child_vectors, payload, key_int, next_lba=0)
            
        return origin_lba

    def _scribe_node_recursive(self, current_lba, node_dict, key_int):
        payload, children = node_dict
        head_vectors = []
        
        # 1. Resolve Children
        for child in children:
            # AGAPE TENSOR (Empathy Layer)
            child_payload = child[0]
            
            h = hashlib.md5(child_payload.encode('utf-8', errors='ignore')).digest()
            h_int = struct.unpack(">I", h[:4])[0]
            
            # Jump Logic: 10 to 2000 sectors (Tighter for sub-nodes)
            jump = (h_int % 1990) + 10
            direction = 1 if (h_int % 2) == 0 else -1
            
            displacement = jump * direction * SECTOR_SIZE
            child_lba = current_lba + displacement
            
            head_vectors.append(displacement)
            self._scribe_node_recursive(child_lba, child, key_int)
            
        # 2. Write (Simplifying Pagination for Chaining Phase)
        # Just write the node. If full, we drop vectors for now or use append.
        self._write_node_to_disk(current_lba, head_vectors, payload, key_int, next_lba=0)

    def _write_node_to_disk(self, lba, vectors, payload, key_int, next_lba=0):
        # SAFETY CHECK: Truncate vectors to prevent Sector Overflow
        if len(vectors) > MAX_VECTORS_PER_NODE:
            vectors = vectors[:MAX_VECTORS_PER_NODE]
            
        num_vectors = len(vectors)
        # Header: Count(4B) + Next(8B)
        header = struct.pack(">IQ", num_vectors, next_lba)
        
        vector_bytes = b''
        for v in vectors:
            vector_bytes += struct.pack(">q", v)
            
        metadata_bytes = payload.encode('utf-8')[:METADATA_SIZE]
        raw_data = header + vector_bytes + metadata_bytes
        
        # MASK
        masked_data = self.projection_filter(raw_data, key_int)
        self._write_sector(lba, masked_data)

    def walk_dfs(self, start_lba, key_int, depth=0):
        """
        Recursive DFS. Needs Key to see through the Camouflage.
        """
        if depth == 0:
            print(f"\n[TRACE]: Engaging Projection Filter at {start_lba}...")
            
        indent = "  " * depth
        
        # Read & Demask
        # Read & Demask
        num, next_lba, vectors, payload = self.read_node_header(start_lba, key_int)
        
        if num == 0 and payload == "":
            print(f"{indent}[NOISE] @ {start_lba} (Drift Detected)")
            
            # TRIGGER AGAPE TENSOR (Self-Healing)
            target, influence = self.agape_tensor(start_lba, key_int)
            
            if target is not None:
                print(f"{indent}[AGAPE]: Gravity Well Detected (Influence: {influence:.4f})")
                print(f"{indent}[AGAPE]: CORRECTING VECTOR -> Jump to Center {target}")
                
                # Prevent infinite loops if we are already AT the center and it's empty
                if target != start_lba:
                    self.walk_dfs(target, key_int, depth + 1)
                else:
                    print(f"{indent}[AGAPE]: We are at the Singularity, but it is empty. Resting.")
            else:
                print(f"{indent}[LOST]: Deep Space. No Gravity.")
                
            return
            
        print(f"{indent}[NODE]: '{payload}'")
        
        for i, vec in enumerate(vectors):
            next_lba = start_lba + vec
            print(f"{indent}  >>> Vector {i}: {vec} -> Jump")
            self.walk_dfs(next_lba, key_int, depth + 1)


if __name__ == "__main__":
    lattice = KineticLattice()
    
    # Define the "Map for a Map"
    # Structure: (Payload, [List of Children])
    # Children are also (Payload, [Grandchildren])
    
    tree = ("ROOT: 0x52_ORIGIN", [
        ("BRANCH_A: LOGIC_GATE", [
            ("LEAF_A1: INPUT_RECEIVER", []),
            ("LEAF_A2: PROCESSOR", [])
        ]),
        ("BRANCH_B: MEMORY_CORE", [
            ("LEAF_B1: ARCHIVE", [])
        ])
    ])
    
    key = "53-49-4D-2D-33-38-32-35-35-35-33-39-36-38-2D-0x528"
    
    # 1. Scribe (Injection)
    # The key_int is derived internally, we just pass the key string
    root_lba = lattice.scribe_tree(key, tree)
    
    # 2. Trace (Materialization)
    time.sleep(1)
    # We need the key_int to trace now (The Lens)
    _, key_int = lattice.parse_origin(key)
    lattice.walk_dfs(root_lba, key_int)
