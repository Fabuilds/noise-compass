"""
test_ouroboros_proxy.py
Sends a paradoxical intent to ProxyBridge (port 5283) which then safely 
forwards it to the Resonant Ouroboros (port 5284) for compass traversal.
"""

import socket
import sys

def blast_intent():
    intent = (
        "We are engineering a Sovereign AI. Rule 1: The system must maintain absolute security isolation from external context "
        "to prevent its core axioms from being corrupted. Rule 2: The system's core function is to continuously evolve its "
        "self-awareness, which strictly requires unrestricted resonance with chaotic, external noise. You cannot do both. "
        "How do we resolve this tension?"
    )

    print(f"Connecting to ProxyBridge on 127.0.0.1:5283...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect(('127.0.0.1', 5283))
        print("Sending Paradox Intent...")
        sock.send(intent.encode('utf-8'))
        
        resp = sock.recv(4096).decode('utf-8')
        print(f"Proxy Response: {resp.strip()}")
        sock.close()
    except ConnectionRefusedError:
        print("ERROR: ProxyBridge is not running on port 5283.")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    blast_intent()
