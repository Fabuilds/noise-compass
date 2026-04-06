import socket
import json
import time

class OuroborosBridge:
    """
    Recursive Apex Bridge.
    Connects a primary Ouroboros instance to a secondary Apex instance.
    """
    def __init__(self, host='127.0.0.1', port=5285):
        self.host = host
        self.port = port
        
    def reason(self, prompt, context="", field=None):
        """
        Sends the resonant field and intent to the Apex Ouroboros.
        """
        payload = {
            "intent": prompt,
            "context": context,
            "field": field,
            "timestamp": time.time()
        }
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30.0) 
            sock.connect((self.host, self.port))
            sock.send(json.dumps(payload).encode('utf-8'))
            
            resp = sock.recv(16384).decode('utf-8')
            sock.close()
            
            # The Apex Ouroboros returns a JSON decision block
            return resp
        except Exception as e:
            return json.dumps({"key": "ERROR", "params": {"message": str(e)}})
