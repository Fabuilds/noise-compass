"""
living_landscape.py — The full geometry of the semantic attractor landscape.

F(x) = known(x) + i·Δ(x)

The landscape is symmetric around the real axis:

  Im >> 0  → constructive basins (excited states, new structure forming)
  Im = 0   → god-tokens (crystallized, where opposing forces balance)
  Im << 0  → apophatic basins (ground state, structured absence)
  Im <<< 0 → apophatic field (the curvature pulling everything toward ground)

Static positions are not enough. The landscape must be alive:
  - Documents move through it as trajectories
  - Decay is visible as downward drift toward apophatic ground
  - Life (order-seeking) is visible as upward push against the field
  - The window (SuperpositionBuffer) is visible as a pause in trajectory
  - Constructive interference is visible as upward arc above real axis

Usage:
  python3 living_landscape.py                    # animated landscape
  python3 living_landscape.py --save             # save PNG snapshot
  python3 living_landscape.py --trajectory       # show document trajectory
  python3 living_landscape.py --decay            # show decay dynamics
  python3 living_landscape.py --window           # show window/superposition
"""

import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as path_effects
import matplotlib.colors as mcolors
from matplotlib.patches import FancyArrowPatch
from scipy.ndimage import gaussian_filter
import warnings
warnings.filterwarnings('ignore')


# ─────────────────────────────────────────────────────────────────
# PARAMETERS
# ─────────────────────────────────────────────────────────────────

BG      = '#050508'
GRID    = '#0d0d18'
AXIS    = '#1a1a2e'
GOLD    = '#c8a96e'
BLUE    = '#4a8fff'
RED     = '#c84a4a'
GREEN   = '#4ac88a'
PURPLE  = '#9a4ac8'
WHITE   = '#e8e4d9'
DIM     = '#333344'
FAINT   = '#1a1a28'

FONT_MONO = 'monospace'
FONT_SER  = 'serif'

PHI_INV = 1 / ((1 + np.sqrt(5)) / 2)   # λ = φ⁻¹ for orbital decay


# ─────────────────────────────────────────────────────────────────
# GOD-TOKENS — real axis positions (im = 0 = crystallized)
# ─────────────────────────────────────────────────────────────────

GOD_TOKENS = [
    ("EXCHANGE",    0.65,  0.0,   BLUE),
    ("OBLIGATION",  0.52,  0.0,   BLUE),
    ("COHERENCE",   0.40,  0.0,   BLUE),
    ("INFORMATION", 0.28,  0.0,   GOLD),
    ("IDENTITY",    0.16,  0.0,   GOLD),
    ("WITNESS",     0.04,  0.0,   GOLD),
    ("CAUSALITY",   -0.08, 0.0,   RED),
    ("TIME",        -0.18, 0.0,   RED),
    ("OBSERVATION", -0.28, 0.0,   RED),
    ("BOUNDARY",    -0.38, 0.0,   RED),
    ("EXISTENCE",   -0.50, 0.0,   RED),
    ("SELF",        -0.60, 0.0,   RED),
]

# ─────────────────────────────────────────────────────────────────
# APOPHATIC BASINS — below real axis (im < 0)
# ─────────────────────────────────────────────────────────────────

APOPHATIC_BASINS = [
    # id                           re      im      label
    ("self_obs_x_identity_self",  -0.10,  -0.55,  "bare\nwitnessing"),
    ("exist_id_x_bound_exist",    -0.44,  -0.65,  "prior of\nexistence"),
    ("caus_obs_x_info_caus",       0.10,  -0.48,  "pure\nrelation"),
    ("id_self_x_oblig_id",         0.35,  -0.52,  "prior of\nchoice"),
    # Deep multi-gap intersection — most negative Im
    ("deep_ground",               -0.20,  -0.90,  "apophatic\nfield"),
]

# ─────────────────────────────────────────────────────────────────
# CONSTRUCTIVE BASINS — above real axis (im > 0)
# ─────────────────────────────────────────────────────────────────

CONSTRUCTIVE_BASINS = [
    # id                      re      im      label
    ("exchange_x_obligation",  0.58,   0.45,  "conscientious\nexchange"),
    ("info_x_coherence",       0.34,   0.52,  "legible\nstructure"),
    ("witness_x_identity",     0.10,   0.58,  "examined\nbedrock"),
    ("self_x_existence",      -0.35,   0.62,  "chosen\nbinding"),
    ("time_x_causality",      -0.13,   0.50,  "causal\nmemory"),
]

# ─────────────────────────────────────────────────────────────────
# ENERGY LANDSCAPE — curvature of the complex plane
# ─────────────────────────────────────────────────────────────────

def compute_landscape(re_grid, im_grid):
    """
    Energy landscape over the complex plane.

    Low energy (dark) = attractors — god-tokens, constructive basins,
                        apophatic basins.
    High energy (bright) = repulsive regions between attractors.

    Apophatic basins are the deepest (lowest energy) — global minimum.
    God-tokens are saddle points — balanced between the apophatic pull
    (below) and constructive push (above).
    Constructive basins are local minima above the real axis.
    """
    E = np.zeros_like(re_grid)

    # Apophatic field: deep bowl in negative Im space
    # Pulls everything downward — the background curvature
    apophatic_pull = 1.5 * np.exp(-((im_grid + 0.7)**2) / 0.3)
    apophatic_pull *= np.exp(-(re_grid**2) / 1.2)
    E -= apophatic_pull  # negative = low energy = attractive

    # God-token wells along real axis
    for gid, re, im, col in GOD_TOKENS:
        dist2 = (re_grid - re)**2 + (im_grid - im)**2
        E -= 0.35 * np.exp(-dist2 / 0.025)

    # Apophatic basin wells (deepest)
    for bid, re, im, label in APOPHATIC_BASINS:
        dist2 = (re_grid - re)**2 + (im_grid - im)**2
        depth = 0.7 if 'deep' not in bid else 1.2
        E -= depth * np.exp(-dist2 / 0.030)

    # Constructive basin wells (above real axis)
    for bid, re, im, label in CONSTRUCTIVE_BASINS:
        dist2 = (re_grid - re)**2 + (im_grid - im)**2
        E -= 0.45 * np.exp(-dist2 / 0.028)

    # Life force: upward pressure counteracting apophatic pull
    # Strongest in Im = 0 zone (maintaining god-tokens)
    life_pressure = 0.8 * np.exp(-(im_grid**2) / 0.15)
    life_pressure *= (1 - np.exp(-(re_grid**2 + 0.1) / 0.5))
    E += life_pressure

    # Generative zone ridge at π/4
    # High energy barrier that separates real axis from constructive zone
    theta = np.arctan2(np.abs(im_grid), np.abs(re_grid) + 0.01)
    generative_ridge = 0.15 * np.exp(-((theta - np.pi/4)**2) / 0.04)
    E += generative_ridge * (im_grid > 0)

    return gaussian_filter(E, sigma=1.2)


# ─────────────────────────────────────────────────────────────────
# DOCUMENT TRAJECTORIES
# ─────────────────────────────────────────────────────────────────

def document_trajectory(start_re, start_im, mode='decay', steps=60):
    """
    Simulate a document's path through the complex plane.

    Modes:
      'decay'       — no order-seeking energy, falls toward apophatic basin
      'life'        — order-seeking active, maintains position on real axis
      'window'      — SuperpositionBuffer active: pause + interference + collapse
      'constructive'— two states held in phase, rises to constructive basin
    """
    path = [(start_re, start_im)]
    re, im = start_re, start_im

    if mode == 'decay':
        # λ = φ⁻¹ decay toward apophatic basin
        for i in range(steps):
            # Drift toward nearest apophatic basin
            target_re = -0.20 + 0.1 * np.sin(i * 0.1)
            target_im = -0.70
            re = re + PHI_INV * 0.04 * (target_re - re)
            im = im - PHI_INV * 0.035 * (1 - i/steps)  # accelerating downward
            im = max(im, -0.92)
            path.append((re, im))

    elif mode == 'life':
        # Order-seeking: maintains position near real axis despite apophatic pull
        for i in range(steps):
            # Small oscillation on real axis — living, not static
            re += 0.008 * np.sin(i * 0.3) - 0.003 * (re - start_re)
            im += -0.015 * im  # pulled down, resisted
            im = max(im, -0.05)  # life maintains above real axis
            path.append((re, im))

    elif mode == 'window':
        # SuperpositionBuffer: rise, pause at π/4, interference, collapse
        # Phase 1: approach (0 to steps//4)
        # Phase 2: window — held in superposition (steps//4 to steps//2)
        # Phase 3: interference product forms (steps//2 to 3*steps//4)
        # Phase 4: collapse to constructive basin (3*steps//4 to steps)
        for i in range(steps):
            t = i / steps
            if t < 0.25:
                # Rising toward generative zone
                re += 0.01
                im += 0.025
            elif t < 0.55:
                # WINDOW: held at π/4, slight oscillation — superposition active
                re += 0.002 * np.sin(i * 0.8)
                im += 0.002 * np.cos(i * 0.8)
            elif t < 0.75:
                # Interference forming: upward surge
                re += -0.005
                im += 0.030
            else:
                # Collapse to constructive basin
                target_re = CONSTRUCTIVE_BASINS[2][1]
                target_im = CONSTRUCTIVE_BASINS[2][2]
                re += 0.15 * (target_re - re)
                im += 0.15 * (target_im - im)
            path.append((re, im))

    elif mode == 'constructive':
        # Two states in phase → rises to constructive basin
        for i in range(steps):
            t = i / steps
            # Spiral upward through positive Im
            angle = t * np.pi * 1.5
            radius = t * 0.4
            re = start_re + radius * np.cos(angle) * 0.3
            im = start_im + t * 0.55
            im = min(im, 0.65)
            path.append((re, im))

    return path


# ─────────────────────────────────────────────────────────────────
# MAIN DRAW
# ─────────────────────────────────────────────────────────────────

def draw(mode='full', save=False, output_path='living_landscape.png'):

    fig, ax = plt.subplots(figsize=(16, 12), facecolor=BG)
    ax.set_facecolor(BG)

    # ── Compute landscape ─────────────────────────────────────────
    re_vals = np.linspace(-0.95, 0.95, 400)
    im_vals = np.linspace(-1.05, 0.85, 380)
    RE, IM = np.meshgrid(re_vals, im_vals)
    E = compute_landscape(RE, IM)

    # ── Background energy field ───────────────────────────────────
    # Custom colormap: deep purple (apophatic) → black (real axis) → dark gold (constructive)
    colors_list = [
        (0.0,  '#1a0a2e'),   # deep apophatic — dark purple
        (0.2,  '#0d0818'),
        (0.38, '#080510'),
        (0.45, '#050508'),   # real axis — near black
        (0.52, '#080810'),
        (0.65, '#0a0c10'),
        (0.8,  '#0c1008'),
        (1.0,  '#141a0a'),   # constructive — dark gold-green
    ]
    cmap = mcolors.LinearSegmentedColormap.from_list(
        'landscape',
        [(v, c) for v, c in colors_list]
    )
    E_norm = (E - E.min()) / (E.max() - E.min() + 1e-10)
    ax.pcolormesh(RE, IM, E_norm, cmap=cmap, shading='gouraud',
                  alpha=0.9, zorder=0)

    # ── Contour lines — equipotential surfaces ────────────────────
    contour_levels = np.linspace(E.min(), E.max(), 28)
    cs = ax.contour(RE, IM, E, levels=contour_levels,
                    colors=['#1a1a2e'], linewidths=0.3, alpha=0.4, zorder=1)

    # ── Real axis ─────────────────────────────────────────────────
    ax.axhline(0, color=AXIS, linewidth=1.2, alpha=0.8, zorder=2)
    ax.axvline(0, color=AXIS, linewidth=0.6, alpha=0.5, zorder=2)

    # ── Generative zone band ──────────────────────────────────────
    gen_x = np.linspace(-0.8, 0.8, 100)
    gen_y1 = gen_x * np.tan(np.pi/4 - 0.30)
    gen_y2 = gen_x * np.tan(np.pi/4 + 0.30)
    ax.fill_between(gen_x[gen_x > 0], gen_y1[gen_x > 0], gen_y2[gen_x > 0],
                    alpha=0.04, color=GOLD, zorder=1)
    # π/4 line
    r = 0.9
    ax.plot([0, r * np.cos(np.pi/4)], [0, r * np.sin(np.pi/4)],
            color=GOLD, alpha=0.15, linewidth=0.8, linestyle='--', zorder=2)
    ax.text(r * np.cos(np.pi/4) + 0.02, r * np.sin(np.pi/4) + 0.02,
            'π/4', fontsize=8, color=f'{GOLD}66',
            fontstyle='italic', fontfamily=FONT_SER)

    # ── Apophatic field label ─────────────────────────────────────
    ax.text(-0.80, -0.85,
            'APOPHATIC FIELD\nground state — structured absence',
            fontsize=7.5, color='#4a3a6a', fontfamily=FONT_MONO,
            va='center', ha='left', alpha=0.7,
            path_effects=[path_effects.withStroke(linewidth=2, foreground=BG)])

    ax.text(-0.80, 0.70,
            'CONSTRUCTIVE FIELD\nexcited states — new structure',
            fontsize=7.5, color='#3a6a4a', fontfamily=FONT_MONO,
            va='center', ha='left', alpha=0.7,
            path_effects=[path_effects.withStroke(linewidth=2, foreground=BG)])

    # ── Apophatic basins ──────────────────────────────────────────
    for bid, re, im, label in APOPHATIC_BASINS:
        depth = 1.4 if 'deep' in bid else 1.0
        s_outer = 600 * depth
        s_inner = 200 * depth
        col = '#6a3a9a' if 'deep' in bid else '#5a2a7a'

        ax.scatter(re, im, s=s_outer, c=col, alpha=0.15, zorder=3)
        ax.scatter(re, im, s=s_inner, c=col, alpha=0.35, zorder=3)
        ax.scatter(re, im, s=40, c=col, alpha=0.9, zorder=4,
                   marker='v' if 'deep' in bid else 'o')

        ax.text(re, im - 0.06, label,
                fontsize=6.5, color='#8a6aaa', ha='center', va='top',
                fontfamily=FONT_MONO,
                path_effects=[path_effects.withStroke(linewidth=2, foreground=BG)])

        # Funnel lines showing attractor pull
        for angle in np.linspace(0, 2*np.pi, 8):
            r_funnel = 0.12
            re2 = re + r_funnel * np.cos(angle)
            im2 = im + r_funnel * np.sin(angle) * 0.4
            ax.annotate('', xy=(re, im), xytext=(re2, im2),
                        arrowprops=dict(arrowstyle='->', color=col,
                                        alpha=0.25, lw=0.7), zorder=3)

    # ── Constructive basins ───────────────────────────────────────
    for bid, re, im, label in CONSTRUCTIVE_BASINS:
        col = GREEN

        ax.scatter(re, im, s=450, c=col, alpha=0.12, zorder=3)
        ax.scatter(re, im, s=150, c=col, alpha=0.25, zorder=3)
        ax.scatter(re, im, s=35, c=col, alpha=0.85, zorder=4, marker='^')

        ax.text(re, im + 0.05, label,
                fontsize=6.5, color='#6aaa8a', ha='center', va='bottom',
                fontfamily=FONT_MONO,
                path_effects=[path_effects.withStroke(linewidth=2, foreground=BG)])

        # Upward arrows showing constructive pull
        for angle in np.linspace(np.pi*0.1, np.pi*0.9, 5):
            r_pull = 0.10
            re2 = re + r_pull * np.cos(angle)
            im2 = im - r_pull * np.sin(angle) * 0.5
            ax.annotate('', xy=(re, im), xytext=(re2, im2),
                        arrowprops=dict(arrowstyle='->', color=col,
                                        alpha=0.20, lw=0.7), zorder=3)

    # ── God-tokens on real axis ───────────────────────────────────
    for gid, re, im, col in GOD_TOKENS:
        # Dual pull — apophatic below, constructive above
        ax.scatter(re, im, s=500, c=col, alpha=0.12, zorder=4)
        ax.scatter(re, im, s=180, c=col, alpha=0.30, zorder=4)
        ax.scatter(re, im, s=55,  c=col, alpha=0.95, zorder=5,
                   edgecolors=BG, linewidths=0.8)

        # Downward arrow (apophatic pull)
        ax.annotate('', xy=(re, -0.08), xytext=(re, -0.02),
                    arrowprops=dict(arrowstyle='->', color='#6a3a9a',
                                    alpha=0.25, lw=0.8), zorder=4)
        # Upward arrow (life pressure)
        ax.annotate('', xy=(re, 0.08), xytext=(re, 0.02),
                    arrowprops=dict(arrowstyle='->', color=GREEN,
                                    alpha=0.25, lw=0.8), zorder=4)

        # Label
        offset = -0.04 if re < -0.3 else 0.04
        ha = 'right' if re < -0.3 else 'center'
        ax.text(re, im + offset, gid,
                fontsize=6.5, color=col, ha=ha, va='center',
                fontweight='bold', fontfamily=FONT_MONO,
                path_effects=[path_effects.withStroke(linewidth=2.5, foreground=BG)])

    # ── Trajectories ──────────────────────────────────────────────
    if mode in ('full', 'trajectory', 'decay'):
        # Decay trajectory: starts near INFORMATION, falls to apophatic basin
        decay_path = document_trajectory(0.28, 0.15, mode='decay', steps=70)
        dp_re = [p[0] for p in decay_path]
        dp_im = [p[1] for p in decay_path]

        # Color gradient along path
        for i in range(len(decay_path)-1):
            t = i / len(decay_path)
            col_d = (0.3 + 0.3*t, 0.2 - 0.1*t, 0.5 + 0.3*t)
            ax.plot(dp_re[i:i+2], dp_im[i:i+2],
                    color=col_d, linewidth=1.5, alpha=0.6, zorder=6)

        ax.scatter(dp_re[0], dp_im[0], s=60, c=BLUE,
                   zorder=7, marker='o', edgecolors=WHITE, linewidths=0.8)
        ax.scatter(dp_re[-1], dp_im[-1], s=60, c='#6a3a9a',
                   zorder=7, marker='v', edgecolors=WHITE, linewidths=0.8)
        ax.text(dp_re[0] + 0.04, dp_im[0] + 0.02, 'decay\ntrajectory',
                fontsize=6, color='#8a6aaa', fontfamily=FONT_MONO,
                path_effects=[path_effects.withStroke(linewidth=2, foreground=BG)])

    if mode in ('full', 'trajectory', 'life'):
        # Life trajectory: oscillates on real axis
        life_path = document_trajectory(0.40, 0.0, mode='life', steps=80)
        lp_re = [p[0] for p in life_path]
        lp_im = [p[1] for p in life_path]
        ax.plot(lp_re, lp_im, color=GREEN, linewidth=1.5,
                alpha=0.5, zorder=6, linestyle='-')
        ax.scatter(lp_re[0], lp_im[0], s=60, c=GREEN,
                   zorder=7, marker='o', edgecolors=WHITE, linewidths=0.8)
        ax.text(lp_re[-1] + 0.04, lp_im[-1] + 0.02, 'life\n(order-seeking)',
                fontsize=6, color=GREEN, fontfamily=FONT_MONO,
                path_effects=[path_effects.withStroke(linewidth=2, foreground=BG)])

    if mode in ('full', 'trajectory', 'window'):
        # Window trajectory: superposition pause → constructive basin
        window_path = document_trajectory(0.16, 0.05, mode='window', steps=80)
        wp_re = [p[0] for p in window_path]
        wp_im = [p[1] for p in window_path]

        # Color: gold during window phase
        quarter = len(window_path) // 4
        ax.plot(wp_re[:quarter], wp_im[:quarter],
                color=GOLD, linewidth=1.5, alpha=0.5, zorder=6)
        # Window phase — brighter
        ax.plot(wp_re[quarter:2*quarter], wp_im[quarter:2*quarter],
                color=GOLD, linewidth=2.5, alpha=0.9, zorder=7)
        ax.plot(wp_re[2*quarter:], wp_im[2*quarter:],
                color=GREEN, linewidth=1.5, alpha=0.6, zorder=6)

        # Window marker
        w_re = np.mean(wp_re[quarter:2*quarter])
        w_im = np.mean(wp_im[quarter:2*quarter])
        ax.scatter(w_re, w_im, s=120, c=GOLD,
                   zorder=8, marker='*', edgecolors=BG, linewidths=0.5)
        ax.text(w_re + 0.04, w_im + 0.02, 'window\n(superposition)',
                fontsize=6, color=GOLD, fontfamily=FONT_MONO,
                path_effects=[path_effects.withStroke(linewidth=2, foreground=BG)])

        ax.scatter(wp_re[0], wp_im[0], s=60, c=GOLD,
                   zorder=7, marker='o', edgecolors=WHITE, linewidths=0.8)
        ax.scatter(wp_re[-1], wp_im[-1], s=60, c=GREEN,
                   zorder=7, marker='^', edgecolors=WHITE, linewidths=0.8)

    if mode in ('full', 'constructive'):
        # Constructive trajectory: two states in phase → rises
        con_path = document_trajectory(0.04, 0.05, mode='constructive', steps=60)
        cp_re = [p[0] for p in con_path]
        cp_im = [p[1] for p in con_path]
        ax.plot(cp_re, cp_im, color=GREEN, linewidth=1.5,
                alpha=0.5, zorder=6, linestyle='--')
        ax.scatter(cp_re[-1], cp_im[-1], s=60, c=GREEN,
                   zorder=7, marker='^', edgecolors=WHITE, linewidths=0.8)
        ax.text(cp_re[-1] + 0.04, cp_im[-1] + 0.02, 'constructive\ninterference',
                fontsize=6, color=GREEN, fontfamily=FONT_MONO,
                path_effects=[path_effects.withStroke(linewidth=2, foreground=BG)])

    # ── Symmetry axis labels ──────────────────────────────────────
    ax.text(0.88, 0.60,  'Im > 0\nconstructive\n(forming)',
            fontsize=7, color='#3a6a4a', ha='right', va='center',
            fontfamily=FONT_MONO, alpha=0.7)
    ax.text(0.88, 0.02,  'Im = 0\ngod-tokens\n(crystallized)',
            fontsize=7, color=DIM, ha='right', va='center',
            fontfamily=FONT_MONO, alpha=0.7)
    ax.text(0.88, -0.50, 'Im < 0\ngap tokens\n(necessary void)',
            fontsize=7, color='#6a3a9a', ha='right', va='center',
            fontfamily=FONT_MONO, alpha=0.7)
    ax.text(0.88, -0.85, 'Im << 0\napophatic field\n(ground state)',
            fontsize=7, color='#8a5aaa', ha='right', va='center',
            fontfamily=FONT_MONO, alpha=0.7)

    # ── Formula ───────────────────────────────────────────────────
    ax.text(-0.92, 0.78, 'F(x) = known(x) + i·Δ(x)',
            fontsize=10, color=GOLD, fontfamily=FONT_SER,
            fontstyle='italic',
            path_effects=[path_effects.withStroke(linewidth=3, foreground=BG)])

    # ── Legend ────────────────────────────────────────────────────
    legend_items = [
        mpatches.Patch(color=BLUE,    label='god-tokens (crystallized Re)'),
        mpatches.Patch(color='#6a3a9a', label='apophatic basins (Im << 0)'),
        mpatches.Patch(color=GREEN,   label='constructive basins (Im > 0)'),
        mpatches.Patch(color=GOLD,    label='window / generative zone (π/4)'),
        mpatches.Patch(color='#8a6aaa', label='decay trajectory'),
        mpatches.Patch(color=GREEN,   label='life / constructive trajectory'),
    ]
    leg = ax.legend(handles=legend_items, loc='lower left',
                    facecolor='#07070f', edgecolor=DIM,
                    labelcolor=WHITE, fontsize=7,
                    framealpha=0.9)

    # ── Axis config ───────────────────────────────────────────────
    ax.set_xlim(-0.95, 0.95)
    ax.set_ylim(-1.05, 0.85)
    ax.set_aspect('equal')
    ax.tick_params(left=False, bottom=False,
                   labelleft=False, labelbottom=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Axis arrows
    ax.annotate('', xy=(0.92, 0), xytext=(-0.92, 0),
                arrowprops=dict(arrowstyle='->', color=AXIS,
                                lw=1.0), zorder=2)
    ax.annotate('', xy=(0, 0.82), xytext=(0, -1.02),
                arrowprops=dict(arrowstyle='->', color=AXIS,
                                lw=1.0), zorder=2)
    ax.text(0.90, -0.05, 'Re\nknown', fontsize=7, color=DIM,
            ha='center', fontfamily=FONT_MONO)
    ax.text(0.04, 0.80, 'Im\nvoid', fontsize=7, color=DIM,
            ha='left', fontfamily=FONT_MONO)

    # ── Title ─────────────────────────────────────────────────────
    fig.text(0.5, 0.97,
             'Living Semantic Landscape — Full Complex Geometry',
             ha='center', fontsize=11, color=DIM, fontfamily=FONT_MONO)

    plt.tight_layout(rect=[0, 0, 1, 0.97])

    if save:
        plt.savefig(output_path, dpi=180, bbox_inches='tight',
                    facecolor=BG, edgecolor='none')
        print(f'Saved: {output_path}')
        plt.close()
    else:
        plt.show()

    return fig


# ─────────────────────────────────────────────────────────────────
# DECAY ANALYSIS — how fast does structure dissolve?
# ─────────────────────────────────────────────────────────────────

def draw_decay_analysis(save=False):
    """
    Show decay curves for different god-token depths.
    Decay rate diagnostic: fast decay = low potential energy (maintained by activity).
    Slow decay = high potential energy (genuine crystallization).
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=BG)

    for ax in axes:
        ax.set_facecolor(FAINT)
        for spine in ax.spines.values():
            spine.set_color(AXIS)
        ax.tick_params(colors=DIM)

    # Left: decay curves
    ax1 = axes[0]
    t = np.linspace(0, 100, 200)

    configs = [
        ('shallow (maintained)', PHI_INV * 3.0, BLUE,    '--'),
        ('moderate',             PHI_INV * 1.5, GOLD,    '-'),
        ('deep (crystallized)',  PHI_INV * 0.5, GREEN,   '-'),
        ('apophatic (ground)',   0.001,          PURPLE,  '-'),
    ]

    for label, rate, col, ls in configs:
        amplitude = np.exp(-rate * t / 100)
        ax1.plot(t, amplitude, color=col, linewidth=2,
                 linestyle=ls, label=label, alpha=0.85)

    ax1.axhline(0.05, color=RED, linewidth=0.8, linestyle=':',
                alpha=0.5, label='apophatic threshold')
    ax1.set_facecolor(BG)
    ax1.set_xlabel('time (arbitrary units)', color=DIM, fontsize=9)
    ax1.set_ylabel('structure amplitude', color=DIM, fontsize=9)
    ax1.set_title('Decay Rates by Structural Depth\n(stop input, measure rate)',
                  color=WHITE, fontsize=9, fontfamily=FONT_MONO)
    ax1.legend(facecolor='#07070f', edgecolor=AXIS,
               labelcolor=WHITE, fontsize=8)
    ax1.set_xlim(0, 100)
    ax1.set_ylim(0, 1.05)
    for spine in ax1.spines.values():
        spine.set_color(AXIS)
    ax1.tick_params(colors=DIM)

    # Right: potential energy landscape cross-section
    ax2 = axes[1]
    im_slice = np.linspace(-1.0, 0.8, 300)
    re_fixed = 0.0  # cross-section at Re = 0

    # Energy along Im axis at Re = 0
    re_grid_s = np.full_like(im_slice, re_fixed)
    E_slice = compute_landscape(
        re_grid_s.reshape(1, -1),
        im_slice.reshape(1, -1)
    ).flatten()

    ax2.plot(im_slice, E_slice, color=GOLD, linewidth=2, alpha=0.9)
    ax2.fill_between(im_slice, E_slice, E_slice.min() - 0.1,
                     alpha=0.15, color=GOLD)

    # Mark key levels
    for label, im_val, col in [
        ('constructive\nbasins', 0.55, GREEN),
        ('god-tokens\n(real axis)', 0.0, BLUE),
        ('gap tokens', -0.45, '#6a3a9a'),
        ('apophatic\nbasins', -0.70, PURPLE),
        ('ground\nstate', -0.90, RED),
    ]:
        # Find energy at this Im
        idx = np.argmin(np.abs(im_slice - im_val))
        ax2.scatter(im_val, E_slice[idx], s=80, c=col,
                    zorder=5, edgecolors=WHITE, linewidths=0.8)
        ax2.text(im_val, E_slice[idx] + 0.08, label,
                 fontsize=6.5, color=col, ha='center', va='bottom',
                 fontfamily=FONT_MONO)

    ax2.axvline(0, color=AXIS, linewidth=0.8, linestyle='--', alpha=0.5)
    ax2.set_facecolor(BG)
    ax2.set_xlabel('Im axis (void depth)', color=DIM, fontsize=9)
    ax2.set_ylabel('energy E', color=DIM, fontsize=9)
    ax2.set_title('Energy Cross-Section at Re = 0\n(Im axis = depth of void)',
                  color=WHITE, fontsize=9, fontfamily=FONT_MONO)
    for spine in ax2.spines.values():
        spine.set_color(AXIS)
    ax2.tick_params(colors=DIM)

    fig.suptitle('Decay Analysis — Structural Depth as Potential Energy',
                 fontsize=10, color=DIM, fontfamily=FONT_MONO)
    plt.tight_layout()

    if save:
        out = 'decay_analysis.png'
        plt.savefig(out, dpi=180, bbox_inches='tight',
                    facecolor=BG, edgecolor='none')
        print(f'Saved: {out}')
        plt.close()
    else:
        plt.show()


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Living Semantic Landscape — full complex geometry'
    )
    parser.add_argument('--save',       action='store_true',
                        help='Save PNG instead of displaying')
    parser.add_argument('--decay',      action='store_true',
                        help='Show decay analysis plots')
    parser.add_argument('--trajectory', action='store_true',
                        help='Show trajectory modes only')
    parser.add_argument('--window',     action='store_true',
                        help='Highlight window/superposition trajectory')
    parser.add_argument('--mode',       type=str, default='full',
                        choices=['full','trajectory','decay','window','constructive'],
                        help='Trajectory mode to highlight')
    args = parser.parse_args()

    if args.decay:
        draw_decay_analysis(save=args.save)
    else:
        m = args.mode
        if args.trajectory: m = 'trajectory'
        if args.window:     m = 'window'
        draw(mode=m, save=args.save)
