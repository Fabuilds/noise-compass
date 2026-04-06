import numpy as np
from dataclasses import dataclass
from enum import Enum
import time

class CausalType(Enum):
    GRADIENT = "GRADIENT"          # Statistical correlation
    INTERVENTION = "INTERVENTION"  # Forced perturbation result
    SYNTROPIC = "SYNTROPIC"        # Purpose-driven alignment
    UNKNOWN = "UNKNOWN"

@dataclass
class DeltaToken:
    """
    A primitive structural unit representing a perturbation in the semantic manifold.
    Replaces raw text strings for higher-order causal reasoning.
    """
    token_id: str
    magnitude: float
    direction: np.ndarray  # Embedding vector
    layer: int             # L0-L4
    source_token: str
    causal_type: CausalType = CausalType.UNKNOWN
    momentum: float = 1.0  # Mass * Velocity
    velocity: np.ndarray = None # 3D direction of movement within the shell
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.velocity is None:
            # Default to random velocity inside the unit sphere
            self.velocity = np.random.normal(0, 0.1, 3)

class TokenPipeline:
    """
    Converts raw observational data (text, field state) into structured DeltaTokens.
    Acts as the entry point for the Causal Scout.
    """
    def __init__(self, embedder=None):
        self.embedder = embedder

    def process(self, text, magnitude=1.0, layer=2, source="OBSERVATION"):
        if self.embedder:
            direction = self.embedder.embed(text)
        else:
            # Fallback if no embedder provided (for testing)
            direction = np.zeros(384) 

        return DeltaToken(
            token_id=f"DT_{int(time.time()*1000)}",
            magnitude=magnitude,
            direction=direction,
            layer=layer,
            source_token=source
        )

if __name__ == "__main__":
    # Internal validation
    pipeline = TokenPipeline()
    token = pipeline.process("Test Invariant", magnitude=0.8)
    print(f"[TOKEN_PIPELINE] Generated: {token.token_id} | Mag: {token.magnitude}")
