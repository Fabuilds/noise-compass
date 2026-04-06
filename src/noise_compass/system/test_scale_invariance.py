from noise_compass.system.interference_engine import InterferenceEngine
import numpy as np

def compare_scales():
    engine = InterferenceEngine()
    
    word = "DOG"
    sentence = "A DOG IS HERE"
    
    print(f"--- SCALE COMPARISON ---")
    print(f"Word: '{word}'")
    print(f"Sentence: '{sentence}'")
    
    field_word = engine.combined_field(word)
    field_sent = engine.combined_field(sentence)
    
    def print_field(name, field):
        print(f"\n{name} Resonance Profile:")
        sorted_field = sorted(field.items(), key=lambda x: x[1]['magnitude'], reverse=True)
        for node, data in sorted_field:
            if data['magnitude'] > 0.5: # Filter noise
                print(f"  {node:12}: {data['magnitude']:.4f} (Phase: {data['phase']:.2f})")

    print_field("WORD", field_word)
    print_field("SENTENCE", field_sent)

    # Intersection analysis
    set_word = set(n for n, d in field_word.items() if d['magnitude'] > 0.8)
    set_sent = set(n for n, d in field_sent.items() if d['magnitude'] > 0.8)
    
    overlap = set_word.intersection(set_sent)
    print(f"\nCORE RESONANCE OVERLAP (>0.8): {overlap}")
    
    if "EXISTENCE" in overlap and "IDENTITY" in set_word:
        print("\nCONCLUSION: Yes, it is understandable. The word 'DOG' provides the core identity, and the sentence 'A DOG IS HERE' projects that identity into Existence and Place without losing the resonant anchor.")
    else:
        print("\nCONCLUSION: The mapping is complex; additional contextual layers are shifting the primary resonance.")

if __name__ == "__main__":
    compare_scales()
