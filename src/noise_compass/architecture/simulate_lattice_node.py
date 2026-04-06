import socket
import json
import time

DISCOVERY_PORT = 52852
HANDSHAKE_MAGIC = "SIM-0x528-MOBIUS-HANDSHAKE"

def simulate_peer(node_id="peer-999-EXT"):
    print(f"[SIMULATOR] Starting Peer Simulation: {node_id}")
    message = json.dumps({
        "magic": HANDSHAKE_MAGIC,
        "node_id": node_id,
        "intent": "Discovery-Mock"
    }).encode('utf-8')

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # Shouting into the void
        print(f"[SIMULATOR] Broadcasting to port {DISCOVERY_PORT}...")
        for _ in range(5):
            sock.sendto(message, ('<broadcast>', DISCOVERY_PORT))
            print("   > Signal Transmitted.")
            time.sleep(2)

if __name__ == "__main__":
    simulate_peer()
