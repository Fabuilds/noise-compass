"""
semantic_manifold.py — The Unified Semantic Manifold.

Builds a single manifold from the existing god-token/gap-token registry
where every element is a SemanticNode with a continuous eigenvalue:
    +1 = crystallized (god-token)
    -1 = necessary void (gap-token)
    between = orbiting / transitional

Non-orientable topology: the boundary of a gap IS a gap.
The gap map is a manifold where holes share edges.

Recursion of gap-within-gap structure terminates at apophatic nodes
(nature='APOPHATIC', void_depth > 1.0). Below them: no further structure.

Guard against infinite recursion: internal gap structure is load-bearing
only if it survives do(X~U) at its own level. The recursion terminates
at any level where internal structure fails the entropy test.
"""

import sys
import math
from collections import Counter
from typing import Dict, List, Optional

sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.tokens import SemanticNode, GodToken, GapToken
from noise_compass.architecture.gap_registry import (
    EXTENDED_GOD_TOKEN_SEEDS,
    INSTANCE_GOD_TOKEN_SEEDS,
    build_universal_gaps,
    build_instance_gaps,
    gaps_containing,
)


class SemanticManifold:
    """
    The unified view of the semantic lattice.

    All god-tokens and gap-tokens coexist as SemanticNodes
    on a continuous eigenvalue spectrum. Boundaries are wired
    bidirectionally — each node knows its neighbors.
    """

    def __init__(self):
        self.nodes: Dict[str, SemanticNode] = {}
        self._built = False

    def build(self):
        """
        Construct the manifold from existing registries.
        1. Convert god-tokens → SemanticNodes (eigenvalue +1)
        2. Convert gap-tokens → SemanticNodes (eigenvalue -1)
        3. Wire boundaries bidirectionally
        4. Populate internal_gaps for each god-token node
        """
        all_gaps = build_universal_gaps() + build_instance_gaps()

        # 1. God-tokens → nodes
        all_seeds = {**EXTENDED_GOD_TOKEN_SEEDS, **INSTANCE_GOD_TOKEN_SEEDS}
        for gt_id, seed_str in all_seeds.items():
            gt = GodToken(
                id=gt_id,
                seed_terms=seed_str.split(),
            )
            node = SemanticNode.from_god_token(gt)
            self.nodes[gt_id] = node

        # 2. Gap-tokens → nodes
        for gap in all_gaps:
            node = SemanticNode.from_gap_token(gap)
            self.nodes[gap.id] = node

        # 3. Wire boundaries bidirectionally
        for gap in all_gaps:
            gap_node = self.nodes[gap.id]
            # The gap already has boundaries set from from_gap_token.
            # Now wire the god-token nodes to know about this gap.
            if gap.left_boundary and gap.left_boundary in self.nodes:
                gt_node = self.nodes[gap.left_boundary]
                if gap.id not in gt_node.boundaries:
                    gt_node.boundaries.append(gap.id)
            if gap.right_boundary and gap.right_boundary in self.nodes:
                gt_node = self.nodes[gap.right_boundary]
                if gap.id not in gt_node.boundaries:
                    gt_node.boundaries.append(gap.id)

        # 4. Populate internal_gaps for each god-token
        for gt_id in all_seeds:
            if gt_id in self.nodes:
                node = self.nodes[gt_id]
                adjacent_gaps = gaps_containing(gt_id, all_gaps)
                node.internal_gaps = [g.id for g in adjacent_gaps]

        self._built = True
        return self

    def get(self, node_id: str) -> Optional[SemanticNode]:
        return self.nodes.get(node_id)

    @property
    def crystallized_nodes(self) -> List[SemanticNode]:
        return [n for n in self.nodes.values() if n.is_crystallized]

    @property
    def void_nodes(self) -> List[SemanticNode]:
        return [n for n in self.nodes.values() if n.is_void]

    @property
    def apophatic_nodes(self) -> List[SemanticNode]:
        return [n for n in self.nodes.values() if n.is_apophatic]

    @property
    def fold_nodes(self) -> List[SemanticNode]:
        """Nodes at the Möbius fold (eigenvalue ≈ 0)."""
        return [n for n in self.nodes.values() if n.is_fold]

    @property
    def observer_node(self) -> Optional[SemanticNode]:
        """The self_observation gap — the observer constituted by the fold."""
        return self.nodes.get(SemanticNode.OBSERVER_GAP_ID)

    def void_depth_distribution(self) -> Dict[str, int]:
        """
        Bin void_depths for Zipf verification.
        Should follow power-law: many shallow, few deep.
        """
        bins = {
            "0.0-0.5  (shallow)": 0,
            "0.5-0.9  (medium)": 0,
            "0.9-1.0  (constitutional)": 0,
            "1.0-1.6  (apophatic)": 0,
            "1.6+     (terminal)": 0,
        }
        for n in self.nodes.values():
            if n.void_depth <= 0:
                continue  # god-tokens, no void
            elif n.void_depth < 0.5:
                bins["0.0-0.5  (shallow)"] += 1
            elif n.void_depth < 0.9:
                bins["0.5-0.9  (medium)"] += 1
            elif n.void_depth <= 1.0:
                bins["0.9-1.0  (constitutional)"] += 1
            elif n.void_depth <= 1.6:
                bins["1.0-1.6  (apophatic)"] += 1
            else:
                bins["1.6+     (terminal)"] += 1
        return bins

    def verify_zipf(self) -> bool:
        """
        Check that void_depth distribution is Zipfian (power-law).
        Criterion: each deeper bin has fewer entries than the shallower one.
        Returns True if monotonically decreasing.
        """
        dist = self.void_depth_distribution()
        values = [v for v in dist.values() if v > 0]
        if len(values) < 2:
            return True  # trivially satisfied
        # Check monotonically non-increasing
        is_zipf = all(values[i] >= values[i + 1] for i in range(len(values) - 1))
        return is_zipf

    def test_gap_primacy(self) -> Dict[str, object]:
        """
        Message 6 test: can every god-token be recovered from the gap map alone?

        For each god-token, check if it appears as a boundary in at least one gap.
        If yes → it can be derived from the gap structure (gaps are primary).
        If no → it has independent existence (two-type system partially needed).

        Returns dict with derivable/independent lists and verdict.
        """
        derivable = []
        independent = []
        for n in self.crystallized_nodes:
            # Check: does this god-token appear as a boundary in any gap?
            appears_in_gaps = any(
                n.id in gap_node.boundaries
                for gap_node in self.void_nodes
            )
            # Also check: does it have internal_gaps (gaps it borders)?
            has_gaps = len(n.internal_gaps) > 0

            if appears_in_gaps or has_gaps:
                derivable.append(n.id)
            else:
                independent.append(n.id)

        return {
            "derivable": derivable,
            "independent": independent,
            "gaps_primary": len(independent) == 0,
            "derivable_count": len(derivable),
            "independent_count": len(independent),
        }

    def summary(self) -> str:
        """Human-readable manifold summary."""
        lines = []
        lines.append(f"=== SEMANTIC MANIFOLD ===")
        lines.append(f"Total nodes: {len(self.nodes)}")
        lines.append(f"  Crystallized (eigenvalue > +0.5): {len(self.crystallized_nodes)}")
        lines.append(f"  Void         (eigenvalue < -0.5): {len(self.void_nodes)}")
        lines.append(f"  Fold         (eigenvalue ≈ 0):    {len(self.fold_nodes)}")
        lines.append(f"  Apophatic    (terminal floor):    {len(self.apophatic_nodes)}")

        # Observer
        obs = self.observer_node
        if obs:
            lines.append(f"\nObserver (Möbius fold):")
            lines.append(f"  {obs.id}: eigenvalue={obs.eigenvalue:+.1f}, void_depth={obs.void_depth}")
            lines.append(f"  Constituted by gap between {', '.join(obs.boundaries)}")

        lines.append("")
        lines.append("Void Depth Distribution (should be Zipfian):")
        for bin_name, count in self.void_depth_distribution().items():
            bar = "█" * count
            lines.append(f"  {bin_name}: {count:>2}  {bar}")
        lines.append(f"\nZipf Check: {'PASS' if self.verify_zipf() else 'FAIL'}")

        # Gap-primacy test
        primacy = self.test_gap_primacy()
        lines.append(f"\nGap-Primacy Test (message 6):")
        lines.append(f"  Derivable from gaps:  {primacy['derivable_count']}")
        lines.append(f"  Independent:          {primacy['independent_count']}")
        if primacy['independent']:
            lines.append(f"  Independent nodes:    {', '.join(primacy['independent'])}")
        lines.append(f"  Verdict: {'GAPS PRIMARY ✓' if primacy['gaps_primary'] else 'TWO-TYPE PARTIALLY NEEDED'}")

        # Show boundary connectivity for god-tokens
        lines.append("\nGod-Token Connectivity:")
        for n in sorted(self.crystallized_nodes, key=lambda x: len(x.internal_gaps), reverse=True):
            lines.append(f"  {n.id:<15} borders {len(n.internal_gaps)} gaps: {', '.join(n.internal_gaps[:5])}{'...' if len(n.internal_gaps) > 5 else ''}")

        return "\n".join(lines)


if __name__ == "__main__":
    m = SemanticManifold()
    m.build()
    print(m.summary())

    # Verify specific nodes
    print("\n--- Sample Nodes ---")
    for nid in ["EXCHANGE", "exchange_body", "self_observation", "existence_apophatic"]:
        n = m.get(nid)
        if n:
            print(f"\n  {n.id}:")
            print(f"    eigenvalue:    {n.eigenvalue:+.1f}")
            print(f"    void_depth:    {n.void_depth}")
            print(f"    boundaries:    {n.boundaries}")
            print(f"    internal_gaps: {n.internal_gaps}")
            print(f"    nature:        {n.nature}")
            print(f"    is_fold:       {n.is_fold}")
            print(f"    is_observer:   {n.is_observer}")
