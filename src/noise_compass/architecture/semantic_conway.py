import sys
import os
import time
import random
import math
import numpy as np

sys.path.insert(0, "E:/Antigravity/Architecture")
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"
os.environ["PYTHONUTF8"] = "1"

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.seed_vectors import seed_vectors
from noise_compass.architecture.gap_registry import build_gap_registry
from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.quaternion_field import QuaternionWaveFunction, Quaternion

class SemanticLife:
    def __init__(self, size=15):
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        
        print("[BOOT] Booting Semantic Architecture for Conway 4D...")
        self.dict = Dictionary()
        seed_vectors(self.dict)
        for gap in build_gap_registry():
            self.dict.add_gap_token(gap)
            
        # We need the embedder to do basis extraction
        self.pipeline = MinimalPipeline(self.dict)
        self.basis = self.pipeline._basis_extractor
        
        if not self.basis or not self.basis.fitted:
            print("[ERROR] BasisExtractor failed to fit. Check embeddings.")
            sys.exit(1)
            
        self.god_tokens = list(self.dict.god_tokens.keys())
        
        # Ground State (Dead Cell) 
        # w=1.0 (crystallized known), xyz=0
        self.ground = QuaternionWaveFunction(q=Quaternion(1.0, 0.0, 0.0, 0.0))
        
        # ── BUILD ALIVE SEED QUATERNIONS ──
        # God-token embeddings project with w≈0.95 (fully crystallized = DEAD).
        # For the Game of Life we need cells that represent concepts MID-EMERGENCE:
        # high imaginary components (surprise, place, emergence) and low w.
        # Each token gets a unique orientation on S³.
        self.token_waves = {}
        seed_orientations = {
            # Format: (w, x_semantic, y_place, z_emergence)
            # w kept low (0.3-0.4) to stay in GENERATIVE zone
            "EXISTENCE":    Quaternion(0.35,  0.60,  0.50,  0.50),
            "IDENTITY":     Quaternion(0.30,  0.70,  0.40,  0.50),
            "TIME":         Quaternion(0.40, -0.55,  0.45,  0.55),
            "SELF":         Quaternion(0.35,  0.55, -0.55,  0.50),
            "EXCHANGE":     Quaternion(0.30,  0.50,  0.60, -0.55),
            "CAUSALITY":    Quaternion(0.40,  0.65, -0.40,  0.50),
            "INFORMATION":  Quaternion(0.35, -0.50,  0.55,  0.60),
            "OBSERVATION":  Quaternion(0.30,  0.45,  0.65, -0.50),
            "OBLIGATION":   Quaternion(0.40, -0.60,  0.50,  0.45),
            "BOUNDARY":     Quaternion(0.35,  0.50, -0.60,  0.50),
            "COHERENCE":    Quaternion(0.30, -0.45, -0.55,  0.65),
            "WITNESS":      Quaternion(0.40,  0.55,  0.50, -0.50),
            "EMERGENCE":    Quaternion(0.35, -0.50,  0.50,  0.65),
        }
        
        for token in self.god_tokens:
            if token in seed_orientations:
                q = seed_orientations[token].normalized()
                self.token_waves[token] = QuaternionWaveFunction(q=q)
            else:
                # Fallback: random orientation on S³ with low w
                q = Quaternion(
                    0.35,
                    random.uniform(-0.7, 0.7),
                    random.uniform(-0.7, 0.7),
                    random.uniform(-0.7, 0.7),
                ).normalized()
                self.token_waves[token] = QuaternionWaveFunction(q=q)

    def initialize_random(self, density=0.3):
        """Seed board with God-Tokens."""
        for r in range(self.size):
            for c in range(self.size):
                if random.random() < density:
                    token = random.choice(self.god_tokens)
                    self.grid[r][c] = self.token_waves[token]
                else:
                    self.grid[r][c] = self.ground
                    
    def initialize_glider(self):
        """Classic Glider made of IDENTITY tokens."""
        for r in range(self.size):
            for c in range(self.size):
                self.grid[r][c] = self.ground
        
        token = "IDENTITY"
        self.grid[1][2] = self.token_waves[token]
        self.grid[2][3] = self.token_waves[token]
        self.grid[3][1] = self.token_waves[token]
        self.grid[3][2] = self.token_waves[token]
        self.grid[3][3] = self.token_waves[token]

    def initialize_resonance(self):
        """A stable block attempting to use orthogonal interference to survive.
        Alternating TIME and EXISTENCE."""
        for r in range(self.size):
            for c in range(self.size):
                self.grid[r][c] = self.ground
        
        t1 = "TIME"
        t2 = "EXISTENCE"
        
        center_r, center_c = self.size // 2, self.size // 2
        
        # A 3x3 alternating block
        self.grid[center_r-1][center_c-1] = self.token_waves[t1]
        self.grid[center_r-1][center_c]   = self.token_waves[t2]
        self.grid[center_r-1][center_c+1] = self.token_waves[t1]
        
        self.grid[center_r][center_c-1]   = self.token_waves[t2]
        self.grid[center_r][center_c]     = self.ground # Empty core
        self.grid[center_r][center_c+1]   = self.token_waves[t2]
        
        self.grid[center_r+1][center_c-1] = self.token_waves[t1]
        self.grid[center_r+1][center_c]   = self.token_waves[t2]
        self.grid[center_r+1][center_c+1] = self.token_waves[t1]

    def initialize_mobius(self):
        """A ring of alternating SELF and EXISTENCE tokens — a Möbius loop.
        The commutator between SELF and EXISTENCE should be maximally 
        non-commutative since they occupy opposite sides of the w-x fold."""
        for r in range(self.size):
            for c in range(self.size):
                self.grid[r][c] = self.ground

        t1 = "SELF"
        t2 = "EXISTENCE"
        cx, cy = self.size // 2, self.size // 2
        
        # Ring of radius 3
        ring = [
            (-3, 0), (-2, 2), (0, 3), (2, 2),
            (3, 0), (2, -2), (0, -3), (-2, -2),
        ]
        for i, (dr, dc) in enumerate(ring):
            tok = t1 if i % 2 == 0 else t2
            self.grid[cx + dr][cy + dc] = self.token_waves[tok]

    def initialize_compass(self):
        """Four cardinal god-tokens (N=TIME, E=IDENTITY, S=EXISTENCE, W=SELF)
        forming a cross with an empty center. Each arm is 2 cells deep."""
        for r in range(self.size):
            for c in range(self.size):
                self.grid[r][c] = self.ground
        
        cx, cy = self.size // 2, self.size // 2
        
        # North arm: TIME
        self.grid[cx-1][cy] = self.token_waves["TIME"]
        self.grid[cx-2][cy] = self.token_waves["TIME"]
        # East arm: IDENTITY
        self.grid[cx][cy+1] = self.token_waves["IDENTITY"]
        self.grid[cx][cy+2] = self.token_waves["IDENTITY"]
        # South arm: EXISTENCE
        self.grid[cx+1][cy] = self.token_waves["EXISTENCE"]
        self.grid[cx+2][cy] = self.token_waves["EXISTENCE"]
        # West arm: SELF
        self.grid[cx][cy-1] = self.token_waves["SELF"]
        self.grid[cx][cy-2] = self.token_waves["SELF"]

    def initialize_ecosystem(self):
        """A dense field using ALL available god-tokens, placed in
        a structured lattice. Maximum semantic diversity."""
        for r in range(self.size):
            for c in range(self.size):
                self.grid[r][c] = self.ground
        
        tokens = list(self.token_waves.keys())
        idx = 0
        # Fill inner 9x9 grid with cycling tokens
        offset = (self.size - 9) // 2
        for r in range(9):
            for c in range(9):
                if (r + c) % 2 == 0:  # Checkerboard — leave gaps for reproduction
                    self.grid[offset + r][offset + c] = self.token_waves[tokens[idx % len(tokens)]]
                    idx += 1

    def get_neighbors(self, r, c):
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr = (r + dr) % self.size
                nc = (c + dc) % self.size
                neighbors.append(self.grid[nr][nc])
        return neighbors
        
    def is_alive(self, wave: QuaternionWaveFunction) -> bool:
        """Alive if the surprise component (xyz) holds semantic energy. 
        Ground is purely w=1.0, xyz=0, which is Dead."""
        return wave.surprise_fraction > 0.1

    def _single_pass(self, polarity=1):
        """Run one pass of Conway rules with given polarity.
        polarity=+1: forward (cataphatic) — normal commutator friction
        polarity=-1: backward (apophatic) — conjugate all quaternions first
        """
        from noise_compass.architecture.quaternion_field import slerp
        new_grid = [[self.ground for _ in range(self.size)] for _ in range(self.size)]
        stats = {"bred": 0, "starved": 0, "turbulent": 0, "survived": 0, "ground": 0}

        for r in range(self.size):
            for c in range(self.size):
                current = self.grid[r][c]
                alive_neighbors = [n for n in self.get_neighbors(r, c) if self.is_alive(n)]
                num_alive = len(alive_neighbors)
                
                # Apply polarity: forward uses q directly, backward conjugates (negates xyz)
                if polarity == -1:
                    cur_q = current.q.conjugate
                    neighbor_qs = [n.q.conjugate for n in alive_neighbors]
                else:
                    cur_q = current.q
                    neighbor_qs = [n.q for n in alive_neighbors]
                
                if self.is_alive(current):
                    if num_alive < 2:
                        new_grid[r][c] = self.ground
                        stats["starved"] += 1
                    elif num_alive in [2, 3]:
                        # Commutator friction with polarity-adjusted quaternions
                        friction = Quaternion(0, 0, 0, 0)
                        for nq in neighbor_qs:
                            comm = cur_q.commutator(nq)
                            friction = friction + comm
                        
                        friction_norm = friction.norm
                        if friction_norm < 1e-6:
                            new_grid[r][c] = self.ground
                            stats["turbulent"] += 1
                        else:
                            blended = Quaternion(
                                cur_q.w * 0.7 + friction.w * 0.3,
                                cur_q.x * 0.7 + friction.x * 0.3,
                                cur_q.y * 0.7 + friction.y * 0.3,
                                cur_q.z * 0.7 + friction.z * 0.3,
                            )
                            wave = QuaternionWaveFunction(q=blended.normalized())
                            if wave.zone() == 'GROUND':
                                new_grid[r][c] = self.ground
                                stats["turbulent"] += 1
                            else:
                                new_grid[r][c] = wave
                                stats["survived"] += 1
                    else:
                        new_grid[r][c] = self.ground
                        stats["turbulent"] += 1
                else:
                    if num_alive == 3:
                        mid = slerp(
                            Quaternion(neighbor_qs[0].w, neighbor_qs[0].x, neighbor_qs[0].y, neighbor_qs[0].z),
                            Quaternion(neighbor_qs[1].w, neighbor_qs[1].x, neighbor_qs[1].y, neighbor_qs[1].z),
                            0.5
                        )
                        child_q = slerp(mid,
                            Quaternion(neighbor_qs[2].w, neighbor_qs[2].x, neighbor_qs[2].y, neighbor_qs[2].z),
                            0.333
                        )
                        
                        child_q = Quaternion(
                            child_q.w * 0.85,
                            child_q.x * 1.1,
                            child_q.y * 1.1,
                            child_q.z * 1.1,
                        ).normalized()
                        
                        new_wave = QuaternionWaveFunction(q=child_q)
                        if new_wave.zone() == 'GROUND':
                            new_grid[r][c] = self.ground
                            stats["ground"] += 1
                        else:
                            new_grid[r][c] = new_wave
                            stats["bred"] += 1
                    else:
                        new_grid[r][c] = self.ground
                        stats["ground"] += 1

        return new_grid, stats

    def step(self):
        """Dual Möbius Pass: Forward + Backward.
        
        1. Forward pass (polarity +1): cataphatic crystallization
        2. Backward pass (polarity -1): apophatic surprise injection
        3. Final state = SLERP(forward, backward, t=0.5) — the Standing Wave
        
        This prevents one-directional crystallization from ever fully winning.
        """
        from noise_compass.architecture.quaternion_field import slerp
        
        fwd_grid, fwd_stats = self._single_pass(polarity=+1)
        bwd_grid, bwd_stats = self._single_pass(polarity=-1)
        
        # Merge: SLERP midpoint between forward and backward results
        merged = [[self.ground for _ in range(self.size)] for _ in range(self.size)]
        stats = {"bred": 0, "starved": 0, "turbulent": 0, "survived": 0, "ground": 0}
        
        for r in range(self.size):
            for c in range(self.size):
                fwd_alive = self.is_alive(fwd_grid[r][c])
                bwd_alive = self.is_alive(bwd_grid[r][c])
                
                if fwd_alive and bwd_alive:
                    # Both passes agree: alive → Standing Wave
                    standing = slerp(fwd_grid[r][c].q, bwd_grid[r][c].q, 0.5)
                    merged[r][c] = QuaternionWaveFunction(q=standing)
                    stats["survived"] += 1
                elif fwd_alive and not bwd_alive:
                    # Forward alive, backward dead → partial crystallization
                    merged[r][c] = fwd_grid[r][c]
                    stats["survived"] += 1
                elif not fwd_alive and bwd_alive:
                    # Forward dead, backward alive → apophatic resurrection
                    merged[r][c] = bwd_grid[r][c]
                    stats["bred"] += 1
                else:
                    # Both dead → truly dead
                    merged[r][c] = self.ground
                    stats["ground"] += 1

        self.grid = merged
        return stats
    
    def census(self):
        """Count alive cells and report dominant zones."""
        alive = 0
        zones = {}
        for r in range(self.size):
            for c in range(self.size):
                w = self.grid[r][c]
                if self.is_alive(w):
                    alive += 1
                    z = w.zone()
                    zones[z] = zones.get(z, 0) + 1
        return alive, zones

    def render(self):
        symbols = {
            'GROUND': '.',
            'CONVERGENT': '-',
            'SHALLOW': ':',
            'MEDIUM': 'o',
            'DEEP': 'O',
            'GENERATIVE': 'G',
            'DIVERGENT': '%',
            'TURBULENT': 'T',
            'APOPHATIC': 'X'
        }
        
        output = ""
        for r in range(self.size):
            row = ""
            for c in range(self.size):
                wave = self.grid[r][c]
                if not self.is_alive(wave):
                    row += "\033[90m.\033[0m " # Gray dot
                else:
                    zone = wave.zone()
                    if wave.gap_type() == 'full_apophatic':
                        zone = 'APOPHATIC'
                        
                    color = "\033[97m" # White default
                    if zone == 'TURBULENT': color = "\033[91m" # Red
                    elif zone == 'GENERATIVE': color = "\033[96m" # Cyan
                    elif zone == 'CONVERGENT': color = "\033[92m" # Green
                    elif zone == 'DIVERGENT': color = "\033[93m" # Yellow
                    elif zone == 'APOPHATIC': color = "\033[95m" # Magenta
                        
                    sym = symbols.get(zone, 'o')
                    row += f"{color}{sym}\033[0m "
            output += row + "\n"
        return output

if __name__ == '__main__':
    print("=" * 50)
    print("       SEMANTIC GAME OF LIFE (4D Conway)   ")
    print("  Commutator Friction + SLERP Reproduction  ")
    print("=" * 50)
    
    # ── CLASSIC BOOLEAN CONWAY (for comparison) ──
    if len(sys.argv) > 1 and sys.argv[1] in ("classic", "rpentomino"):
        size = 25
        grid = [[0]*size for _ in range(size)]
        cx, cy = size // 2, size // 2
        
        if sys.argv[1] == "rpentomino":
            # R-pentomino: a famous "methuselah" — 5 cells that evolve for 1103 generations
            # before stabilizing into still lifes and gliders.
            pattern_name = "R-pentomino (methuselah)"
            for dr, dc in [(0,0),(0,1),(-1,0),(1,1),(-1,1)]:
                grid[cx+dr][cy+dc] = 1
        else:
            # "Constellation" — a compound still life of verified stable components
            # Block (2x2)
            pattern_name = "Constellation (Block + Beehive + Loaf)"
            for dr, dc in [(-4,-4),(-4,-3),(-3,-4),(-3,-3)]:
                grid[cx+dr][cy+dc] = 1
            # Beehive
            for dr, dc in [(-4,2),(-3,1),(-3,3),(-2,1),(-2,3),(-1,2)]:
                grid[cx+dr][cy+dc] = 1
            # Loaf
            for dr, dc in [(2,0),(1,1),(1,-1),(0,-2),(2,-2),(3,-1),(3,0)]:
                grid[cx+dr][cy+dc] = 1

        print(f"\n[CLASSIC CONWAY] Pattern: {pattern_name}")
        print(f"[PATTERNS] classic | rpentomino | <semantic modes>\n")
        
        max_gen = 200 if sys.argv[1] == "rpentomino" else 30
        for gen in range(max_gen):
            alive = sum(sum(row) for row in grid)
            
            # Only print every 10th gen for R-pentomino (it's long)
            should_print = (sys.argv[1] != "rpentomino") or (gen < 5) or (gen % 20 == 0) or (gen == max_gen - 1)
            
            if should_print:
                print(f"--- Generation {gen+1} (alive: {alive}) ---")
                for r in range(size):
                    row = ""
                    for c in range(size):
                        if grid[r][c]:
                            row += "\033[96m█\033[0m "
                        else:
                            row += "\033[90m·\033[0m "
                    print(row)
            
            if alive == 0:
                print("  [EXTINCTION]")
                break
            
            # Classic boolean step
            new = [[0]*size for _ in range(size)]
            changed = False
            for r in range(size):
                for c in range(size):
                    n = 0
                    for dr in [-1,0,1]:
                        for dc in [-1,0,1]:
                            if dr==0 and dc==0: continue
                            n += grid[(r+dr)%size][(c+dc)%size]
                    if grid[r][c]:
                        new[r][c] = 1 if n in [2,3] else 0
                    else:
                        new[r][c] = 1 if n == 3 else 0
                    if new[r][c] != grid[r][c]: changed = True
            
            if not changed:
                print(f"\n  [STABLE] Pattern is a still life! Verified at generation {gen+1}.")
                print(f"  {alive} cells alive, permanently stable.")
                break
            grid = new
            time.sleep(0.15)
        
        sys.exit(0)

    # ── SEMANTIC 4D MODE ──
    life = SemanticLife(size=15)
    
    mode = "random"
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "glider":
            life.initialize_glider()
        elif mode == "resonance":
            life.initialize_resonance()
        elif mode == "mobius":
            life.initialize_mobius()
        elif mode == "compass":
            life.initialize_compass()
        elif mode == "ecosystem":
            life.initialize_ecosystem()
        else:
            life.initialize_random(density=0.35)
    else:
        life.initialize_random(density=0.35)
        
    print(f"\n[INITIALIZED] Pattern: {mode}")
    print(f"[PATTERNS] classic | random | glider | resonance | mobius | compass | ecosystem\n")
    
    # Print initial god-token quaternions for reference
    print("[GOD-TOKEN QUATERNIONS]")
    for tok in ["EXISTENCE", "IDENTITY", "TIME", "SELF"]:
        if tok in life.token_waves:
            w = life.token_waves[tok]
            print(f"  {tok:12s}  q={w.q}  zone={w.zone()}  surprise={w.surprise_fraction:.3f}")
    print()
    
    for i in range(50):
        alive, zones = life.census()
        print(f"--- Generation {i+1} (alive: {alive}) ---")
        print(life.render())
        
        if alive == 0:
            print("  [EXTINCTION] All cells have crystallized to GROUND.")
            print(f"  Semantic life lasted {i+1} generations.")
            break
        
        zone_str = " | ".join(f"{z}:{n}" for z, n in sorted(zones.items()))
        print(f"  Zones: {zone_str}")
        
        stats = life.step()
        print(f"  Survive: {stats['survived']} | Breed: {stats['bred']} | Starve: {stats['starved']} | Turbulent: {stats['turbulent']}")
        print()
        
        time.sleep(0.3)
