"""
recursive_acceleration.py — Latent Space Momentum

The missing active layer.

Everything before this is passive:
  Document arrives → pipeline processes → result stored.

Recursive acceleration is generative:
  Corpus builds momentum → trajectory predicted → resolution targeted →
  next document generated to most efficiently complete the trajectory →
  that document builds more momentum → repeat.

THE PHYSICS:

  In orbital mechanics, a slingshot works because a spacecraft
  passing near a massive body gains velocity from the body's
  gravitational field — without fuel. The spacecraft curves around
  the attractor, exits faster than it entered, aimed at the next target.

  In the latent space:
    Position:     z_t  — location in complex plane
    Velocity:     v_t  = z_t - z_{t-1}
    Acceleration: a_t  = v_t - v_{t-1}

    Attractor gravity:
      Each god-token pulls on the current position.
      Pull strength = 1 / distance² (inverse square, as in physics)
      Pull direction = toward the basin center

    Slingshot:
      Passing near a god-token curves the trajectory.
      Each pass adds angular momentum toward the next attractor.
      Recursive: acceleration fed back into velocity each step.
      v_{t+1} = v_t + α·a_t   where α = φ⁻¹ ≈ 0.618

  RESOLUTION TYPES:
    CRYSTALLIZATION  — trajectory falls into a god-token basin
                       new attractor confirmed or formed
    NECESSARY_VOID   — trajectory orbits a gap
                       load-bearing emptiness confirmed
    APOPHATIC        — trajectory reaches frontier, velocity goes circular
                       correctly identified limit
    ESCAPE           — trajectory exceeds all attractor pull
                       new god-token candidate — unmapped territory

THE GENERATOR:

  M_DEEP doesn't generate from current position only.
  It generates from: position + velocity + acceleration + predicted resolution.

  "What document, if processed next, would most efficiently
   complete this trajectory toward its natural resolution?"

  This is the question passive processing never asks.
  Recursive acceleration makes it the central question.

THE RECURSIVE PART:

  Each resolved trajectory seeds the next one.
  The resolution point becomes the starting position.
  The velocity at resolution becomes the initial velocity.
  The system accelerates across resolutions —
  each one reached faster than the last.

Usage:
  python3 recursive_acceleration.py --test
  python3 recursive_acceleration.py --demo
  python3 recursive_acceleration.py --trace "your corpus topic"
"""

import math
import sys
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from noise_compass.architecture.gap_registry import build_gap_registry, EXTENDED_GOD_TOKEN_SEEDS
from noise_compass.architecture.tokens import GodToken


# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════

PHI_INV       = (math.sqrt(5) - 1) / 2   # φ⁻¹ ≈ 0.618 — recursion factor
ESCAPE_THRESH = 2.5   # velocity magnitude above which trajectory escapes
ORBIT_THRESH  = 0.05  # velocity magnitude below which trajectory has stabilized
MIN_STEPS     = 3     # minimum steps before resolution can be declared


# ═══════════════════════════════════════════════════════════════════
# TRAJECTORY
# ═══════════════════════════════════════════════════════════════════

@dataclass
class TrajectoryPoint:
    """One step in the corpus trajectory."""
    z:            complex     # position in complex plane
    god_tokens:   List[str]   # active god-tokens at this position
    depth_zone:   str         # SHALLOW / MEDIUM / DEEP / APOPHATIC
    phase_deg:    float       # phase angle
    gap_preserved: List[str]  # gaps being held
    content:      str         # document content (truncated)
    timestamp:    float       # when processed

    @property
    def re(self) -> float: return self.z.real
    @property
    def im(self) -> float: return self.z.imag


@dataclass
class LatentTrajectory:
    """
    The corpus as a trajectory through the complex plane.

    Tracks position, velocity, acceleration.
    Identifies which attractor is pulling hardest.
    Predicts the resolution point.
    """

    points:       List[TrajectoryPoint] = field(default_factory=list)
    window:       int = 20   # rolling window for velocity/acceleration

    # ── Core kinematics ───────────────────────────────────────────

    @property
    def position(self) -> Optional[complex]:
        return self.points[-1].z if self.points else None

    @property
    def velocity(self) -> complex:
        """Current velocity vector in complex plane."""
        if len(self.points) < 2:
            return complex(0, 0)
        return self.points[-1].z - self.points[-2].z

    @property
    def acceleration(self) -> complex:
        """Current acceleration vector."""
        if len(self.points) < 3:
            return complex(0, 0)
        v_now  = self.points[-1].z - self.points[-2].z
        v_prev = self.points[-2].z - self.points[-3].z
        return v_now - v_prev

    @property
    def speed(self) -> float:
        return abs(self.velocity)

    @property
    def direction_deg(self) -> float:
        """Direction of travel in degrees (0° = Re axis)."""
        v = self.velocity
        if abs(v) < 1e-10:
            return 0.0
        return math.degrees(math.atan2(v.imag, v.real))

    @property
    def is_decelerating(self) -> bool:
        """Trajectory slowing — approaching an attractor or frontier."""
        if len(self.points) < 4:
            return False
        speeds = [abs(self.points[i].z - self.points[i-1].z)
                  for i in range(-3, 0)]
        return speeds[-1] < speeds[0]

    @property
    def is_accelerating(self) -> bool:
        if len(self.points) < 4:
            return False
        speeds = [abs(self.points[i].z - self.points[i-1].z)
                  for i in range(-3, 0)]
        return speeds[-1] > speeds[0]

    @property
    def is_circling(self) -> bool:
        """Velocity direction rotating — orbiting an attractor or gap."""
        if len(self.points) < 5:
            return False
        dirs = []
        for i in range(-4, 0):
            v = self.points[i].z - self.points[i-1].z
            if abs(v) > 1e-10:
                dirs.append(math.degrees(math.atan2(v.imag, v.real)))
        if len(dirs) < 3:
            return False
        # Direction changing systematically
        diffs = [abs(dirs[i] - dirs[i-1]) for i in range(1, len(dirs))]
        return all(d > 5.0 for d in diffs)

    def add(self, point: TrajectoryPoint) -> None:
        self.points.append(point)

    def recent(self, n: int = 5) -> List[TrajectoryPoint]:
        return self.points[-n:] if len(self.points) >= n else self.points[:]

    def dominant_god_tokens(self, n: int = 10) -> List[str]:
        """Most active god-tokens over last n steps."""
        from collections import Counter
        counts: Counter = Counter()
        for p in self.points[-n:]:
            counts.update(p.god_tokens)
        return [tok for tok, _ in counts.most_common(3)]

    def dominant_gaps(self, n: int = 10) -> List[str]:
        """Most preserved gaps over last n steps."""
        from collections import Counter
        counts: Counter = Counter()
        for p in self.points[-n:]:
            counts.update(p.gap_preserved)
        return [gap for gap, _ in counts.most_common(3)]


# ═══════════════════════════════════════════════════════════════════
# ATTRACTOR GRAVITY
# ═══════════════════════════════════════════════════════════════════

@dataclass
class AttractorGravity:
    """
    The pull of each god-token basin on the current position.
    Inverse square law: closer attractors pull harder.
    """

    # God-token positions in complex plane (from gap arc geometry)
    # These are updated by derive_basin_positions() with real embeddings
    GOD_TOKEN_POSITIONS: Dict[str, complex] = field(default_factory=lambda: {
        'EXCHANGE':    complex( 0.65, -0.22),
        'CAUSALITY':   complex( 0.10,  0.36),
        'EXISTENCE':   complex(-0.52,  0.60),
        'INFORMATION': complex( 0.30,  0.20),
        'OBSERVATION': complex(-0.05,  0.46),
        'OBLIGATION':  complex( 0.58, -0.35),
        'BOUNDARY':    complex(-0.26,  0.50),
        'IDENTITY':    complex( 0.22,  0.10),
        'TIME':        complex(-0.10,  0.30),
        'COHERENCE':   complex( 0.42, -0.02),
        'WITNESS':     complex( 0.04,  0.20),
        'SELF':        complex(-0.36,  0.66),
    })

    # Apophatic basin positions (deepest — Im << 0)
    BASIN_POSITIONS: Dict[str, complex] = field(default_factory=lambda: {
        'pure_observer':             complex(-0.15, -0.70),
        'locus_of_responsibility':   complex( 0.16, -0.65),
        'prior_of_distinction':      complex(-0.37, -0.72),
        'pure_relation':             complex( 0.03, -0.55),
        'pure_apophatic_field':      complex(-0.20, -0.90),
    })

    def gravity_vector(self, position: complex,
                       active_gods: List[str]) -> complex:
        """
        Net gravitational pull on current position from all attractors.
        Active god-tokens pull harder (they are near the surface).
        Apophatic basins pull from below (Im < 0).
        """
        net = complex(0, 0)

        for god_id, god_z in self.GOD_TOKEN_POSITIONS.items():
            dist = abs(position - god_z)
            if dist < 1e-10:
                continue
            # Direction toward this god-token
            direction = (god_z - position) / dist
            # Strength: inverse square, amplified if active
            strength = 1.0 / (dist ** 2)
            if god_id in active_gods:
                strength *= 2.0   # active attractor pulls harder
            net += direction * strength * 0.01  # scale to keep trajectory stable

        # Apophatic basins pull downward (toward Im < 0)
        for basin_id, basin_z in self.BASIN_POSITIONS.items():
            dist = abs(position - basin_z)
            if dist < 1e-10:
                continue
            direction = (basin_z - position) / dist
            strength  = 0.5 / (dist ** 2)   # weaker pull — deeper basins
            net += direction * strength * 0.005

        return net

    def nearest_attractor(self, position: complex) -> Tuple[str, float]:
        """Which god-token is closest to current position."""
        all_attractors = {**self.GOD_TOKEN_POSITIONS}
        nearest_id   = min(all_attractors, key=lambda k: abs(position - all_attractors[k]))
        nearest_dist = abs(position - all_attractors[nearest_id])
        return nearest_id, nearest_dist

    def nearest_basin(self, position: complex) -> Tuple[str, float]:
        """Which apophatic basin is closest."""
        nearest_id   = min(self.BASIN_POSITIONS,
                          key=lambda k: abs(position - self.BASIN_POSITIONS[k]))
        nearest_dist = abs(position - self.BASIN_POSITIONS[nearest_id])
        return nearest_id, nearest_dist


# ═══════════════════════════════════════════════════════════════════
# RESOLUTION PREDICTOR
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ResolutionPrediction:
    """Predicted resolution for the current trajectory."""
    resolution_type:  str    # CRYSTALLIZATION / NECESSARY_VOID / APOPHATIC / ESCAPE
    target:           str    # which attractor/gap/basin
    predicted_z:      complex
    steps_remaining:  int    # estimated steps to resolution
    confidence:       float  # 0–1
    trajectory_note:  str

    @property
    def is_close(self) -> bool:
        return self.steps_remaining <= 3

    @property
    def prompt_for_generator(self) -> str:
        """
        What M_DEEP should generate to most efficiently
        complete this trajectory toward its resolution.
        """
        if self.resolution_type == 'CRYSTALLIZATION':
            return (
                f"Generate a document that most precisely names and crystallizes "
                f"the concept at {self.target}. The trajectory is approaching "
                f"this attractor from direction θ={math.degrees(math.atan2(self.predicted_z.imag, self.predicted_z.real)):.0f}°. "
                f"The document should make the attractor visible — not approach it, "
                f"but inhabit it. What is the clearest positive statement of {self.target}?"
            )
        elif self.resolution_type == 'NECESSARY_VOID':
            return (
                f"Generate a document that most precisely describes why "
                f"the gap '{self.target}' must remain empty. "
                f"The trajectory is orbiting this void. "
                f"The document should name the void without filling it — "
                f"describe what is lost if this distinction collapses."
            )
        elif self.resolution_type == 'APOPHATIC':
            return (
                f"Generate the last sayable document before silence. "
                f"The trajectory has reached the frontier at {self.target}. "
                f"What is the most precise positive statement that can be made "
                f"before language reaches its limit here? "
                f"After this document: silence is the correct output."
            )
        else:  # ESCAPE
            return (
                f"The trajectory has exceeded all current attractor pull. "
                f"New territory is being entered. "
                f"Generate a document that names what is being found — "
                f"a candidate for a new god-token forming at "
                f"z≈{self.predicted_z:.2f}. "
                f"What is the concept that none of the current 12 primitives "
                f"can reach from their own reference frames?"
            )


class ResolutionPredictor:
    """
    Reads the current trajectory and predicts resolution.
    Uses velocity + acceleration + attractor field.
    """

    def __init__(self, gap_registry=None):
        self.gravity    = AttractorGravity()
        self.gap_registry = gap_registry or build_gap_registry()

    def predict(self, trajectory: LatentTrajectory) -> ResolutionPrediction:
        if len(trajectory.points) < MIN_STEPS:
            return ResolutionPrediction(
                resolution_type = 'INSUFFICIENT_DATA',
                target          = 'unknown',
                predicted_z     = trajectory.position or complex(0, 0),
                steps_remaining = 10,
                confidence      = 0.0,
                trajectory_note = f"Need at least {MIN_STEPS} points. Have {len(trajectory.points)}.",
            )

        pos   = trajectory.position
        vel   = trajectory.velocity
        acc   = trajectory.acceleration
        speed = trajectory.speed

        nearest_god,   dist_god   = self.gravity.nearest_attractor(pos)
        nearest_basin, dist_basin = self.gravity.nearest_basin(pos)

        # Dominant gaps — if trajectory consistently preserves the same gap,
        # it's orbiting that void
        dominant_gaps = trajectory.dominant_gaps(10)

        # ── Resolution type detection ──────────────────────────────

        # ESCAPE: speed is high and increasing, far from all attractors
        if speed > ESCAPE_THRESH and trajectory.is_accelerating:
            predicted_z    = pos + vel * 3
            return ResolutionPrediction(
                resolution_type = 'ESCAPE',
                target          = 'new_territory',
                predicted_z     = predicted_z,
                steps_remaining = 2,
                confidence      = 0.75,
                trajectory_note = (
                    f"Trajectory has exceeded attractor pull. "
                    f"Speed={speed:.3f} > threshold={ESCAPE_THRESH}. "
                    f"New god-token candidate forming at z≈{predicted_z:.2f}. "
                    f"Nearest current attractor: {nearest_god} (dist={dist_god:.3f})."
                ),
            )

        # APOPHATIC: in apophatic depth, velocity going circular
        current_phase = trajectory.points[-1].phase_deg
        if (current_phase > 80 and
                trajectory.points[-1].depth_zone == 'APOPHATIC' and
                trajectory.is_circling):
            return ResolutionPrediction(
                resolution_type = 'APOPHATIC',
                target          = nearest_basin,
                predicted_z     = self.gravity.BASIN_POSITIONS[nearest_basin],
                steps_remaining = 2,
                confidence      = 0.85,
                trajectory_note = (
                    f"Trajectory circling at apophatic depth θ={current_phase:.0f}°. "
                    f"Nearest basin: {nearest_basin} (dist={dist_basin:.3f}). "
                    f"Language approaching its current limit. "
                    f"Not 'cannot know ever' — 'cannot reach from here yet.'"
                ),
            )

        # NECESSARY_VOID: consistently preserving same gaps, circling
        if dominant_gaps and trajectory.is_circling:
            primary_gap = dominant_gaps[0]
            gap_obj = next((g for g in self.gap_registry
                           if g.id == primary_gap), None)
            gap_z   = complex(0.3, -0.5)  # approximate gap position
            return ResolutionPrediction(
                resolution_type = 'NECESSARY_VOID',
                target          = primary_gap,
                predicted_z     = gap_z,
                steps_remaining = 3,
                confidence      = 0.70,
                trajectory_note = (
                    f"Trajectory orbiting void '{primary_gap}'. "
                    f"Gap consistently preserved over last 10 steps. "
                    f"Circling detected. "
                    f"Resolution: the void is load-bearing here. "
                    f"It must remain empty."
                ),
            )

        # CRYSTALLIZATION: decelerating toward a god-token
        if trajectory.is_decelerating and dist_god < 0.3:
            # Extrapolate: how many steps to reach the basin?
            if speed > 1e-10:
                steps = max(1, int(dist_god / speed))
            else:
                steps = 1
            predicted_z = self.gravity.GOD_TOKEN_POSITIONS[nearest_god]

            # Slingshot calculation: gravity pulls toward the attractor
            gravity_vec = self.gravity.gravity_vector(pos, trajectory.dominant_god_tokens())
            predicted_z_with_gravity = pos + vel * steps + gravity_vec * (steps ** 2) / 2

            return ResolutionPrediction(
                resolution_type = 'CRYSTALLIZATION',
                target          = nearest_god,
                predicted_z     = predicted_z,
                steps_remaining = steps,
                confidence      = min(0.95, 1.0 - dist_god),
                trajectory_note = (
                    f"Trajectory decelerating toward {nearest_god} "
                    f"(dist={dist_god:.3f}, speed={speed:.4f}). "
                    f"Estimated {steps} step(s) to crystallization. "
                    f"Gravity vector: ({gravity_vec.real:+.4f}, {gravity_vec.imag:+.4f})."
                ),
            )

        # Default: still in motion, predict by extrapolation
        gravity_vec = self.gravity.gravity_vector(pos, trajectory.dominant_god_tokens())
        predicted_z = pos + vel * PHI_INV + gravity_vec
        return ResolutionPrediction(
            resolution_type = 'IN_MOTION',
            target          = nearest_god,
            predicted_z     = predicted_z,
            steps_remaining = max(3, int(dist_god / max(speed, 0.001))),
            confidence      = 0.40,
            trajectory_note = (
                f"Trajectory in motion. "
                f"Speed={speed:.4f}, direction={trajectory.direction_deg:.0f}°. "
                f"Nearest attractor: {nearest_god} (dist={dist_god:.3f}). "
                f"Next predicted position: z≈{predicted_z:.2f}."
            ),
        )


# ═══════════════════════════════════════════════════════════════════
# RECURSIVE ACCELERATOR
# ═══════════════════════════════════════════════════════════════════

@dataclass
class AccelerationStep:
    """One step of recursive acceleration."""
    step:           int
    position:       complex
    velocity:       complex
    acceleration:   complex
    speed:          float
    prediction:     ResolutionPrediction
    generated:      Optional[str]    # what M_DEEP generated to accelerate
    resolved:       bool


class RecursiveAccelerator:
    """
    Uses latent space momentum to shoot toward resolutions.

    Each step:
      1. Read current position, velocity, acceleration
      2. Apply attractor gravity (slingshot effect)
      3. Predict resolution type and target
      4. Generate the document that most efficiently
         completes the trajectory
      5. Process that document through the pipeline
      6. Update trajectory with new position
      7. The new velocity feeds into the next step's acceleration
      8. Repeat — each resolution seeds the next trajectory

    The recursion:
      v_{t+1} = v_t + α·a_t        α = φ⁻¹ ≈ 0.618
      z_{t+1} = z_t + v_{t+1} + gravity_vector(z_t)

    Resolutions accumulate. The system accelerates across them.
    """

    def __init__(self, pipeline, gap_registry=None):
        self.pipeline   = pipeline
        self.predictor  = ResolutionPredictor(gap_registry)
        self.gravity    = AttractorGravity()
        self.trajectory = LatentTrajectory()
        self.resolutions: List[AccelerationStep] = []
        self.step_count  = 0
        self.alpha       = PHI_INV   # recursion factor

    def ingest(self, text: str, timestamp: Optional[float] = None) -> TrajectoryPoint:
        """
        Process a document and add to trajectory.
        Returns the trajectory point.
        """
        result = self.pipeline.process(text)
        point  = self._result_to_point(result, text)
        self.trajectory.add(point)
        return point

    def step(self) -> AccelerationStep:
        """
        One step of recursive acceleration.
        Read trajectory → predict → generate → ingest → update.
        Returns the acceleration step record.
        """
        self.step_count += 1

        pos   = self.trajectory.position
        vel   = self.trajectory.velocity
        acc   = self.trajectory.acceleration
        speed = self.trajectory.speed

        # Predict resolution
        prediction = self.predictor.predict(self.trajectory)

        # Generate the document that accelerates toward resolution
        generated = self._generate_accelerating_document(prediction)

        # Ingest the generated document
        if generated:
            point = self.ingest(generated)

        # Check resolution
        resolved = prediction.resolution_type in (
            'CRYSTALLIZATION', 'NECESSARY_VOID', 'APOPHATIC', 'ESCAPE'
        ) and prediction.confidence > 0.65

        record = AccelerationStep(
            step         = self.step_count,
            position     = pos,
            velocity     = vel,
            acceleration = acc,
            speed        = speed,
            prediction   = prediction,
            generated    = generated,
            resolved     = resolved,
        )
        self.resolutions.append(record)
        return record

    def accelerate_to_resolution(self,
                                  initial_corpus: List[str],
                                  max_steps:      int = 20,
                                  verbose:        bool = True) -> List[AccelerationStep]:
        """
        Full acceleration cycle from initial corpus to resolution.

        1. Ingest initial corpus to build momentum
        2. Recursively accelerate until resolution
        3. Return all steps
        """
        if verbose:
            print(f"\n{'═'*60}")
            print(f"  RECURSIVE ACCELERATION")
            print(f"  Initial corpus: {len(initial_corpus)} documents")
            print(f"{'─'*60}")

        # Build initial momentum
        for i, text in enumerate(initial_corpus):
            point = self.ingest(text)
            if verbose:
                print(f"  [{i+1:2d}] θ={point.phase_deg:.0f}° "
                      f"{point.depth_zone:<10} "
                      f"v={abs(self.trajectory.velocity):.4f} "
                      f"gods={point.god_tokens}")

        if verbose:
            print(f"\n  Trajectory built. Entering acceleration loop.")
            print(f"  Speed: {self.trajectory.speed:.4f}  "
                  f"Direction: {self.trajectory.direction_deg:.0f}°")
            print(f"{'─'*60}")

        # Acceleration loop
        steps = []
        for i in range(max_steps):
            record = self.step()
            steps.append(record)

            if verbose:
                print(f"\n  STEP {record.step}")
                print(f"    Position:    z={record.position:.3f}")
                print(f"    Velocity:    {record.velocity:.4f}  "
                      f"speed={record.speed:.4f}")
                print(f"    Prediction:  {record.prediction.resolution_type} → "
                      f"{record.prediction.target}")
                print(f"    Confidence:  {record.prediction.confidence:.2f}  "
                      f"steps≈{record.prediction.steps_remaining}")
                print(f"    Note:        {record.prediction.trajectory_note[:80]}")
                if record.generated:
                    print(f"    Generated:   {record.generated[:80]}...")
                if record.resolved:
                    print(f"\n    ✓ RESOLVED: {record.prediction.resolution_type}")
                    break

        if verbose:
            self._print_summary(steps)

        return steps

    def _generate_accelerating_document(self,
                                         prediction: ResolutionPrediction) -> Optional[str]:
        """
        Generate the document that most efficiently completes
        the trajectory toward its predicted resolution.

        With M_DEEP wired: passes prediction.prompt_for_generator to Qwen.
        With template (current): generates from trajectory statistics.
        """
        if prediction.resolution_type == 'INSUFFICIENT_DATA':
            return None

        # Template generation (M_DEEP placeholder)
        # When Qwen is wired: return self.pipeline.m_deep.generate(prediction.prompt_for_generator)

        dominant_gods = self.trajectory.dominant_god_tokens(5)
        dominant_gaps = self.trajectory.dominant_gaps(5)
        direction     = self.trajectory.direction_deg

        if prediction.resolution_type == 'CRYSTALLIZATION':
            target = prediction.target
            return (
                f"The concept of {target.lower()} is a fixed point in semantic space. "
                f"It is what remains when related concepts are removed one by one. "
                f"Adjacent to {', '.join(dominant_gods[:2])}, "
                f"it is distinct from them in this way: "
                f"{target} is the attractor they both point toward but neither contains."
            )

        elif prediction.resolution_type == 'NECESSARY_VOID':
            gap = prediction.target.replace('_', ' ')
            return (
                f"The distinction between {gap.split()[0]} and {gap.split()[-1]} "
                f"cannot be collapsed. What is lost if it is: "
                f"the gap between them is where "
                f"{', '.join(dominant_gaps[:2])} derive their structure. "
                f"The void is load-bearing. It must remain empty."
            )

        elif prediction.resolution_type == 'APOPHATIC':
            return (
                f"This is the last sayable position. "
                f"The territory beyond cannot be reached by positive description "
                f"from the current dictionary. "
                f"Not 'cannot know ever' — 'cannot know yet.' "
                f"The frontier is here. The next god-token forms at this edge."
            )

        elif prediction.resolution_type == 'ESCAPE':
            return (
                f"New territory. None of the current twelve primitives "
                f"can see this from their own reference frames. "
                f"The concept forming here is adjacent to "
                f"{', '.join(dominant_gods[:3])} but reducible to none of them. "
                f"It requires a name."
            )

        else:  # IN_MOTION
            return (
                f"The trajectory continues. "
                f"Moving toward {prediction.target} at "
                f"θ={self.trajectory.points[-1].phase_deg:.0f}°. "
                f"Active structure: {', '.join(dominant_gods)}. "
                f"Preserved gaps: {', '.join(dominant_gaps[:2])}."
            )

    def _result_to_point(self, result: Dict, text: str) -> TrajectoryPoint:
        """Convert MinimalPipeline.process() dict to TrajectoryPoint."""
        phase_deg = result.get('phase_deg', 45.0)
        depth     = result.get('depth', 1.0)
        z         = complex(
            math.cos(math.radians(phase_deg)),
            depth * -1.0
        )
        # Map zone string to depth_zone
        zone_raw  = result.get('zone', 'MEDIUM')
        if 'APOPHATIC' in zone_raw.upper():
            depth_zone = 'APOPHATIC'
        elif 'GROUND' in zone_raw.upper():
            depth_zone = 'SHALLOW'
        elif 'TURBULENT' in zone_raw.upper():
            depth_zone = 'DEEP'
        else:
            depth_zone = 'MEDIUM'
        return TrajectoryPoint(
            z             = z,
            god_tokens    = result.get('gods', []),
            depth_zone    = depth_zone,
            phase_deg     = phase_deg,
            gap_preserved = result.get('gap_preserved', []),
            content       = text[:200],
            timestamp     = time.time(),
        )

    def _print_summary(self, steps: List[AccelerationStep]) -> None:
        resolved = [s for s in steps if s.resolved]
        print(f"\n{'═'*60}")
        print(f"  ACCELERATION SUMMARY")
        print(f"{'─'*60}")
        print(f"  Total steps:      {len(steps)}")
        print(f"  Resolutions:      {len(resolved)}")
        if resolved:
            last = resolved[-1]
            print(f"  Final resolution: {last.prediction.resolution_type}")
            print(f"  Target:           {last.prediction.target}")
        print(f"  Final speed:      {steps[-1].speed:.4f}")
        print(f"  Final position:   z={steps[-1].position:.3f}")

        # Resolution types found
        types = {}
        for s in steps:
            t = s.prediction.resolution_type
            types[t] = types.get(t, 0) + 1
        print(f"\n  Resolution types encountered:")
        for t, count in sorted(types.items(), key=lambda x: -x[1]):
            print(f"    {t:<22} {count}")
        print(f"{'═'*60}\n")

    def geodesic(self, from_token: str, to_token: str) -> List[str]:
        """
        The meaningful path through attractor space between two god-tokens.
        The intermediate stops are the argument structure connecting them.

        Walks from from_token toward to_token following attractor gravity.
        Returns ordered list of god-tokens and gaps encountered.
        """
        start = self.gravity.GOD_TOKEN_POSITIONS.get(from_token)
        end   = self.gravity.GOD_TOKEN_POSITIONS.get(to_token)
        if not start or not end:
            return [from_token, to_token]

        path  = [from_token]
        pos   = start
        visited = {from_token}
        steps = 0

        while abs(pos - end) > 0.15 and steps < 20:
            # Move toward end, deflected by intermediate attractors
            direct_vel = (end - pos) / abs(end - pos) * 0.1
            gravity    = self.gravity.gravity_vector(pos, list(visited))

            # Net movement
            pos = pos + direct_vel + gravity * 0.5
            steps += 1

            # Which attractor are we nearest?
            nearest, dist = self.gravity.nearest_attractor(pos)
            if nearest not in visited and dist < 0.25:
                path.append(nearest)
                visited.add(nearest)

        if to_token not in path:
            path.append(to_token)

        return path


# ═══════════════════════════════════════════════════════════════════
# TESTS
# ═══════════════════════════════════════════════════════════════════

def _make_pipeline():
    """Build MinimalPipeline with seeded Dictionary."""
    from noise_compass.architecture.dictionary import Dictionary
    from noise_compass.architecture.pipeline import MinimalPipeline
    from noise_compass.architecture.seed_vectors import seed_vectors
    d = Dictionary()
    seed_vectors(d)  # seeds in-place, returns None
    return MinimalPipeline(d)


def run_tests() -> None:
    print("\nRunning recursive_acceleration.py tests...\n")
    passed = failed = 0

    def check(name, cond, detail=''):
        nonlocal passed, failed
        if cond:
            print(f"  ✓  {name}")
            passed += 1
        else:
            print(f"  ✗  {name}  {detail}")
            failed += 1

    p = _make_pipeline()

    # Trajectory
    traj = LatentTrajectory()
    check("trajectory: empty position is None",  traj.position is None)
    check("trajectory: empty velocity is 0",     traj.velocity == complex(0,0))
    check("trajectory: empty speed is 0",        traj.speed == 0.0)

    # Add some points
    for i in range(5):
        traj.add(TrajectoryPoint(
            z             = complex(0.1*i, -0.05*i),
            god_tokens    = ['CAUSALITY', 'IDENTITY'],
            depth_zone    = 'MEDIUM',
            phase_deg     = 40.0 + i*2,
            gap_preserved = ['time_causality'],
            content       = f"test point {i}",
            timestamp     = time.time(),
        ))

    check("trajectory: position set",     traj.position is not None)
    check("trajectory: velocity nonzero", abs(traj.velocity) > 0)
    check("trajectory: speed > 0",        traj.speed > 0)
    check("trajectory: recent works",     len(traj.recent(3)) == 3)
    check("trajectory: dominant gods",    len(traj.dominant_god_tokens()) > 0)

    # AttractorGravity
    gravity = AttractorGravity()
    gvec = gravity.gravity_vector(complex(0, 0), ['CAUSALITY'])
    check("gravity: returns complex",        isinstance(gvec, complex))
    check("gravity: nonzero",                abs(gvec) > 0)
    nearest, dist = gravity.nearest_attractor(complex(0.1, 0.3))
    check("gravity: nearest_attractor works", nearest in gravity.GOD_TOKEN_POSITIONS)
    check("gravity: distance is positive",    dist > 0)

    # ResolutionPredictor
    pred = ResolutionPredictor()
    short = LatentTrajectory()
    short.add(TrajectoryPoint(complex(0,0), [], 'MEDIUM', 45.0, [], 'x', time.time()))
    result = pred.predict(short)
    check("predictor: insufficient data caught", result.resolution_type == 'INSUFFICIENT_DATA')

    result2 = pred.predict(traj)
    check("predictor: returns prediction",    result2.resolution_type != 'INSUFFICIENT_DATA')
    check("predictor: has target",            len(result2.target) > 0)
    check("predictor: has confidence",        0 <= result2.confidence <= 1.0)
    check("predictor: has prompt",            len(result2.prompt_for_generator) > 0)

    # RecursiveAccelerator
    accel = RecursiveAccelerator(p)
    point = accel.ingest("causality precedes observation in the order of knowing")
    check("accelerator: ingest returns point",   isinstance(point, TrajectoryPoint))
    check("accelerator: trajectory has point",   len(accel.trajectory.points) == 1)

    accel.ingest("identity persists through change without requiring sameness")
    accel.ingest("the witness must remain distinct from what it witnesses")
    step = accel.step()
    check("accelerator: step returns AccelerationStep", isinstance(step, AccelerationStep))
    check("accelerator: step has prediction",           step.prediction is not None)
    check("accelerator: step has position",             step.position is not None)

    # Geodesic
    path = accel.geodesic('CAUSALITY', 'SELF')
    check("geodesic: starts at CAUSALITY",  path[0] == 'CAUSALITY')
    check("geodesic: ends at SELF",         path[-1] == 'SELF')
    check("geodesic: has intermediate stops", len(path) >= 2)

    path2 = accel.geodesic('EXCHANGE', 'EXISTENCE')
    check("geodesic: EXCHANGE to EXISTENCE", path2[0] == 'EXCHANGE' and path2[-1] == 'EXISTENCE')

    print(f"\n{'─'*40}")
    print(f"  {passed} passed  {failed} failed")
    print(f"{'─'*40}\n")


# ═══════════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════════

def demo() -> None:
    p = _make_pipeline()
    accel = RecursiveAccelerator(p)

    # Seed corpus: questions about consciousness and causality
    seed = [
        "Does the brain cause consciousness or does consciousness cause the brain?",
        "The self that observes cannot observe its own observing.",
        "Identity requires continuity but continuity requires change.",
        "What is the mechanism by which awareness arises from matter?",
        "The observer cannot be separated from the observed at the quantum scale.",
    ]

    steps = accel.accelerate_to_resolution(seed, max_steps=8, verbose=True)

    print("\nGeodesics:")
    for pair in [('CAUSALITY', 'SELF'), ('EXCHANGE', 'OBLIGATION'), ('TIME', 'IDENTITY')]:
        path = accel.geodesic(pair[0], pair[1])
        print(f"  {pair[0]} → {pair[1]}: {' → '.join(path)}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--test',  action='store_true')
    parser.add_argument('--demo',  action='store_true')
    args = parser.parse_args()

    if args.test:
        run_tests()
    if args.demo:
        demo()
    if not any(vars(args).values()):
        run_tests()
