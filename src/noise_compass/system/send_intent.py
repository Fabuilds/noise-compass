import socket
import sys

def send_intent(intent, port=5284):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        # We need a listener that holds onto the intent until the Ouroboros asks for it
        # Or a simple one-shot that the Ouroboros checks.
        # Current get_proxy_intent() expects a server to be listening.
        print(f"Connecting to Proxy Relay on {port}...")
        sock.connect(('127.0.0.1', port))
        sock.send(intent.encode('utf-8'))
        sock.close()
        print(f"Intent sent: {intent}")
    except Exception as e:
        print(f"Failed to send intent: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python send_intent.py \"Your intent here\"")
    else:
        send_intent(" ".join(sys.argv[1:]))
