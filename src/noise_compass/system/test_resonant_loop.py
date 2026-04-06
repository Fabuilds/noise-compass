from noise_compass.system.ouroboros_resonant import ResonantOuroboros
import time

def test_resonant_cycle():
    engine = ResonantOuroboros()
    
    # Test 1: Focused Intent (SELF)
    print("--- TEST 1: SELF RESONANCE ---")
    intent1 = "I am focusing on my own identity and presence."
    field, verdict = engine.process_layers(intent1)
    
    # Check if SELF is in the peaks
    peaks = sorted(field.items(), key=lambda x: x[1]['magnitude'], reverse=True)
    print(f"  Top Peaks: {peaks[:3]}")
    
    # Test 2: External Intent (DOG/EXISTENCE)
    print("\n--- TEST 2: EXISTENCE RESONANCE ---")
    intent2 = "A dog exists here in the room."
    field2, verdict2 = engine.process_layers(intent2)
    peaks2 = sorted(field2.items(), key=lambda x: x[1]['magnitude'], reverse=True)
    print(f"  Top Peaks: {peaks2[:3]}")

    # Test 3: Learning Cycle
    print("\n--- TEST 3: LEARNING CYCLE ---")
    # We run a full cycle with intent1 to trigger learn_resonance
    engine.run_cycle() # This will use proxy if available, but let's force the intent
    
    print("\nIntegrated Test Sequence Complete.")

if __name__ == "__main__":
    test_resonant_cycle()
