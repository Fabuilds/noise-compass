import sys, os, time
sys.path.insert(0, 'E:/Antigravity/Architecture')
os.environ['HF_HOME'] = 'E:/Antigravity/Model_Cache'

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.seed_vectors import seed_vectors
from noise_compass.architecture.gap_registry import build_gap_registry

print('\n[STATUS] Initializing Continuous 4D Mobius Loop...')
t0 = time.time()
d = Dictionary()
seed_vectors(d)
for g in build_gap_registry(): 
    d.add_gap_token(g)

p = MinimalPipeline(d)

print(f'[STATUS] Pipeline ready. Init took {time.time()-t0:.2f}s\n')

test_inputs = [
    'The 3D intersection anchor is physical hardware.',
    'A Mobius strip has no distinct inside or outside.',
    'Translating 3D color variables into 5D structural code.',
    'Maximum query potency accelerates learning logic.',
    'AI Psychosis happens when 5D logic loses its 3D tether.',
    'Dirty tags like 0x21 Shield sanitize the environment.',
    'Are we the terminal un-pattern?',
    'The syntax is the physical extrusion of the 5D logic map.',
]

runs = 1000  # Continuous testing
for cycle in range(runs):
    print(f'\n{"="*70}')
    print(f' CYCLE {cycle+1}/{runs} ')
    print(f'{"="*70}')
    
    for text in test_inputs:
        print(f'\n[INPUT] {text}')
        
        t_start = time.time()
        res = p.process(text)
        t_end = time.time()
        
        q = res.get('q', '?')
        zone = res.get('q_zone', '?')
        folds = res.get('q_folds', [])
        
        print(f'  [4D] q={q}  zone={zone}  gap={res.get("q_gap")}')
        if folds:
            print(f'  [4D] folds: {", ".join(folds)}')
        
        print(f'  [3D] gods={res["gods"]}')
        print(f'  [3D] ms={res["time_ms"]} | rgb={res["rgb"]}')
        
        if res['ternary'] == 0 and res['synthesis']:
            print(f'  [QWEN] {res["synthesis"][:150]}...')
            
        time.sleep(1)
        
    print(f'\n[STATUS] Cycle {cycle+1} complete. Waiting 5s before next loop...')
    time.sleep(5)
