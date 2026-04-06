import os
import json
import time
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity

class SmartOrganizer:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        print(f"[SMART_ORGANIZER] Loading model {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.file_data = []

    def load_directory(self, directory_path, extensions=('.md', '.py', '.txt', '.json')):
        print(f"[SMART_ORGANIZER] Scanning {directory_path}...")
        for root, _, files in os.walk(directory_path):
            if '_QUARANTINE' in root or '__pycache__' in root:
                continue
            for file in files:
                if file.endswith(extensions):
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        if len(content.strip()) < 10:
                            continue
                        self.file_data.append({
                            'path': path,
                            'name': file,
                            'content': content
                        })
                    except Exception as e:
                        print(f"[WARNING] Could not read {path}: {e}")

    def index_files(self):
        if not self.file_data:
            print("[SMART_ORGANIZER] No files to index.")
            return
        
        print(f"[SMART_ORGANIZER] Embedding {len(self.file_data)} files...")
        contents = [f['content'] for f in self.file_data]
        embeddings = self.model.encode(contents, show_progress_bar=True)
        
        for i, emb in enumerate(embeddings):
            self.file_data[i]['embedding'] = emb

    def find_near_duplicates(self, threshold=0.95):
        print(f"[SMART_ORGANIZER] Searching for near-duplicates (threshold > {threshold})...")
        embeddings = np.array([f['embedding'] for f in self.file_data])
        similarities = cosine_similarity(embeddings)
        
        duplicates = []
        seen = set()
        
        for i in range(len(similarities)):
            if i in seen: continue
            for j in range(i + 1, len(similarities)):
                if j in seen: continue
                if similarities[i][j] > threshold:
                    duplicates.append({
                        'file_a': self.file_data[i]['path'],
                        'file_b': self.file_data[j]['path'],
                        'similarity': float(similarities[i][j])
                    })
                    # Use a simple heuristic: keep the one with shorter/cleaner name or more recent?
                    # For now, just mark b for quarantine
                    seen.add(j)
        
        return duplicates

    def cluster_files(self, n_clusters=None, distance_threshold=0.5):
        print("[SMART_ORGANIZER] Generating semantic clusters...")
        embeddings = np.array([f['embedding'] for f in self.file_data])
        
        # Agglomerative clustering is better for unknown number of clusters
        clustering = AgglomerativeClustering(
            n_clusters=n_clusters, 
            distance_threshold=distance_threshold,
            metric='cosine',
            linkage='average'
        )
        labels = clustering.fit_predict(embeddings)
        
        clusters = {}
        for i, label in enumerate(labels):
            label = int(label)
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(self.file_data[i]['path'])
            
        return clusters

    def generate_manifest(self, output_path="pruning_manifest.json"):
        duplicates = self.find_near_duplicates()
        clusters = self.cluster_files()
        
        manifest = {
            "timestamp": time.ctime(),
            "summary": {
                "total_files_analyzed": len(self.file_data),
                "duplicate_groups_found": len(duplicates),
                "suggested_clusters": len(clusters)
            },
            "pruning_candidates": duplicates,
            "semantic_groupings": {f"Cluster_{k}": v for k, v in clusters.items()}
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=4)
        
        print(f"[SMART_ORGANIZER] Manifest generated at {output_path}")
        return manifest

if __name__ == "__main__":
    organizer = SmartOrganizer()
    # Scan Shop and System Logic
    organizer.load_directory("E:/Antigravity/Shop")
    organizer.load_directory("E:/Antigravity/Package/src/noise_compass/system")
    
    organizer.index_files()
    organizer.generate_manifest()
