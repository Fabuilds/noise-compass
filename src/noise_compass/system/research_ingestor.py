import os
import sys
import numpy as np
import time
from pypdf import PdfReader
from noise_compass.system.h5_manager import H5Manager
from noise_compass.system.interference_engine import InterferenceEngine

class ResearchIngestor:
    def __init__(self):
        self.h5 = H5Manager()
        self.engine = InterferenceEngine()

    def ingest_paper(self, pdf_path):
        filename = os.path.basename(pdf_path)
        module_name = filename.replace(".pdf", "").replace(" ", "_").lower()
        
        # Singleton Guard
        pid_file = f"E:/Antigravity/Runtime/{module_name}.pid"
        if os.path.exists(pid_file):
            print(f"[WARINING] Ingestion for {module_name} may already be in progress. Aborting to prevent bloat.")
            return
        with open(pid_file, 'w') as f: f.write(str(os.getpid()))
        
        try:
            print(f"--- INGESTING RESEARCH PAPER: {filename} ---")
            print(f"Generating H5 module: {module_name}.h5")
            
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)
            print(f"Total Pages detected: {total_pages}")
            
            batch_size = 8 # Smaller batch for embedding
            flush_interval_pages = 10 # Flush to H5 every 10 pages
            
            current_chunks = []
            overall_chunk_idx = 0
            
            with self.h5.get_file(module=module_name, mode='a') as f:
                for page_idx, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if not page_text or len(page_text.strip()) < 10:
                        continue
                    
                    # Split page into 1k char chunks
                    page_chunks = [page_text[i:i+1000] for i in range(0, len(page_text), 1000)]
                    current_chunks.extend(page_chunks)
                    
                    # Process if batch full OR every N pages OR last page
                    if len(current_chunks) >= batch_size or (page_idx + 1) % flush_interval_pages == 0 or (page_idx + 1) == total_pages:
                        if not current_chunks: continue
                        
                        try:
                            embeddings = self.engine.embed_batch(current_chunks)
                            for chunk, embedding in zip(current_chunks, embeddings):
                                field = self.engine.combined_field_from_embedding(embedding)
                                primary = sorted(field.items(), key=lambda x: x[1]['magnitude'], reverse=True)[0][0]
                                
                                group_path = f"crystallized_content/{primary}"
                                if group_path not in f: f.create_group(group_path)
                                
                                chunk_id = f"chunk_{overall_chunk_idx:06d}"
                                dset_path = f"{group_path}/{chunk_id}"
                                if dset_path in f: del f[dset_path]
                                
                                interleaved = np.concatenate([embedding.real.astype(np.float32), embedding.imag.astype(np.float32)])
                                dset = f.create_dataset(dset_path, data=interleaved, dtype=np.float32)
                                dset.attrs['text'] = chunk
                                dset.attrs['timestamp'] = time.time()
                                
                                overall_chunk_idx += 1
                            
                            f.flush() # Force flush to disk
                            print(f"  Processed page {page_idx + 1}/{total_pages}... (Total Chunks: {overall_chunk_idx})")
                            current_chunks = [] # Clear handled chunks
                            
                        except Exception as e:
                            print(f"  [ERROR] Page {page_idx} Batch Failed: {e}")
                            current_chunks = []
        
        finally:
            print(f"--- INGESTION COMPLETE: {module_name}.h5 stabilized with {overall_chunk_idx} fragments. ---")
            if os.path.exists(pid_file): os.remove(pid_file)
        
        print(f"--- INGESTION COMPLETE: {module_name}.h5 stabilized. ---")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python research_ingestor.py <pdf_path>")
    else:
        ingestor = ResearchIngestor()
        ingestor.ingest_paper(sys.argv[1])
