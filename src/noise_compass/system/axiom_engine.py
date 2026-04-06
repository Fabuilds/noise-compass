import os
import glob
import importlib.util
import traceback

class AxiomEngine:
    """
    Parses and dynamically runs Python scripts accreted by the intelligence.
    These are mathematical formulas that permanently modify the Interference Field,
    acting as the AI's immutable laws.
    """
    def __init__(self, directory="E:/Antigravity/Qwen/processed"):
        self.directory = directory
        self.active_axioms = []
        self.prompt_directives = []
        self.load_axioms()

    def load_axioms(self):
        self.active_axioms = []
        self.prompt_directives = []
        
        try:
            from noise_compass.system.h5_manager import H5Manager
            manager = H5Manager()
            axioms = manager.get_active_axioms()
            
            for axiom_id, data in axioms.items():
                source = data['source']
                try:
                    # Dynamically execute source string
                    # We create a new module object to keep namespaces clean
                    module_name = f"h5_axiom_{axiom_id}"
                    spec = importlib.util.spec_from_loader(module_name, loader=None)
                    module = importlib.util.module_from_spec(spec)
                    
                    # Execute source in the module's namespace
                    exec(source, module.__dict__)
                    
                    # Dynamic hook 1: Execute field math
                    if hasattr(module, "apply_axiom"):
                        self.active_axioms.append(module.apply_axiom)
                    
                    # Dynamic hook 2: Evolve textual prompts
                    if hasattr(module, "get_prompt_directive"):
                        directive = module.get_prompt_directive()
                        if directive:
                            self.prompt_directives.append(directive)
                            
                except Exception as e:
                    print(f"[AXIOM_ENGINE] Error executing H5 axiom {axiom_id}: {e}")
            print(f"[AXIOM_ENGINE] Successfully streamed {len(self.active_axioms)} recursive laws from H5 substrate.")
                    
        except Exception as e:
            print(f"[AXIOM_ENGINE] CRITICAL: Failed to stream H5 axioms: {e}")
            # Fallback to legacy filesystem if needed (optional)

    def process_field(self, field):
        """Pipes the interference field through all active axioms."""
        for axiom in self.active_axioms:
            try:
                field = axiom(field)
            except Exception as e:
                print(f"[AXIOM_ENGINE] Error applying axiom: {e}")
        return field
        
    def get_evolution_prompt(self):
        """Returns the concatenated directives for prompt formulation."""
        if not self.prompt_directives:
            return ""
        
        prompt = "\n=== EVOLVED AXIOMATIC LAWS ===\nYou must perfectly obey the following synthesized mathematical rules:\n"
        for idx, d in enumerate(self.prompt_directives):
            prompt += f"{idx+1}. {d}\n"
        prompt += "==============================\n"
        return prompt
