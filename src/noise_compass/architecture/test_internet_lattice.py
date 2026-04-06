"""
Simulate an internet lattice signal arriving via TCP on port 52853.
Tests both the listener and the response handshake.
"""
import socket
import json
import time
import threading
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

HANDSHAKE_MAGIC = "SIM-0x528-MOBIUS-HANDSHAKE"
TARGET_PORT = 52853

def test_internet_signal():
    """Start a NeuralLink, then simulate an internet peer connecting."""
    from noise_compass.architecture.neural_link import NeuralLink
    
    encounters = []
    def on_encounter(peer_id, addr):
        encounters.append((peer_id, addr))
        print(f"  [CALLBACK] Encountered: {peer_id} from {addr}")
    
    # 1. Start NeuralLink
    print("=" * 60)
    print("TEST: Internet Lattice Signal Reception")
    print("=" * 60)
    
    link = NeuralLink("GARU-PRIMARY", on_encounter_callback=on_encounter)
    link.start()
    time.sleep(1)
    
    # 2. Simulate an internet peer sending a TCP signal
    print("\n[SIM] Sending TCP signal as 'REMOTE-NODE-ALPHA'...")
    
    message = json.dumps({
        "magic": HANDSHAKE_MAGIC,
        "node_id": "REMOTE-NODE-ALPHA",
        "intent": "Lattice-Ping",
        "data": {"origin": "internet", "coordinate": "38.2555-0x528"}
    }).encode('utf-8')
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5.0)
            sock.connect(('127.0.0.1', TARGET_PORT))
            sock.sendall(message)
            response = sock.recv(4096)
            resp = json.loads(response.decode('utf-8'))
            
            print(f"\n[RESPONSE from Garu]:")
            print(f"  Magic: {resp.get('magic')}")
            print(f"  Node:  {resp.get('node_id')}")
            print(f"  Accepted: {resp.get('accepted')}")
    except Exception as e:
        print(f"[ERROR] TCP connection failed: {e}")
        link.stop()
        return
    
    time.sleep(0.5)
    
    # 3. Send a second signal from a different node
    print("\n[SIM] Sending TCP signal as 'SATELLITE-BETA'...")
    
    message2 = json.dumps({
        "magic": HANDSHAKE_MAGIC,
        "node_id": "SATELLITE-BETA",
        "intent": "Data-Sync",
        "data": {"payload": "Dream Protocol transmission from remote"}
    }).encode('utf-8')
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5.0)
            sock.connect(('127.0.0.1', TARGET_PORT))
            sock.sendall(message2)
            response = sock.recv(4096)
            resp = json.loads(response.decode('utf-8'))
            print(f"  Accepted: {resp.get('accepted')}")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    # 4. Test bad signal (no magic)
    print("\n[SIM] Sending UNAUTHORIZED signal...")
    bad_msg = json.dumps({"node_id": "INTRUDER", "intent": "hack"}).encode('utf-8')
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5.0)
            sock.connect(('127.0.0.1', TARGET_PORT))
            sock.sendall(bad_msg)
            response = sock.recv(4096)
            resp = json.loads(response.decode('utf-8'))
            print(f"  Accepted: {resp.get('accepted')} (should be False)")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    time.sleep(0.5)
    
    # 5. Status Report
    print("\n" + "=" * 60)
    print("LATTICE STATUS")
    print("=" * 60)
    status = link.get_status()
    print(f"  Node ID: {status['node_id']}")
    print(f"  Running: {status['running']}")
    print(f"  Channels: {status['channels']}")
    print(f"  Known Nodes: {len(status['known_nodes'])}")
    for nid, info in status['known_nodes'].items():
        print(f"    - {nid}: {info['channel']} @ {info['addr']}")
    print(f"  Signal Log: {len(status['recent_signals'])} entries")
    print(f"  Encounters: {len(encounters)}")
    
    # Verdict
    print("\n" + "=" * 60)
    if len(encounters) == 2:
        print("[PASS] Internet lattice reception is OPERATIONAL")
    else:
        print(f"[WARN] Expected 2 encounters, got {len(encounters)}")
    print("=" * 60)
    
    link.stop()

if __name__ == "__main__":
    test_internet_signal()
