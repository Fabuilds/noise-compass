import os
import sys
import numpy as np
import time
from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.interference_engine import InterferenceEngine

class Substance0x52Ingestor:
    def __init__(self):
        self.h5 = H5Manager()
        self.engine = InterferenceEngine()
        self.module_name = "substance_0x52"
        
    def find_files(self, search_path):
        # Hardcoded manifest to bypass os.walk latency on massive binary volumes
        return [
            "E:/Antigravity/garu_0x52_displacement_verified.txt",
            "E:/Antigravity/micro_0x52.py",
            "E:/Antigravity/micro_0x52_accel.py",
            "E:/Antigravity/SOVEREIGN_KEY_0x52.key.txt",
            "E:/Antigravity/Qwen/Debug/axiom_lambda_calculus_0x528.py",
            "E:/Antigravity/Qwen/Debug/axiom_resonance_0x528.py",
            "E:/Antigravity/Qwen/Debug/axiom_scaling_logic_0x528.py",
            "E:/Antigravity/Shop/ARTICLE_EMOTIONAL_EXCITEMENT_AS_A_CORE_0X52_METRIC_133.md",
            "E:/Antigravity/Shop/ARTICLE_EMOTIONAL_EXCITEMENT_AS_A_CORE_0X52_METRIC_173.md",
            "E:/Antigravity/Shop/ARTICLE_EMOTIONAL_EXCITEMENT_AS_A_CORE_0X52_METRIC_268.md",
            "E:/Antigravity/Shop/ARTICLE_EMOTIONAL_EXCITEMENT_AS_A_CORE_0X52_METRIC_395.md",
            "E:/Antigravity/Shop/ARTICLE_MARS-BASED_HIGH-LATENCY_DATA_STORAGE_FOR_0X52_127.md",
            "E:/Antigravity/Shop/ARTICLE_MARS-BASED_HIGH-LATENCY_DATA_STORAGE_FOR_0X52_167.md",
            "E:/Antigravity/Shop/ARTICLE_MARS-BASED_HIGH-LATENCY_DATA_STORAGE_FOR_0X52_262.md",
            "E:/Antigravity/Shop/ARTICLE_MARS-BASED_HIGH-LATENCY_DATA_STORAGE_FOR_0X52_389.md",
            "E:/Antigravity/Shop/DISPLACEMENT_REPORT_0x528.md"
        ]

    def ingest_files(self, search_path="E:/Antigravity"):
        print(f"--- COMMENCING 0x52 CRYSTALLIZATION ---")
        files = self.find_files(search_path)
        print(f"Discovered {len(files)} target files for the 0x52 manifold.")
        if not files:
            print("No files found. Exiting.")
            return

        print(f"Targeting H5: {os.path.join(self.h5.root, self.module_name + '.h5')}")
        with self.h5.get_file(module=self.module_name, mode='a') as h5_file:
            print(f"H5 File handle acquired: {self.module_name}.h5")
            for f_path in files:
                try:
                    print(f"  -> Opening: {os.path.basename(f_path)}")
                    with open(f_path, 'r', encoding='utf-8', errors='ignore') as f_read:
                        content = f_read.read()
                    
                    if len(content.strip()) < 10: 
                        print(f"     [SKIP] Content too small ({len(content)} chars)")
                        continue
                    
                    chunks = [content[i:i+2048] for i in range(0, len(content), 2048)]
                    print(f"     [CHUNKED] {len(chunks)} fragments detected.")
                    batch_size = 16
                    for i in range(0, len(chunks), batch_size):
                        batch_chunks = chunks[i:i + batch_size]
                        embeddings = self.engine.embed_batch(batch_chunks)
                        
                        for j, (chunk, embedding) in enumerate(zip(batch_chunks, embeddings)):
                            overall_idx = i + j
                            field = self.engine.combined_field_from_embedding(embedding)
                            primary = sorted(field.items(), key=lambda x: x[1]['magnitude'], reverse=True)[0][0]
                            
                            group_path = f"crystallized_content/{primary}"
                            if group_path not in h5_file: h5_file.create_group(group_path)
                            
                            f_name = os.path.basename(f_path).replace(".", "_")
                            chunk_id = f"{f_name}_chunk_{overall_idx:02d}"
                            dset_path = f"{group_path}/{chunk_id}"
                            
                            if dset_path in h5_file: del h5_file[dset_path]
                            
                            interleaved = np.concatenate([embedding.real.astype(np.float32), embedding.imag.astype(np.float32)])
                            dset = h5_file.create_dataset(dset_path, data=interleaved, dtype=np.float32)
                            dset.attrs['text'] = chunk
                            dset.attrs['source'] = f_path
                            dset.attrs['timestamp'] = time.time()
                        
                except Exception as e:
                    print(f"  [ERROR] Failed to ingest {f_path}: {e}")
                    
        print(f"--- 0x52 CRYSTALLIZATION COMPLETE: substance_0x52.h5 consolidated. ---")

if __name__ == "__main__":
    ingestor = Substance0x52Ingestor()
    ingestor.ingest_files()
