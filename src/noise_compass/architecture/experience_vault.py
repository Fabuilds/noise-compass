import os
import json
import pickle
import numpy as np # Kept for np.ndarray and other numpy operations
from typing import List, Dict, Optional, Tuple # Kept for type hints
from datetime import datetime # Kept for msg.timestamp type (if ArchiverMessage uses it)
import sys
from pathlib import Path

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.tokens import ArchiverMessage

class ExperienceVault:
    """
    Persistent Episodic Memory (The Causal Vault).
    Stores ArchiverMessages indexed by semantic embeddings for k-NN retrieval.
    """
    def __init__(self, storage_path: str = "E:/Antigravity/Architecture/archives/experience_vault.pkl"):
        self.storage_path = storage_path
        self.experiences: List[Dict] = []  # List of dicts for easy serialization
        self.embeddings: Optional[np.ndarray] = None
        self.load()

    def add_experience(self, msg: ArchiverMessage):
        """Add a new experience to the vault."""
        # Convert ArchiverMessage to a serializable dict if needed, 
        # but here we keep high-level attributes and the embedding.
        exp = {
            "timestamp": msg.timestamp,
            "content_preview": msg.content_preview,
            "zone": msg.zone,
            "causal_type": msg.causal_type,
            "embedding": msg.collapsed_state.known + msg.collapsed_state.delta, # Centroid
            "god_tokens": [g.id for g in msg.god_token_activations],
            "ternary": msg.ternary,
            "energy": msg.energy_level
        }
        
        self.experiences.append(exp)
        
        # Update embedding matrix for k-NN
        new_emb = exp["embedding"].reshape(1, -1)
        if self.embeddings is None:
            self.embeddings = new_emb
        else:
            self.embeddings = np.vstack([self.embeddings, new_emb])
            
        # Limit vault size to prevent entropy bloat (e.g., last 2000 experiences)
        if len(self.experiences) > 2000:
            self.experiences = self.experiences[-2000:]
            self.embeddings = self.embeddings[-2000:]

    def retrieve(self, query_emb: np.ndarray, k: int = 3, threshold: float = 0.75) -> List[Dict]:
        """Retrieve k similar past experiences based on cosine similarity."""
        if self.embeddings is None or len(self.experiences) == 0:
            return []

        # Normalize query
        q_norm = np.linalg.norm(query_emb)
        if q_norm < 1e-10: return []
        q_unit = query_emb / q_norm

        # Normalize all stored embeddings
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        norms[norms < 1e-10] = 1.0
        unit_embs = self.embeddings / norms

        # Cosine similarity
        similarities = np.dot(unit_embs, q_unit)
        
        # Get top k indices above threshold
        indices = np.where(similarities >= threshold)[0]
        if len(indices) == 0:
            return []
            
        top_indices = sorted(indices, key=lambda i: similarities[i], reverse=True)[:k]
        
        results = []
        for idx in top_indices:
            res = self.experiences[idx].copy()
            res["similarity"] = float(similarities[idx])
            results.append(res)
            
        return results

    def save(self):
        """Persist vault to disk."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "wb") as f:
            pickle.dump({
                "experiences": self.experiences,
                "embeddings": self.embeddings
            }, f)
        print(f"[VAULT] Persisted {len(self.experiences)} experiences to {self.storage_path}")

    def load(self):
        """Load vault from disk."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "rb") as f:
                    data = pickle.load(f)
                    self.experiences = data.get("experiences", [])
                    self.embeddings = data.get("embeddings", None)
                print(f"[VAULT] Loaded {len(self.experiences)} experiences.")
            except Exception as e:
                print(f"[VAULT] Load failed: {e}. Starting fresh.")
                self.experiences = []
                self.embeddings = None
