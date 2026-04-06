import os
import numpy as np
import time

class MetricVault:
    def __init__(self, storage_path="e:/Antigravity/Runtime/Autonomous_Output/metric_vault.npz"):
        self.storage_path = os.path.abspath(storage_path)
        self.lock_path = self.storage_path + ".lock"
        self.history_size = 5000 
        self._initialize_vault()

    def _initialize_vault(self):
        if not self._acquire_lock():
            return
        try:
            if not os.path.exists(self.storage_path):
                dir_name = os.path.dirname(self.storage_path)
                os.makedirs(dir_name, exist_ok=True)
                
                data = {
                    'timestamps': np.zeros(self.history_size),
                    'geometry_edges': np.zeros((self.history_size, 3)),
                    'stability': np.zeros(self.history_size),
                    'agape_resonance': np.zeros(self.history_size),
                    'index': np.array([0])
                }
                # Save to temp and move for safety
                tmp_init = self.storage_path + ".init"
                np.savez(tmp_init, **data)
                actual_tmp = tmp_init + ".npz"
                if os.path.exists(self.storage_path):
                    os.remove(self.storage_path)
                os.replace(actual_tmp, self.storage_path)
        finally:
            self._release_lock()

    def _acquire_lock(self, timeout=10):
        start_time = time.time()
        while True:
            try:
                os.mkdir(self.lock_path)
                return True
            except FileExistsError:
                if time.time() - start_time > timeout:
                    return False
                time.sleep(0.1)
            except Exception:
                return False

    def _release_lock(self):
        try:
            if os.path.exists(self.lock_path):
                os.rmdir(self.lock_path)
        except:
            pass

    def record(self, edges, stability, agape_resonance, log_func=print):
        if not self._acquire_lock():
            log_func("[METRIC_VAULT ERROR]: Lock timeout.")
            return

        try:
            if not os.path.exists(self.storage_path):
                # Try to initialize if missing
                data = {
                    'timestamps': np.zeros(self.history_size),
                    'geometry_edges': np.zeros((self.history_size, 3)),
                    'stability': np.zeros(self.history_size),
                    'agape_resonance': np.zeros(self.history_size),
                    'index': np.array([0])
                }
            else:
                with np.load(self.storage_path) as vault:
                    data = {k: vault[k] for k in vault.files}
            
            idx = int(data['index'][0])
            data['timestamps'][idx] = time.time()
            data['geometry_edges'][idx] = np.array(edges)
            data['stability'][idx] = stability
            data['agape_resonance'][idx] = agape_resonance
            
            data['index'][0] = (idx + 1) % self.history_size
            
            # Temporary file
            tmp_path = self.storage_path + ".tmp"
            np.savez(tmp_path, **data)
            actual_tmp = tmp_path + ".npz"
            
            # Use os.replace + retry loop for Windows stubbornness
            max_retries = 5
            for i in range(max_retries):
                try:
                    if os.path.exists(self.storage_path):
                        os.remove(self.storage_path)
                    os.replace(actual_tmp, self.storage_path)
                    break
                except Exception as e:
                    if i == max_retries - 1: raise e
                    time.sleep(0.2)
            
        except Exception as e:
            log_func(f"[METRIC_VAULT ERROR]: Record failed: {e}")
        finally:
            self._release_lock()
