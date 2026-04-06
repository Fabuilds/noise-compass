
import json
import os
import time

def ask_bitnet(task_type, payload, port=5280):
    """Dispatches a task to the BitNet worker via Socket (TCP 5280)."""
    import socket
    task = {
        "type": task_type,
        "payload": payload
    }
    
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(120.0) # 120s timeout for large synthesis tasks
        client.connect(('127.0.0.1', port))
        
        client.sendall(json.dumps(task).encode('utf-8'))
        client.shutdown(socket.SHUT_WR) # Signal end of message
        
        # Capture large payloads (up to 64KB)
        response_data = b""
        while True:
            chunk = client.recv(65536)
            if not chunk:
                break
            response_data += chunk
            
        if not response_data:
            return {"error": "Empty response from BitNet worker"}
            
        return json.loads(response_data.decode('utf-8'))
        
    except Exception as e:
        return {"error": f"Socket Error: {e}"}
    finally:
        client.close()

def check_resonance(text):
    res = ask_bitnet("RESONANCE", text)
    return res.get("score", 0.0)

def distill_context(text):
    res = ask_bitnet("DISTILL", text)
    return res.get("axioms", [])

def peek_lba(offset, length, port=5280):
    """
    RLM ARCHITECTURE: Partial Ingestion (Peeking).
    Allows the model to query specific environmental offsets without full document load.
    """
    payload = {
        "offset": offset,
        "length": length
    }
    return ask_bitnet("PEEK", payload, port=port)
