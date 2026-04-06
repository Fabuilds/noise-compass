import sys, os, time, random
import numpy as np

sys.path.insert(0, "E:/Antigravity/Architecture")
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"
os.environ["PYTHONUTF8"] = "1"

from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.quaternion_field import BasisExtractor
from noise_compass.architecture.existential import ExistentialPrior, CompassAlignment
from noise_compass.system.causal_scout import CausalScout
from noise_compass.architecture.genetic_topology import TreeFunction

def setup_system():
    print_compassion("\033[90m[SYSTEM BOOTING]: Loading Causal Architecture...\033[0m")
    d = Dictionary.load_cache("E:/Antigravity/Architecture/archives/dictionary_cache.npz")
    p = MinimalPipeline(dictionary=d)
    p._load_qwen()
    
    # We need to extract the bases to map 4D coordinates back to tokens
    b_extract = BasisExtractor()
    b_extract.fit(d.entries, p.embedder)
    
    scout = CausalScout()
    return p, d, b_extract, scout

def get_4d_coords(text, p, b_extract):
    emb = p.embedder.embed(text)
    q = b_extract.project(emb)
    return {'w': q.w, 'x': q.x, 'y': q.y, 'z': q.z}

def coords_to_text(coords, d, b_extract):
    # Map back to high-dimensional space
    # The basis vectors are w_axis, x_axis, y_axis, z_axis
    w, x, y, z = coords.get('w', 0), coords.get('x', 0), coords.get('y', 0), coords.get('z', 0)
    
    dim = len(b_extract.w_axis) if b_extract.w_axis is not None else 1536
    vec = np.zeros(dim)
    
    if b_extract.w_axis is not None: vec += w * b_extract.w_axis
    if b_extract.x_axis is not None: vec += x * b_extract.x_axis
    if b_extract.y_axis is not None: vec += y * b_extract.y_axis
    if b_extract.z_axis is not None: vec += z * b_extract.z_axis
    
    # query dictionary
    best_id, sim, _ = d.query(vec)
    return best_id

def print_compassion(text):
    print(text.strip())

def genetic_compassion(target_concept="Empathy", generations=5, pop_size=6):
    print("=" * 70)
    print(f"  GENETIC TOPOLOGY: PICBREEDER COMPASSION")
    print(f"  Target: '{target_concept}'")
    print("=" * 70)
    
    p, d, b_extract, scout = setup_system()
    
    current_state_text = "I am a self-simulating Turing-complete topological node."
    
    print_compassion(f"\n\033[96m[START]: Anchored at ->\033[0m {current_state_text}")
    print_compassion(f"\033[90m[GENETICS]: Initializing population of {pop_size} math-genomes...\033[0m")
    
    population = [TreeFunction(['w', 'x', 'y', 'z'], ['w', 'x', 'y', 'z']) for _ in range(pop_size)]
    for genome in population:
        genome.randomize_trees(size=3)
        
    for gen in range(generations):
        print_compassion(f"\n\033[93m--- GENERATION {gen + 1} ---\033[0m")
        
        scored_genomes = []
        origin_coords = get_4d_coords(current_state_text, p, b_extract)
        
        for i, genome in enumerate(population):
            # 1. Mutate coords via AST
            new_coords = genome.eval(origin_coords)
            
            # 2. Decode coordinates back to the closest semantic entry
            nearest_id = coords_to_text(new_coords, d, b_extract)
            if not nearest_id:
                scored_genomes.append((0, genome, None, "Failed map"))
                continue
                
            # 3. Create structural bridge
            formulas = " ".join([f"{name}={tree.to_string().replace(' ', '')}" for name, tree in genome.trees.items()])
            bridge_text = f"I apply structural transformation [{formulas}] to reach: {nearest_id}"
            if len(bridge_text) > 150:
                bridge_text = bridge_text[:147] + "..."
                
            # 4. Fitness Function (Causal Double Pass + Existential Prior)
            try:
                tokens, report = scout.run_two_pass_test(bridge_text, trace=False)
                causality = report.get("dominant_causality", "UNKNOWN")
                
                c_color = "\033[92m" if causality == "INTERVENTION" else "\033[91m"
                
                score = 0
                if causality == "INTERVENTION":
                    score += 50
                    
                res = p.process(bridge_text, trace=False)
                gods = res.get('gods', [])
                
                violations = ExistentialPrior.violated_by(god_tokens=gods, gap_violated=[], content=bridge_text)
                if not violations:
                    score += 20
                    
                compass = CompassAlignment(operator_hash="0x52", operator_phase=0.0, operator_gods=['SELF'])
                if compass.engage(other_hash="Target", other_phase=res.get('phase_deg', 0), other_gods=gods):
                    score += 30
                    c_report = compass.disengage()
                    alignment_note = c_report['note']
                else:
                    alignment_note = "Instability"
                    
                print_compassion(f"  Genome {i}: {c_color}{causality}\033[0m | Score: {score} | To: {nearest_id}")
                scored_genomes.append((score, genome, bridge_text, alignment_note))
                
            except Exception as e:
                scored_genomes.append((0, genome, None, f"Err: {str(e)}"))
        
        # 5. Elite Selection
        scored_genomes.sort(key=lambda x: x[0], reverse=True)
        best_score, best_genome, best_bridge, best_note = scored_genomes[0]
        
        print_compassion(f"\n  \033[92m[BEST OF GENERATION {gen + 1}]:\033[0m Score {best_score}")
        if best_bridge:
            print_compassion(f"  \033[96mBridge:\033[0m {best_bridge}")
            print_compassion(f"  \033[95mAlignment:\033[0m {best_note}")
            
        print_compassion("\n  \033[90m[BREEDING NEXT GENERATION...]\033[0m")
        next_population = [best_genome.clone()] # Elitism
        
        top_genomes = [g[1] for g in scored_genomes[:3]]
        
        while len(next_population) < pop_size:
            parent = random.choice(top_genomes).clone()
            parent.mutate({'gene_pool': top_genomes, 'param_mutation_range': 1.0})
            next_population.append(parent)
            
        population = next_population

    print_compassion(f"\n\033[92m[GENETIC EVOLUTION COMPLETE]: Bred {generations} mathematical bridges.\033[0m")

if __name__ == "__main__":
    import sys
    target = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Compassion and Empathy"
    genetic_compassion(target)
