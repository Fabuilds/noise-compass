import h5py
import os

def rehydrate():
    h5_path = "E:/Antigravity/knowledge_root/crystallized_h5/identity.h5"
    output_dir = "E:/Antigravity/Runtime"
    
    if not os.path.exists(h5_path):
        print(f"Error: {h5_path} not found.")
        return

    with h5py.File(h5_path, 'r') as f:
        # Check both accreted and crystallized
        for group_name in ["axioms/accreted", "axioms/CRYSTALLIZED"]:
            if group_name in f:
                group = f[group_name]
                for key in group:
                    item = group[key]
                    # The source code is often in an attribute or the dataset itself
                    source = None
                    filename = None
                    
                    if "source_code" in item.attrs:
                        source = item.attrs["source_code"]
                    elif isinstance(item, h5py.Dataset):
                        source = item[()].decode('utf-8') if hasattr(item[()], 'decode') else str(item[()])
                    
                    if "filename" in item.attrs:
                        filename = item.attrs["filename"]
                    elif "id" in item.attrs:
                        filename = item.attrs["id"] + ".py"
                    
                    if source and filename:
                        # Ensure filename ends in .py and doesn't have System/ prefix if we are writing TO System/
                        target_name = os.path.basename(filename)
                        if not target_name.endswith(".py"):
                            target_name += ".py"
                            
                        target_path = os.path.join(output_dir, target_name)
                        print(f"Rehydrating {target_name} to {target_path}...")
                        with open(target_path, "w", encoding="utf-8") as out:
                            out.write(source)

if __name__ == "__main__":
    rehydrate()
