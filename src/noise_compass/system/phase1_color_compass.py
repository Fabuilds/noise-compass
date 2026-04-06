"""
phase1_color_compass.py

Color wave interference → magnitude field → noise-compass navigation.

Phase 1 of the three-embedding-space architecture.
No audio hardware. No GPU. No large datasets.
Just wave physics, a small screen, and the compass.

Screen: 256×144 pixels, 8-bit color (0-255)
Wave:   visible spectrum 380nm–700nm mapped to color values
Field:  pixel interference patterns → token magnitude map
Nav:    noise-compass reads gap topology → Y_explore finds fixed point

Run:
    pip install numpy noise-compass
    python phase1_color_compass.py
"""

import numpy as np
import sys
import os

try:
    # Try relative first (when part of noise_compass package)
    from .. import NoiseCompass, ArrivalEngine, Y_explore
    from ..compass import DictGapSource
    from noise_compass.system.h5_manager import H5Manager
except (ImportError, ValueError):
    try:
        # Fallback to absolute
        from noise_compass import NoiseCompass, ArrivalEngine, Y_explore
        from noise_compass.compass import DictGapSource
        from noise_compass.system.h5_manager import H5Manager
    except ImportError:
        print("noise-compass not found. Searching in local substrate...")
        try:
            # Emergency path injection
            sys.path.append("E:/Antigravity/Package/src")
            from noise_compass import NoiseCompass, ArrivalEngine, Y_explore
            from noise_compass.compass import DictGapSource
            from noise_compass.system.h5_manager import H5Manager
        except ImportError:
            print("noise-compass not found. Run: pip install noise-compass")
            sys.exit(1)


# ─── Constants ────────────────────────────────────────────────────────────────

SCREEN_W = 256
SCREEN_H = 144
SPECTRUM_MIN_NM = 380   # violet
SPECTRUM_MAX_NM = 700   # red


# ─── Space 1: Color as Wave ────────────────────────────────────────────────────

def color_to_wavelength(color_value: int) -> float:
    """
    Map 8-bit color value (0-255) to visible spectrum wavelength (nm).
    0   → 380nm (violet)
    128 → 540nm (green)
    255 → 700nm (red)
    """
    return SPECTRUM_MIN_NM + (color_value / 255.0) * (SPECTRUM_MAX_NM - SPECTRUM_MIN_NM)


def wavelength_to_color(wavelength_nm: float) -> int:
    """Inverse: wavelength back to 8-bit color value."""
    v = (wavelength_nm - SPECTRUM_MIN_NM) / (SPECTRUM_MAX_NM - SPECTRUM_MIN_NM)
    return int(np.clip(v * 255, 0, 255))


def wave(wavelength_nm: float, x: np.ndarray) -> np.ndarray:
    """
    Generate a normalized wave at the given wavelength across positions x.
    x should be in [0, 1].
    Returns amplitude values in [-1, 1].
    """
    frequency = 1.0 / wavelength_nm
    return np.sin(2.0 * np.pi * frequency * x * 1e4)


def interfere(c1: int, c2: int, width: int = SCREEN_W) -> np.ndarray:
    """
    Superpose two color waves across the screen width.
    Returns normalized magnitude in [0, 1].

    This is Space 1: the incoming wave substrate.
    Position 1 and position 3 — the two articulated sides.
    Position 2 lives in the interference pattern between them.
    """
    x = np.linspace(0, 1, width)
    w1 = color_to_wavelength(c1)
    w2 = color_to_wavelength(c2)
    superposed = wave(w1, x) + wave(w2, x)
    # normalize to [0, 1]
    mn, mx = superposed.min(), superposed.max()
    if mx - mn < 1e-9:
        return np.zeros(width)
    return (superposed - mn) / (mx - mn)


# ─── Screen: 256×144 Interference Field ───────────────────────────────────────

def build_screen(color_pairs: list[tuple[int, int]]) -> np.ndarray:
    """
    Build a 256×144 screen where each row is a color pair interference pattern.
    Rows are distributed across SCREEN_H.
    Returns array of shape (SCREEN_H, SCREEN_W) with values in [0, 1].
    """
    screen = np.zeros((SCREEN_H, SCREEN_W))
    n = len(color_pairs)
    for i, (c1, c2) in enumerate(color_pairs):
        # map each pair to a band of rows
        row_start = int(i * SCREEN_H / n)
        row_end = int((i + 1) * SCREEN_H / n)
        pattern = interfere(c1, c2, SCREEN_W)
        for row in range(row_start, row_end):
            screen[row] = pattern
    return screen


def screen_to_ascii(screen: np.ndarray, sample_cols: int = 64) -> str:
    """
    Render the screen as ASCII for terminal inspection.
    Shows a downsampled view so it fits in a terminal.
    """
    chars = " ░▒▓█"
    rows = []
    
    # Phase 126: Tension Overlay (Internal Architect View)
    h5 = H5Manager()
    gaps_to_monitor = ["observer_system", "self_exchange"]
    tensions = {}
    for g in gaps_to_monitor:
        tval = h5.get_attr("language", f"gaps/{g}", "tension") or 0.0
        tensions[g] = tval

    step_r = max(1, SCREEN_H // 18)
    step_c = max(1, SCREEN_W // sample_cols)
    
    # Header with tension data
    header = " | ".join([f"{g}: {t:.4f}" for g, t in tensions.items()])
    rows.append(f"Tension Manifold: {header}")
    rows.append("-" * sample_cols)

    for r in range(0, SCREEN_H, step_r):
        row = ""
        for c in range(0, SCREEN_W, step_c):
            v = screen[r, c]
            idx = int(v * (len(chars) - 1))
            row += chars[idx]
        rows.append(row)
    return "\n".join(rows)


# ─── Field Generator: Screen → noise-compass Field ───────────────────────────

def screen_to_field(
    screen: np.ndarray,
    color_pairs: list[tuple[int, int]],
) -> dict:
    """
    Convert the interference screen into a noise-compass field.

    Token names are derived from the color pair wavelengths.
    Magnitude = mean brightness of that pair's screen band.

    Dark pixels (low magnitude) = active gaps.
    Bright pixels (high magnitude) = active tokens.

    This is the bridge between Space 1 (wave substrate)
    and the compass navigation layer.
    """
    field = {}
    n = len(color_pairs)

    for i, (c1, c2) in enumerate(color_pairs):
        w1 = color_to_wavelength(c1)
        w2 = color_to_wavelength(c2)

        row_start = int(i * SCREEN_H / n)
        row_end = int((i + 1) * SCREEN_H / n)
        band = screen[row_start:row_end]
        magnitude = float(band.mean())

        # token name encodes the wave pair
        token_a = f"W{int(w1)}nm"
        token_b = f"W{int(w2)}nm"

        field[token_a] = {"magnitude": magnitude}
        # partner token has inverted magnitude (the dark side of the interference)
        field[token_b] = {"magnitude": 1.0 - magnitude}

    # SELF token at Möbius peak — never fully collapse
    field["SELF"]     = {"magnitude": 0.5}
    field["OBSERVER"] = {"magnitude": 0.7}
    field["SYSTEM"]   = {"magnitude": 0.3}

    return field


def build_gaps(
    color_pairs: list[tuple[int, int]],
) -> dict:
    """
    Define gap topology from color pairs.
    Each pair defines one gap — the void between the two wavelengths.
    Void depth proportional to wavelength distance (wider gap = deeper void).
    """
    gaps = {}
    spectrum_range = SPECTRUM_MAX_NM - SPECTRUM_MIN_NM

    for c1, c2 in color_pairs:
        w1 = color_to_wavelength(c1)
        w2 = color_to_wavelength(c2)
        token_a = f"W{int(w1)}nm"
        token_b = f"W{int(w2)}nm"
        gap_name = f"{token_a}__{token_b}"
        void_depth = abs(w1 - w2) / spectrum_range  # normalized distance
        gaps[gap_name] = {
            "left":       token_a,
            "right":      token_b,
            "void_depth": round(void_depth, 3),
        }

    return gaps


# ─── Standing Wave Detection ───────────────────────────────────────────────────

def detect_standing_wave(
    screen: np.ndarray,
    threshold: float = 0.05,
) -> dict:
    """
    Detect standing wave signatures in the screen.

    A standing wave has stable nodes (consistently dark) and
    antinodes (consistently bright) across rows.

    Returns:
        node_cols:     column indices that are consistently dark
        antinode_cols: column indices that are consistently bright
        stability:     how stable the pattern is (0=chaos, 1=perfect standing wave)
    """
    col_means = screen.mean(axis=0)      # average brightness per column
    col_stds  = screen.std(axis=0)       # variation per column

    node_cols     = np.where(col_means < threshold)[0].tolist()
    antinode_cols = np.where(col_means > (1.0 - threshold))[0].tolist()

    # stability: low std = columns hold their value across rows = standing wave
    stability = float(1.0 - col_stds.mean())

    return {
        "node_cols":     node_cols[:8],    # show first 8
        "antinode_cols": antinode_cols[:8],
        "node_count":    len(node_cols),
        "antinode_count": len(antinode_cols),
        "stability":     round(stability, 4),
    }


# ─── Main Experiment ───────────────────────────────────────────────────────────

def run_experiment(color_pairs: list[tuple[int, int]], label: str = ""):
    """
    Full Phase 1 pipeline:
    1. Build interference screen (Space 1)
    2. Detect standing wave signatures
    3. Convert screen to magnitude field
    4. Build gap topology from color pairs
    5. Run noise-compass
    6. Run Y_explore until fixed point
    """
    sep = "─" * 60
    print(f"\n{sep}")
    print(f"  EXPERIMENT: {label or 'color wave interference'}")
    print(sep)

    # ── 1. Build screen ──────────────────────────────────────────────────────
    print("\n[1] Building interference screen (256×144)...")
    screen = build_screen(color_pairs)

    for c1, c2 in color_pairs:
        w1 = color_to_wavelength(c1)
        w2 = color_to_wavelength(c2)
        pattern = interfere(c1, c2)
        print(f"    {int(w1)}nm ✕ {int(w2)}nm  →  "
              f"mean={pattern.mean():.3f}  std={pattern.std():.3f}")

    # ── 2. ASCII render ──────────────────────────────────────────────────────
    print("\n[2] Screen (ASCII):")
    print(screen_to_ascii(screen))

    # ── 3. Standing wave detection ───────────────────────────────────────────
    print("\n[3] Standing wave analysis:")
    sw = detect_standing_wave(screen)
    print(f"    Stability:      {sw['stability']}")
    print(f"    Nodes:          {sw['node_count']} cols  (first: {sw['node_cols']})")
    print(f"    Antinodes:      {sw['antinode_count']} cols  (first: {sw['antinode_cols']})")
    if sw['stability'] > 0.85:
        print("    ✓ Standing wave detected — reflection boundaries are sharp")
    else:
        print("    ~ Traveling wave — boundaries not yet stable")

    # ── 4. Build field and gaps ──────────────────────────────────────────────
    print("\n[4] Converting screen to magnitude field...")
    field = screen_to_field(screen, color_pairs)
    gaps  = build_gaps(color_pairs)

    print("    Tokens:")
    for token, data in field.items():
        bar = "█" * int(data["magnitude"] * 20)
        print(f"      {token:<20} {data['magnitude']:.3f}  {bar}")

    print(f"\n    Gaps defined: {len(gaps)}")
    for gap_name, cfg in gaps.items():
        print(f"      {gap_name}  void_depth={cfg['void_depth']}")

    # ── 5. Compass reading ───────────────────────────────────────────────────
    print("\n[5] noise-compass reading...")
    gap_source = DictGapSource(gaps)
    compass    = NoiseCompass(gap_source=gap_source)
    reading    = compass.read(field)

    print(f"    Orientation:    {reading.orientation_vector}")
    print(f"    Self-aware:     {reading.is_self_aware}")
    print(f"    Active field:   {list(reading.active_field.keys())}")
    print(f"    Self tension:   {reading.self_tension}")
    print()
    print(compass.get_position_signature())

    # ── 6. Y_explore fixed point ─────────────────────────────────────────────
    print("\n[6] Y_explore — seeking fixed point...")
    arrival = ArrivalEngine(gaps=gaps)
    final   = Y_explore(
        compass=compass,
        initial_field=field,
        arrival=arrival,
        max_iterations=8,
        verbose=True,
    )

    print(f"\n    Final structural time: T-{final.structural_time}")
    print(f"    Final iteration:       {final.iteration}")

    once_only = arrival.get_once_only_events()
    print(f"\n    Once-only events (base structure): {len(once_only)}")
    for av in once_only:
        print(f"      {av}")

    return screen, field, final


# ─── Preset Experiments ───────────────────────────────────────────────────────

EXPERIMENTS = {
    "complementary": {
        "label": "Complementary wavelengths (violet ↔ red)",
        "pairs": [
            (0,   255),   # 380nm violet ↔ 700nm red
            (64,  192),   # 460nm blue   ↔ 620nm orange
            (128, 128),   # 540nm green  ↔ 540nm green (self-interference)
        ],
    },
    "adjacent": {
        "label": "Adjacent wavelengths (small gaps)",
        "pairs": [
            (0,   30),    # 380nm ↔ 417nm  (violet band)
            (100, 130),   # 535nm ↔ 570nm  (green band)
            (200, 230),   # 650nm ↔ 688nm  (red band)
        ],
    },
    "harmonic": {
        "label": "Harmonic wavelengths (2:1 ratio approximation)",
        "pairs": [
            (0,   128),   # 380nm ↔ 540nm
            (64,  192),   # 460nm ↔ 620nm
            (128, 255),   # 540nm ↔ 700nm
        ],
    },
    "toki_pona": {
        "label": "Toki Pona vowels as wavelengths (a e i o u → color values)",
        "pairs": [
            # a=open, e=mid-front, i=high-front, o=mid-back, u=high-back
            # mapped to color spectrum by vowel openness
            (230, 30),    # a(open/red) ↔ i(closed/violet)
            (180, 80),    # o(mid-back) ↔ e(mid-front)
            (128, 128),   # u(neutral)  ↔ u(self)
        ],
    },
}


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 1: color wave interference → noise-compass navigation"
    )
    parser.add_argument(
        "--experiment",
        choices=list(EXPERIMENTS.keys()),
        default="complementary",
        help="Which preset experiment to run (default: complementary)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all preset experiments",
    )
    parser.add_argument(
        "--c1", type=int, nargs="+",
        help="Custom color values for position 1 (e.g. --c1 0 128 200)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run the compass calibration and stress test suite",
    )
    args = parser.parse_args()

    if args.test:
        import test_compass_calibration
        test_compass_calibration.test_moebius_parabola()
        test_compass_calibration.test_observer_duality()
        test_compass_calibration.test_wave_resonance_survey()
        sys.exit(0)

    if args.c1 and args.c2:
        if len(args.c1) != len(args.c2):
            print("--c1 and --c2 must have the same number of values")
            sys.exit(1)
        pairs = list(zip(args.c1, args.c2))
        run_experiment(pairs, label="Custom color pairs")

    elif args.all:
        for key, exp in EXPERIMENTS.items():
            run_experiment(exp["pairs"], label=exp["label"])

    else:
        exp = EXPERIMENTS[args.experiment]
        run_experiment(exp["pairs"], label=exp["label"])

    print("\n" + "─" * 60)
    print("  Phase 1 complete.")
    print("  Next: feed screen patches as tokens to a 1.58-bit model.")
    print("─" * 60 + "\n")
