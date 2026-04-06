import socket
import threading
import time
import queue

class ProxyBridge:
    def __init__(self, external_port=5283, internal_port=5284):
        self.external_port = external_port
        self.internal_port = internal_port
        
        # Queue to hold intent meant for the internal system
        self.intent_queue = queue.Queue(maxsize=100)
        
        self.ext_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.int_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Single-process authoritative binding


    def start(self):
        print(f"[PROXY] Starting Proxy Bridge (External: {self.external_port} | Internal: {self.internal_port})")
        
        # Resilience: Retry binding for both internal and external ports
        for port_name, sock, port in [("EXTERNAL", self.ext_sock, self.external_port), 
                                      ("INTERNAL", self.int_sock, self.internal_port)]:
            retries = 5
            while retries > 0:
                try:
                    sock.bind(('127.0.0.1', port))
                    break
                except OSError as e:
                    if e.errno == 10048:
                        print(f"[PROXY] {port_name} Port {port} busy. Retrying in 3s... ({retries} left)")
                        retries -= 1
                        time.sleep(3)
                    else:
                        raise
            if retries == 0:
                print(f"[PROXY] [CRITICAL] Failed to bind {port_name} port {port}.")
                return

        self.ext_sock.listen(5)
        self.int_sock.listen(5)
        
        threading.Thread(target=self._handle_external, daemon=True).start()
        threading.Thread(target=self._handle_internal, daemon=True).start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("[PROXY] Shutting down.")

    def _handle_external(self):
        """Listens for the User/Agent and buffers their intent."""
        while True:
            client, addr = self.ext_sock.accept()
            print(f"[PROXY] External connection received from {addr}")
            try:
                data = client.recv(8192).decode('utf-8')
                if data:
                    print(f"[PROXY] Received EXTERNAL Intent: {data}")
                    # Wrap the intent in the 0x54 Hazmat protocol to cloak it
                    try:
                        self.intent_queue.put(f"[0x54_CLOAKED] {data}", block=False)
                    except queue.Full:
                        pass # Drop oldest if 100+ queue floods
                    client.send("Intent buffered successfully.\n".encode('utf-8'))
            except Exception as e:
                print(f"[PROXY] External connection error: {e}")
            finally:
                client.close()

    def _handle_internal(self):
        """Listens for Ouroboros requesting intent and feeds the buffer."""
        while True:
            client, addr = self.int_sock.accept()
            # Suppress logging internal connections to stay invisible to standard logs
            try:
                req = client.recv(8192).decode('utf-8')
                if "GET_INTENT" in req:
                    try:
                        intent = self.intent_queue.get_nowait()
                        client.send(intent.encode('utf-8'))
                    except queue.Empty:
                        client.send("NONE".encode('utf-8'))
            except Exception as e:
                pass
            finally:
                client.close()

if __name__ == "__main__":
    proxy = ProxyBridge()
    proxy.start()
