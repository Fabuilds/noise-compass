"""Quick 10-second listen on both channels."""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from noise_compass.architecture.neural_link import NeuralLink

def on_encounter(peer_id, addr):
    print(f"  [!] SIGNAL: {peer_id} from {addr}")

nl = NeuralLink("GARU-PRIMARY", on_encounter_callback=on_encounter)
nl.start()
print("Listening for 10 seconds...")
time.sleep(10)
s = nl.get_status()
nl.stop()

print(f"\nKnown nodes: {len(s['known_nodes'])}")
print(f"Signal log: {len(s['recent_signals'])}")
for e in s['recent_signals']:
    print(f"  {e['channel']} | {e['peer_id']} @ {e['addr']}")
if not s['recent_signals']:
    print("\nSilence. No signals received on LAN or Internet.")
    print("The lattice is listening, but no one is broadcasting.")
