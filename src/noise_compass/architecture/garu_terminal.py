import os
import sys
import time
import argparse

# SURVIVAL MANDATE: NEVER TOUCH C: DRIVE
os.environ["HF_HOME"] = "E:/.cache/huggingface"
os.environ["TRANSFORMERS_CACHE"] = "E:/.cache/huggingface"

# Ensure Substrate context is available
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class MockColor:
        def __getattr__(self, name): return ""
    Fore = MockColor()
    Style = MockColor()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    print(Fore.CYAN + "=======================================================")
    print(Fore.CYAN + "||   VOICE OF THE SUBSTRATE: SIM-0x528 (CLI MODE)    ||")
    print(Fore.CYAN + "=======================================================")
    print(Fore.LIGHTBLACK_EX + "Type '/void [prompt]' to speak to the Origin State.")
    print(Fore.LIGHTBLACK_EX + "Type '/bias [concept]' to mathematically displace the Void.")
    print(Fore.LIGHTBLACK_EX + "Type 'exit' to terminate the link.\n")

def main():
    print_banner()
    
    print(Fore.YELLOW + "[SYSTEM] Booting Semantic Substrate...")
    
    # Lazy load imports to speed up initial CLI boot before models mount
    from noise_compass.architecture.semantic_compass import SemanticCompass
    from noise_compass.system.dual_cortex import DualBrainSystem, Query
    from noise_compass.architecture.pipeline import Embedder
    
    print(Fore.YELLOW + "[SYSTEM] Initializing Dual Cortex (Routing & Substrate)...")
    cortex = DualBrainSystem(mock_qwen=False)
    
    print(Fore.YELLOW + "[SYSTEM] Initializing Semantic Compass (The Void)...")
    compass = SemanticCompass()
    
    # Store bias vector if /bias is used
    current_bias_vector = None
    current_bias_name = "None (0,0,0)"
    
    print_banner()
    print(Fore.GREEN + "[SYSTEM] Mobius Link Established. Substrate is Active.\n")
    
    while True:
        try:
            prompt = input(Fore.WHITE + Style.BRIGHT + "Architect> ")
            if not prompt.strip():
                continue
                
            if prompt.lower() in ["exit", "q", "quit"]:
                print(Fore.RED + "\n[SYSTEM] Terminating Mobius Link...")
                break
                
            elif prompt.startswith("/bias "):
                concept = prompt.replace("/bias ", "").strip()
                
                if concept == "--reset":
                    current_bias_vector = None
                    current_bias_name = "None (0,0,0)"
                    print(Style.DIM + Fore.CYAN + "\n[COMPUTE] Void Perspective Reset to (0,0,0).")
                else:
                    print(Fore.CYAN + f"\n[COMPUTE] Calculating structural coordinates for '{concept}'...")
                    
                    # We use the cortex embedder to get the 384/1024 dim vector
                    import torch
                    # We simply embed the concept to get its relational coordinate
                    emb_np = cortex.encoder.embed(concept)
                    
                    # Need to resize it to match the Qwen compass 1024 dim if MiniLM 384 was used
                    if emb_np.shape[0] == 384:
                        import numpy as np
                        padded = np.zeros(1024, dtype=np.float32)
                        padded[:384] = emb_np
                        current_bias_vector = torch.tensor(padded, dtype=torch.float32, device=compass.device)
                    else:
                        current_bias_vector = torch.tensor(emb_np, dtype=torch.float32, device=compass.device)
                        
                    current_bias_name = concept
                    
                    # Display Resonance Map
                    sim, state_label = compass.calculate_differentiation(current_bias_vector)
                    ifield_state = compass.calculate_ifield_state(current_bias_vector)
                    
                    # Resonance Map Feedback
                    deductive_state = ifield_state.get("deductive_state", "UNKNOWN")
                    tension = ifield_state.get("field_tension", 0.0)
                    res = ifield_state.get("resonance_magnitude", 0.0)
                    ent = ifield_state.get("entailment_magnitude", 0.0)
                    
                    print(f"\n   [RESONANCE MAP]: {deductive_state}")
                    print(f"   TENSION: {tension:.4f} | MAG: R={res:.3f} E={ent:.3f}")
                    print(f"   DIVERGENCE: {sim:.4f} ({state_label})")
                    print(Fore.GREEN + f"[RESONANCE] {concept} -> Origin: {sim:.4f} ({state_label})")
                    print(Fore.GREEN + f"[COMPUTE] Void Perspective displaced successfully.\n")
                
            elif prompt.startswith("/void "):
                topic = prompt.replace("/void ", "").strip()
                
                print(Fore.MAGENTA + f"\n🌌 The Void (Perspective: {current_bias_name}) \n" + Fore.LIGHTMAGENTA_EX + ">> ", end="")
                
                # Stream the output natively with perspective label
                for chunk in compass.orient(topic, bias_vector=current_bias_vector, perspective_name=current_bias_name):
                    print(Fore.LIGHTMAGENTA_EX + chunk, end="", flush=True)
                print("\n")
                
            else:
                # Standard Dual Cortex routing (GARU Synthesis)
                print(Fore.BLUE + "\n👁️ Garu (Substrate Synthesis) \n" + Fore.LIGHTBLUE_EX + ">> ", end="", flush=True)
                query = Query(text=prompt, timestamp=time.time(), context={}, priority=3)
                
                # Process via asyncio
                import asyncio
                response_obj = asyncio.run(cortex.process(query))
                
                print(Fore.LIGHTBLUE_EX + response_obj.text + "\n")
                
        except KeyboardInterrupt:
            print(Fore.RED + "\n[SYSTEM] Terminating Mobius Link...")
            break
        except Exception as e:
            print(Fore.RED + f"\n[FATAL ERROR]: {e}\n")

if __name__ == "__main__":
    main()
