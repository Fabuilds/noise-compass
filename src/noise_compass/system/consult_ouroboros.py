import socket
import json
import sys

def consult_ouroboros(intent, port=5284):
    """
    Connects to the Antigravity Ouroboros Listener to perform a structural 
    resonance check on a given intent.
    """
    payload = {
        "intent": intent,
        "mode": "consultation"
    }
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(60.0) # Allow time for Qwen/RLM reasoning
        sock.connect(('127.0.0.1', port))
        sock.send(json.dumps(payload).encode('utf-8'))
        
        # Receive the response (verdict, field, etc.)
        resp_data = b""
        while True:
            chunk = sock.recv(16384)
            if not chunk: break
            resp_data += chunk
            if len(chunk) < 16384: break
            
        sock.close()
        return json.loads(resp_data.decode('utf-8'))
    except Exception as e:
        return {"error": str(e), "status": "FAILED"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python consult_ouroboros.py \"Intent String\"")
    else:
        query = " ".join(sys.argv[1:])
        result = consult_ouroboros(query)
        print(json.dumps(result, indent=2))
