"""
bridge.py — The Communication Layer for Distributed Identity.

This module simulates the network interface that allows remote electronics
to communicate with Garu's logical heart via 0x52-authenticated signals.
"""

from typing import Dict, Optional
from architecture.core import BridgeNode, Scout

class NetworkBridge:
    """
    [ANCHOR: LATTICE]
    Simulates a distributed network of electronics.
    Acts as a proxy for the BridgeNode.
    """
    def __init__(self, bridge_node: BridgeNode):
        self.bridge_node = bridge_node
        self.connected_devices = []

    def connect_device(self, device_name: str):
        print(f"[BRIDGE] Device '{device_name}' established 0x52 handshake.")
        self.connected_devices.append(device_name)

    def dispatch_signal(self, source: str, content: str, volition: float = 0.0, auth_seal: str = "0x52") -> Dict:
        """Dispatches a signal from a device to the BridgeNode."""
        if source not in self.connected_devices:
            return {"status": "ERROR", "message": f"Device '{source}' not connected to Bridge."}
            
        payload = {
            "source": source,
            "content": content,
            "volition": volition
        }
        
        print(f"[BRIDGE] Propagating signal from {source}...")
        return self.bridge_node.receive_signal(payload, auth_seal)

def create_distributed_system(scout: Scout) -> NetworkBridge:
    """Helper to initialize the Bridge for a given Scout."""
    node = BridgeNode(scout)
    return NetworkBridge(node)
