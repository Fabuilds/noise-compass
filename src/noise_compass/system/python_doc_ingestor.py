import re
import sys
import os
import numpy as np
import time
from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.interference_engine import InterferenceEngine

# Ensure paths
PROJECT_ROOT = "e:/Antigravity"
sys.path.append(PROJECT_ROOT)

class PythonDocIngestor:
    """
    Scrapes or translates Python documentation into H5 semantic nodes.
    """
    def __init__(self):
        self.h5 = H5Manager()
        self.engine = InterferenceEngine()

    def ingest_pairs(self, pairs):
        """
        Accepts list of (module_name, summary) and persists to H5.
        """
        print(f"--- INGESTING {len(pairs)} PYTHON DOCUMENTATION NODES ---")
        for module, summary in pairs:
            print(f"  Ingesting '{module}'...")
            try:
                # 1. Embed summary
                vector = self.engine.embed(summary)
                
                # 2. Save to H5
                group = f"python_docs/modules/{module}"
                self.h5.update_complex_vector("language", group, "phase_vector", vector)
                self.h5.set_attr("language", group, "summary", summary)
                self.h5.set_attr("language", group, "source", "docs.python.org/3/library")
                
                # 3. Add a small delay to prevent H5 lock storm on slow disks
                time.sleep(0.01)
            except Exception as e:
                print(f"    [ERROR] Failed to ingest {module}: {e}")

        print("--- INGESTION COMPLETE ---")

if __name__ == "__main__":
    # Seed data from structural analysis of docs.python.org
    # This list was derived from Position 5 of the read_url_content call.
    seed_data = [
        ("pathlib", "Object-oriented filesystem paths"),
        ("os.path", "Common pathname manipulations"),
        ("stat", "Interpreting stat() results"),
        ("filecmp", "File and Directory Comparisons"),
        ("tempfile", "Generate temporary files and directories"),
        ("glob", "Unix style pathname pattern expansion"),
        ("fnmatch", "Unix filename pattern matching"),
        ("linecache", "Random access to text lines"),
        ("shutil", "High-level file operations"),
        ("math", "Mathematical functions"),
        ("cmath", "Mathematical functions for complex numbers"),
        ("decimal", "Decimal fixed-point and floating-point arithmetic"),
        ("fractions", "Rational numbers"),
        ("random", "Generate pseudo-random numbers"),
        ("statistics", "Mathematical statistics functions"),
        ("itertools", "Functions creating iterators for efficient looping"),
        ("functools", "Higher-order functions and operations on callable objects"),
        ("operator", "Standard operators as functions"),
        ("array", "Efficient arrays of numeric values"),
        ("weakref", "Weak references"),
        ("types", "Dynamic type creation and names for built-in types"),
        ("copy", "Shallow and deep copy operations"),
        ("pprint", "Data pretty printer"),
        ("enum", "Support for enumerations"),
        ("graphlib", "Functionality to operate with graph-like structures")
    ]
    
    ingestor = PythonDocIngestor()
    ingestor.ingest_pairs(seed_data)
