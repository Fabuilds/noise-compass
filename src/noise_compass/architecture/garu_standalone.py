import sys
import os
import argparse
import numpy as np

# Ensure Architecture is in the path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary
from noise_compass.architecture.bridge import NetworkBridge

def start_garu_standalone(mode):
    print("\n" + "═"*75)
    print(" [0x52] SUMMONING GARU (STANDALONE SUBSTRATE)")
    print("═"*75)
    print("Loading 363GB Logic Mass... (Simulated)")
    
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    
    scout = Scout(dictionary=dictionary, soup_id="standalone_anchor")
    bridge = NetworkBridge(scout)
    
    print(" » Substrate Acquired. Logic Stabilized.")
    print(f" » Operating Mode: {mode.upper()}")
    print("═"*75)
    
    if mode == "interactive":
        print("\n[Interactive Mode] Enter 'exit' to terminate.")
        while True:
            try:
                user_input = input("\nArchitect (0x528) > ")
                if user_input.lower() == 'exit':
                    break
                
                # Use bridge to ensure proper 0x52 signal routing
                response = bridge.receive_signal("local_admin", user_input, auth_token="0x52")
                print(f"\nGaru > {response}")
                
            except KeyboardInterrupt:
                break
    
    elif mode == "scavenge":
        from noise_compass.architecture.tools import Toolbox
        toolbox = Toolbox()
        print("\n[Scavenger Mode] Initiating single sweep of Shop substrates...")
        
        # Simulated sweep logic
        target = "huggingface/transformers"
        vuln = "Pickle RCE"
        
        print(f" » Target: {target} | Gap: {vuln}")
        res = toolbox.call("huntr_scout", {"repository": target, "vulnerability": vuln})
        print(f" » {res}")
        
    print("\n[0x52] Garu Disconnected from Substrate.")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.environ['PYTHONUTF8'] = '1' # Enforce Unicode
    
    parser = argparse.ArgumentParser(description="Garu Standalone Execution Interface")
    parser.add_argument('--mode', type=str, choices=['interactive', 'scavenge'], default='interactive',
                        help='Execution mode: interactive (chat) or scavenge (hunt)')
    
    args = parser.parse_args()
    start_garu_standalone(args.mode)
