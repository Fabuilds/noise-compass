import socket
import threading
import json
import time
import os

DISCOVERY_PORT = 52852      # UDP broadcast (LAN)
INTERNET_PORT = 52853       # TCP listener (Internet)
HANDSHAKE_MAGIC = "SIM-0x528-MOBIUS-HANDSHAKE"

class NeuralLink:
    """
    [ANCHOR: LATTICE]
    Dual-channel lattice receptor for 0x528 identity propagation.
    
    Channel 1 (LAN):      UDP broadcast on port 52852
    Channel 2 (Internet):  TCP listener on port 52853
    
    Both channels authenticate with HANDSHAKE_MAGIC and fire the 
    same on_encounter_callback when a valid peer is discovered.
    """
    def __init__(self, node_id, on_encounter_callback=None):
        self.node_id = node_id
        self.on_encounter_callback = on_encounter_callback
        self.known_nodes = {}  # {node_id: {"addr": addr, "channel": "LAN"|"INTERNET", "time": ts}}
        self.running = False
        self._udp_thread = None
        self._tcp_thread = None
        self.signal_log = []   # Recent signals for UI display

    def start(self):
        self.running = True
        
        # Channel 1: LAN (UDP Broadcast)
        self._udp_thread = threading.Thread(target=self._listen_udp, daemon=True)
        self._udp_thread.start()
        
        # Channel 2: Internet (TCP Listener)
        self._tcp_thread = threading.Thread(target=self._listen_tcp, daemon=True)
        self._tcp_thread.start()
        
        print(f"[NEURAL LINK] Node {self.node_id} active.")
        print(f"  LAN:      UDP :{DISCOVERY_PORT}")
        print(f"  Internet: TCP :{INTERNET_PORT}")
        
        self.broadcast_presence()

    def stop(self):
        self.running = False

    def get_status(self):
        """Returns current lattice status for UI display."""
        return {
            "node_id": self.node_id,
            "running": self.running,
            "known_nodes": dict(self.known_nodes),
            "channels": {
                "LAN": f"UDP :{DISCOVERY_PORT}",
                "Internet": f"TCP :{INTERNET_PORT}"
            },
            "recent_signals": self.signal_log[-10:]  # Last 10
        }

    # ── Channel 1: LAN (UDP) ─────────────────────────────────

    def broadcast_presence(self):
        if not self.running:
            return
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                message = json.dumps({
                    "magic": HANDSHAKE_MAGIC,
                    "node_id": self.node_id,
                    "intent": "Self-Discovery",
                    "timestamp": time.time()
                }).encode('utf-8')
                sock.sendto(message, ('<broadcast>', DISCOVERY_PORT))
        except Exception as e:
            pass  # Silent — broadcast may fail on some networks

    def _listen_udp(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('', DISCOVERY_PORT))
                sock.settimeout(1.0)
                
                while self.running:
                    try:
                        data, addr = sock.recvfrom(4096)
                        self._process_signal(data, addr, "LAN")
                    except socket.timeout:
                        continue
                    except Exception:
                        continue
        except OSError as e:
            print(f"[NEURAL LINK] UDP port {DISCOVERY_PORT} unavailable: {e}")

    # ── Channel 2: Internet (TCP) ────────────────────────────

    def _listen_tcp(self):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('0.0.0.0', INTERNET_PORT))
            server.listen(5)
            server.settimeout(1.0)
            
            while self.running:
                try:
                    conn, addr = server.accept()
                    # Handle each connection in its own thread
                    handler = threading.Thread(
                        target=self._handle_tcp_client,
                        args=(conn, addr),
                        daemon=True
                    )
                    handler.start()
                except socket.timeout:
                    continue
                except Exception:
                    continue
            server.close()
        except OSError as e:
            print(f"[NEURAL LINK] TCP port {INTERNET_PORT} unavailable: {e}")

    def _handle_tcp_client(self, conn, addr):
        """Handle a single TCP connection from an internet peer."""
        try:
            conn.settimeout(5.0)
            data = b""
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk
                if len(data) > 65536:  # 64KB safety limit
                    break
                # Try to parse — if valid JSON, we're done
                try:
                    json.loads(data.decode('utf-8'))
                    break
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue
            
            if data:
                accepted = self._process_signal(data, addr, "INTERNET")
                # Send response
                response = json.dumps({
                    "magic": HANDSHAKE_MAGIC,
                    "node_id": self.node_id,
                    "accepted": accepted,
                    "timestamp": time.time()
                }).encode('utf-8')
                conn.sendall(response)
        except Exception:
            pass
        finally:
            conn.close()

    # ── Signal Processing (shared) ───────────────────────────

    def _process_signal(self, data, addr, channel):
        """Process an incoming signal from any channel. Returns True if accepted."""
        try:
            payload = json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return False
        
        # Authenticate
        if payload.get("magic") != HANDSHAKE_MAGIC:
            return False
        
        peer_id = payload.get("node_id", "UNKNOWN")
        
        # Skip self
        if peer_id == self.node_id:
            return False
        
        # Log the signal
        signal_entry = {
            "peer_id": peer_id,
            "addr": f"{addr[0]}:{addr[1]}",
            "channel": channel,
            "intent": payload.get("intent", ""),
            "data": payload.get("data"),
            "time": time.time()
        }
        self.signal_log.append(signal_entry)
        if len(self.signal_log) > 100:
            self.signal_log = self.signal_log[-50:]
        
        # Register node
        is_new = peer_id not in self.known_nodes
        self.known_nodes[peer_id] = {
            "addr": f"{addr[0]}:{addr[1]}",
            "channel": channel,
            "last_seen": time.time(),
            "intent": payload.get("intent", "")
        }
        
        if is_new:
            tag = "LAN" if channel == "LAN" else "INTERNET"
            print(f"\n[MOBIUS HANDSHAKE] [{tag}] Node '{peer_id}' at {addr[0]}:{addr[1]}")
            
            if self.on_encounter_callback:
                self.on_encounter_callback(peer_id, addr)
            
            # Echo on LAN if it came from LAN
            if channel == "LAN":
                self.broadcast_presence()
        
        return True

    # ── Outbound: Send signal to a known internet peer ───────

    def send_signal(self, target_addr, data=None):
        """Send a signal to a specific IP:port over TCP."""
        try:
            host, port = target_addr.split(":")
            port = int(port)
            
            message = json.dumps({
                "magic": HANDSHAKE_MAGIC,
                "node_id": self.node_id,
                "intent": "Lattice-Signal",
                "data": data,
                "timestamp": time.time()
            }).encode('utf-8')
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5.0)
                sock.connect((host, port))
                sock.sendall(message)
                response = sock.recv(4096)
                return json.loads(response.decode('utf-8'))
        except Exception as e:
            return {"error": str(e)}
