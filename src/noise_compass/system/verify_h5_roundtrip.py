import numpy as np
import os
import sys
import time
from noise_compass.system.h5_manager import H5Manager

# Ensure paths
PROJECT_ROOT = "e:/Antigravity"
sys.path.append(PROJECT_ROOT)

def audit_roundtrip():
    print("--- INITIATING H5 SUBSTRATE INTEGRITY AUDIT ---")
    manager = H5Manager()
    
    # 1. COMPLEX ROUND-TRIP (384-D Session 12 standard)
    print("\n[1/3] Auditing 384-D Complex Vector Precision...")
    test_vec = (np.random.randn(384) + 1j * np.random.randn(384)).astype(np.complex64)
    group = "audit/test_complex"
    dset = "roundtrip_vector"
    
    manager.update_complex_vector("language", group, dset, test_vec)
    retrieved_vec = manager.get_complex_vector("language", group, dset)
    
    if retrieved_vec is None:
        print("  [ERROR] RETRIEVAL FAILED: Dataset not found.")
        return False
        
    diff = np.abs(test_vec - retrieved_vec)
    max_err = np.max(diff)
    
    if np.allclose(test_vec, retrieved_vec, atol=1e-7):
        print(f"  [SUCCESS] Match confirmed. Max error: {max_err:.2e}")
    else:
        print(f"  [FAILURE] Precision loss detected! Max error: {max_err:.2e}")
        return False

    # 2. FLOAT16 LEGACY/LATTICE AUDIT
    print("\n[2/3] Auditing Multi-D Float Vector Persistence...")
    test_float = np.random.randn(512).astype(np.float16)
    group_f = "audit/test_float"
    dset_f = "float_vector"
    
    manager.update_vector("language", group_f, dset_f, test_float)
    retrieved_float = manager.get_vector("language", group_f, dset_f)
    
    if np.allclose(test_float, retrieved_float, atol=1e-3):
        print("  [SUCCESS] Float16 persistence confirmed.")
    else:
        print("  [FAILURE] Float16 drift detected!")
        return False

    # 3. ATTRIBUTE & GROUP INTEGRITY
    print("\n[3/3] Auditing Attribute Integrity...")
    test_str = "PERSISTENCE_OF_VISION_0x123"
    test_val = 1.6262
    
    manager.set_attr("language", "audit/metadata", "string_val", test_str)
    manager.set_attr("language", "audit/metadata", "float_val", test_val)
    
    res_str = manager.get_attr("language", "audit/metadata", "string_val")
    res_val = manager.get_attr("language", "audit/metadata", "float_val")
    
    if res_str == test_str and abs(res_val - test_val) < 1e-6:
        print("  [SUCCESS] Metadata persistence confirmed.")
    else:
        print(f"  [FAILURE] Metadata mismatch! -> '{res_str}', {res_val}")
        return False

    print("\n--- AUDIT COMPLETE: SUBSTRATE CERTIFIED ---")
    return True

if __name__ == "__main__":
    success = audit_roundtrip()
    sys.exit(0 if success else 1)
