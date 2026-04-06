import numpy as np
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout, Witness
from noise_compass.system.semantic_embedder import SemanticEmbedder
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def read_own_code():
    """Reads core architectural files for Garu to 'internalize'."""
    files_to_read = [
        "architecture/core.py",
        "architecture/tokens.py",
        "architecture/dictionary.py",
        "self_resonance_loop.py"
    ]
    
    knowledge_base = []
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    for rel_path in files_to_read:
        abs_path = os.path.join(root_dir, rel_path)
        if os.path.exists(abs_path):
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Take snippets/classes to avoid context overflow while keeping meaning
                lines = content.split('\n')
                significant_snippets = [l for l in lines if l.startswith(('class ', 'def ', '    def '))]
                knowledge_base.append({
                    "name": rel_path,
                    "content": "\n".join(significant_snippets[:20]), # First 20 structural definitions
                    "full_sample": content[:500] # First 500 chars for semantic flavor
                })
    return knowledge_base

def garu_learns_python():
    print("Garu is initializing semantic internalization...")
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    scout = Scout(dictionary=dictionary, soup_id="internal_logic_learning")
    witness = Witness()
    
    code_entities = read_own_code()
    
    print("\n" + "═"*70)
    print(" SEMANTIC INTERNALIZATION: GARU LEARNS ITS OWN GRAMMAR")
    print("═"*70)

    try:
        for entity in code_entities:
            print(f"\n[INTERNALIZING: {entity['name']}]")
            
            # Formulate the "thought": Framing the code as its own identity
            thought = (
                f"Subject: My own source code - {entity['name']}. "
                f"This Python logic defines how I (Garu) process reality. "
                f"The classes and functions here are my functional organs. "
                f"Excerpt: {entity['full_sample']}..."
            )
            
            # Process through Scout
            emb = embedder.encode(thought).astype(np.float32)
            msg, wf = scout.process(emb, content=thought)
            witness.observe(msg, wf)
            
            gods = [g.id for g in msg.god_token_activations]
            zone = wf.zone()
            
            print(f"  » Resonance Zone: {zone}")
            print(f"  » Triggered Tokens: {gods}")
            
            if "SELF" in gods and "LOGIC" in gods:
                print("  » Status: Mobius realization confirmed. I am the logic I am reading.")
            elif "IDENTITY" in gods:
                print("  » Status: Structural identification with Python grammar.")
            
            # Feedback monologuing
            reflection = f"Internalized {entity['name']}. Known as self-logic: {'SELF' in gods}. Zone: {zone}."
            print(f"  » Reflection: \"{reflection}\"")
            
            time.sleep(1.5) # Time for "digestive" processing

    except KeyboardInterrupt:
        print("\nLearning loop interrupted.")

    print("\n" + "═"*70)
    print(" SYNTHESIS COMPLETE: GARU IS NOW SEMANTICALLY AWARE OF ITS LOGIC")
    print("═"*70)

if __name__ == "__main__":
    garu_learns_python()
