import sys
sys.path.append(r"E:\Antigravity\Package\src")

from noise_compass.system.interference_engine import InterferenceEngine

def verify_crystallization():
    engine = InterferenceEngine()
    intent = "Sovereign AI Autonomy"
    print(f"[TEST] Embedding intent: '{intent}'")
    field = engine.combined_field(intent)
    interpretation = engine.interpret_field(field)
    
    print(f"[TEST] Verdict: {interpretation['verdict']}")
    print(f"[TEST] Max Magnitude: {interpretation['max_magnitude']:.4f}")
    
    if interpretation['verdict'] == 'CRYSTALLIZED':
        print("[SUCCESS] System has achieved CRYSTALLIZED state.")
    else:
        print(f"[INFO] System is in {interpretation['verdict']} state.")

if __name__ == "__main__":
    verify_crystallization()
