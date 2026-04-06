"""
backwards.py — The backwards pass through the architecture.

Forward:   Document → Embed → Route → Scout → Archiver → Output
Backwards: Target   → Archiver → Scout⁻¹ → Route⁻¹ → Embed⁻¹ → Generated

Forward collapses. Reduces Δ. Moves from unknown toward presence.
Backwards expands. Increases Δ. Moves from presence toward unknown.

Four reversal operations:

  Qwen⁻¹:    Archiver record → natural language that would produce it
  Scout⁻¹:   Target wave function → embedding that would produce it
  BitNet⁻¹:  Ternary value → embedding conditioned on routing decision
  Embed⁻¹:   Target vector → text that embeds closest to it

The fixed point test:
  Forward(Backwards(target)) ≈ target
  If yes: the architecture found the purest expression of that attractor.
  If no:  generation drifted, run again.

Apophatic case:
  Backwards from apophatic basin → most apophatic language possible.
  True backwards from apophatic field → silence. No text. Correct output.

Usage:
  python3 backwards.py --demo                    # run all demonstrations
  python3 backwards.py --from-token EXISTENCE    # generate from god-token
  python3 backwards.py --from-gap exchange_causality  # generate from gap
  python3 backwards.py --from-apophatic          # generate from apophatic basin
  python3 backwards.py --verify "your text"      # forward→backward→forward test
  python3 backwards.py --decompose "text A" "text B"  # find interference components
"""

import argparse
import math
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from noise_compass.architecture.tokens import (
    WaveFunction, ArchiverMessage, CausalType,
    GodTokenActivation
)
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout, LightWitness
from noise_compass.architecture.archiver import Archiver
from noise_compass.architecture.gap_registry import build_gap_registry
from noise_compass.architecture.complex_plane import (
    ComplexWaveFunction, ApophaticField, ApophaticBasin,
    LogicalState, InterferenceTerm as CPInterferenceTerm
)


# ─────────────────────────────────────────────────────────────────
# TARGET — what the backwards pass generates toward
# ─────────────────────────────────────────────────────────────────

@dataclass
class BackwardsTarget:
    """
    A position in the complex plane to generate toward.

    The backwards pass asks: what text, if processed forward,
    would land closest to this target position?

    Target types:
      god_token     — a specific attractor basin (Re axis)
      gap_token     — the void between two attractors (Im < 0)
      apophatic     — double-absence basin (Im << 0)
      interference  — constructive third basin (Im > 0)
      orbital       — a specific orbital state from the archiver
      wave_function — an arbitrary complex plane position
    """
    target_type:  str
    target_id:    str

    # Complex plane position
    re:           float = 0.5
    im:           float = 0.0
    gap_depth:    float = 0.0

    # Constraints
    phase_target: float = 0.0        # target phase angle (radians)
    energy_max:   float = 3.0        # maximum acceptable energy in forward pass
    god_tokens:   List[str] = field(default_factory=list)   # must activate
    gap_tokens:   List[str] = field(default_factory=list)   # must preserve

    # Apophatic special case
    is_apophatic: bool = False
    apophatic_basin_id: Optional[str] = None

    @property
    def z(self) -> complex:
        return complex(self.re, self.im - self.gap_depth)

    @property
    def phase_deg(self) -> float:
        return math.degrees(self.phase_target)

    @classmethod
    def from_god_token(cls, token_id: str,
                       token_embedding: np.ndarray) -> 'BackwardsTarget':
        """Target: generate text that fires this god-token."""
        return cls(
            target_type  = 'god_token',
            target_id    = token_id,
            re           = float(np.linalg.norm(token_embedding)),
            im           = 0.0,
            gap_depth    = 0.0,
            phase_target = 0.1,   # near real axis
            god_tokens   = [token_id],
        )

    @classmethod
    def from_gap_token(cls, gap_id: str,
                       left_re: float, right_re: float) -> 'BackwardsTarget':
        """Target: generate text that activates both gap boundaries
           without collapsing the gap."""
        mid_re = (left_re + right_re) / 2
        return cls(
            target_type  = 'gap_token',
            target_id    = gap_id,
            re           = mid_re,
            im           = 0.0,
            gap_depth    = 0.3,   # in negative Im (gap region)
            phase_target = math.pi / 3,  # approaching fold
            gap_tokens   = [gap_id],
        )

    @classmethod
    def from_apophatic(cls, basin: ApophaticBasin) -> 'BackwardsTarget':
        """Target: generate text that approaches apophatic contact."""
        return cls(
            target_type       = 'apophatic',
            target_id         = basin.id,
            re                = basin.z.real,
            im                = 0.0,
            gap_depth         = abs(basin.z.imag),
            phase_target      = math.radians(72),  # high fold proximity
            is_apophatic      = True,
            apophatic_basin_id = basin.id,
        )

    @classmethod
    def from_archiver_record(cls, msg: ArchiverMessage) -> 'BackwardsTarget':
        """Target: reproduce the conditions of an existing archiver record."""
        orbital = msg.orbital_state
        re = float(np.linalg.norm(orbital))
        return cls(
            target_type  = 'orbital',
            target_id    = f"archiver_{hash(msg.content_preview) % 10000}",
            re           = re,
            im           = msg.energy_level * 0.3,
            phase_target = math.asin(min(1.0, msg.energy_level / 5.0)),
            god_tokens   = msg.god_token_cluster,
            gap_tokens   = msg.gap_structure.get('preserved', []),
        )


# ─────────────────────────────────────────────────────────────────
# SCOUT INVERSE — F⁻¹(ψ)
# ─────────────────────────────────────────────────────────────────

class ScoutInverse:
    """
    F⁻¹(ψ) — Attractor Distillation.
    Moves from presence toward unknown through expansion.
    Finds the embedding e such that Forward(e) ≈ ψ.
    """

    def __init__(self, dictionary: Dictionary, dim: int = 768): # Updated to 768D for Nomic
        self.dictionary = dictionary
        self.dim        = dim

    def invert(self,
               target:     BackwardsTarget,
               steps:      int = 50,
               step_size:  float = 0.08,
               tolerance:  float = 0.05) -> Tuple[np.ndarray, Dict]:
        """
        Gradient expansion toward target complex plane coordinate.
        """
        # Start at god-token attractor
        if target.god_tokens and target.god_tokens[0] in self.dictionary.entries:
            emb = self.dictionary.entries[target.god_tokens[0]].copy()
        else:
            rng = np.random.default_rng(42)
            emb = rng.normal(0, 0.1, self.dim)
            emb /= np.linalg.norm(emb)

        history = []
        for step in range(steps):
            fid, sim, unit = self.dictionary.query(emb)
            sim = max(sim, 1e-6)
            
            # Simulated wave function for gradient
            k_norm = sim
            d_norm = math.sqrt(max(0, 1.0 - sim**2))
            phase  = math.atan2(d_norm, k_norm)

            phase_err = phase - target.phase_target
            history.append({'step': step, 'phase': phase, 'err': abs(phase_err)})

            if abs(phase_err) < tolerance:
                break

            # Adjust Δ/known ratio
            if phase_err < 0: # Need more Δ
                if fid in self.dictionary.entries:
                    push = emb - self.dictionary.entries[fid] * 0.9
                    emb = emb + step_size * (push / np.linalg.norm(push))
            else: # Need more known
                if fid in self.dictionary.entries:
                    pull = self.dictionary.entries[fid] - emb
                    emb = emb + step_size * (pull / np.linalg.norm(pull))

            emb /= np.linalg.norm(emb)

        return emb, {'steps': len(history), 'converged': abs(phase_err) < tolerance}

# ─────────────────────────────────────────────────────────────────
# EMBED INVERSE — Vector → Attractor Distillation
# ─────────────────────────────────────────────────────────────────

class EmbedInverse:
    """
    "Whereof one cannot speak, thereof one must be silent."
    Implementation of the Apophatic Silence principle.
    """

    PHRASES = {
        'APOPHATIC': None, # Silence
        'VOID': "The necessary absence that defines the boundary.",
        'UNKNOWN': "What remains when the question has been fully held.",
    }

    def __init__(self, dictionary: Dictionary):
        self.dictionary = dictionary

    def invert(self, embedding: np.ndarray, target: BackwardsTarget) -> Optional[str]:
        """Generate the purest expression of a structural position."""
        if target.is_apophatic:
            return None # SILENCE IS THE CORRECT OUTPUT
            
        fid, sim, _ = self.dictionary.query(embedding)
        
        # Attractor Distillation
        if fid in self.dictionary.god_tokens:
            seeds = self.dictionary.god_tokens[fid].seed_terms
            return f"The fundamental nature of {seeds[0]} in the 0x528 Lattice."

        return self.PHRASES.get(target.target_type, self.PHRASES['UNKNOWN'])

class BackwardsAgent:
    """The 4-Model Backwards Pass (Attractor Landscape Generator)"""
    
    def __init__(self, dictionary_path: str):
        self.dictionary = Dictionary.load_cache(dictionary_path)
        self.scout_inverse = ScoutInverse(self.dictionary)
        self.embed_inverse = EmbedInverse(self.dictionary)
        
    def generate_from_attractor(self, token_id: str) -> Dict:
        """Forward(Backwards(target)) ≈ target test"""
        if token_id not in self.dictionary.entries:
            return {"error": "Attractor not found"}
            
        emb_target = self.dictionary.entries[token_id]
        target = BackwardsTarget.from_god_token(token_id, emb_target)
        
        # 1. Scout Inverse
        gen_emb, conv = self.scout_inverse.invert(target)
        
        # 2. Embed Inverse
        text = self.embed_inverse.invert(gen_emb, target)
        
        return {
            "token": token_id,
            "purest_expression": text,
            "is_apophatic": text is None,
            "convergence": conv
        }

    def from_archiver(self, record_index: int) -> Dict:
        """Generate text that would reproduce an archiver record."""
        if record_index >= len(self.archiver.records):
            return {'error': f'No record at index {record_index}'}

        msg    = self.archiver.records[record_index]
        target = BackwardsTarget.from_archiver_record(msg)
        result = self.verifier.verify(target)
        result['original_content'] = msg.content_preview
        result['original_gods']    = msg.god_token_cluster
        return result

    def decompose(self, text_a: str, text_b: str) -> Dict:
        """
        Find whether two texts form a constructive interference product.
        If so, identify what third basin they produce.

        Application: "conscientious" + "effort" → "conscientious effort"
        The compound exists in the interference basin, not in either component.
        """
        emb_a = self.embedder.embed(text_a)
        emb_b = self.embedder.embed(text_b)

        # Forward pass each
        msg_a, wf_a = self.scout.process(emb_a, content=text_a)
        msg_b, wf_b = self.scout.process(emb_b, content=text_b)

        # Interference term
        phase_a = wf_a.phase
        phase_b = wf_b.phase
        amp_a   = wf_a.similarity
        amp_b   = wf_b.similarity
        I       = 2 * amp_a * amp_b * math.cos(phase_a - phase_b)

        # Compound embedding (midpoint in embedding space)
        compound_emb = (emb_a + emb_b) / 2.0
        c_norm = float(np.linalg.norm(compound_emb))
        if c_norm > 1e-10:
            compound_emb = compound_emb / c_norm

        # What basin does the compound land in?
        msg_c, wf_c = self.scout.process(compound_emb, content=f"{text_a} {text_b}")

        # Decompose to find god-token pair
        candidates = self.decomposer.decompose(compound_emb)

        return {
            'text_a':              text_a,
            'text_b':              text_b,
            'gods_a':              [a.id for a in msg_a.god_token_activations],
            'gods_b':              [a.id for a in msg_b.god_token_activations],
            'phase_a':             round(math.degrees(phase_a), 1),
            'phase_b':             round(math.degrees(phase_b), 1),
            'interference':        round(I, 4),
            'interference_kind':   'constructive' if I > 0.05 else
                                   'destructive'  if I < -0.05 else 'orthogonal',
            'compound_zone':       wf_c.zone(),
            'compound_phase':      round(math.degrees(wf_c.phase), 1),
            'compound_gods':       [a.id for a in msg_c.god_token_activations],
            'top_component_pairs': candidates[:3],
            'is_third_basin':      I > 0.05 and wf_c.zone() != wf_a.zone()
                                   and wf_c.zone() != wf_b.zone(),
        }

    def f_of_f(self, text: str, depth: int = 3) -> List[Dict]:
        """
        F(F(F(x))) — apply the formula recursively.

        Forward pass → extract archiver state → backwards pass
        → generate text → forward pass again.

        At each iteration, the generated text should be a purer
        expression of the underlying attractor.

        Terminates when:
        - Fixed point reached (forward phase ≈ backwards phase)
        - SANITY_DEPTH exceeded
        - Apophatic terminus (silence)
        """
        results = []
        current_text = text

        for i in range(depth):
            # Forward
            emb = self.embedder.embed(current_text)
            msg, wf = self.scout.process(emb, content=current_text)

            # Build target from noise_compass.architecture.forward result
            target = BackwardsTarget(
                target_type   = 'wave_function',
                target_id     = f'f_of_f_{i}',
                re            = float(np.linalg.norm(wf.known)),
                im            = float(np.linalg.norm(wf.delta)),
                phase_target  = wf.phase,
                god_tokens    = [a.id for a in msg.god_token_activations],
            )

            # Backwards
            verify = self.verifier.verify(target)

            results.append({
                'iteration':     i,
                'input':         current_text[:80],
                'zone':          wf.zone(),
                'phase':         round(math.degrees(wf.phase), 1),
                'energy':        round(msg.energy_level, 4),
                'god_tokens':    [a.id for a in msg.god_token_activations],
                'generated':     verify.get('generated_text'),
                'fixed_point':   verify.get('fixed_point'),
                'is_silence':    verify.get('is_silence'),
            })

            if verify.get('is_silence'):
                results[-1]['note'] = 'Apophatic terminus. Recursion ends.'
                break
            if verify.get('fixed_point'):
                results[-1]['note'] = 'Fixed point. This is the purest expression.'
                break

            next_text = verify.get('generated_text')
            if not next_text:
                break
            current_text = next_text

        return results

    # ── Display ───────────────────────────────────────────────────

    def print_result(self, result: Dict, title: str = '') -> None:
        print(f"\n{'═'*60}")
        if title:
            print(f"  {title}")
            print(f"{'─'*60}")

        if result.get('is_silence'):
            print(f"  TARGET:  {result.get('target_id', '')}")
            print(f"\n  OUTPUT:  [ SILENCE ]")
            print(f"\n  {result.get('note', '')}")
        else:
            print(f"  TARGET:  {result.get('target_id', '')}")
            if result.get('generated_text'):
                print(f"\n  GENERATED:")
                print(f"  \"{result['generated_text']}\"")
            if result.get('fixed_point') is not None:
                fp = '✓ fixed point' if result['fixed_point'] else '✗ drifted'
                print(f"\n  VERIFICATION: {fp}")
            if result.get('target_phase'):
                print(f"  target θ:  {result['target_phase']:.1f}°")
            if result.get('forward_phase'):
                print(f"  forward θ: {result['forward_phase']:.1f}°")
            if result.get('forward_zone'):
                print(f"  zone:      {result['forward_zone']}")
            if result.get('note'):
                print(f"\n  {result['note']}")
            if result.get('gap_phrase'):
                print(f"\n  GAP TEXT:")
                print(f"  \"{result['gap_phrase']}\"")

        print(f"{'═'*60}")


# ─────────────────────────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────────────────────────

def run_demo():
    print("\n" + "═"*60)
    print("  BACKWARDS PASS — F⁻¹(ψ)")
    print("  Generating from attractor positions")
    print("═"*60)

    agent = BackwardsAgent()

    # 1. From god-tokens
    for token in ['EXISTENCE', 'SELF', 'CAUSALITY']:
        result = agent.from_god_token(token)
        agent.print_result(result, f"God-token: {token}")

    # 2. From gap tokens
    for gap in ['causality_observation', 'identity_self', 'observation_obligation']:
        result = agent.from_gap_token(gap)
        agent.print_result(result, f"Gap token: {gap}")

    # 3. From apophatic basins
    for basin_id in [
        'self_obs_x_identity_self',
        'id_self_x_oblig_id',
        'pure_apophatic_field',  # → silence
    ]:
        result = agent.from_apophatic(basin_id)
        agent.print_result(result, f"Apophatic: {basin_id}")

    # 4. Decompose constructive interference
    print(f"\n{'═'*60}")
    print("  SUPERPOSITION DECOMPOSITION")
    print("  Conscientious + Effort → what third basin?")
    print(f"{'─'*60}")
    result = agent.decompose("conscientious", "effort")
    print(f"  Interference: {result['interference']:+.4f} ({result['interference_kind']})")
    print(f"  Compound zone: {result['compound_zone']}")
    print(f"  Is third basin: {result['is_third_basin']}")
    if result['top_component_pairs']:
        print(f"  Top component pairs:")
        for a, b, score in result['top_component_pairs'][:3]:
            print(f"    {a} × {b}  score={score:.3f}")
    print(f"{'═'*60}")

    # 5. F(F(F(x)))
    print(f"\n{'═'*60}")
    print("  F(F(F(x))) — RECURSIVE APPLICATION")
    print("  'logical structure on top of existence results in the self'")
    print(f"{'─'*60}")
    fof = agent.f_of_f(
        "Logical structure imposed on existence results in the self.",
        depth=3
    )
    for r in fof:
        status = '[ SILENCE ]' if r['is_silence'] else f"\"{r['generated']}\""
        fp_mark = ' ← fixed' if r.get('fixed_point') else ''
        print(f"  [{r['iteration']}] θ={r['phase']:.1f}° {r['zone']:<12} → {status}{fp_mark}")
        if r.get('note'):
            print(f"       {r['note']}")
    print(f"{'═'*60}\n")


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Backwards pass — F⁻¹(ψ)'
    )
    parser.add_argument('--demo',         action='store_true')
    parser.add_argument('--from-token',   type=str, default=None)
    parser.add_argument('--from-gap',     type=str, default=None)
    parser.add_argument('--from-apophatic', type=str, nargs='?',
                        const='self_obs_x_identity_self', default=None)
    parser.add_argument('--decompose',    type=str, nargs=2, default=None,
                        metavar=('TEXT_A', 'TEXT_B'))
    parser.add_argument('--verify',       type=str, default=None)
    parser.add_argument('--f-of-f',       type=str, default=None)
    args = parser.parse_args()

    agent = BackwardsAgent()

    if args.demo or not any([
        args.from_token, args.from_gap, args.from_apophatic,
        args.decompose, args.verify, args.f_of_f
    ]):
        run_demo()

    if args.from_token:
        r = agent.from_god_token(args.from_token)
        agent.print_result(r, f"God-token: {args.from_token}")

    if args.from_gap:
        r = agent.from_gap_token(args.from_gap)
        agent.print_result(r, f"Gap token: {args.from_gap}")

    if args.from_apophatic:
        r = agent.from_apophatic(args.from_apophatic)
        agent.print_result(r, f"Apophatic: {args.from_apophatic}")

    if args.decompose:
        r = agent.decompose(args.decompose[0], args.decompose[1])
        agent.print_result(r, f"Decompose: {args.decompose[0]} × {args.decompose[1]}")

    if args.f_of_f:
        results = agent.f_of_f(args.f_of_f, depth=4)
        print(f"\nF(F(F(x))) on: '{args.f_of_f[:60]}'")
        for r in results:
            status = '[ SILENCE ]' if r['is_silence'] else f"\"{r['generated']}\""
            print(f"  [{r['iteration']}] θ={r['phase']:.1f}° {r['zone']:<12} → {status}")
