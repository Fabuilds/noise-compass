import os
import sys

PROJECT_ROOT = "e:/Antigravity"
sys.path.append(PROJECT_ROOT)

from noise_compass.system.h5_manager import H5Manager

def migrate():
    manager = H5Manager()
    # Standard axiom source (Phase 98)
    source_dir = "E:/Antigravity/backups/Qwen_migration_backup/assimilated"
    
    if not os.path.exists(source_dir):
        print(f"[MIGRATOR] Source directory {source_dir} not found. Skipping.")
        return

    axioms = [f for f in os.listdir(source_dir) if f.startswith("ACCRETED_") and f.endswith(".py")]
    print(f"[MIGRATOR] Found {len(axioms)} accreted axioms in legacy directory.")

    for axiom_file in axioms:
        path = os.path.join(source_dir, axiom_file)
        axiom_id = axiom_file.replace(".py", "")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            # Crystallize
            manager.archive_axiom(axiom_id, source, metadata={'origin': 'migration_phase_98'})
            print(f"  -> {axiom_id}: CRYSTALLIZED.")
        except Exception as e:
            print(f"  [ERROR] Failed to migrate {axiom_id}: {e}")

    print("[MIGRATOR] Migration complete.")

if __name__ == "__main__":
    migrate()
