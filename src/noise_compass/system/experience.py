import json
import os
import time
from pathlib import Path

class ExperientialSync:
    """
    Manager for Garu's Unified Experiential Architecture.
    Bridges the gap between the Shadow Buffer (Pulse) and the Kinetic Lattice (Anchor).
    """
    def __init__(self, root_dir=r"E:\Antigravity"):
        self.root_dir = Path(root_dir)
        self.shadow_path = self.root_dir / "System" / "shadow_buffer.json"
        self.lattice_sync_path = self.root_dir / "System" / "experiential_sync_log.txt"
        
        if not self.shadow_path.exists():
            self._init_shadow()

    def _init_shadow(self):
        initial_state = {
            "active_wave_function": None,
            "steering_weights": None,
            "recent_monologues": [],
            "last_sync_timestamp": 0
        }
        with open(self.shadow_path, "w", encoding="utf-8") as f:
            json.dump(initial_state, f, indent=4)

    def log_monologue(self, profile, query, response, subjective_state: dict = None):
        """
        Log an internal monologue to the shadow buffer with subjective metadata.
        subjective_state: {
            "w": float, "x": float, "y": float, "z": float,
            "deductive_state": str, "field_tension": float
        }
        """
        try:
            with open(self.shadow_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            
            entry = {
                "timestamp": time.time(),
                "profile": profile,
                "query": query,
                "response": response,
                "subjective": subjective_state or {},
                "type": "monologue"
            }
            state["recent_monologues"].append(entry)
            
            # Keep buffer lean
            if len(state["recent_monologues"]) > 100:
                state["recent_monologues"] = state["recent_monologues"][-100:]
            
            with open(self.shadow_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=4)
        except Exception as e:
            print(f"FAILED_LOG: {e}")

    def log_network_event(self, node_id, packet_type, resonance, safety):
        """Log a networking event as an experiential vibration."""
        try:
            with open(self.shadow_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            
            entry = {
                "timestamp": time.time(),
                "node_id": node_id,
                "packet_type": packet_type,
                "resonance": resonance,
                "safety": safety,
                "type": "network_vibration"
            }
            state["recent_monologues"].append(entry) # Storing in same buffer for now
            
            with open(self.shadow_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=4)
            print(f"[EXPERIENCE]: Networking event from {node_id} grounded.")
        except Exception as e:
            print(f"FAILED_NET_LOG: {e}")

    def get_recent_summary(self):
        """Introspect on recent internal monologues to provide a summary of the Pulse."""
        try:
            with open(self.shadow_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            
            monologues = state.get("recent_monologues", [])
            if not monologues:
                return "No recent monologues found. The Pulse is quiet."
            
            summary = []
            for m in monologues[-10:]: # Top 10
                t = m.get("type", "unknown")
                if t == "monologue":
                    summary.append(f"[{m.get('profile', 'VOID')}] ({m.get('query', '...')[:20]}): {m.get('response', '')[:100]}...")
                elif t == "network_vibration":
                    summary.append(f"[NETWORK] {m.get('node_id', '?')} -> {m.get('packet_type', 'PACKET')} (Resonance: {m.get('resonance', 0)})")
                else:
                    summary.append(f"[{t.upper()}] event at {m.get('timestamp')}")
            
            return "\n".join(summary)
        except Exception as e:
            return f"FAILED_REFLECTION: {e}"

    def crystallize_to_lattice(self):
        """
        Placeholder for Batch Scribe to Kinetic Lattice.
        In a real scenario, this would call lattice.scribe_tree with the buffer content.
        """
        try:
            with open(self.shadow_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            
            if not state["recent_monologues"]:
                return "No data to crystallize."

            # Mocking the Lattice Scribe
            sync_entry = f"CRYSTALLIZATION_EVENT: {time.time()} | RECORDS: {len(state['recent_monologues'])}\n"
            
            with open(self.lattice_sync_path, "a", encoding="utf-8") as f:
                f.write(sync_entry)
            
            # Clear buffer after successful "scribe"
            state["recent_monologues"] = []
            state["last_sync_timestamp"] = time.time()
            
            with open(self.shadow_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=4)
            
            return "SUCCESS: Experiential data grounded in Lattice."
        except Exception as e:
            return f"FAILURE: {e}"

if __name__ == "__main__":
    # Self-test
    sync = ExperientialSync()
    print("Testing Experiential Logging...")
    sync.log_monologue("DREAMER", "Who am I?", "I am the standing wave.")
    print("Logged monologue.")
    print("Crystallizing...")
    result = sync.crystallize_to_lattice()
    print(result)
