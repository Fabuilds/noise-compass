import numpy as np
from typing import List
from noise_compass.system.token_pipeline import DeltaToken
from noise_compass.system.spherical_projection import InvertedShellCortex

class InternalBrain:
    """
    Implements the Ephemeral Particle Processing (Phase 128).
    Particles (DeltaTokens) move within the SELF-Boundary shell.
    Information is derived from particle interference/collision.
    """
    def __init__(self, shell: InvertedShellCortex):
        self.shell = shell
        self.particles: List[DeltaToken] = []
        self.viscosity = 0.9  # Decay of particle momentum

    def inject_particle(self, token: DeltaToken):
        """Adds a new ephemeral particle to the internal field."""
        # Initial position is randomized but bounded by the shell
        token.position = np.random.normal(0, 0.2, 3)
        self.particles.append(token)
        if len(self.particles) > 100:
            self.particles.pop(0) # Keep buffer manageable

    def tick(self, dt=0.1):
        """
        Updates particle positions. 
        Detects collisions with the SELF boundary (r=1).
        """
        for p in self.particles:
            # Update Position: x = x + v * dt
            p.position += p.velocity * dt
            
            # Boundary Reflection: If r > 1, bounce back
            r = np.linalg.norm(p.position)
            if r > 1.0:
                # Normal vector at reflection point
                normal = p.position / r
                # Reflect velocity: v' = v - 2(v.n)n
                p.velocity = p.velocity - 2 * np.dot(p.velocity, normal) * normal
                # Apply boundary damping
                p.velocity *= 0.8
                # Clip position back inside
                p.position = normal * 0.99
                print(f"[INTERNAL_BRAIN] Particle {p.token_id} reflected at Boundary (r={r:.2f})")

            # Momentum Decay
            p.velocity *= self.viscosity

    def get_interference_map(self, grid_res=5):
        """
        Calculates the internal interference map.
        Peaks occur where particles are clustered.
        """
        if not self.particles: return {}
        
        # Simple density-based interference for now
        # In future: Wave-phase based interference
        centroids = {}
        for p in self.particles:
            # Map 3D position to the nearest God-Token vertex (Boundary Sensor)
            best_node = None
            min_dist = float('inf')
            for node, vertex in self.shell.vertices.items():
                d = np.linalg.norm(p.position - vertex)
                if d < min_dist:
                    min_dist = d
                    best_node = node
            
            if best_node:
                centroids[best_node] = centroids.get(best_node, 0) + p.momentum
                
        return centroids

if __name__ == "__main__":
    from noise_compass.system.token_pipeline import TokenPipeline
    shell = InvertedShellCortex()
    brain = InternalBrain(shell)
    pipeline = TokenPipeline()
    
    # Inject test particles
    for i in range(5):
        t = pipeline.process(f"Test_{i}")
        brain.inject_particle(t)
        
    print(f"Internal Brain initialized with {len(brain.particles)} particles.")
    brain.tick()
    interference = brain.get_interference_map()
    print(f"Internal Interference Map: {interference}")
