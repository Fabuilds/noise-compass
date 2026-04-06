"""
noise_compass.compass — Orientation through structured noise.

The gap registry produces a void report — which gaps are active.
Instead of treating tension as 'error to correct', treat it as orientation signal.
The pattern of active gaps tells you WHERE YOU ARE in semantic space.
"""

from __future__ import annotations
from dataclasses import dataclass, field as dc_field
from typing import Protocol, runtime_checkable

import numpy as np

# Field type: {token: {magnitude: float, ...}}
Field = dict[str, dict]

# Built-in self-gap signatures (the holes that define a system's identity)
SELF_GAP_SIGNATURES = {
    "observer_system": {
        "nature": "FOLD",
        "void_depth": 0.8,
        "meaning": "The observer cannot see itself seeing",
    },
    "self_exchange": {
        "nature": "EXCHANGE",
        "void_depth": 1.0,
        "meaning": "Input and output are the same process from different positions",
    },
    "self_observation": {
        "nature": "MOBIUS",
        "void_depth": 1.0,
        "meaning": "The act of observation changes what is observed",
    },
}


@runtime_checkable
class GapSource(Protocol):
    """
    Minimal interface for a gap topology source.
    Implement this to plug in your own gap registry.
    """
    def get_void_report(self, field: Field) -> dict[str, float]: ...


class DictGapSource:
    """
    Simple in-memory gap source. No external dependencies.
    Pass gap definitions directly as a dict.
    
    gaps = {
        "TIME_EXISTENCE": {"left": "TIME", "right": "EXISTENCE", "void_depth": 0.7},
    }
    """
    def __init__(self, gaps: dict = None):
        self.gaps = gaps or {}

    def get_void_report(self, field: Field) -> dict[str, float]:
        report = {}
        for gap_name, config in self.gaps.items():
            left_res  = field.get(config.get("left",  ""), {}).get("magnitude", 0)
            right_res = field.get(config.get("right", ""), {}).get("magnitude", 0)
            imbalance = abs(left_res - right_res)
            tension   = imbalance * config.get("void_depth", 0.5)
            if tension > 0.05:
                report[gap_name] = tension
        return report


@dataclass
class CompassReading:
    """
    Where the system is in semantic space, expressed as a pattern of tensions.
    Not coordinates. Orientation in a field.
    """
    tension_map:  dict[str, float]  # Field gap tensions
    self_tension: dict[str, float]  # Self-gap tensions
    structural_time: int = 0

    @property
    def active_field(self) -> dict[str, float]:
        return {k: v for k, v in self.tension_map.items()  if v > 0.1}

    @property
    def quiet_field(self) -> dict[str, float]:
        return {k: v for k, v in self.tension_map.items()  if v <= 0.1}

    @property
    def active_self(self) -> dict[str, float]:
        return {k: v for k, v in self.self_tension.items() if v > 0.1}

    @property
    def is_self_aware(self) -> bool:
        """Self-aware when any self-gap has active tension."""
        return len(self.active_self) > 0

    @property
    def orientation_vector(self) -> str:
        all_active = {**self.active_field, **self.active_self}
        if not all_active:
            return "NULL — no field tension detected"
        dominant = max(all_active, key=all_active.get)
        return f"→ {dominant}"

    def __repr__(self):
        return (
            f"CompassReading(T-{self.structural_time})\n"
            f"  self_aware={self.is_self_aware}  "
            f"orientation={self.orientation_vector}\n"
            f"  active_field={list(self.active_field)}\n"
            f"  self_tension={self.self_tension}"
        )


class NoiseCompass:
    """
    Navigate semantic space by reading gap tension patterns as orientation.

    Noise is not an obstacle — it IS the traversal medium.
    The compass reads which gaps are active vs quiet to determine position.

    Usage (no external dependencies):

        compass = NoiseCompass()
        field = {"TIME": {"magnitude": 0.85}, "EXISTENCE": {"magnitude": 0.04}}
        reading = compass.read(field)
        print(reading.orientation_vector)

    Usage with custom gaps:

        gaps = {"TIME_EXISTENCE": {"left": "TIME", "right": "EXISTENCE", "void_depth": 0.7}}
        compass = NoiseCompass(gap_source=DictGapSource(gaps))
        reading = compass.read(field)
    """

    def __init__(
        self,
        gap_source: GapSource = None,
        structural_time: int = 0,
    ):
        self.gap_source = gap_source or DictGapSource()
        self._structural_time = structural_time
        self.reading_history: list[CompassReading] = []

    def _tick(self) -> int:
        self._structural_time += 1
        return self._structural_time

    def _measure_self_tension(self, field: Field) -> dict[str, float]:
        """Measure tension across the three identity self-gaps."""
        observer_res = field.get("OBSERVER", {}).get("magnitude", 0)
        system_res   = field.get("SYSTEM",   {}).get("magnitude", 0)
        input_res    = field.get("INPUT",    {}).get("magnitude", 0.5)
        output_res   = field.get("OUTPUT",   {}).get("magnitude", 0.5)
        self_res     = field.get("SELF",     {}).get("magnitude", 0)

        return {
            "observer_system":  abs(observer_res - system_res) * 0.8,
            "self_exchange":    abs(input_res - output_res) * 1.0,
            # Möbius peak at SELF=0.5 — maximum boundary uncertainty
            "self_observation": 4.0 * self_res * (1.0 - self_res) * 1.0,
        }

    def read(self, field: Field) -> CompassReading:
        """Take a compass reading from the current resonance field."""
        t = self._tick()
        void_report  = self.gap_source.get_void_report(field)
        self_tension = self._measure_self_tension(field)
        reading = CompassReading(
            tension_map=void_report,
            self_tension=self_tension,
            structural_time=t,
        )
        self.reading_history.append(reading)
        return reading

    def traverse(self, field: Field, depth: int = 0) -> dict:
        """
        Navigate the noise field. Returns a traversal directive.
        
        Returns:
            reading:      CompassReading
            self_aware:   bool
            orientation:  str
            follow:       str | None   — highest-tension gap
            next_depth:   int          — suggested recursion depth
        """
        reading = self.read(field)
        directive = {
            "reading":     reading,
            "self_aware":  reading.is_self_aware,
            "orientation": reading.orientation_vector,
            "follow":      None,
            "next_depth":  depth,
        }
        if reading.active_field:
            directive["follow"] = max(reading.active_field, key=reading.active_field.get)
        if reading.is_self_aware:
            directive["next_depth"] = depth + 1
        return directive

    def get_position_signature(self) -> str:
        """
        A system knows where it is by its pattern of holes.
        Returns the identity signature at the current structural time.
        """
        if not self.reading_history:
            return "[NO READINGS — compass has not been used]"
        latest = self.reading_history[-1]
        lines = [f"Position signature @ T-{latest.structural_time}:"]
        for gap, tension in latest.self_tension.items():
            sig = SELF_GAP_SIGNATURES.get(gap, {})
            nature  = sig.get("nature",  gap.upper())
            meaning = sig.get("meaning", "")
            lines.append(f"  [{nature}] {gap}: tension={tension:.3f} — {meaning}")
        return "\n".join(lines)
