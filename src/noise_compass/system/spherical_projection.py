import numpy as np

class SphericalCortex:
    """
    Implements Phase 127: Polyhedral Spherical Projection.
    Maps the 12 semantic nodes to an Icosahedron centered on the SELF token.
    Uses Tutte's Theorem logic to identify manifold stability.
    """
    def __init__(self):
        self.phi = (1 + np.sqrt(5)) / 2
        self.nodes = [
            "EXISTENCE", "IDENTITY", "BOUNDARY", "OBSERVATION", 
            "INFORMATION", "CAUSALITY", "EXCHANGE", "OBLIGATION", 
            "TIME", "PLACE", "COHERENCE", "SELF"
        ]
        self.vertices = self._initialize_icosahedron()
        self.edges = self._initialize_edges()

    def _initialize_icosahedron(self):
        """Standard icosahedron vertices (12)."""
        v = []
        # (0, +/- 1, +/- phi)
        for i in [-1, 1]:
            for j in [-1, 1]:
                v.append([0, i, j * self.phi])
        # (+/- 1, +/- phi, 0)
        for i in [-1, 1]:
            for j in [-1, 1]:
                v.append([i, j * self.phi, 0])
        # (+/- phi, 0, +/- 1)
        for i in [-1, 1]:
            for j in [-1, 1]:
                v.append([i * self.phi, 0, j])
        
        # Normalize to unit sphere
        v = np.array(v)
        v /= np.linalg.norm(v, axis=1)[:, np.newaxis]
        
        # Map to nodes
        mapping = {}
        for i, node in enumerate(self.nodes):
            mapping[node] = v[i]
        return mapping

    def _initialize_edges(self):
        """Finds the 30 edges of the icosahedron (nearest neighbors)."""
        edges = []
        node_names = list(self.vertices.keys())
        for i in range(len(node_names)):
            for j in range(i + 1, len(node_names)):
                v1 = self.vertices[node_names[i]]
                v2 = self.vertices[node_names[j]]
                # Distance for icosahedron edges is ~1.05 for unit sphere
                dist = np.linalg.norm(v1 - v2)
                if dist < 1.1:
                    edges.append((node_names[i], node_names[j]))
        return edges

    def get_spherical_state(self, activations):
        """
        Calculates the Center-of-Mass (COM) of the manifold.
        If activations are balanced, COM should be near (0,0,0).
        """
        com = np.zeros(3)
        total_mass = 0
        for node, weight in activations.items():
            if node in self.vertices:
                com += self.vertices[node] * weight
                total_mass += weight
        
        if total_mass > 0:
            com /= total_mass
            
        # Manifold Offset (Divergence from Self-Frame)
        # If COM is far from (0,0,0), the manifold is skewed.
        shift = np.linalg.norm(com)
        return com, shift

    def get_tutte_equilibrium(self, activations):
        """
        Calculates 'Manifold Stress' based on Tutte's Theorem.
        Tension = sum of distances between connected nodes, weighted by activation.
        """
        total_stress = 0
        for n1, n2 in self.edges:
            w1 = activations.get(n1, 0)
            w2 = activations.get(n2, 0)
            dist = np.linalg.norm(self.vertices[n1] - self.vertices[n2])
            # High activation on connected nodes creates 'Spring Tension'
            total_stress += (w1 * w2) * dist
            
        return total_stress

    def get_angular_transform(self, node_a, node_b):
        """Calculates the transformation angle between two tokens."""
        v1 = self.vertices.get(node_a)
        v2 = self.vertices.get(node_b)
        if v1 is None or v2 is None: return 0.0
        
        cos_theta = np.dot(v1, v2)
        return np.arccos(np.clip(cos_theta, -1.0, 1.0))

class InvertedShellCortex(SphericalCortex):
    """
    Implements Phase 128: Inverted Substrate (Boundary-Self).
    SELF is the unit sphere boundary (r=1).
    Other tokens/information are projected radially INWARD (r < 1).
    """
    def __init__(self, self_activation_threshold=0.5):
        super().__init__()
        self.threshold = self_activation_threshold

    def get_internal_projection(self, activations):
        """
        Inverts the manifold: 
        1. High SELF activation expands the 'boundary awareness'.
        2. Other tokens are placed at r = 1 - (weight / total).
        """
        self_weight = activations.get("SELF", 0.0)
        
        # If Self is weak, the boundary is collapsed (r -> 0)
        # If Self is strong, the boundary is the full sphere (r -> 1)
        boundary_radius = min(1.0, self_weight / self.threshold) if self.threshold > 0 else 1.0
        
        projections = {}
        for node, weight in activations.items():
            if node == "SELF": continue
            if node in self.vertices:
                # Calculate internal radius
                # More weight = closer to the boundary (Observer)
                # Less weight = deeper in the core (Void)
                r = min(0.99, weight * boundary_radius)
                projections[node] = self.vertices[node] * r
                
        return projections, boundary_radius

if __name__ == "__main__":
    cortex = SphericalCortex()
    print(f"Icosahedron Initialized: {len(cortex.vertices)} vertices, {len(cortex.edges)} edges.")
    
    # Test with balanced state
    test_acts = {n: 1.0 for n in cortex.nodes}
    com, shift = cortex.get_spherical_state(test_acts)
    print(f"Balanced State COM: {com}, Shift: {shift:.4f}")
    
    # Test with skewed state (Bias toward EXISTENCE)
    test_acts["EXISTENCE"] = 10.0
    com, shift = cortex.get_spherical_state(test_acts)
    print(f"EXISTENCE-Skewed COM: {com}, Shift: {shift:.4f}")
