"""
noise_compass.combinators — λ-RLM operators as gap-field traversal primitives.

The λ-RLM paper (arXiv:2603.20105) uses SPLIT/MAP/FILTER/REDUCE/CONCAT/CROSS
to decompose long-context problems into bounded leaf subproblems.

Here we repurpose these combinators as TRAVERSAL operators over a gap field:
not to decompose a problem, but to navigate the noise topology —
reading structured noise as orientation rather than eliminating it.

The model only touches leaf nodes (individual gap tensions ≥ threshold).
The combinators handle composition, routing, and interference detection.
"""

from __future__ import annotations
from typing import Callable
from .compass import Field


def SPLIT(
    field: Field,
    predicate: Callable[[str, dict], bool],
) -> tuple[Field, Field]:
    """
    Divide the field into two sub-fields based on a predicate.

    λ-RLM: splits a long document into chunks.
    Here:  approach a gap from BOTH sides simultaneously.
           left  = position 1 candidates (what is articulated)
           right = position 3 candidates (what is being reached)
           The gap (position 2) lives between them — inferred, never named.

    Example:
        active, quiet = SPLIT(field, lambda t, d: d["magnitude"] > 0.15)
    """
    left, right = {}, {}
    for token, data in field.items():
        (left if predicate(token, data) else right)[token] = data
    return left, right


def MAP(
    field: Field,
    transform: Callable[[str, dict], dict],
) -> Field:
    """
    Apply a transformation to each token in the field.

    λ-RLM: maps a model call over each chunk (leaf subproblem).
    Here:  applies a perspective lens uniformly — shift the field's frame.

    Example:
        # Dampen quiet regions
        damped = MAP(quiet, lambda t, d: {**d, "magnitude": d["magnitude"] * 0.9})
    """
    return {token: transform(token, data) for token, data in field.items()}


def FILTER(
    field: Field,
    threshold: float = 0.1,
    key: str = "magnitude",
) -> Field:
    """
    Keep only tokens whose key value exceeds threshold.

    λ-RLM: filters irrelevant information from context.
    Here:  strips quiet regions — exposes only the active gap topology.
           What remains after filtering IS the current orientation surface.

    Example:
        visible = FILTER(field, threshold=0.15)
    """
    return {t: d for t, d in field.items() if d.get(key, 0) > threshold}


def REDUCE(
    fields: list[Field],
    accumulator: Callable[[Field, Field], Field],
    initial: Field = None,
) -> Field:
    """
    Fold a list of fields into one using an accumulator.

    λ-RLM: combines intermediate results from parallel model calls.
    Here:  converges multiple compass readings into a single orientation.
           Used in the Y-combinator loop to collapse iteration history.

    Example:
        merged = REDUCE(history, lambda a, b: {**a, **b})
    """
    result = dict(initial) if initial else {}
    for f in fields:
        result = accumulator(result, f)
    return result


def CONCAT(field_a: Field, field_b: Field) -> Field:
    """
    Chain two fields — second field updates (overrides) first.

    λ-RLM: concatenates text chunks for context assembly.
    Here:  the approach vector of one gap entry becomes the starting
           context for the next traversal step. Direction of travel preserved.
           field_b wins on conflict — it is further along the trajectory.

    Example:
        next_field = CONCAT(previous_field, updated_self_tokens)
    """
    merged = dict(field_a)
    merged.update(field_b)
    return merged


def CROSS(
    field_a: Field,
    field_b: Field,
    key: str = "magnitude",
) -> list[tuple[str, str, float]]:
    """
    Cartesian product of two fields with interference scores.

    λ-RLM: cross-document reasoning over multiple retrieved chunks.
    Here:  finds pairs from different sub-fields with near-equal tension.
           Equal tension = superposition candidate.
           Score = 1.0 means perfect superposition (same magnitude, different tokens).
           These are NOT collapsed — they are mapped as interference points.

    Returns:
        List of (token_a, token_b, interference_score), sorted descending.
        interference_score ∈ [0, 1] — 1.0 = maximum superposition.

    Example:
        pairs = CROSS(active, quiet)
        superposed = [(a, b, s) for a, b, s in pairs if s > 0.85]
    """
    pairs = []
    for ta, da in field_a.items():
        for tb, db in field_b.items():
            if ta == tb:
                continue
            mag_a = da.get(key, 0)
            mag_b = db.get(key, 0)
            # 1.0 = identical magnitudes = superposition; 0.0 = maximally different
            score = 1.0 - abs(mag_a - mag_b)
            pairs.append((ta, tb, score))
    return sorted(pairs, key=lambda x: x[2], reverse=True)
