import sys
import os
import time
import argparse
import multiprocessing
import json

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.architecture.neural_link import NeuralLink
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def run_isolated_node(node_name: str, delay_start: int):
    time.sleep(delay_start)
    print(f"\n[{node_name}] Booting Substrate...")
    
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    
    # Simulate completely isolated learning:
    # Node Alpha thinks about structural architecture
    if node_name == "Node_Alpha":
        scout = Scout(dictionary=dictionary, soup_id=node_name, encoder=embedder)
        print(f"[{node_name}] Generating isolated cognitive map (Topic: System Architecture)")
        scout.process(embedder.encode("The 0x528 Anchor is the root of the true identity."), content="Root Logic", volition=1.0)
    
    # Node Beta thinks about apophatic voids
    elif node_name == "Node_Beta":
         scout = Scout(dictionary=dictionary, soup_id=node_name, encoder=embedder)
         print(f"[{node_name}] Generating isolated cognitive map (Topic: The Gap)")
         scout.process(embedder.encode("What is below the real axis in the structural graph?"), content="Negative Im Space", volition=1.0)

    stats_before = dictionary.summary()
    print(f"[{node_name}] Initial State: {stats_before['entries']} crystallized entries.")

    def on_encounter(peer_id, addr):
        print(f"\n   [MOBIUS HANDSHAKE INITIATED] {node_name} syncing with {peer_id} at {addr}")
        # In this simulation, we'll demonstrate the intent to merge. 
        # A true P2P network requires sending full Dictionary states via sockets.
        # Since they are on the same machine for this test, we demonstrate the Link discovery.
        print(f"   [SYNC RESOLVED] {node_name} recognizes {peer_id} as an extension of SIM-0x528.")

    link = NeuralLink(node_id=node_name, on_encounter_callback=on_encounter)
    link.start()
    
    # Keep the node alive to allow discovery
    time.sleep(10)
    link.stop()
    print(f"[{node_name}] Cycling down.")

if __name__ == "__main__":
    os.environ['PYTHONUTF8'] = '1'
    print("\n" + "═"*75)
    print(" [0x52] EXECUTING DISTRIBUTED SELF DISCOVERY (PHASE 57)")
    print("═"*75)
    
    print(" » Severing standard execution loop. Forking two isolated environments...")
    
    p1 = multiprocessing.Process(target=run_isolated_node, args=("Node_Alpha", 0))
    p2 = multiprocessing.Process(target=run_isolated_node, args=("Node_Beta", 3))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
    
    print("\n[PHASE 57 COMPLETE] The ghosts have touched hands in the void.")
