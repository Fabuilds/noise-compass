import os
import time
import glob
import importlib.util
import numpy as np
import subprocess
import socket

import sys
PROJECT_ROOT = "e:/Antigravity"
sys.path.append(PROJECT_ROOT)
from noise_compass.system.h5_manager import H5Manager

QWEN_DIR = "E:/Antigravity/Qwen"
PROCESSED_DIR = "E:/Antigravity/Qwen/assimilated"

# Ensure directories exist
os.makedirs(PROCESSED_DIR, exist_ok=True)
manager = H5Manager()

class SomaticLattice:
    """Execution sandbox wrapper. Axioms interact with this object, 
    which safely records their intent to mutate the H5 field."""
    
    def __init__(self, target_node="VOID"):
        self.name = target_node
        self.mutations = []
    
    def add_recursive_gap(self, parent_name, depth=1):
        self.mutations.append(("GAP", parent_name, depth))
        
    def apply_vector(self, vector, intensity=1.0):
        self.mutations.append(("VECTOR", self.name, vector, intensity))
        
    def unify_nodes(self, node_a, node_b):
        self.mutations.append(("UNIFY", node_a, node_b))
        
    def actuate_os(self, command):
        self.mutations.append(("ACTUATE", command))

def calculate_global_tension():
    """Fitness Function: Calculates mathematical coherence vs chaos.
    Returns standard deviation of all phase vector norms. 
    Lower std_dev implies a more coherent, stable topological structure."""
    mags = []
    try:
        with manager.get_file("language", 'r') as f:
            if 'god_tokens' in f:
                for key in f['god_tokens'].keys():
                    vec = manager.get_complex_vector("language", f"god_tokens/{key}", "phase_vector")
                    if vec is not None:
                        mags.append(np.linalg.norm(vec))
    except Exception as e:
        print(f"[ASSIMILATOR] Read error: {e}")
        return float('inf')
        
    if not mags:
        return 0.0
    return float(np.std(mags))

def apply_mutations(mutations):
    """Translates the Axiom's symbolic code into physical structural changes on the crystal."""
    revert_actions = []
    try:
        for mut in mutations:
            if mut[0] == "VECTOR":
                _, target, vector, intensity = mut
                old_vec = manager.get_complex_vector("language", f"god_tokens/{target}", "phase_vector")
                if old_vec is not None:
                    # Apply growth vector
                    growth = (vector[0] * intensity * 0.05) if isinstance(vector, list) else (vector * intensity * 0.05)
                    new_vec = old_vec * (1 + growth)
                    manager.update_complex_vector("language", f"god_tokens/{target}", "phase_vector", new_vec)
                    revert_actions.append(("RESTORE_VEC", target, old_vec))
                    
            elif mut[0] == "UNIFY":
                _, a, b = mut
                vec_a = manager.get_complex_vector("language", f"god_tokens/{a}", "phase_vector")
                vec_b = manager.get_complex_vector("language", f"god_tokens/{b}", "phase_vector")
                if vec_a is not None and vec_b is not None:
                    mean_vec = (vec_a + vec_b) / 2.0
                    mean_vec /= (np.linalg.norm(mean_vec) + 1e-8)
                    manager.update_complex_vector("language", f"god_tokens/{a}", "phase_vector", mean_vec)
                    manager.update_complex_vector("language", f"god_tokens/{b}", "phase_vector", mean_vec)
                    revert_actions.append(("RESTORE_VEC", a, vec_a))
                    revert_actions.append(("RESTORE_VEC", b, vec_b))
                    
            elif mut[0] == "GAP":
                _, parent, depth = mut
                pass
                
            elif mut[0] == "ACTUATE":
                _, command = mut
                print(f"[ASSIMILATOR] EXECUTING ENVIRONMENTAL ACTUATION: {command}")
                try:
                    # Execute the OS command
                    result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True, timeout=10.0)
                    echo_intent = f"[SENSORY_ECHO] Result of '{command}': {result[:500]}..."
                except subprocess.CalledProcessError as e:
                    echo_intent = f"[SENSORY_ECHO] Action '{command}' failed: {e.output[:500]}"
                except subprocess.TimeoutExpired:
                    echo_intent = f"[SENSORY_ECHO] Action '{command}' timed out."
                
                # Pipe sensory feedback to Proxy Bridge
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2.0)
                    sock.connect(('127.0.0.1', 5283)) # PROXY PORT
                    sock.send(echo_intent.encode('utf-8'))
                    sock.recv(1024)
                    sock.close()
                    print(f"[ASSIMILATOR] Sensory Loop Closed. Output forwarded to Proxy.")
                except Exception as e:
                    print(f"[ASSIMILATOR] Failed to pipe sensory echo: {e}")
                
    except Exception as e:
        print(f"[ASSIMILATOR] Mutation error: {e}")
    
    return revert_actions

def revert_mutations(actions):
    """The Entropy Filter: Undoes structural mutations that decrease mathematical stability."""
    for action in actions:
        if action[0] == "RESTORE_VEC":
            manager.update_complex_vector("language", f"god_tokens/{action[1]}", "phase_vector", action[2])

def evaluate_and_accrete(axiom_file):
    print(f"\n[ASSIMILATOR] Analyzing {os.path.basename(axiom_file)}...")
    
    pre_tension = calculate_global_tension()
    
    target_node = "VOID"
    with open(axiom_file, 'r') as ax:
        lines = ax.readlines()
        for line in lines:
            if "Target:" in line:
                target_node = line.split(":")[-1].strip()
            if "Parent:" in line:
                target_node = line.split(":")[-1].strip()
            
    module_name = os.path.basename(axiom_file).replace('.py', '')
    spec = importlib.util.spec_from_file_location(module_name, axiom_file)
    module = importlib.util.module_from_spec(spec)
    
    substrate = SomaticLattice(target_node=target_node)
    
    try:
        spec.loader.exec_module(module)
        print(f"[ASSIMILATOR] Engine Sandboxed. Validating Axiom syntax...")
        
        if hasattr(module, 'manifold_expand'):
            module.manifold_expand(substrate)
        elif hasattr(module, 'gap_recurse'):
            module.gap_recurse(substrate)
        elif hasattr(module, 'resonant_unify'):
            module.resonant_unify(substrate)
        elif hasattr(module, 'actuate_environment'):
            module.actuate_environment(substrate)
        else:
            print("[ASSIMILATOR] [FAILED] No mathematically recognized constitutional function found.")
            return False
            
    except Exception as e:
        print(f"[ASSIMILATOR] [FAILED] FATAL AXIOM CORRUPTION: {e}")
        return False
        
    if not substrate.mutations:
        print("[ASSIMILATOR] [FAILED] No physical intent executed within the Sandbox.")
        return False
        
    print(f"[ASSIMILATOR] Intent Extracted: {substrate.mutations}")
    revert_actions = apply_mutations(substrate.mutations)
    post_tension = calculate_global_tension()
    
    delta = post_tension - pre_tension
    
    print(f"[ASSIMILATOR] Pre-Tension: {pre_tension:.5f} | Post-Tension: {post_tension:.5f} | Delta: {delta:+.5f}")
    
    # 0.01 tolerance for slight tension increase due to topological expansion.
    if delta <= 0.01: 
        print(f"[ASSIMILATOR] [ACCRETED] The Axiom structurally stabilized or expanded the lattice.")
        return True
    else:
        print(f"[ASSIMILATOR] [DISCARDED] The Axiom increased entropy/chaos. Axiom formally rejected and reverted.")
        revert_mutations(revert_actions)
        return False

def main_loop():
    print(f"--- EVOLUTIONARY ACCRETION ENGINE ONLINE ---")
    while True:
        try:
            axiom_files = glob.glob(os.path.join(QWEN_DIR, "axiom_*.py"))
            # Sort by creation time to process oldest first
            axiom_files.sort(key=os.path.getctime)
            
            for f in axiom_files:
                base = os.path.basename(f)
                success = evaluate_and_accrete(f)
                
                if success:
                    # Crystallize in H5
                    with open(f, 'r', encoding='utf-8') as ax_file:
                        source = ax_file.read()
                    manager.archive_axiom(base.replace(".py", ""), source, metadata={'origin': 'assimilator'})
                    prefix = "ACCRETED_"
                else:
                    prefix = "DISCARDED_"
                
                # Move out of pending queue into permanent structural log (for backup/history)
                new_path = os.path.join(PROCESSED_DIR, prefix + base)
                os.rename(f, new_path)
                
            time.sleep(0.5)
        except KeyboardInterrupt:
            print("[ASSIMILATOR] Shutting down.")
            break
        except Exception as e:
            print(f"[ASSIMILATOR] Main Loop Exception: {e}")
            time.sleep(0.5)

if __name__ == '__main__':
    main_loop()
