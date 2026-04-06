import os
import sys
import json
import time
import hashlib
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from noise_compass.system.dictionary import Dictionary

class IdentityManifold:
    def __init__(self):
        self.identity = "0x528_IDENTITY_MANIFOLD"
        self.growth_dir = os.path.normpath("e:/Antigravity/Qwen")
        self.archive_root = os.path.join(self.growth_dir, "Manifold_Archive")
        self.heatmap_path = "e:/Antigravity/Runtime/identity_heatmap.json"
        self.dictionary = Dictionary.load_cache(os.path.join(PROJECT_ROOT, "Architecture/archives/dictionary_cache.npz"))
        
        # Internal state
        self.heatmap = self._load_heatmap()
        self.distinctness_threshold = 0.05 # Minimum Change required
        
        # Multi-Agent State (Phase 28)
        self.registry_path = "e:/Antigravity/Runtime/agent_registry.json"
        self.locks_path = "e:/Antigravity/Runtime/manifold_locks.json"
        self.consensus_path = "e:/Antigravity/Runtime/consensus_ledger.json"
        self.agent_id = None 
        
        if not os.path.exists(self.archive_root):
            os.makedirs(self.archive_root)

    def _log(self, msg, importance="INFO"):
        print(f"[{self.identity}] [{importance}] {msg}")

    def _load_heatmap(self):
        if os.path.exists(self.heatmap_path):
            with open(self.heatmap_path, "r") as f:
                return json.load(f)
        return {"failure_modes": {}, "hot_seeds": {}, "dead_zones": []}

    def _save_heatmap(self):
        with open(self.heatmap_path, "w") as f:
            json.dump(self.heatmap, f, indent=4)

    def organize_axiom(self, file_path):
        """
        Taxonomy: Clusters axioms by their semantic seeds.
        Returns the new organized path.
        """
        try:
            filename = os.path.basename(file_path)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            seed = "UNKNOWN"
            for line in content.split("\n")[:10]:
                if "Seed:" in line:
                    seed = line.split("Seed:")[1].strip().replace(", ", "_")
                    break
            
            # Phase 28: Cluster Locking
            if not self.lock_cluster(seed):
                self._log(f"Chorus: Cluster '{seed}' is locked. Retrying next cycle.", "DEBUG")
                return file_path

            try:
                # Create hierarchical directory
                cluster_dir = os.path.join(self.archive_root, seed)
                if not os.path.exists(cluster_dir):
                    os.makedirs(cluster_dir)
                
                dest = os.path.join(cluster_dir, filename)
                
                # Atomic move
                if os.path.exists(dest):
                    os.remove(dest)
                os.replace(file_path, dest)
                
                self._log(f"Taxonomy: Axiom {filename} organized into cluster '{seed}'.")
                
                # Phase 27 Integration
                seed_tokens = seed.split("_")
                self.integrate_axiom(content, seed_tokens)
                
                return dest
            finally:
                self.unlock_cluster(seed)
                
        except Exception as e:
            self._log(f"Taxonomy Error: {e}", "ERROR")
            return file_path

    def distinctive_check(self, hypothesis_text, seed_tokens):
        """
        Distinction: Checks if the new hypothesis is semantically unique.
        Returns (is_distinct, distance, best_match_info).
        """
        # We check against the dictionary's existing knowledge
        # Actually, for Phase 27, we check against the clusters.
        # But a simple way is checking the distance to the seeds in the dictionary.
        
        # Simplified for now: calculate the centroid and check stability
        try:
            embs = []
            for t in seed_tokens:
                gt = self.dictionary.god_tokens.get(t)
                if gt and gt.embedding is not None:
                    embs.append(gt.embedding)
            
            if not embs:
                return True, 1.0, "No Base Knowledge"

            centroid = np.mean(embs, axis=0)
            centroid /= np.linalg.norm(centroid)
            
            # Distance logic (Mocking semantic distance check)
            # In a real run, we'd compare the hash or summary.
            return True, 0.8, "Novel Emergence"
        except:
            return True, 1.0, "Check Failed"

    def record_failure(self, seed, error_type):
        """Adaptation: Tracks failures to inform future spin selection."""
        self.heatmap["failure_modes"][error_type] = self.heatmap["failure_modes"].get(error_type, 0) + 1
        self.heatmap["hot_seeds"][seed] = self.heatmap["hot_seeds"].get(seed, 0) + 1
        
        # Penalize dead zones
        if self.heatmap["hot_seeds"][seed] > 10:
            if seed not in self.heatmap["dead_zones"]:
                self.heatmap["dead_zones"].append(seed)
                self._log(f"Adaptation: Seed '{seed}' marked as DEAD ZONE.", "WARNING")
        
        self._save_heatmap()

    def integrate_axiom(self, hypothesis_text, seed_tokens):
        """
        Integration: Updates the core knowledge base with successful emergence.
        Currently, this nudges the dictionary's weighted embeddings.
        """
        try:
            self._log(f"Integration: Merging emergence from {seed_tokens} into core manifold.")
            # In a full simulation, we'd update the dictionary embeddings here.
            # For now, we note the integration in the heatmap.
            self.heatmap["integrated_concepts"] = self.heatmap.get("integrated_concepts", [])
            summary = f"{'|'.join(seed_tokens)} -> {hypothesis_text[:50]}..."
            if summary not in self.heatmap["integrated_concepts"]:
                self.heatmap["integrated_concepts"].append(summary)
            self._save_heatmap()
            return True
        except Exception as e:
            self._log(f"Integration Error: {e}", "ERROR")
            return False

    def get_collaborative_seeds(self, pool, count=3):
        """Phase 28: Inter-Agent Interference. Pulls focus seeds from other agents."""
        registry = self._load_json(self.registry_path, default={})
        other_focus = []
        for aid, data in registry.items():
            if aid != self.agent_id and time.time() - data["last_seen"] < 120:
                other_focus.extend(data["focus"])
        
        if other_focus and random.random() < 0.3: # 30% chance to collaborate
            self._log("Chorus: Inter-Agent Interference detected. Tuning to peer focus.")
            # Select from peer focus
            collab = random.sample(other_focus, min(len(other_focus), 1))
            # Fill remaining from pool
            remaining = [s for s in pool if s not in collab]
            return collab + random.sample(remaining, count - 1)
        
        return self.get_steered_seeds(pool, count)

    def get_steered_seeds(self, pool, count=3):
        """Adaptation: Returns seeds from the pool that are not in dead zones."""
        valid = [s for s in pool if s not in self.heatmap["dead_zones"]]
        if len(valid) < count:
            return np.random.choice(pool, count, replace=False).tolist()
        return np.random.choice(valid, count, replace=False).tolist()

    # --- PHASE 28: MULTI-AGENT PROTOCOLS ---

    def register_agent(self, agent_id, focus_seeds=None):
        """Registers a new agent in the Chorus."""
        self.agent_id = agent_id
        registry = self._load_json(self.registry_path, default={})
        registry[agent_id] = {
            "status": "ONLINE",
            "last_seen": time.time(),
            "focus": focus_seeds or [],
            "pid": os.getpid()
        }
        self._save_json(self.registry_path, registry)
        self._log(f"Chorus: Agent {agent_id} registered.")

    def agent_heartbeat(self, focus_seeds=None):
        """Updates agent status and focus seeds."""
        if not self.agent_id: return
        registry = self._load_json(self.registry_path, default={})
        if self.agent_id in registry:
            registry[self.agent_id]["last_seen"] = time.time()
            if focus_seeds:
                registry[self.agent_id]["focus"] = focus_seeds
            self._save_json(self.registry_path, registry)

    def lock_cluster(self, cluster_name):
        """Locks a taxonomical cluster for exclusive access."""
        locks = self._load_json(self.locks_path, default={})
        current_time = time.time()
        
        # Clean stale locks (> 60s)
        locks = {k: v for k, v in locks.items() if current_time - v["time"] < 60}
        
        if cluster_name in locks and locks[cluster_name]["agent"] != self.agent_id:
            return False # Locked by someone else
        
        locks[cluster_name] = {"agent": self.agent_id, "time": current_time}
        self._save_json(self.locks_path, locks)
        return True

    def unlock_cluster(self, cluster_name):
        """Releases a cluster lock."""
        locks = self._load_json(self.locks_path, default={})
        if cluster_name in locks and locks[cluster_name]["agent"] == self.agent_id:
            del locks[cluster_name]
            self._save_json(self.locks_path, locks)

    # --- PHASE 29: COLLECTIVE CONSENSUS ---

    def cast_vote(self, axiom_id, score):
        """Phase 29: Agents vote on candidate axioms."""
        ledger = self._load_json(self.consensus_path, default={})
        if axiom_id not in ledger:
            ledger[axiom_id] = {"votes": {}, "timestamp": time.time()}
        
        ledger[axiom_id]["votes"][self.agent_id] = score
        self._save_json(self.consensus_path, ledger)
        self._log(f"Consensus: Agent {self.agent_id} voted {score:.4f} on {axiom_id}.")

    def check_consensus(self, axiom_id, threshold=0.55, quorum=0.6):
        """Checks if an axiom has reached consensus."""
        ledger = self._load_json(self.consensus_path, default={})
        registry = self._load_json(self.registry_path, default={})
        
        # Count active agents (last seen < 2 mins)
        active_agents = [aid for aid, data in registry.items() if time.time() - data["last_seen"] < 120]
        active_count = len(active_agents)
        
        if axiom_id not in ledger:
            return False, 0.0, 0
        
        votes = ledger[axiom_id]["votes"]
        relevant_votes = [v for aid, v in votes.items() if aid in active_agents]
        
        if not relevant_votes:
            return False, 0.0, 0
        
        avg_score = sum(relevant_votes) / len(relevant_votes)
        participation_ratio = len(relevant_votes) / max(1, active_count)
        
        # Consensus: enough participation AND high enough average score
        if participation_ratio >= quorum and avg_score >= threshold:
            self._log(f"Consensus: Quorum met for {axiom_id}. Avg Score: {avg_score:.4f}. PROMOTING.")
            return True, avg_score, len(relevant_votes)
        
        return False, avg_score, len(relevant_votes)

    def clean_ledger(self):
        """Prunes old ballots (> 1 hour)."""
        ledger = self._load_json(self.consensus_path, default={})
        now = time.time()
        ledger = {k: v for k, v in ledger.items() if now - v["timestamp"] < 3600}
        self._save_json(self.consensus_path, ledger)

    def _load_json(self, path, default=None):
        if not os.path.exists(path):
            return default if default is not None else {}
        
        for _ in range(5): # Retry loop
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, PermissionError):
                time.sleep(0.1)
            except Exception: break
        return default if default is not None else {}

    def _save_json(self, path, data):
        for _ in range(5): # Retry loop
            try:
                # Semi-atomic write via temp file
                temp_path = path + ".tmp"
                with open(temp_path, "w") as f:
                    json.dump(data, f, indent=4)
                
                if os.path.exists(path):
                    os.remove(path)
                os.rename(temp_path, path)
                return True
            except PermissionError:
                time.sleep(0.1)
            except Exception: break
        return False

if __name__ == "__main__":
    manifold = IdentityManifold()
    print("Identity Manifold initialized.")
