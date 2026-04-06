"""
tension.py — The TensionManifold.

A component that finds where new attractors are forming—the densest 
regions of the generative zone that no current god-token captures.

While the ApophaticFrontier finds what cannot be known yet, 
the TensionManifold finds what is struggling to be named.
"""

import numpy as np
from typing import List, Dict, Optional
import sys
from pathlib import Path

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.tokens import WaveFunction

class TensionManifold:
    """
    Finds structural tension in the semantic field.
    
    High Tension = High density of Generative phase documents (π/4) 
    that lack a strong (+0.3) similarity to any existing GodToken.
    """
    
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.buffer: List[Dict] = []
        
    def record(self, emb: np.ndarray, wf: WaveFunction, 
               god_tokens: List[str], content: str = "") -> float:
        """
        Record a state and return its local tension score.
        Tension = (1 - max_sim) * in_generative_zone_weight
        """
        # Generative weight is highest at π/4 (0.785 rad)
        phase = wf.phase
        generative_weight = np.exp(-((phase - np.pi/4)**2) / 0.1)
        
        max_sim = wf.similarity
        tension = (1.0 - max_sim) * generative_weight
        
        if tension > 0.4:  # Only record high-tension events
            self.buffer.append({
                'embedding': emb.copy(),
                'tension': float(tension),
                'phase': float(phase),
                'god_tokens': god_tokens,
                'content_preview': content[:100]
            })
            
            # Maintain capacity
            if len(self.buffer) > self.capacity:
                self.buffer.sort(key=lambda x: x['tension'], reverse=True)
                self.buffer = self.buffer[:self.capacity]
                
        return float(tension)

    def find_attractor_candidates(self, min_cluster_size: int = 5) -> List[Dict]:
        """
        Cluster high-tension points to find candidate god-tokens.
        Uses simple cosine-similarity clustering for now.
        """
        if len(self.buffer) < min_cluster_size:
            return []
            
        candidates = []
        processed = [False] * len(self.buffer)
        
        for i in range(len(self.buffer)):
            if processed[i]: continue
            
            cluster = [self.buffer[i]]
            processed[i] = True
            
            for j in range(i + 1, len(self.buffer)):
                if processed[j]: continue
                
                sim = np.dot(self.buffer[i]['embedding'], self.buffer[j]['embedding'])
                if sim > 0.85:  # Tight cluster
                    cluster.append(self.buffer[j])
                    processed[j] = True
            
            if len(cluster) >= min_cluster_size:
                # Calculate centroid
                centroid = np.mean([c['embedding'] for c in cluster], axis=0)
                centroid /= (np.linalg.norm(centroid) + 1e-10)
                
                avg_tension = np.mean([c['tension'] for c in cluster])
                
                candidates.append({
                    'centroid': centroid,
                    'avg_tension': float(avg_tension),
                    'evidence_count': len(cluster),
                    'samples': [c['content_preview'] for c in cluster[:3]],
                    'nearby_gods': list(set([g for c in cluster for g in c['god_tokens']]))
                })
                
        return sorted(candidates, key=lambda x: x['avg_tension'], reverse=True)

    def tension_report(self) -> str:
        candidates = self.find_attractor_candidates()
        if not candidates:
            return "TensionManifold: No stable attractor candidates forming yet."
            
        lines = ["TensionManifold — Attractor Candidates Forming:"]
        for c in candidates[:3]:
            lines.append(f"  [T={c['avg_tension']:.3f}] {c['evidence_count']} points clustering near {c['nearby_gods'][:2]}")
            lines.append(f"  Samples: {c['samples'][0]}...")
            
        return "\n".join(lines)
