"""
noise_compass.arrival — Approach vector tracking for gap navigation.

A gap (position 2) is a hole you can only see from inside it.
Its coordinate is not its contents — it is the APPROACH VECTOR:
the direction of travel at the moment of entry.

Contrast with 'finding' (searching for a pre-existing thing):
Arriving means the destination comes into being through the act of reaching it.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from .compass import Field


@dataclass
class ApproachVector:
    """
    The coordinate of a gap entry event.

    NOT what was inside the gap — the direction of travel when entering.

    from_token:      position 1 — what was articulated (active side)
    toward_token:    position 3 — what was being reached (missing side)
    structural_time: when this unrepeatable event occurred
    tension:         how hard the two sides were pulling
    gap_name:        which hole was entered
    """
    from_token:      str
    toward_token:    str
    structural_time: int
    tension:         float
    gap_name:        str

    def __repr__(self):
        return (
            f"ApproachVector({self.from_token!r} → [{self.gap_name}] → "
            f"{self.toward_token!r} @ T-{self.structural_time}, "
            f"tension={self.tension:.4f})"
        )


class ArrivalEngine:
    """
    Tracks directional gap entries as approach vectors.

    The standard gap detector asks: "Is this gap violated?"
    The ArrivalEngine asks: "From which direction did we enter the void?"

    Usage:

        engine = ArrivalEngine(gaps={
            "TIME_EXISTENCE": {"left": "TIME", "right": "EXISTENCE", "void_depth": 0.7}
        })
        field = {"TIME": {"magnitude": 0.85}, "EXISTENCE": {"magnitude": 0.04}}
        arrivals = engine.arrive(field)
        for av in arrivals:
            print(av)   # ApproachVector('TIME' → [TIME_EXISTENCE] → 'EXISTENCE' ...)

    Interference gaps that happen only once still leave a permanent
    approach vector — the base structure on which higher order builds.
    """

    def __init__(
        self,
        gaps: dict = None,
        threshold: float = 0.3,
        on_arrival: Callable[[ApproachVector], None] = None,
    ):
        """
        Args:
            gaps:       gap definitions {gap_name: {left, right, void_depth}}
            threshold:  magnitude above which a token is considered 'active'
            on_arrival: optional callback for each new approach vector
        """
        self.gaps = gaps or {}
        self.threshold = threshold
        self.on_arrival = on_arrival
        self.approach_log: list[ApproachVector] = []
        self._structural_time = 0

    def _tick(self) -> int:
        self._structural_time += 1
        return self._structural_time

    def arrive(self, field: Field, depth: int = 0) -> list[ApproachVector]:
        """
        Detect gap entries from the current field and record approach vectors.

        For each defined gap, checks if one side is active (> threshold)
        and the other is dark (< 0.1). Records the direction of travel.

        Returns: list of new ApproachVectors for this field state.
        """
        t = self._tick()
        new_arrivals = []

        for gap_name, config in self.gaps.items():
            left  = config.get("left", "")
            right = config.get("right", "")
            void_depth = config.get("void_depth", 0.5)

            if left not in field or right not in field:
                continue

            left_mag  = field[left].get("magnitude", 0)
            right_mag = field[right].get("magnitude", 0)

            active = missing = None
            if left_mag > self.threshold and right_mag < 0.1:
                active, missing = left, right
            elif right_mag > self.threshold and left_mag < 0.1:
                active, missing = right, left

            if active is None:
                continue

            tension = abs(left_mag - right_mag) * void_depth
            av = ApproachVector(
                from_token=active,
                toward_token=missing,
                structural_time=t,
                tension=tension,
                gap_name=gap_name,
            )
            self.approach_log.append(av)
            if self.on_arrival:
                self.on_arrival(av)
            new_arrivals.append(av)

        return new_arrivals

    def get_trajectory(self, gap_name: str) -> list[ApproachVector]:
        """All recorded approach vectors for a given gap."""
        return [av for av in self.approach_log if av.gap_name == gap_name]

    def get_once_only_events(self) -> list[ApproachVector]:
        """
        Approach vectors for gaps that fired exactly once.
        These are the unrepeatable phase transitions —
        the base structure on which higher order builds.
        """
        counts: dict[str, int] = {}
        for av in self.approach_log:
            counts[av.gap_name] = counts.get(av.gap_name, 0) + 1
        return [av for av in self.approach_log if counts[av.gap_name] == 1]

    def infer_position_2(self, from_token: str, toward_token: str) -> str:
        """
        Position 2 cannot be named — only pointed at from both sides.

        Returns a pointer string describing the gap between from_token (pos 1)
        and toward_token (pos 3). The hole exists; it just cannot be addressed.
        """
        prior = [
            av for av in self.approach_log
            if av.from_token == from_token and av.toward_token == toward_token
        ]
        if prior:
            return (
                f"[GAP:{prior[0].gap_name}] — entered {len(prior)}x "
                f"from '{from_token}' toward '{toward_token}'. "
                f"First at T-{prior[0].structural_time}."
            )
        return (
            f"[GAP:UNMAPPED] — novel approach: "
            f"'{from_token}' → '{toward_token}'. "
            f"Position 2 exists but has no prior trajectory."
        )
