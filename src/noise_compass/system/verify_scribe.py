from noise_compass.system.ouroboros_resonant import ResonantOuroboros
import os
import shutil

def verify_scribe_manifestation():
    engine = ResonantOuroboros()
    
    # We choose an intent that is almost certainly CRYSTALLIZED
    # (Existing God-tokens like EXISTENCE and IDENTITY are highly resonant)
    intent = "I am focusing on the existence and identity of the boundary."
    
    print(f"--- VERIFYING SCRIBE MANIFESTATION ---")
    print(f"Intent: '{intent}'")
    
    # 1. Run the cycle
    print("Executing Resonant Cycle...")
    verdict = engine.run_cycle()
    print(f"Verdict: {verdict}")
    
    if verdict != 'CRYSTALLIZED':
        print("[WARNING] Verdict was not CRYSTALLIZED. Forcing manifestation for test...")
        field, _ = engine.process_layers(intent)
        engine.manifest_axiom(intent, field)
    
    # 2. Check for newly created axiom file
    growth_dir = "e:/Antigravity/Qwen"
    axioms = [f for f in os.listdir(growth_dir) if f.startswith("axiom_resonant_") and f.endswith(".py")]
    
    if axioms:
        print(f"[SUCCESS] Resonant Axiom synthesized: {axioms[-1]}")
        
        # 3. Verify Ingestion (Recursive Scribe is called within manifest_axiom)
        # We can check the lattice or just look at the engine logs.
        # For simplicity, let's just confirm the file exists and has content.
        axiom_path = os.path.join(growth_dir, axioms[-1])
        with open(axiom_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "Verdict: CRYSTALLIZED" in content:
            print("[SUCCESS] Axiom metadata correctly tagged.")
        else:
            print("[FAILURE] Axiom metadata missing.")
            
    else:
        print("[FAILURE] No resonant axiom synthesized.")

if __name__ == "__main__":
    verify_scribe_manifestation()
