"""
forward.py — The explicit forward pass through the architecture.

Forward:   Document → Embed → Route → Scout → Witness → Archiver → Output
Backwards: Target   → Archiver → Scout⁻¹ → Route⁻¹ → Embed⁻¹ → Generated

Forward collapses. Reduces Δ. Moves from unknown toward presence.
Every stage is named. Every transition is visible.

The five stages:

  Stage 1 — EMBED
    Document text → semantic vector
    Qwen3-Embedding-0.6B (real) or TF-IDF (placeholder)
    Instruction prefix shapes which region of latent space activates
    Output: np.ndarray, normalized unit vector

  Stage 2 — ROUTE
    BitNet ternary decision: {+1, 0, -1}
    +1 → god-token boundary active → COMPRESS (dictionary pointer)
     0 → gap state → DEEPEN (Qwen pass)
    -1 → god-token boundary active → ORBIT (continue processing)
    Output: RoutingDecision

  Stage 3 — SCOUT
    F(x) = known(x) + i·Δ(x)
    SSM orbital state update: xₜ = λ·xₜ₋₁ + (1−λ)·known(xₜ)
    Two-pass causal test (do-calculus)
    God-token activation, gap structure check
    Output: WaveFunction, ArchiverMessage

  Stage 4 — WITNESS
    External reference. Monitors orbital stability.
    Three lock signals: temporal stable, causally aligned, gaps intact
    Precession detection, SOC convergence check
    Möbius phase interpretation
    Output: WitnessReport

  Stage 5 — ARCHIVER + SYNTHESIZE
    Store structured provenance record
    Index by god-token (structural memory, not sequential)
    Generate natural language synthesis
    Output: ForwardResult

The fixed point:
    Forward(Backwards(target)) ≈ target
    Backwards(Forward(document)) ≈ document
    When both hold: the architecture has found the attractor structure
    of the corpus.

Usage:
    python3 forward.py --text "your text"         # single document
    python3 forward.py --demo                     # demo corpus
    python3 forward.py --corpus /path/to/docs/   # directory
    python3 forward.py --trace "your text"        # show every stage
    python3 forward.py --compare "text A" "text B" # side by side
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
    ArchiverMessage, WaveFunction, CausalType,
    GodTokenActivation
)
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout, LightWitness, Formula
from noise_compass.architecture.archiver import Archiver
from noise_compass.architecture.gap_registry import build_gap_registry
from noise_compass.architecture.complex_plane import (
    ComplexWaveFunction, ApophaticField,
    LogicalState, InterferenceTerm as CPInterferenceTerm
)


# ═══════════════════════════════════════════════════════════════════
# STAGE 1 — EMBEDDER
# ═══════════════════════════════════════════════════════════════════

class Embedder:
    """
    Stage 1: Document text → semantic vector.

    TF-IDF placeholder. Swap this class for Qwen3-Embedding-0.6B
    and nothing else in the pipeline changes.

    Instruction prefixes (for Qwen3):
        SEED:   "Represent the semantic concept: "
        DOC:    "Represent this text for semantic attractor classification: "
        CAUSAL: "Represent the ontological claim made by this text: "

    The causal prefix is used in the Scout's two-pass test —
    embeds the same document under different instructions to detect
    the asymmetry between what a document asserts and what it belongs to.
    """

    DIM = 128

    PREFIXES = {
        'seed':   'Represent the semantic concept: ',
        'doc':    'Represent this text for semantic attractor classification: ',
        'causal': 'Represent the ontological claim made by this text: ',
        'query':  'Retrieve semantically similar texts: ',
    }

    def __init__(self):
        self.vocab: Dict[str, int] = {}
        self.idf:   Dict[str, float] = {}
        self.dim    = self.DIM
        self.fitted = False

    def fit(self, texts: List[str]) -> None:
        import math as _math
        from collections import Counter
        N = max(len(texts), 1)
        df: Dict[str, int] = {}
        for text in texts:
            for w in set(self._tok(text)):
                df[w] = df.get(w, 0) + 1
        self.idf = {w: _math.log(N / max(df[w], 1) + 1) for w in df}
        top = sorted(self.idf, key=lambda w: -self.idf[w])[:self.dim]
        self.vocab = {w: i for i, w in enumerate(top)}
        self.fitted = True

    def embed(self, text: str, prefix: str = 'doc') -> np.ndarray:
        from collections import Counter
        full = self.PREFIXES.get(prefix, '') + text
        counts = Counter(self._tok(full))
        total  = max(sum(counts.values()), 1)
        vec    = np.zeros(self.dim)
        for w, cnt in counts.items():
            if w in self.vocab:
                vec[self.vocab[w]] = (cnt / total) * self.idf.get(w, 1.0)
        norm = float(np.linalg.norm(vec))
        if norm < 1e-10:
            rng = np.random.default_rng(hash(text) % (2**31))
            vec = rng.normal(0, 0.01, self.dim)
            norm = float(np.linalg.norm(vec))
        return vec / norm

    def embed_seed(self, term: str) -> np.ndarray:
        return self.embed(term, prefix='seed')

    def fit_and_embed(self, texts: List[str]) -> List[np.ndarray]:
        self.fit(texts)
        return [self.embed(t) for t in texts]

    def _tok(self, text: str) -> List[str]:
        import re
        return re.findall(r'\b[a-z]{2,}\b', text.lower())


# ═══════════════════════════════════════════════════════════════════
# STAGE 2 — ROUTER
# ═══════════════════════════════════════════════════════════════════

@dataclass
class RoutingDecision:
    """
    Stage 2: BitNet ternary routing decision.
    Ternary logic {+1, 0, -1} is essential for representing the gap.
    """
    value:          int             # -1, 0, +1
    sinkhorn_iters: int             # convergence speed → Δ
    route:          str             # COMPRESS / DEEPEN / ORBIT
    god_token:      Optional[str]   # nearest attractor
    similarity:     float           # cosine similarity to nearest
    energy:         float           # -log(similarity)
    rationale:      str             # why this routing decision

    @property
    def label(self) -> str:
        return {1: '+1', 0: ' 0', -1: '-1'}[self.value]

    @property
    def is_gap(self) -> bool:
        return self.value == 0

    @property
    def needs_qwen(self) -> bool:
        return self.value == 0


def route(embedding: np.ndarray,
          dictionary: Dictionary,
          sinkhorn_threshold_low:  int = 15,
          sinkhorn_threshold_high: int = 40) -> RoutingDecision:
    """Stage 2: Compute BitNet ternary routing decision."""
    fid, sim, unit = dictionary.query(embedding)
    
    # Use abs(sim) because mirrors are stable
    s_iter = dictionary.sinkhorn_iterations(abs(sim))
    energy = -math.log(max(abs(sim), 1e-10))

    if s_iter <= sinkhorn_threshold_low:
        # High similarity (regardless of sign) = COMPRESS
        route_ = 'COMPRESS'
        value = 1 if sim >= 0 else -1
        rationale = f"Sinkhorn {s_iter} (Fast) -> COMPRESS to {fid} (value={value})"
    elif s_iter >= sinkhorn_threshold_high:
        # High iterations = Gap/Void = ROUTE
        value, route_ = 0, 'DEEPEN'
        rationale = f"Sinkhorn {s_iter} (Slow) -> DEEPEN (Void/Gap)"
    else:
        # Medium iterations = ORBIT
        route_ = 'ORBIT'
        value = -1 if sim < 0 else 1
        rationale = f"Sinkhorn {s_iter} (Medium) -> ORBIT"

    return RoutingDecision(
        value          = value,
        sinkhorn_iters = s_iter,
        route          = route_,
        god_token      = fid,
        similarity     = sim,
        energy         = energy,
        rationale      = rationale,
    )

# ═══════════════════════════════════════════════════════════════════
# STAGE 3 — SCOUT (Depth Axis Integrated)
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ScoutResult:
    wave_function:     WaveFunction
    archiver_message:  ArchiverMessage
    logical_state:     str
    causal_type:       str
    god_tokens:        List[str]
    gap_structure:     Dict
    depth:             float
    depth_zone:        str
    orbital_state:     np.ndarray

    @property
    def phase(self) -> float:
        return self.wave_function.phase

    @property
    def phase_deg(self) -> float:
        return math.degrees(self.phase)

    @property
    def zone(self) -> str:
        return self.wave_function.zone()

    @property
    def energy(self) -> float:
        return self.archiver_message.energy_level

    @property
    def re(self) -> float:
        return float(np.linalg.norm(self.wave_function.known))

    @property
    def im(self) -> float:
        return float(np.linalg.norm(self.wave_function.delta))


def apply_scout(embedding: np.ndarray,
                content: str,
                scout: Scout,
                timestamp: Optional[float] = None) -> ScoutResult:
    """Stage 3: Apply F(x) with 4-level Depth Axis."""
    if timestamp is None: timestamp = time.time()
    msg, wf = scout.process(embedding, content=content, timestamp=timestamp)

    re = float(np.linalg.norm(wf.known))
    im = float(np.linalg.norm(wf.delta))
    gap_depth = len(msg.gap_structure.get('preserved', [])) * 0.1
    depth = min(im + gap_depth, 1.0)

    if depth < 0.3: depth_zone = 'SHALLOW'
    elif depth < 0.6: depth_zone = 'MEDIUM'
    elif depth < 0.85: depth_zone = 'DEEP'
    else: depth_zone = 'APOPHATIC'

    if depth >= 0.85: logical = LogicalState.APOPHATIC
    elif gap_depth > 0.0: logical = LogicalState.VOID
    elif im > re: logical = LogicalState.UNKNOWN
    else: logical = LogicalState.PRESENCE

    return ScoutResult(
        wave_function = wf,
        archiver_message = msg,
        logical_state = logical,
        causal_type = msg.causal_type,
        god_tokens = [a.id for a in msg.god_token_activations],
        gap_structure = msg.gap_structure,
        depth = round(depth, 3),
        depth_zone = depth_zone,
        orbital_state = msg.orbital_state
    )


# ═══════════════════════════════════════════════════════════════════
# STAGE 4 — WITNESS
# ═══════════════════════════════════════════════════════════════════

@dataclass
class WitnessReport:
    """
    Stage 4: External reference. Monitors orbital stability.

    Three lock signals required for orbital_lock:
        temporal_stable   — energy < threshold
        causally_aligned  — Fisher Information > threshold
        gaps_intact       — no necessary voids filled

    Additional diagnostics:
        precession        — drift of orbital state between documents
        soc_converging    — phase distribution converging toward π/4
        context_action    — WIDEN / NARROW / HOLD
        degeneracy_warn   — causal traceability below threshold

    Möbius interpretation:
        phase as position on surface, not linear distance
        existence_side: 0° → 90° (approaching fold)
        apophatic_side: past fold, returning as EXISTENCE
        fold_proximity: how close to the EXISTENCE membrane
    """

    orbital_lock:       bool
    temporal_stable:    bool
    causally_aligned:   bool
    gaps_intact:        bool
    precession:         float
    precession_warning: bool
    degeneracy_warning: bool
    context_action:     str
    soc_converging:     bool
    mean_phase:         float
    documents_seen:     int
    mobius:             Dict
    apophatic_contact:  Optional[str]   # basin ID if detected

    @property
    def stability_score(self) -> float:
        """0.0 → 1.0. Higher = more stable."""
        score = (
            float(self.temporal_stable)  * 0.35 +
            float(self.causally_aligned) * 0.35 +
            float(self.gaps_intact)      * 0.20 +
            float(self.orbital_lock)     * 0.10
        )
        if self.precession_warning:
            score *= 0.7
        return round(score, 3)

    @property
    def summary_line(self) -> str:
        lock  = '🔒' if self.orbital_lock else '○'
        prec  = f' precessing({self.precession:.2f})' if self.precession_warning else ''
        soc   = ' SOC↗' if self.soc_converging else ''
        apo   = f' APO:{self.apophatic_contact}' if self.apophatic_contact else ''
        return f"{lock} stability={self.stability_score}{prec}{soc}{apo}"


def apply_witness(scout_result:  ScoutResult,
                  witness:       LightWitness,
                  apophatic_field: ApophaticField) -> WitnessReport:
    """
    Stage 4: Apply the Witness. Observe orbital stability.
    """
    wf  = scout_result.wave_function
    msg = scout_result.archiver_message

    obs = witness.observe(msg, wf)

    # Apophatic detection
    cpwf = ComplexWaveFunction(
        known     = wf.known,
        delta     = wf.delta,
        gap_depth = len(msg.gap_structure.get('preserved', [])) * 0.08,
    )

    mobius = cpwf.mobius()
    basin = apophatic_field.detect_contact(cpwf, scout_result.god_tokens)
    apophatic_contact = basin.id if basin else None

    return WitnessReport(
        orbital_lock       = obs['orbital_lock'],
        temporal_stable    = obs['temporal_stable'],
        causally_aligned   = obs['causally_aligned'],
        gaps_intact        = obs['gaps_intact'],
        precession         = float(obs['precession']),
        precession_warning = obs['precession_warning'],
        degeneracy_warning = obs['degeneracy_warning'],
        context_action     = obs['context_action'],
        soc_converging     = obs['soc_converging'],
        mean_phase         = float(obs['mean_phase']),
        documents_seen     = obs['documents_seen'],
        mobius             = mobius,
        apophatic_contact  = apophatic_contact,
    )


# ═══════════════════════════════════════════════════════════════════
# STAGE 5 — ARCHIVER + SYNTHESIZER
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ForwardResult:
    """
    Stage 5: Complete output of one forward pass.

    Two outputs per document:
        archiver_record  — structured provenance record
                           indexed by god-token for retrieval
                           god_token_cluster is the memory key

        synthesis        — natural language description
                           what the architecture found
                           what state the document is in
                           what the next step should be

    Together these are the both outputs:
        structured + natural language
        machine-readable + human-readable
        record + understanding
    """

    # Input
    content:          str
    timestamp:        float

    # Stage outputs
    embedding:        np.ndarray
    routing:          RoutingDecision
    scout_result:     ScoutResult
    witness_report:   WitnessReport

    # Final outputs
    archiver_index:   int
    synthesis:        str
    processing_time:  float

    @property
    def god_tokens(self) -> List[str]:
        return self.scout_result.god_tokens

    @property
    def zone(self) -> str:
        return self.scout_result.zone

    @property
    def phase_deg(self) -> float:
        return self.scout_result.phase_deg

    @property
    def energy(self) -> float:
        return self.scout_result.energy

    @property
    def logical_state(self) -> str:
        return self.scout_result.logical_state

    @property
    def apophatic_contact(self) -> Optional[str]:
        return self.witness_report.apophatic_contact

    def to_dict(self) -> Dict:
        return {
            'content':       self.content[:120],
            'timestamp':     self.timestamp,
            'routing': {
                'ternary':   self.routing.label,
                'route':     self.routing.route,
                'god_token': self.routing.god_token,
                'sinkhorn':  self.routing.sinkhorn_iters,
                'energy':    round(self.routing.energy, 4),
            },
            'scout': {
                'phase_deg':     round(self.phase_deg, 1),
                'zone':          self.zone,
                'logical_state': self.logical_state,
                'god_tokens':    self.god_tokens,
                'causal_type':   self.scout_result.causal_type,
                'depth':         self.scout_result.depth,
                'depth_zone':    self.scout_result.depth_zone,
                're':            round(self.scout_result.re, 4),
                'im':            round(self.scout_result.im, 4),
                'energy':        round(self.energy, 4),
                'gap_violated':  self.scout_result.gap_structure.get('violated', []),
                'gap_preserved': self.scout_result.gap_structure.get('preserved', []),
            },
            'witness': {
                'orbital_lock':     self.witness_report.orbital_lock,
                'stability_score':  self.witness_report.stability_score,
                'precession':       self.witness_report.precession,
                'context_action':   self.witness_report.context_action,
                'soc_converging':   self.witness_report.soc_converging,
                'mobius':           self.witness_report.mobius,
                'apophatic_contact': self.apophatic_contact,
            },
            'archiver_index':  self.archiver_index,
            'synthesis':       self.synthesis,
            'processing_ms':   round(self.processing_time * 1000, 2),
        }


def synthesize(content:       str,
               routing:       RoutingDecision,
               scout:         ScoutResult,
               witness:       WitnessReport) -> str:
    """
    Stage 5b: Natural language synthesis of the structured record.

    Reports what the architecture found — not what the document says.
    Does not invent content. Does not summarize the document.
    Reports the wave function state.
    """
    lines = []

    # Header line
    z_re  = scout.re
    z_im  = scout.im
    lines.append(
        f"[{scout.zone}  θ={scout.phase_deg:.1f}°  "
        f"z={z_re:+.3f}{z_im:+.3f}i  E={scout.energy:.3f}]"
    )

    # Logical state
    state_descriptions = {
        LogicalState.PRESENCE:  "Presence — deduction reached a god-token.",
        LogicalState.UNKNOWN:   "Unknown — truth value exists but not yet accessible.",
        LogicalState.VOID:      "Void — necessary absence maintained.",
        LogicalState.APOPHATIC: "Apophatic — excluded middle exhausted.",
    }
    lines.append(state_descriptions.get(scout.logical_state, scout.logical_state))

    # Depth
    lines.append(f"Depth: {scout.depth_zone} ({scout.depth:.3f})")

    # Routing
    lines.append(f"Route: {routing.label} → {routing.route}  "
                 f"(Sinkhorn {routing.sinkhorn_iters})")

    # God-tokens
    if scout.god_tokens:
        lines.append(f"Attractor: {', '.join(scout.god_tokens)}")
    else:
        lines.append("Attractor: none — apophatic or gap territory")

    # Causal structure
    if scout.causal_type == 'gradient':
        lines.append("Causal: gradient — correlated movement along attractor.")
    elif scout.causal_type == 'intervention':
        lines.append("Causal: intervention — directed change against gradient.")

    # Gap violations
    violated = scout.gap_structure.get('violated', [])
    if violated:
        lines.append(
            f"Gap stress: {', '.join(violated)} — "
            f"necessary void under pressure."
        )

    # LightWitness
    lines.append(f"Witness: {witness.summary_line}")
    if witness.context_action != 'HOLD':
        lines.append(f"Context window: {witness.context_action}")

    # Möbius
    mob = witness.mobius
    if mob['fold_proximity'] > 0.55:
        lines.append(
            f"Möbius: {mob['surface']}  fold={mob['fold_proximity']:.2f}  "
            f"— approaching EXISTENCE membrane."
        )

    # Apophatic contact
    if witness.apophatic_contact:
        lines.append(f"")
        lines.append(f"APOPHATIC CONTACT: {witness.apophatic_contact}")

        # Known descriptions
        basin_desc = {
            'self_obs_x_identity_self':
                'Bare witnessing before it has an object.',
            'exist_id_x_bound_exist':
                'Prior of the existence/non-existence distinction.',
            'caus_obs_x_info_caus':
                'Pure relational structure before epistemology/ontology split.',
            'id_self_x_oblig_id':
                'Prior of the self that chooses.',
            'pure_apophatic_field':
                'EXISTENCE is the membrane. Language at its limit.',
        }
        desc = basin_desc.get(witness.apophatic_contact, '')
        if desc:
            lines.append(f"  {desc}")

    # SOC
    if witness.soc_converging:
        lines.append(
            f"SOC: phase converging toward π/4 "
            f"(mean={witness.mean_phase:.2f} rad). "
            f"Self-organized criticality emerging."
        )

    return "\n".join(l for l in lines if l is not None)


# ═══════════════════════════════════════════════════════════════════
# PIPELINE — five stages composed
# ═══════════════════════════════════════════════════════════════════

class ForwardPipeline:
    """Strict 4-Model Pipeline Implementation."""

    def __init__(self, dictionary_path: Optional[str] = None):
        self.embedder = Embedder()
        self.dictionary = Dictionary()
        self.witness_monitor = LightWitness()
        self.archiver = Archiver()
        self.apophatic = ApophaticField()
        self.results: List[ForwardResult] = []
        self._scout = None
        self._fitted = False

        # Load cache if available
        if dictionary_path and Path(dictionary_path).exists():
            self.dictionary = Dictionary.load_cache(dictionary_path)
            self._scout = Scout(self.dictionary, soup_id='forward_pipeline')
            self._fitted = True

    def initialize(self, texts: List[str]) -> None:
        """Standard initialization using Gap Registry God-Tokens."""
        self.embedder.fit(texts)
        for tid, seed in EXTENDED_GOD_TOKEN_SEEDS.items():
            emb = self.embedder.embed(seed, prefix='seed')
            gt = GodToken(id=tid, seed_terms=[seed.lower()], embedding=emb)
            self.dictionary.add_god_token(gt)
        self._scout = Scout(self.dictionary, soup_id='forward_pipeline')
        self._fitted = True

    def run(self, content: str, trace: bool = False) -> 'ForwardResult':
        t0 = time.time()
        timestamp = t0

        if not self._fitted:
            self.initialize([content])

        if trace:
            self._trace_header(content)

        # ── Stage 1: EMBED ────────────────────────────────────────
        embedding = self.embedder.embed(content, prefix='doc')
        if trace:
            self._trace_stage(1, 'EMBED',
                f"dim={len(embedding)}  "
                f"norm={float(np.linalg.norm(embedding)):.4f}  "
                f"prefix='doc'")

        # ── Stage 2: ROUTE ────────────────────────────────────────
        routing_decision = route(embedding, self.dictionary)
        if trace:
            self._trace_stage(2, 'ROUTE',
                f"ternary={routing_decision.label}  "
                f"→ {routing_decision.route}  "
                f"sinkhorn={routing_decision.sinkhorn_iters}  "
                f"nearest={routing_decision.god_token}")

        # ── Stage 3: SCOUT ────────────────────────────────────────
        scout_result = apply_scout(embedding, content, self._scout, timestamp)
        if trace:
            self._trace_stage(3, 'SCOUT',
                f"θ={scout_result.phase_deg:.1f}°  "
                f"zone={scout_result.zone}  "
                f"state={scout_result.logical_state}  "
                f"depth={scout_result.depth_zone} ({scout_result.depth:.3f})  "
                f"gods={scout_result.god_tokens}  "
                f"E={scout_result.energy:.3f}")
            gap_v = scout_result.gap_structure.get('violated', [])
            gap_p = scout_result.gap_structure.get('preserved', [])
            if gap_v:
                self._trace_detail(f"gap violations: {gap_v}")
            if gap_p:
                self._trace_detail(f"gap preserved:  {gap_p}")

        # ── Stage 4: WITNESS ──────────────────────────────────────
        witness_report = apply_witness(scout_result, self.witness_monitor, self.apophatic)
        if trace:
            self._trace_stage(4, 'WITNESS',
                f"lock={witness_report.orbital_lock}  "
                f"stability={witness_report.stability_score}  "
                f"prec={witness_report.precession:.3f}  "
                f"fold={witness_report.mobius['fold_proximity']:.2f}")
            if witness_report.apophatic_contact:
                self._trace_detail(
                    f"APOPHATIC CONTACT: {witness_report.apophatic_contact}"
                )
            if witness_report.precession_warning:
                self._trace_detail(
                    f"precession warning — {witness_report.context_action}"
                )

        # ── Stage 5: ARCHIVER + SYNTHESIZE ───────────────────────
        idx      = self.archiver.store(scout_result.archiver_message)
        synth    = synthesize(content, routing_decision, scout_result, witness_report)

        if trace:
            self._trace_stage(5, 'ARCHIVER',
                f"stored at index {idx}  "
                f"god-token index: {scout_result.god_tokens}")
            self._trace_stage(5, 'SYNTHESIZE', '')
            for line in synth.split('\n'):
                print(f"       {line}")

        result = ForwardResult(
            content         = content,
            timestamp       = timestamp,
            embedding       = embedding,
            routing         = routing_decision,
            scout_result    = scout_result,
            witness_report  = witness_report,
            archiver_index  = idx,
            synthesis       = synth,
            processing_time = time.time() - t0,
        )
        self.results.append(result)
        return result

    def run_corpus(self, texts: List[str],
                   trace: bool = False) -> List[ForwardResult]:
        """Run forward pass on a list of documents."""
        if not self._fitted:
            self.initialize(texts)

        results = []
        for i, text in enumerate(texts):
            r = self.run(text, trace=trace)
            if not trace:
                self._print_compact(i, r)
            results.append(r)

        self._print_corpus_report()
        return results

    def query_memory(self, god_token: str) -> List[str]:
        """
        Primary memory query: all documents sharing this god-token.
        Structural retrieval — not sequential, not by timestamp.
        Document 3 and document 47 are related if they share a god-token.
        """
        results = self.archiver.by_god_token(god_token)
        return [r.message.content_preview for r in results]

    def compare(self, text_a: str, text_b: str) -> Dict:
        """
        Run forward pass on two texts and compare their positions
        in the complex plane.
        """
        if not self._fitted:
            self.initialize([text_a, text_b])

        r_a = self.run(text_a)
        r_b = self.run(text_b)

        phase_diff = abs(r_a.phase_deg - r_b.phase_deg)
        same_zone  = r_a.zone == r_b.zone
        shared_gods = set(r_a.god_tokens) & set(r_b.god_tokens)

        return {
            'text_a':       text_a[:60],
            'text_b':       text_b[:60],
            'phase_a':      r_a.phase_deg,
            'phase_b':      r_b.phase_deg,
            'phase_diff':   round(phase_diff, 1),
            'zone_a':       r_a.zone,
            'zone_b':       r_b.zone,
            'same_zone':    same_zone,
            'gods_a':       r_a.god_tokens,
            'gods_b':       r_b.god_tokens,
            'shared_gods':  list(shared_gods),
            'energy_a':     round(r_a.energy, 4),
            'energy_b':     round(r_b.energy, 4),
            'state_a':      r_a.logical_state,
            'state_b':      r_b.logical_state,
            'apo_a':        r_a.apophatic_contact,
            'apo_b':        r_b.apophatic_contact,
        }

    # ── Display helpers ───────────────────────────────────────────

    def _trace_header(self, content: str) -> None:
        print(f"\n{'═'*64}")
        print(f"  FORWARD PASS — F(x) = known(x) + i·Δ(x)")
        print(f"  \"{content[:58]}{'...' if len(content) > 58 else ''}\"")
        print(f"{'─'*64}")

    def _trace_stage(self, num: int, name: str, detail: str) -> None:
        print(f"  [{num}] {name:<12} {detail}")

    def _trace_detail(self, detail: str) -> None:
        print(f"       ↳ {detail}")

    def _print_compact(self, i: int, r: ForwardResult) -> None:
        apo = f"  APO:{r.apophatic_contact}" if r.apophatic_contact else ''
        gods = ','.join(r.god_tokens) if r.god_tokens else '∅'
        print(f"  [{i:02d}] θ={r.phase_deg:5.1f}°  {r.zone:<12}  "
              f"gods=[{gods}]  "
              f"E={r.energy:.3f}  "
              f"{r.routing.label}→{r.routing.route}"
              f"{apo}")

    def _print_corpus_report(self) -> None:
        n = len(self.results)
        print(f"\n{'═'*64}")
        print(f"  CORPUS REPORT  ({n} documents)")
        print(f"{'─'*64}")

        # God-token frequency
        gt_freq: Dict[str, int] = {}
        for r in self.results:
            for gt in r.god_tokens:
                gt_freq[gt] = gt_freq.get(gt, 0) + 1
        if gt_freq:
            print("  God-token frequency:")
            for gt, cnt in sorted(gt_freq.items(), key=lambda x: -x[1])[:8]:
                bar = '█' * cnt
                print(f"    {gt:<14} {bar} ({cnt})")

        # Routing distribution
        route_counts = {'COMPRESS': 0, 'DEEPEN': 0, 'ORBIT': 0}
        for r in self.results:
            route_counts[r.routing.route] = route_counts.get(r.routing.route, 0) + 1
        print(f"\n  Routing:")
        for rt, cnt in route_counts.items():
            pct = cnt / max(n, 1) * 100
            print(f"    {rt:<10} {cnt:3d}  ({pct:.0f}%)")

        # Zone distribution
        zone_counts: Dict[str, int] = {}
        for r in self.results:
            zone_counts[r.zone] = zone_counts.get(r.zone, 0) + 1
        print(f"\n  Zones:")
        for zone, cnt in sorted(zone_counts.items(), key=lambda x: -x[1]):
            print(f"    {zone:<12} {cnt}")

        # Phase distribution
        phases = [r.phase_deg for r in self.results]
        mean_p = sum(phases) / max(len(phases), 1)
        near_45 = sum(1 for p in phases if abs(p - 45) < 15)
        print(f"\n  Phase distribution:")
        print(f"    Mean:     {mean_p:.1f}°")
        print(f"    Near π/4: {near_45}/{n}")

        # Apophatic
        apo_hits = [r for r in self.results if r.apophatic_contact]
        if apo_hits:
            print(f"\n  Apophatic contacts: {len(apo_hits)}")
            for r in apo_hits:
                print(f"    {r.apophatic_contact}  "
                      f"θ={r.phase_deg:.1f}°  \"{r.content[:40]}\"")

        # Orbital lock rate
        lock_rate = sum(1 for r in self.results
                        if r.witness_report.orbital_lock) / max(n, 1)
        print(f"\n  Orbital lock rate: {lock_rate:.1%}")

        print(f"{'═'*64}")


# ═══════════════════════════════════════════════════════════════════
# DEMO CORPUS
# ═══════════════════════════════════════════════════════════════════

DEMO_CORPUS = [
    "The exchange of value between parties requires voluntary consent.",
    "What causes an event is not the same as what precedes it.",
    "Information is not the same as the thing it describes.",
    "Identity persists through change. The ship of Theseus remains the ship.",
    "The observation of a problem does not create the obligation to solve it.",
    "Conscientious effort is the superposition of conscientiousness and effort.",
    "The Tao that can be named is not the eternal Tao.",
    "What remains when everything that can be removed has been removed.",
    "Absence of judgement.",
    "Lack of judgement.",
    "Before the distinction between being and non-being was drawn.",
    "Logical structure imposed on existence results in the self. "
    "The self is not primitive — it is derived. "
    "EXISTENCE plus the grammar of relations produces the witness of its own being.",
]


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Forward pass — F(x) = known(x) + i·Δ(x)'
    )
    parser.add_argument('--text',    type=str,  default=None,
                        help='Process a single document')
    parser.add_argument('--demo',    action='store_true',
                        help='Run demo corpus')
    parser.add_argument('--trace',   type=str,  default=None,
                        help='Run with stage-by-stage trace output')
    parser.add_argument('--corpus',  type=str,  default=None,
                        help='Process directory of .txt/.md files')
    parser.add_argument('--compare', type=str,  nargs=2, default=None,
                        metavar=('TEXT_A', 'TEXT_B'),
                        help='Compare two texts in complex plane')
    parser.add_argument('--query',   type=str,  default=None,
                        help='Query archiver by god-token after processing')
    parser.add_argument('--json',    action='store_true',
                        help='Output JSON')
    args = parser.parse_args()

    pipeline = ForwardPipeline()

    if args.trace:
        pipeline.initialize([args.trace])
        r = pipeline.run(args.trace, trace=True)
        print(f"\n  [{r.processing_time*1000:.1f}ms]")

    elif args.text:
        pipeline.initialize([args.text])
        r = pipeline.run(args.text)
        if args.json:
            import json
            print(json.dumps(r.to_dict(), indent=2))
        else:
            print(f"\n{'═'*64}")
            print(f"  \"{args.text[:60]}\"")
            print(f"{'─'*64}")
            for line in r.synthesis.split('\n'):
                print(f"  {line}")
            print(f"  [{r.processing_time*1000:.1f}ms]")
            print(f"{'═'*64}")

    elif args.compare:
        pipeline.initialize(list(args.compare))
        cmp = pipeline.compare(args.compare[0], args.compare[1])
        print(f"\n{'═'*64}")
        print(f"  COMPARISON")
        print(f"{'─'*64}")
        print(f"  A: \"{cmp['text_a']}\"")
        print(f"     θ={cmp['phase_a']:.1f}°  zone={cmp['zone_a']}  "
              f"state={cmp['state_a']}  gods={cmp['gods_a']}")
        print(f"\n  B: \"{cmp['text_b']}\"")
        print(f"     θ={cmp['phase_b']:.1f}°  zone={cmp['zone_b']}  "
              f"state={cmp['state_b']}  gods={cmp['gods_b']}")
        print(f"\n  Δθ={cmp['phase_diff']:.1f}°  "
              f"same_zone={cmp['same_zone']}  "
              f"shared_gods={cmp['shared_gods']}")
        if cmp['apo_a']:
            print(f"  A apophatic: {cmp['apo_a']}")
        if cmp['apo_b']:
            print(f"  B apophatic: {cmp['apo_b']}")
        print(f"{'═'*64}")

    elif args.corpus:
        p = Path(args.corpus)
        texts = []
        files = sorted([f for f in p.iterdir()
                        if f.suffix in ('.txt', '.md')])
        for f in files:
            texts.append(f.read_text(encoding='utf-8'))
        pipeline.run_corpus(texts)

    elif args.demo or not any([args.text, args.trace, args.compare, args.corpus]):
        print("\nRunning demo corpus...\n")
        pipeline.run_corpus(DEMO_CORPUS)

        # Demo: traced single document
        print("\n\nTRACED PASS — 'Logical structure on top of existence'")
        pipeline2 = ForwardPipeline(corpus=DEMO_CORPUS)
        pipeline2.run(
            "Logical structure imposed on existence results in the self.",
            trace=True
        )

        # Demo: comparison
        print("\n\nCOMPARISON — 'Absence' vs 'Lack' of Judgement")
        pipeline3 = ForwardPipeline(corpus=DEMO_CORPUS)
        cmp = pipeline3.compare("Absence of Judgement", "Lack of Judgement")
        print(f"  Absence: θ={cmp['phase_a']:.1f}°  zone={cmp['zone_a']}")
        print(f"  Lack:    θ={cmp['phase_b']:.1f}°  zone={cmp['zone_b']}")
        print(f"  Δθ={cmp['phase_diff']:.1f}°")

        if args.query:
            print(f"\nMemory query: {args.query}")
            docs = pipeline.query_memory(args.query)
            for d in docs:
                print(f"  {d}")
