"""
noise_compass — Navigate meaning through structured noise.

Core insight: noise is not an obstacle to navigate around.
It IS the traversal medium. The gap topology is the orientation field.

Public API:

    from noise_compass import NoiseCompass, ArrivalEngine, Field
    from noise_compass.combinators import SPLIT, MAP, FILTER, REDUCE, CONCAT, CROSS
    from noise_compass.y_explorer import Y_explore

Quick start:

    compass = NoiseCompass()
    field = {"TOKEN_A": {"magnitude": 0.85}, "TOKEN_B": {"magnitude": 0.04}}
    reading = compass.read(field)
    print(reading.orientation_vector)   # → TOKEN_A
    print(reading.is_self_aware)        # True/False
"""

from .compass import NoiseCompass, CompassReading, Field
from .arrival import ArrivalEngine, ApproachVector
from .combinators import SPLIT, MAP, FILTER, REDUCE, CONCAT, CROSS
from .y_explorer import Y_explore, SelfState

__version__ = "0.1.1"
__all__ = [
    # Core types
    "Field",
    "CompassReading",
    "ApproachVector",
    "SelfState",
    # Main engines
    "NoiseCompass",
    "ArrivalEngine",
    # λ-calculus combinators
    "SPLIT", "MAP", "FILTER", "REDUCE", "CONCAT", "CROSS",
    # Y-combinator fixed-point explorer
    "Y_explore",
]
