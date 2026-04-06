import sys, os
sys.path.insert(0, 'E:/Antigravity/Architecture')
os.environ['HF_HOME'] = 'E:/Antigravity/Model_Cache'

print("1. Imports")
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.seed_vectors import seed_vectors
from noise_compass.architecture.gap_registry import build_gap_registry

print("2. Building dictionary")
d = Dictionary()

print("3. Seeding vectors")
seed_vectors(d)

print("4. Building gap registry")
for g in build_gap_registry():
    d.add_gap_token(g)

print("5. Init pipeline")
p = MinimalPipeline(d)

print("6. Bypassing Qwen")
p._load_qwen = lambda: False

print("7. Running process")
r = p.process("the silence of the pure observer")
print(r)
print("DONE")
