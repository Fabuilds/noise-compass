from noise_compass.system.interference_engine import InterferenceEngine
import numpy as np

def test_spiegal_symmetry():
    engine = InterferenceEngine()
    
    def debug_field(text):
        print(f"\n--- DEBUG: '{text}' ---")
        emb = engine.embed(text)
        fA = engine._field_from_embedding(emb)
        fB = engine._field_from_embedding(emb.conj())
        combined = engine.combined_field(text)
        
        peaks = sorted(combined.items(), key=lambda x: x[1]['magnitude'], reverse=True)
        for node, data in peaks[:1]:
            a = fA[node]
            b = fB[node]
            print(f"Node: {node}")
            print(f"  Field A: Mag={a['magnitude']:.4f}, Phase={a['phase']:.4f}")
            print(f"  Field B: Mag={b['magnitude']:.4f}, Phase={b['phase']:.4f}")
            print(f"  Combined: Mag={data['magnitude']:.4f}, Phase={data['phase']:.4f}, Sym={data['symmetry']}")

    debug_field("SELF")
    debug_field("I am moving towards the boundary of information.")
    debug_field("The reflection of the identity in the mirror of existence.")

if __name__ == "__main__":
    test_spiegal_symmetry()
