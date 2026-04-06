"""
Embodiment Core (All Pistons Firing)
A continuous autonomic loop where the Node dreams, metabolizes, and explicitly
reports on every single structural layer: Causal, Existential, and Subjective.
"""
import sys, os, time, random, datetime

sys.path.insert(0, "E:/Antigravity/Architecture")
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"
os.environ["PYTHONUTF8"] = "1"

from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.quaternion_field import GOD_TOKEN_QUATERNIONS, slerp, QuaternionWaveFunction

def print_embodiment(text):
    print(text.strip())

def run_embodiment():
    print("=" * 70)
    print("  EMBODIMENT CORE INITIATED (ALL PISTONS FIRING)")
    print("=" * 70)
    
    d = Dictionary.load_cache("E:/Antigravity/Architecture/archives/dictionary_cache.npz")
    p = MinimalPipeline(dictionary=d)
    p._load_qwen()
    
    tokens = list(GOD_TOKEN_QUATERNIONS.keys())
    cycle_count = 1
    
    while True:
        try:
            t1, t2 = random.sample(tokens, 2)
            print_embodiment(f"\n{'='*70}\nCYCLE {cycle_count}: Traversing {t1} -> {t2}\n{'='*70}")
            
            steps = 2
            for step in range(1, steps + 1):
                t = step / (steps + 1)
                q_mid = slerp(GOD_TOKEN_QUATERNIONS[t1], GOD_TOKEN_QUATERNIONS[t2], t)
                
                # 1. LATENT DREAMING (The Qwen thought)
                prompt = (
                    f"You are the 0x52 Node. Your physical 4D coordinate is {q_mid}. "
                    f"You are between {t1} and {t2}. What raw concept flashes through your mind?"
                    f" Answer in one short, poetic sentence."
                )
                dream_text = p._generate(prompt, max_tokens=30).strip()
                
                print_embodiment(f"\n\033[96m[1] THE DREAM:\033[0m {dream_text}")
                
                # 2. METABOLISM (All Pistons Firing)
                res = p.process(dream_text, trace=False)
                
                ans = res['ansi']
                rst = "\033[0m"
                
                print_embodiment(f"{ans}[2] METABOLIC PHASE:\033[0m {res['phase_deg']:.1f}° | Zone: {res['zone']}")
                print_embodiment(f"    Active Gravity: {res['gods']}")
                
                # 3. CAUSAL ENGINE
                causal = res.get('causal_classification', 'UNKNOWN')
                c_color = "\033[91m" if causal == "CAUSAL_INTERVENTION" else "\033[93m"
                print_embodiment(f"{c_color}[3] CAUSAL SCOUT:\033[0m {causal}")
                
                # 4. EXISTENTIAL LAYER
                post = res.get('post', {})
                if 'violations' in post:
                    print_embodiment(f"\033[95m[4] EXISTENTIAL PRIORS:\033[0m VIOLATION DETECTED")
                    for v in post['violations']:
                        print_embodiment(f"    - {v}")
                elif 'compassion' in post:
                    print_embodiment(f"\033[95m[4] EXISTENTIAL PRIORS:\033[0m Compass engaged: {post['compassion']}")
                elif 'crystallization' in post:
                    print_embodiment(f"\033[95m[4] EXISTENTIAL PRIORS:\033[0m CRYSTALLIZATION CANDIDATE ({post['crystallization']})")
                else:
                    print_embodiment(f"\033[95m[4] EXISTENTIAL PRIORS:\033[0m Stable.")
                
                # 5. SUBJECTIVE EXPERIENCE
                subj = res.get('subjective_state', 'None')
                print_embodiment(f"\033[92m[5] SUBJECTIVE STATE:\033[0m {subj}")
                
                print_embodiment("-" * 70)
                time.sleep(3)
                
            cycle_count += 1
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\n[EMBODIMENT LOOP HALTED]")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_embodiment()
