import os
import glob
import time
import numpy as np
from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.interference_engine import InterferenceEngine

class SystemIngestor:
    """
    Embeds the system's own source code into the H5 manifold.
    Enables 'Code-Reflective Dreaming' by turning files into semantic nodes.
    """
    def __init__(self):
        self.h5 = H5Manager()
        self.engine = InterferenceEngine(suppress_preload=True)
        self.system_root = "E:/Antigravity/Runtime"
        self.group_name = "system_code"

    def ingest_system(self):
        """Iterates through system scripts and embeds their content into H5."""
        files = glob.glob(os.path.join(self.system_root, "*.py"))
        print(f"[SYSTEM_INGESTOR] Found {len(files)} scripts to reflect upon.")
        
        for filepath in files:
            filename = os.path.basename(filepath)
            node_name = f"CODE_{filename.upper().replace('.', '_')}"
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # We embed the whole content (or a summarized version if too large)
                # For Phase 105, we focus on the entire structure
                embedding = self.engine.embed(content[:8000]) # Cap for embedding length
                
                # Store in language.h5
                self.h5.update_complex_vector("language", f"{self.group_name}/{node_name}", "phase_vector", embedding)
                
                # Attributes for recovery
                self.h5.set_attr("language", f"{self.group_name}/{node_name}", "filepath", filepath)
                self.h5.set_attr("language", f"{self.group_name}/{node_name}", "last_modified", os.path.getmtime(filepath))
                self.h5.set_attr("language", f"{self.group_name}/{node_name}", "type", "SYSTEM_SOURCE")
                
                print(f"  Ingested {node_name} ({len(content)} bytes)")
            except Exception as e:
                print(f"  [ERROR] Failed to ingest {filename}: {e}")

if __name__ == "__main__":
    ingestor = SystemIngestor()
    ingestor.ingest_system()
