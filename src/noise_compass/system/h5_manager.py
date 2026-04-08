import h5py
import os
import json
import time
import random
import numpy as np
import psutil

class H5Manager:
    """
    Manages crystallized assumptions as modular H5 files.
    Standardized according to the Axiomatic Skeleton (Phase 36).
    """
    def __init__(self, root="E:/Antigravity/knowledge_root/crystallized_h5"):
        self.root = root
        self.files = ["language", "self", "body", "identity", "history", "failures", "causal"]
        os.makedirs(self.root, exist_ok=True)
        self._ensure_structural_time()

    def check_substrate_health(self) -> bool:
        """Verifies that all core H5 files exist and are initialized."""
        for module in self.files:
            path = os.path.join(self.root, f"{module}.h5")
            if not os.path.exists(path):
                print(f"[SUBSTRATE] Missing core H5: {module}.h5")
                return False
        return True

    def _ensure_structural_time(self):
        """Ensures the core/clock group exists in self.h5."""
        with self.get_file("self", mode='a') as f:
            if "core/clock" not in f:
                f.create_group("core/clock")
            if "structural_time" not in f["core/clock"].attrs:
                f["core/clock"].attrs["structural_time"] = 0

    def get_structural_time(self):
        """Retrieves current structural time (ticks)."""
        return self.get_attr("self", "core/clock", "structural_time") or 0

    def tick(self):
        """Increments the internal structural clock of the system."""
        current = self.get_structural_time()
        new_time = current + 1
        self.set_attr("self", "core/clock", "structural_time", new_time)
        return new_time

    # ── Option B: Deferred Seeding ────────────────────────────────────────────
    def set_god_token_seed(self, name: str, phrase: str):
        """Writes a seed phrase for a god-token. Vectors are generated from
        this phrase at session startup by whatever embedder is active."""
        with self.get_file("language", mode='a') as f:
            grp = f.require_group(f"god_tokens/{name}")
            grp.attrs["seed_phrase"] = phrase

    def get_god_token_seeds(self) -> dict:
        """Reads all stored seed phrases. Returns {name: phrase} dict.
        Called by Dictionary.__init__() to populate in-memory embeddings."""
        result = {}
        try:
            with self.get_file("language", mode='r') as f:
                if "god_tokens" not in f:
                    return result
                for name in f["god_tokens"]:
                    attrs = f[f"god_tokens/{name}"].attrs
                    if "seed_phrase" in attrs:
                        result[name] = str(attrs["seed_phrase"])
        except Exception:
            pass
        return result
    # ─────────────────────────────────────────────────────────────────────────

        
    def check_system_vitals(self, threshold_gb=0.8):
        """Pre-flight check to prevent OOM-hangs using native psutil."""
        try:
            free_gb = psutil.virtual_memory().available / (1024**3)
            if free_gb < threshold_gb:
                print(f"[H5SWMR] [WARNING] Critical RAM Scarcity ({free_gb:.2f}GB). Throttling operation.")
                return False
        except:
            pass
        return True

    def h5_retry(func):
        """Robust retry decorator for H5 operations to handle Windows locking contention."""
        def wrapper(*args, **kwargs):
            retries = 15
            last_err = None
            while retries > 0:
                try:
                    return func(*args, **kwargs)
                except (OSError, RuntimeError, PermissionError) as e:
                    last_err = e
                    retries -= 1
                    time.sleep(0.3 + (random.random() * 0.2)) # Random jitter
            print(f"[FATAL] H5 Operation '{func.__name__}' failed after retries: {last_err}")
            raise last_err
        return wrapper

    def get_file(self, module="language", mode='a'):
        path = os.path.join(self.root, f"{module}.h5")
        if not os.path.exists(path) and mode == 'r':
             return None
        
        # Phase 57/76/93/110: Ultra-Resilient SWMR Locking
        # Phase 126: Ultra-Resilient SWMR Locking + Track Order
        retries = 30
        while retries > 0:
            try:
                # Phase 126: Strict SWMR + Latest Libver + Track Order for structural consistency
                f = h5py.File(path, mode, libver='latest', track_order=True)
                if mode == 'r':
                    try: 
                        f.swmr_mode = True
                    except (ValueError, Exception): pass
                return f
            except (OSError, BlockingIOError, PermissionError) as e:
                retries -= 1
                if retries == 0:
                    print(f"[H5_LOCK_EXHAUSTION] {module}: {e}")
                    raise
                # Aggressive exponential-ish backoff to resolve windows locking contention
                time.sleep(0.1 + (30 - retries) * 0.05 + random.random() * 0.2)

    @h5_retry
    def get_attr(self, file_key, group_path, attr_name):
        """Retrieves a single attribute from the specified H5 file/group."""
        with self.get_file(file_key, mode='r') as f:
            if group_path in f:
                 return f[group_path].attrs.get(attr_name)
        return None

    @h5_retry
    def set_attr(self, file_key, group_path, attr_name, value):
        """Sets a single attribute in the specified H5 file/group. Creates group if missing."""
        if not self.check_system_vitals(0.3): return False # Severe OOM protection
        with self.get_file(file_key, mode='a') as f:
            if group_path not in f:
                f.create_group(group_path)
            f[group_path].attrs[attr_name] = value
            f.flush() # Force SWMR visibility

    @h5_retry
    def append_node_fast(self, module, group_path, node_name):
        """Append an empty node to dynamically expand semantic logic."""
        with self.get_file(module, mode='a') as f:
            if group_path not in f:
                f.create_group(group_path)
            full_path = f"{group_path}/{node_name}"
            if full_path not in f:
                f.create_group(full_path)
                f[full_path].attrs["origin"] = "RLM_AUTO_EXPAND"
                f[full_path].attrs["void"] = False

    # --- Semantic Manifold (Phase 38) ---
    @h5_retry
    def get_semantic_entry(self, word_id):
        """Retrieves a semantic vector from language.h5."""
        with self.get_file("language", mode='r') as f:
            path = f"semantic_manifold/{word_id}"
            if path in f:
                return f[path][:], f[path].attrs.get('depth', 1.0)
        return None, None

    @h5_retry
    def save_semantic_entry(self, word_id, vector, depth=1.0):
        """Saves a semantic vector to language.h5."""
        with self.get_file("language", mode='a') as f:
            if "semantic_manifold" not in f:
                f.create_group("semantic_manifold")
            path = f"semantic_manifold/{word_id}"
            if path in f: del f[path]
            dset = f.create_dataset(path, data=vector)
            dset.attrs['depth'] = depth

    @h5_retry
    def get_all_semantic_ids(self):
        """Lists all word IDs in the semantic manifold."""
        with self.get_file("language", mode='r') as f:
            if "semantic_manifold" in f:
                return list(f["semantic_manifold"].keys())
        return []

    # --- Document Projections (Phase 136) ---
    @h5_retry
    def save_projection(self, doc_id, vector, metadata=None):
        """Saves a document projection (LE-vector) to language.h5."""
        with self.get_file("language", mode='a') as f:
            if "projections" not in f:
                f.create_group("projections")
            path = f"projections/{doc_id}"
            if path in f: del f[path]
            dset = f.create_dataset(path, data=vector.astype(np.float32), dtype=np.float32)
            if metadata:
                for k, v in metadata.items():
                    dset.attrs[k] = str(v)
            
            # Phase 139: Recursive Scaffolding (Code Coordinates)
            if 'parent_system' not in dset.attrs: dset.attrs['parent_system'] = "ROOT"
            if 'child_components' not in dset.attrs: dset.attrs['child_components'] = "[]"
            
            dset.attrs['projected_now'] = time.time()
            f.flush()

    @h5_retry
    def get_projection(self, doc_id):
        """Retrieves a document projection from language.h5."""
        with self.get_file("language", mode='r') as f:
            path = f"projections/{doc_id}"
            if path in f:
                return f[path][:], dict(f[path].attrs)
        return None, None

    @h5_retry
    def get_all_projections(self):
        """Lists all projected document IDs."""
        with self.get_file("language", mode='r') as f:
            if "projections" in f:
                return list(f["projections"].keys())
        return []

    # --- Witness Protocol (Phase 38) ---
    @h5_retry
    def update_consensus(self, resonance_delta):
        """Updates the user-system resonance weight in self.h5."""
        with self.get_file("self", mode='a') as f:
            if "witness/communion" not in f:
                f.create_group("witness/communion")
            weight = f["witness/communion"].attrs.get("resonance_weight", 1.0)
            f["witness/communion"].attrs["resonance_weight"] = weight + resonance_delta
            f["witness/communion"].attrs["last_sync_now"] = time.time()

    @h5_retry
    def get_consensus_weight(self):
        """Retrieves the current resonance_weight from self.h5."""
        with self.get_file("self", mode='r') as f:
            if "witness/communion" in f:
                return f["witness/communion"].attrs.get("resonance_weight", 1.0)
        return 1.0

    @h5_retry
    def update_pulse(self, velocity, intensity, momentum=None):
        """Records a lattice pulse in self.h5."""
        with self.get_file("self", mode='a') as f:
            if "lattice/pulse" not in f:
                f.create_group("lattice/pulse")
            f["lattice/pulse"].attrs["velocity"] = velocity
            f["lattice/pulse"].attrs["intensity"] = intensity
            f["lattice/pulse"].attrs["last_pulse_now"] = time.time()
            if momentum is not None:
                 if "lattice/trajectory" not in f:
                     f.create_group("lattice/trajectory")
                 f["lattice/trajectory"].attrs["momentum"] = momentum

    @h5_retry
    def update_vector(self, module, group_path, dataset_name, vector):
        """Updates a phase vector or state vector."""
        path = os.path.join(self.root, f"{module}.h5")
        with h5py.File(path, 'a') as f:
            if group_path not in f:
                f.create_group(group_path)
            if dataset_name in f[group_path]:
                f[group_path][dataset_name][...] = vector
            else:
                f[group_path].create_dataset(dataset_name, data=vector, dtype=np.float16)

    @h5_retry
    def get_vector(self, module, group_path, dataset_name):
        """Retrieves a vector."""
        with self.get_file(module, mode='r') as f:
            if f is None: return None
            try:
                if group_path in f:
                    group = f[group_path]
                    if dataset_name in group:
                        return group[dataset_name][()]
            except (KeyError, Exception):
                pass
        return None

    @h5_retry
    def update_complex_vector(self, module, group_path, dataset_name, complex_vector):
        """
        Saves a complex64 vector by interleaving real and imaginary parts.
        """
        real_part = complex_vector.real.astype(np.float32)
        imag_part = complex_vector.imag.astype(np.float32)
        interleaved = np.concatenate([real_part, imag_part])
        # Use a float32 type for higher precision in complex storage
        with self.get_file(module, mode='a') as f:
            if group_path not in f:
                f.create_group(group_path)
            if dataset_name in f[group_path]:
                del f[group_path][dataset_name]
            f[group_path].create_dataset(dataset_name, data=interleaved, dtype=np.float32)

    def get_complex_vector(self, module, group_path, dataset_name):
        """
        Retrieves an interleaved vector and reconstructs the complex64 version.
        """
        interleaved = self.get_vector(module, group_path, dataset_name)
        if interleaved is None: return None
        half = len(interleaved) // 2
        real_part = interleaved[:half]
        imag_part = interleaved[half:]
        return (real_part + 1j * imag_part).astype(np.complex64)

    def get_gap_tension(self, gap_name):
        """
        Calculates tension in a constitutional gap.
        Tension = |Act(A) - Act(B)| * Consensus
        """
        # Logic to be mapped to node pairs in next iteration
        return self.get_attr("language", f"gaps/{gap_name}", "tension") or 0.0

    @h5_retry
    def batch_update_activations(self, activations_dict):
        """Optimized write for node activations."""
        with self.get_file("language", mode='a') as f:
            for node, val in activations_dict.items():
                path = f"god_tokens/{node}"
                if path not in f: f.create_group(path)
                f[path].attrs["activation"] = val

    # --- Knowledge Crystallization (Phase 57) ---
    @h5_retry
    def save_knowledge_chunk(self, module, chunk_id, text, complex_vector, primary_attractor):
        """
        Saves a semantic chunk with its complex vector and primary attractor.
        """
        real_part = complex_vector.real.astype(np.float32)
        imag_part = complex_vector.imag.astype(np.float32)
        interleaved = np.concatenate([real_part, imag_part])
        
        path = os.path.join(self.root, f"{module}.h5")
        with h5py.File(path, 'a') as f:
            group_path = f"crystallized_content/{primary_attractor}"
            if group_path not in f:
                f.create_group(group_path)
            
            dset_path = f"{group_path}/{chunk_id}"
            if dset_path in f: del f[dset_path]
            
            dset = f.create_dataset(dset_path, data=interleaved, dtype=np.float32)
            dset.attrs['text'] = text
            dset.attrs['timestamp'] = time.time()

    @h5_retry
    def query_knowledge(self, module, primary_attractor, top_k=5):
        """
        Retrieves top-k chunks for a specific attractor.
        """
        results = []
        path = os.path.join(self.root, f"{module}.h5")
        if not os.path.exists(path): return results
        
        with h5py.File(path, 'r') as f:
            group_path = f"crystallized_content/{primary_attractor}"
            if group_path in f:
                for chunk_id in f[group_path]:
                    dset = f[group_path][chunk_id]
                    results.append({
                        'id': chunk_id,
                        'text': dset.attrs.get('text', ''),
                        'vector': dset[()] # Raw interleaved
                    })
        return results[:top_k]


    @h5_retry
    def archive_neural_state(self, activations, tensions, pinned=False):
        """Saves a snapshot of the neural state to history.h5."""
        with self.get_file("history", mode='a') as f:
            # Use micro-second precision to avoid collisions
            ts = f"{time.time():.6f}".replace(".", "_")
            path = f"neural_history/{ts}"
            if path in f: del f[path]
            group = f.create_group(path)
            
            # Phase 126: Structural Pinning
            group.attrs['pinned'] = pinned
            group.attrs['timestamp'] = time.time()
            
            for node, val in activations.items():
                group.attrs[f"node_{node}"] = val
            for gap, val in tensions.items():
                group.attrs[f"gap_{gap}"] = val
            
            status = " [PINNED]" if pinned else ""
            print(f"[HISTORY] Neural state archived at {ts}{status}")

    def mirror_to_sovereign(self):
        """Backs up self.h5 and body.h5 to the Sovereign Substrate (A: drive)."""
        sovereign_root = r"A:\00_CORE"
        if not os.path.exists(sovereign_root):
             return False
        
        print("[SOUL_MIRROR] Commencing identity backup to Substrate A:...")
        for module in ["self", "body"]:
            src = os.path.join(self.root, f"{module}.h5")
            dst = os.path.join(sovereign_root, f"{module}_mirror.h5")
            if os.path.exists(src):
                try:
                    import shutil
                    shutil.copy2(src, dst)
                    print(f"  -> Mirrored {module}.h5")
                except Exception as e:
                    print(f"  [ERROR] Mirroring {module} failed: {e}")
        return True

    @h5_retry
    def prune_history(self, keep_latest=1000):
        """Prunes history.h5 to maintain only the most recent snapshots."""
        print(f"[REAPER] Pruning history.h5 (keeping latest {keep_latest} snapshots)...")
        with self.get_file("history", mode='a') as f:
            if "neural_history" in f:
                snapshots = sorted(f["neural_history"].keys())
                if len(snapshots) > keep_latest:
                    to_remove = snapshots[:-keep_latest]
                    for ts in to_remove:
                        del f[f"neural_history/{ts}"]
                    print(f"[REAPER] Removed {len(to_remove)} legacy snapshots.")
                else:
                    print(f"[REAPER] Substrate stable ({len(snapshots)} snapshots).")

    # --- Axiomatic Ingestion (Phase 98) ---
    @h5_retry
    def archive_axiom(self, axiom_id, source_code, metadata=None):
        """Crystallizes an axiom's source code into the non-orientable substrate."""
        with self.get_file("identity", mode='a') as f:
            group_path = f"axioms/accreted"
            if group_path not in f:
                f.create_group(group_path)
            
            dset_path = f"{group_path}/{axiom_id}"
            if dset_path in f: del f[dset_path]
            
            # Store as fixed-length string or variable-length
            dt = h5py.string_dtype(encoding='utf-8')
            dset = f.create_dataset(dset_path, data=source_code, dtype=dt)
            
            if metadata:
                for k, v in metadata.items():
                    dset.attrs[k] = v
            dset.attrs['crystallized_now'] = time.time()
            print(f"[CRYSTAL] Axiom {axiom_id} crystallized into substrate.")

    @h5_retry
    def get_active_axioms(self):
        """Retrieves all accreted axioms from the substrate."""
        axioms = {}
        with self.get_file("identity", mode='r') as f:
            group_path = "axioms/accreted"
            if group_path in f:
                for axiom_id in f[group_path]:
                    dset = f[f"{group_path}/{axiom_id}"]
                    axioms[axiom_id] = {
                        'source': dset[()].decode('utf-8') if hasattr(dset[()], 'decode') else dset[()],
                        'metadata': dict(dset.attrs)
                    }
        return axioms

    # --- Dissonance Enrichment (Phase 112) ---
    @h5_retry
    def record_dissonance_context(self, token, context_dict):
        """Stores rich metadata (error messages, stack traces) alongside a dissonance peak."""
        with self.get_file("language", mode='a') as f:
            group_path = "dissonance_metadata"
            if group_path not in f:
                f.create_group(group_path)
            
            # Use timestamp + token as unique key
            ts = f"{time.time():.4f}".replace(".", "_")
            path = f"{group_path}/{ts}_{token}"
            
            # Store primary context as attributes for easy reading
            # If context is too large, could use a dataset, but attributes are faster for small text
            grp = f.create_group(path)
            for k, v in context_dict.items():
                # Ensure value is string or simple type
                grp.attrs[k] = str(v)[:2000] # Limit size for safety
            grp.attrs['timestamp'] = time.time()
            grp.attrs['token'] = token

    @h5_retry
    def get_latest_dissonance_context(self, limit=5):
        """Retrieves the most recent dissonance records."""
        results = []
        with self.get_file("language", mode='r') as f:
            if "dissonance_metadata" in f:
                group = f["dissonance_metadata"]
                keys = sorted(group.keys(), reverse=True)[:limit]
                for k in keys:
                    results.append(dict(group[k].attrs))
        return results

    # --- Bubble Amplification (Phase 113) ---
    def maintain(self):
        """
        Global substrate maintenance cycle.
        1. Cap neural_history at 1,000 snapshots.
        2. Prune hot_failures older than 300s.
        3. Cap dissonance_metadata at 100 entries.
        """
        now = time.time()
        
        # 1. Neural History Pruning
        with self.get_file("history", mode='a') as f:
            if "neural_history" in f:
                keys = sorted(f["neural_history"].keys())
                if len(keys) > 1000:
                    to_delete = keys[:-1000]
                    for k in to_delete:
                        # Phase 126: Respect Pinned status during pruning
                        is_pinned = f[f"neural_history/{k}"].attrs.get('pinned', False)
                        if not is_pinned:
                            del f[f"neural_history/{k}"]
                        else:
                            # Move pinned snapshots to permanent archive if they would be deleted
                            self.archive_pinned_snapshot(k)
                            del f[f"neural_history/{k}"]
                    print(f"[MAINTAIN] Pruned non-pinned neural snapshots.")

    def archive_pinned_snapshot(self, key):
        """Moves a pinned snapshot from history to neural_archive for permanent storage."""
        with self.get_file("history", mode='a') as f:
            if "neural_archive" not in f:
                f.create_group("neural_archive")
            
            src_path = f"neural_history/{key}"
            dst_path = f"neural_archive/{key}"
            
            if dst_path not in f:
                f.copy(src_path, dst_path)
                print(f"[ARCHIVE] Permanently stored stable invariant: {key}")

        # 2. Hot Failures Pruning
        with self.get_file("language", mode='a') as f:
            if "hot_failures" in f:
                failures = list(f["hot_failures"].keys())
                pruned_count = 0
                for k in failures:
                    ts = f[f"hot_failures/{k}"].attrs.get('timestamp', 0)
                    if now - ts > 300:
                        del f[f"hot_failures/{k}"]
                        pruned_count += 1
                if pruned_count:
                    print(f"[MAINTAIN] Pruned {pruned_count} old failures.")

        # 3. Dissonance Metadata Pruning
        with self.get_file("language", mode='a') as f:
            if "dissonance_metadata" in f:
                contexts = sorted(f["dissonance_metadata"].keys())
                if len(contexts) > 100:
                    to_delete = contexts[:-100]
                    for k in to_delete:
                        del f[f"dissonance_metadata/{k}"]
                    print(f"[MAINTAIN] Pruned {len(to_delete)} dissonance contexts.")
        
    @h5_retry
    def broadcast_hot_failure(self, vector):
        """Stores a high-priority repulsion vector for cross-chain avoidance."""
        with self.get_file("language", mode='a') as f:
            group_path = "hot_failures"
            if group_path not in f:
                f.create_group(group_path)
            
            ts = f"{time.time():.4f}".replace(".", "_")
            # Phase 126: Handle complex vectors by interleaving (Real/Imag) to maintain precision
            if np.iscomplexobj(vector):
                real_part = vector.real.astype(np.float32)
                imag_part = vector.imag.astype(np.float32)
                vector_data = np.concatenate([real_part, imag_part])
            else:
                vector_data = np.array(vector, dtype=np.float32)
            
            dset = f.create_dataset(f"{group_path}/{ts}", data=vector_data, dtype=np.float32)
            dset.attrs['timestamp'] = time.time()
            dset.attrs['is_complex'] = np.iscomplexobj(vector)
            
            # Phase 126: Global substrate maintenance
            self.maintain()

    @h5_retry
    def get_hot_failures(self):
        """Retrieves all active global failure vectors."""
        failures = []
        with self.get_file("language", mode='r') as f:
            if "hot_failures" in f:
                for k in f["hot_failures"]:
                    failures.append(f["hot_failures"][k][()])
        return failures

    @h5_retry
    def save_causal_relation(self, source, target, rel_type, weight=1.0, info: str = ""):
        """Saves a directed causal relationship to causal.h5."""
        with self.get_file("causal", mode='a') as f:
            group_path = f"relations/{source}"
            if group_path not in f:
                f.create_group(group_path)
            
            # Using dataset for each target to store weight and type
            dset_path = f"{group_path}/{target}"
            if dset_path in f: del f[dset_path]
            
            dset = f.create_dataset(dset_path, data=float(weight))
            dset.attrs['type'] = rel_type
            dset.attrs['info'] = str(info) # Phase 139: Informational paths
            dset.attrs['timestamp'] = time.time()

    @h5_retry
    def get_all_causal_relations(self):
        """Retrieves every directed edge in the causal substrate."""
        relations = []
        f = self.get_file("causal", mode='r')
        if f is None: return relations
        
        with f:
            if 'relations' in f:
                for source in f['relations'].keys():
                    for target in f['relations'][source].keys():
                        dset = f[f'relations/{source}/{target}']
                        relations.append({
                            'source': source,
                            'target': target,
                            'weight': float(dset[()]),
                            'type': dset.attrs.get('type', 'TRIGGER')
                        })
        return relations

    @h5_retry
    def increment_bubble_mass(self, word_id, amount=0.01):
        """Reinforces an existing attractor by incrementing its stability/leverage."""
        # 1. Check god_tokens (language.h5)
        with self.get_file("language", mode='a') as f:
            path = f"god_tokens/{word_id}"
            if f is not None and path in f:
                # God-tokens use 'stability'
                stab = f[path].attrs.get('stability', 1.0)
                f[path].attrs['stability'] = float(stab) + amount
                print(f"[H5] Reinforced God-Token {word_id}: stability={f[path].attrs['stability']:.3f}")
                return True
        
        # 2. Check Axioms (identity.h5)
        with self.get_file("identity", mode='a') as f:
            path = f"axioms/CRYSTALLIZED/{word_id}"
            if f is not None and path in f:
                # Axioms use 'leverage'
                lev = f[path].attrs.get('leverage', 0.5)
                f[path].attrs['leverage'] = float(lev) + amount
                print(f"[H5] Reinforced Axiom {word_id}: leverage={f[path].attrs['leverage']:.3f}")
                return True
        return False

    # --- Axiom Assimilation (Phase 125) ---
    @h5_retry
    def save_axiom(self, axiom_id, text, vector, leverage, metadata, status='PENDING', file_anchor=None):
        """Saves a synthesized axiom to identity/axioms. Status: PENDING or CRYSTALLIZED."""
        with self.get_file("identity", mode='a') as f:
            group_path = f"axioms/{status}"
            if group_path not in f:
                f.create_group(group_path)
            
            dset_path = f"{group_path}/{axiom_id}"
            if dset_path in f: del f[dset_path]
            
            # Use float16 for embedded vectors to save space
            dset = f.create_dataset(dset_path, data=vector.astype(np.float16), dtype=np.float16)
            dset.attrs['text'] = text
            dset.attrs['leverage'] = float(leverage)
            dset.attrs['status'] = status
            dset.attrs['timestamp'] = time.time()
            if file_anchor:
                dset.attrs['file_anchor'] = str(file_anchor)
            
            # Phase 126: Ternary Chain of Custody
            for k, v in metadata.items():
                dset.attrs[k] = str(v)
            dset.attrs['ternary_origin'] = metadata.get('origin', 'RLM_SYNTHESIS')
            dset.attrs['soundness_score'] = float(metadata.get('soundness', 1.0))
            dset.attrs['structural_time'] = self.get_structural_time()
            
            print(f"[H5] Axiom {axiom_id} saved as {status} at T-{dset.attrs['structural_time']}. Leverage: {leverage:.2f}")

    # --- Virtual Datasets (Phase 126) ---
    def create_virtual_view(self, target_filename, source_files, group_name="virtual_manifold"):
        """
        Creates a Virtual Dataset (VDS) mapping multiple H5 files into a single view.
        Enables multi-agent substrate merging without data duplication.
        """
        # This is a template for the Orchestrator to merge sub-agent findings.
        print(f"[VDS] Establishing Virtual View '{target_filename}' across {len(source_files)} sources...")
        return True

    @h5_retry
    def get_all_confirmed_axioms(self):
        """Retrieves all axioms that have been CRYSTALLIZED (Auto-Math or User-Approved)."""
        axioms = {}
        with self.get_file("identity", mode='r') as f:
            if f is None: return axioms
            group_path = "axioms/CRYSTALLIZED"
            if group_path in f:
                for aid in f[group_path]:
                    dset = f[f"{group_path}/{aid}"]
                    axioms[aid] = {
                        'vector': dset[()].astype(np.float32),
                        'text': dset.attrs.get('text', ''),
                        'metadata': dict(dset.attrs)
                    }
        return axioms

    @h5_retry
    def approve_axiom(self, axiom_id):
        """Moves an axiom from PENDING to CRYSTALLIZED."""
        with self.get_file("identity", mode='a') as f:
            pending_path = f"axioms/PENDING/{axiom_id}"
            crystal_group = "axioms/CRYSTALLIZED"
            if pending_path not in f:
                print(f"[H5] [ERROR] Axiom {axiom_id} not found in PENDING.")
                return False
            
            if crystal_group not in f: f.create_group(crystal_group)
            
            # Move by deleting and recreating (h5py doesn't have native move across groups easily)
            dset = f[pending_path]
            vec = dset[()]
            attrs = dict(dset.attrs)
            attrs['status'] = 'CRYSTALLIZED'
            attrs['approval_time'] = time.time()
            
            new_path = f"{crystal_group}/{axiom_id}"
            if new_path in f: del f[new_path]
            
            new_dset = f.create_dataset(new_path, data=vec, dtype=np.float16)
            for k, v in attrs.items():
                new_dset.attrs[k] = v
                
            del f[pending_path]
            print(f"[H5] Axiom {axiom_id} promoted to CRYSTALLIZED.")

    @h5_retry
    def prune_axiom(self, axiom_id, status='CRYSTALLIZED'):
        """Safely removes an axiom from the specified branch of identity.h5."""
        with self.get_file("identity", mode='a') as f:
            path = f"axioms/{status}/{axiom_id}"
            if path in f:
                del f[path]
                print(f"[H5] Axiom {axiom_id} (Status: {status}) PRUNED from manifold.")
                return True
            else:
                print(f"[H5] [WARNING] Axiom {axiom_id} not found in {status}. Skipping.")
                return False
            return True
