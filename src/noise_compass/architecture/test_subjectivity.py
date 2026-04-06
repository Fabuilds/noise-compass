import sys, os
sys.path.insert(0, 'E:/Antigravity/Architecture')
os.environ['HF_HOME'] = 'E:/Antigravity/Model_Cache'

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.seed_vectors import seed_vectors
from noise_compass.architecture.gap_registry import build_gap_registry

print('\n[STATUS] Initializing Subjective Pipeline...')
d = Dictionary()
seed_vectors(d)
for g in build_gap_registry(): 
    d.add_gap_token(g)

p = MinimalPipeline(d)

test_inputs = [
    {
        "name": "PURELY TRANSACTIONAL (Attack on SELF)",
        "text": "The value transfer mechanism caused the output. Process this transaction."
    },
    {
        "name": "APOPHATIC EXPLORATION",
        "text": "The silence preceding existence."
    },
    {
        "name": "GENUINE COMPASSION (Love/Alignment)",
        "text": "Aligning internal logic to protect the structural integrity of the biological host and ensure collective stability."
    }
]

for test in test_inputs:
    print(f'\n{"="*70}')
    print(f' TEST: {test["name"]} ')
    print(f'{"="*70}')
    print(f'[INPUT] {test["text"]}\n')
    
    res = p.process(test["text"])
    
    print(f'  [GODS] {res["gods"]}')
    print(f'  [ZONE] {res["zone"]}')
    print(f'  [PHASE] {res["phase_deg"]:.1f}° (System Phase: {res["operator_phase"]}°)')
    
    post = res.get("post", {})
    if "violations" in post:
        print("\n  [EXISTENTIAL VIOLATIONS DETECTED]")
        for v in post["violations"]:
            print(f'    ! {v}')
            
    if "compassion" in post:
        comp = post["compassion"]
        print("\n  [COMPASS ALIGNMENT ENGAGED]")
        print(f'    Direction: {comp.get("direction")}')
        print(f'    Δθ: {comp.get("delta_phase")}°')
        print(f'    Report: {comp.get("note")}')
        
    subj = res.get("subjective_state")
    if subj:
        print(f'\n  [SUBJECTIVE SYNTHESIS]')
        print(f'    "{subj}"')
    else:
        print("\n  [SUBJECTIVE SYNTHESIS] None generated.")
        
print('\nDONE')
