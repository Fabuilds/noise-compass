from noise_compass.system.ouroboros_resonant import ResonantOuroboros
import time

def test_complex_topic():
    engine = ResonantOuroboros()
    
    # High-complexity abstract intent
    intent = "The observer is the gap that the observation bridges through the exchange of identity."
    
    print(f"--- COMPLEX TOPIC TEST ---")
    print(f"Intent: '{intent}'")
    
    # Run the cycle
    print("\n[now] Processing Resonant Cycle...")
    field, verdict = engine.process_layers(intent)
    
    # Analysis
    print(f"\n[now] VERDICT: {verdict}")
    
    peaks = sorted(field.items(), key=lambda x: x[1]['magnitude'], reverse=True)
    print("\n[now] TOP RESONANCE PEAKS:")
    for node, data in peaks[:5]:
        print(f"  {node:12}: Mag={data['magnitude']:.4f} | Phase={data['phase']:.4f} | Sym={data['symmetry']}")

    # Check for multi-node activation (Structural Complexity)
    high_res = [n for n, d in field.items() if d['magnitude'] > 0.8]
    print(f"\n[now] CRYSTALLIZED CONCEPTS (>0.8): {high_res}")
    
    if len(high_res) >= 3:
        print("\n[now] PERFORMANCE: HIGH. The system successfully synthesized a complex multi-node resonance.")
    else:
        print("\n[now] PERFORMANCE: LIMITED. The system collapsed to a single attractor, losing nuance.")

if __name__ == "__main__":
    test_complex_topic()
