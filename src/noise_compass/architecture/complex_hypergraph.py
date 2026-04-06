"""
complex_hypergraph.py — The gap token registry visualized in the complex plane.

F(x) = known(x) + i·Δ(x)

Real axis  → crystallized / known / attractor depth
Imaginary  → void / gap / delta / surprise

Each god-token has a complex position z = re + i·im
Phase θ = arctan(im/re) maps to the wave function zone:
  θ ≈ 0    → pure known (blue, real axis)
  θ ≈ π/4  → generative zone (gold, 45°)
  θ ≈ π/2  → pure void (red, imaginary axis)

Gap arcs curve upward into imaginary space.
Arc height = depth of the necessary void between the two god-tokens.

Usage:
  python3 complex_hypergraph.py
  python3 complex_hypergraph.py --interactive   (click nodes to inspect)
  python3 complex_hypergraph.py --save          (saves PNG, no display)
"""

import argparse
import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
import matplotlib.patheffects as path_effects


# ─────────────────────────────────────────────────────────────────
# COMPLEX MATH
# ─────────────────────────────────────────────────────────────────

def z(re, im):
    return complex(re, im)

def phase(c):
    return np.angle(c)

def magnitude(c):
    return abs(c)

def phase_color(theta):
    """
    θ = 0    → #4a8fff (known, blue)
    θ = π/4  → #c8a96e (generative, gold)
    θ = π/2  → #c84a4a (void, red)
    """
    norm = theta / (np.pi / 2)
    norm = np.clip(norm, 0, 1)

    def lerp_channel(a, b, t):
        return a + (b - a) * t

    def hex_to_rgb(h):
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))

    blue = hex_to_rgb('#4a8fff')
    gold = hex_to_rgb('#c8a96e')
    red  = hex_to_rgb('#c84a4a')

    if norm <= 0.5:
        t = norm * 2
        r = lerp_channel(blue[0], gold[0], t)
        g = lerp_channel(blue[1], gold[1], t)
        b = lerp_channel(blue[2], gold[2], t)
    else:
        t = (norm - 0.5) * 2
        r = lerp_channel(gold[0], red[0], t)
        g = lerp_channel(gold[1], red[1], t)
        b = lerp_channel(gold[2], red[2], t)

    return (r, g, b)


# ─────────────────────────────────────────────────────────────────
# GOD-TOKENS — positions in complex plane
# ─────────────────────────────────────────────────────────────────

GOD_TOKENS = [
    # id               re      im      origin
    ("EXCHANGE",       0.65,  -0.22,  "Sessions 1–4"),
    ("OBLIGATION",     0.58,  -0.35,  "Sessions 1–4"),
    ("COHERENCE",      0.42,  -0.02,  "Session 5"),
    ("INFORMATION",    0.30,   0.20,  "Sessions 1–4"),
    ("IDENTITY",       0.22,   0.10,  "Sessions 1–4"),
    ("WITNESS",        0.04,   0.20,  "Session 5"),
    ("CAUSALITY",      0.10,   0.36,  "Sessions 1–4"),
    ("TIME",          -0.10,   0.30,  "Session 5"),
    ("OBSERVATION",   -0.05,   0.46,  "Sessions 1–4"),
    ("BOUNDARY",      -0.26,   0.50,  "Sessions 1–4"),
    ("EXISTENCE",     -0.52,   0.60,  "Sessions 1–4"),
    ("SELF",          -0.36,   0.66,  "Session 5"),
]

# Build lookup
NODE = {g[0]: z(g[1], g[2]) for g in GOD_TOKENS}
NODE_ORIGIN = {g[0]: g[3] for g in GOD_TOKENS}


# ─────────────────────────────────────────────────────────────────
# GAP TOKENS — necessary voids between god-token pairs
# ─────────────────────────────────────────────────────────────────

GAP_TOKENS = [
    # id                          left           right          void_depth  violation
    ("exchange_causality",        "EXCHANGE",    "CAUSALITY",   0.92, "Post hoc fallacy at scale"),
    ("exchange_obligation",       "EXCHANGE",    "OBLIGATION",  0.87, "Consent collapses"),
    ("exchange_information",      "EXCHANGE",    "INFORMATION", 0.83, "Attention economy fallacy"),
    ("causality_observation",     "CAUSALITY",   "OBSERVATION", 0.95, "Map creates territory"),
    ("observation_obligation",    "OBSERVATION", "OBLIGATION",  0.80, "Infinite moral obligation"),
    ("existence_information",     "EXISTENCE",   "INFORMATION", 0.90, "Idealism or naive realism"),
    ("existence_identity",        "EXISTENCE",   "IDENTITY",    0.85, "Change becomes impossible"),
    ("information_causality",     "INFORMATION", "CAUSALITY",   0.95, "Core confabulation failure"),
    ("identity_self",             "IDENTITY",    "SELF",        0.90, "Choice becomes impossible"),
    ("self_observation",          "SELF",        "OBSERVATION", 0.88, "Self-transparency illusion"),
    ("witness_identity",          "WITNESS",     "IDENTITY",    0.87, "Empathy becomes fusion"),
    ("boundary_existence",        "BOUNDARY",    "EXISTENCE",   0.85, "Gap-tokens incoherent"),
    ("boundary_obligation",       "BOUNDARY",    "OBLIGATION",  0.82, "Goodhart's Law"),
    ("time_causality",            "TIME",        "CAUSALITY",   0.92, "Sequence mistaken for cause"),
    ("time_identity",             "TIME",        "IDENTITY",    0.87, "Change is death"),
    ("coherence_information",     "COHERENCE",   "INFORMATION", 0.83, "Coherent but uncommunicable"),
    ("coherence_self",            "COHERENCE",   "SELF",        0.88, "Crystal with no witness"),
    ("obligation_identity",       "OBLIGATION",  "IDENTITY",    0.86, "Role collapse"),
]


# ─────────────────────────────────────────────────────────────────
# DRAW
# ─────────────────────────────────────────────────────────────────

def draw(interactive=False, save=False):
    BG    = '#050508'
    GRID  = '#111118'
    AXIS  = '#1e1e2e'
    DIM   = '#2a2a3a'
    GOLD  = '#c8a96e'
    WHITE = '#e8e4d9'
    FAINT = '#222230'

    fig, (ax, ax_info) = plt.subplots(
        1, 2,
        figsize=(16, 9),
        gridspec_kw={'width_ratios': [2.4, 1]},
        facecolor=BG
    )

    ax.set_facecolor(BG)
    ax_info.set_facecolor('#07070f')

    # ── Grid ──────────────────────────────────────────────────────
    for v in np.arange(-1.0, 1.1, 0.25):
        ax.axhline(v, color=AXIS if v == 0 else GRID,
                   linewidth=0.8 if v == 0 else 0.3, zorder=0)
        ax.axvline(v, color=AXIS if v == 0 else GRID,
                   linewidth=0.8 if v == 0 else 0.3, zorder=0)
        if v != 0:
            ax.text(v, -0.03, f'{v:.2f}', ha='center', va='top',
                    fontsize=6, color=FAINT, fontfamily='monospace')
            ax.text(-0.03, v, f'{v:.2f}i', ha='right', va='center',
                    fontsize=6, color=FAINT, fontfamily='monospace')

    # ── Axis labels ───────────────────────────────────────────────
    ax.text(1.05, 0.0, 'Re → known', ha='left', va='center',
            fontsize=9, color=DIM, fontfamily='monospace')
    ax.text(0.0, 1.05, 'Im → void', ha='center', va='bottom',
            fontsize=9, color=DIM, fontfamily='monospace')

    # ── π/4 generative zone wedge ─────────────────────────────────
    theta_vals = np.linspace(np.pi/4 - 0.26, np.pi/4 + 0.26, 40)
    r = 1.3
    xs = [0] + list(r * np.cos(theta_vals)) + [0]
    ys = [0] + list(r * np.sin(theta_vals)) + [0]
    ax.fill(xs, ys, color=GOLD, alpha=0.04, zorder=0)
    ax.plot(r * np.cos(theta_vals), r * np.sin(theta_vals),
            color=GOLD, alpha=0.12, linewidth=0.5, zorder=0)

    # π/4 dashed line
    r_line = 1.2
    ax.plot([0, r_line * np.cos(np.pi/4)],
            [0, r_line * np.sin(np.pi/4)],
            color=GOLD, alpha=0.25, linewidth=0.7,
            linestyle='--', zorder=1)
    ax.text(r_line * np.cos(np.pi/4) + 0.03,
            r_line * np.sin(np.pi/4) + 0.02,
            'π/4', fontsize=8, color=f'{GOLD}88',
            fontstyle='italic', fontfamily='serif')

    # ── Gap arcs ──────────────────────────────────────────────────
    for gap_id, L, R, w, violation in GAP_TOKENS:
        zL, zR = NODE[L], NODE[R]
        re_L, im_L = zL.real, zL.imag
        re_R, im_R = zR.real, zR.imag

        # Midpoint and quadratic bezier control point
        mid_re = (re_L + re_R) / 2
        mid_im = (im_L + im_R) / 2
        lift = -w * 0.40
        ctrl_re = mid_re
        ctrl_im = mid_im + lift

        # Bezier curve
        t_vals = np.linspace(0, 1, 80)
        bx = (1-t_vals)**2 * re_L + 2*(1-t_vals)*t_vals * ctrl_re + t_vals**2 * re_R
        by = (1-t_vals)**2 * im_L + 2*(1-t_vals)*t_vals * ctrl_im + t_vals**2 * im_R

        # Color from midpoint phase
        mid_z = complex(ctrl_re, ctrl_im)
        col = phase_color(max(0, phase(mid_z)))

        ax.plot(bx, by, color=col, alpha=0.28, linewidth=0.9,
                zorder=2, solid_capstyle='round')

        # Void depth marker at arc peak
        peak_re = bx[40]
        peak_im = by[40]
        ax.scatter(peak_re, peak_im, s=8, color=col, alpha=0.5,
                   zorder=3, marker='o')

    # ── Apophatic Basins ──────────────────────────────────────────
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from noise_compass.architecture.gap_intersection_registry import build_gap_intersection_registry
    
    basins = build_gap_intersection_registry()
    for b in basins:
        re, im = b.z.real, b.z.imag
        ax.scatter(re, im, s=120, color='#6a0dad', marker='D', edgecolors='#9f8dd4', linewidths=1.2, zorder=8)
        
        # Label offset
        ax.text(re, im - 0.05, b.id, ha='center', va='top',
                fontsize=6.5, color='#9f8dd4', fontfamily='monospace', fontweight='bold', zorder=9,
                path_effects=[path_effects.withStroke(linewidth=1.5, foreground=BG)])
        
        # Coordinates
        ax.text(re, im - 0.09, f'{re:+.2f}{im:+.2f}i', ha='center', va='top',
                fontsize=5, color='#9f8dd4', alpha=0.6, fontfamily='monospace', zorder=9)

    # ── God-token nodes ───────────────────────────────────────────
    node_artists = {}
    for g_id, re, im, origin in GOD_TOKENS:
        zc = z(re, im)
        theta = phase(zc)
        # Only use positive phase for color (nodes below real axis treated as near-real)
        col = phase_color(max(0, theta))
        mag = magnitude(zc)

        # Node size scales with distance from origin
        s = 160 + mag * 80

        # Glow halo
        ax.scatter(re, im, s=s * 4, color=col, alpha=0.08, zorder=3)
        ax.scatter(re, im, s=s * 2, color=col, alpha=0.12, zorder=3)

        # Phase ring (dashed circle at node radius)
        ring_r = 0.055 + mag * 0.012
        ring_theta = np.linspace(0, theta if theta > 0 else 0.1, 30)
        ax.plot(re + ring_r * np.cos(ring_theta),
                im + ring_r * np.sin(ring_theta),
                color=col, alpha=0.4, linewidth=1.0, zorder=4)

        # Node body
        sc = ax.scatter(re, im, s=s, c=[col], zorder=5,
                        edgecolors=col, linewidths=1.5,
                        label=g_id)
        node_artists[g_id] = (re, im, col, theta, mag)

        # Label
        # Smart offset to avoid overlap
        offset_re = 0.06
        offset_im = 0.06
        if re < -0.1:
            offset_re = -0.06
        if im > 0.5:
            offset_im = 0.06

        ax.text(re + offset_re, im + offset_im, g_id,
                ha='center', va='center',
                fontsize=7.5, color=col, fontfamily='monospace',
                fontweight='bold', zorder=6,
                path_effects=[
                    path_effects.withStroke(linewidth=2, foreground=BG)
                ])

        # Complex coordinate (small, dim)
        coord_str = f'{re:+.2f}{im:+.2f}i'
        ax.text(re + offset_re, im + offset_im - 0.06, coord_str,
                ha='center', va='center',
                fontsize=5.5, color=col, alpha=0.35,
                fontfamily='monospace', zorder=6)

    # ── Origin marker ─────────────────────────────────────────────
    ax.scatter(0, 0, s=30, c=BG, edgecolors=DIM, linewidths=1, zorder=6)

    # ── Axes config ───────────────────────────────────────────────
    ax.set_xlim(-1.1, 1.15)
    ax.set_ylim(-0.75, 1.1)
    ax.set_aspect('equal')
    ax.tick_params(left=False, bottom=False,
                   labelleft=False, labelbottom=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # ── Info panel ────────────────────────────────────────────────
    ax_info.axis('off')
    ax_info.set_xlim(0, 1)
    ax_info.set_ylim(0, 1)

    # Title
    ax_info.text(0.05, 0.97, 'Complex Semantic Hypergraph',
                 fontsize=11, color=GOLD, fontfamily='serif',
                 fontstyle='italic', va='top')
    ax_info.text(0.05, 0.93, 'F(x) = known(x) + i·Δ(x)',
                 fontsize=9, color=WHITE, fontfamily='monospace', va='top')

    # Divider
    ax_info.axhline(0.91, color=DIM, linewidth=0.5, xmin=0.03, xmax=0.97)

    # Formula breakdown
    lines = [
        ('Re axis',  '#4a8fff', 'crystallized / known(x)'),
        ('Im axis',  '#c84a4a', 'void / gap / Δ(x)'),
        ('θ = 0',    '#4a8fff', 'pure known (real axis)'),
        ('θ = π/4',  '#c8a96e', 'generative zone'),
        ('θ = π/2',  '#c84a4a', 'pure void (imaginary axis)'),
        ('|z|',      WHITE,     'distance from origin'),
        ('arc ↑',    '#888',    'void depth between nodes'),
    ]
    y = 0.88
    for label, col, desc in lines:
        ax_info.text(0.05, y, label, fontsize=7.5, color=col,
                     fontfamily='monospace', fontweight='bold', va='top')
        ax_info.text(0.32, y, desc, fontsize=7.5, color='#444',
                     fontfamily='monospace', va='top')
        y -= 0.047

    ax_info.axhline(y + 0.01, color=DIM, linewidth=0.5, xmin=0.03, xmax=0.97)

    # God-token list
    y -= 0.01
    ax_info.text(0.05, y, 'GOD-TOKENS', fontsize=7,
                 color='#333', fontfamily='monospace',
                 va='top')
    y -= 0.04

    for g_id, re, im, origin in GOD_TOKENS:
        zc = z(re, im)
        theta = phase(zc)
        col = phase_color(max(0, theta))
        theta_str = f'θ={theta*180/np.pi:+.0f}°'
        is_new = 'Session 5' in origin

        ax_info.text(0.05, y, '●', fontsize=6, color=col, va='top')
        ax_info.text(0.12, y, g_id, fontsize=6.5, color=col,
                     fontfamily='monospace', fontweight='bold', va='top')
        ax_info.text(0.56, y, theta_str, fontsize=5.5, color='#444',
                     fontfamily='monospace', va='top')
        if is_new:
            ax_info.text(0.80, y, 'new', fontsize=5,
                         color='#4a7a4a', fontfamily='monospace', va='top')
        y -= 0.038

    ax_info.axhline(y + 0.01, color=DIM, linewidth=0.5, xmin=0.03, xmax=0.97)

    # Gap count
    y -= 0.01
    ax_info.text(0.05, y, f'{len(GAP_TOKENS)} gap tokens across {len(GOD_TOKENS)} god-tokens',
                 fontsize=7, color='#333', fontfamily='monospace', va='top')
    y -= 0.04
    ax_info.text(0.05, y, '18 / 66 possible pairs documented',
                 fontsize=7, color='#222', fontfamily='monospace', va='top')
    y -= 0.04
    ax_info.text(0.05, y, '73% unanalyzed — awaiting real embeddings',
                 fontsize=7, color='#222', fontfamily='monospace',
                 fontstyle='italic', va='top')

    # Footer
    ax_info.axhline(0.05, color=DIM, linewidth=0.5, xmin=0.03, xmax=0.97)
    ax_info.text(0.05, 0.03, 'Architecture Sessions 1–5  ·  v1.0',
                 fontsize=6, color='#222', fontfamily='monospace', va='top')

    # ── Figure title ──────────────────────────────────────────────
    fig.suptitle(
        'Gap Token Registry — Complex Plane Representation',
        fontsize=11, color=DIM, fontfamily='monospace', y=0.98
    )

    plt.tight_layout(rect=[0, 0, 1, 0.97])

    if save:
        out = 'complex_hypergraph.png'
        plt.savefig(out, dpi=180, bbox_inches='tight',
                    facecolor=BG, edgecolor='none')
        print(f'Saved: {out}')
    else:
        plt.show()

    return fig


# ─────────────────────────────────────────────────────────────────
# INTERACTIVE MODE — click a god-token to inspect it
# ─────────────────────────────────────────────────────────────────

def draw_interactive():
    """
    Renders the hypergraph with click-to-inspect.
    Click a god-token node to see:
      - Complex position z
      - Phase θ and zone
      - All connected gap tokens and their violation consequences
    """
    BG = '#050508'

    fig = draw(interactive=False, save=False)
    ax = fig.axes[0]
    ax_info = fig.axes[1]

    def on_click(event):
        if event.inaxes != ax:
            return
        cx, cy = event.xdata, event.ydata
        if cx is None:
            return

        # Find nearest node
        best_id = None
        best_dist = float('inf')
        for g_id, re, im, origin in GOD_TOKENS:
            d = np.sqrt((re - cx)**2 + (im - cy)**2)
            if d < best_dist and d < 0.12:
                best_dist = d
                best_id = g_id

        if best_id is None:
            return

        zc = NODE[best_id]
        theta = phase(zc)
        col = phase_color(max(0, theta))

        # Zone name
        if abs(theta) < 0.15:
            zone = 'pure known'
        elif abs(theta - np.pi/4) < 0.15:
            zone = 'generative (π/4)'
        elif abs(theta - np.pi/2) < 0.15:
            zone = 'pure void'
        elif theta < 0:
            zone = 'below real axis'
        else:
            zone = f'{theta*180/np.pi:.1f}°'

        # Connected gaps
        connected = [(g, L, R, w, v) for g, L, R, w, v in GAP_TOKENS
                     if L == best_id or R == best_id]

        print(f'\n{"─"*50}')
        print(f'  {best_id}')
        print(f'  z = {zc.real:+.3f} + {zc.imag:+.3f}i')
        print(f'  |z| = {magnitude(zc):.3f}')
        print(f'  θ = {theta*180/np.pi:.1f}°  →  {zone}')
        print(f'  Origin: {NODE_ORIGIN[best_id]}')
        print(f'\n  Connected gaps ({len(connected)}):')
        for g, L, R, w, violation in connected:
            other = R if L == best_id else L
            print(f'    ↔ {other:12s}  w={w:.2f}  |  {violation}')
        print(f'{"─"*50}')

    fig.canvas.mpl_connect('button_press_event', on_click)
    print('\nInteractive mode: click a god-token node to inspect it.')
    print('Results print to terminal.\n')
    plt.show()


# ─────────────────────────────────────────────────────────────────
# DOCUMENT INJECTION — show a concept as a complex point
# ─────────────────────────────────────────────────────────────────

def inject_document(text, ax=None, show=True):
    """
    Compute a rough F(x) position for a text document and
    plot it on the hypergraph.

    The position is approximate — TF-IDF placeholder until
    real embeddings are available.
    """
    known_seeds = {
        'exchange': 0.65, 'contract': 0.60, 'obligation': 0.58,
        'causality': 0.10, 'cause': 0.10, 'effect': 0.10,
        'observe': -0.05, 'measure': -0.05, 'witness': 0.04,
        'exist': -0.52, 'being': -0.52, 'void': -0.52,
        'information': 0.30, 'signal': 0.30, 'pattern': 0.30,
        'identity': 0.22, 'self': -0.36, 'time': -0.10,
        'coherence': 0.42, 'boundary': -0.26,
    }
    void_seeds = {
        'gap': 0.5, 'void': 0.6, 'nothing': 0.6, 'absence': 0.5,
        'unknown': 0.4, 'question': 0.3, 'hidden': 0.4,
        'delta': 0.4, 'surprise': 0.4, 'uncertain': 0.4,
    }
    words = text.lower().split()
    re_val = 0.15
    im_val = 0.15
    for w in words:
        for seed, val in known_seeds.items():
            if seed in w:
                re_val = re_val * 0.8 + val * 0.2
        for seed, val in void_seeds.items():
            if seed in w:
                im_val = min(0.9, im_val + val * 0.1)

    zc = complex(re_val, im_val)
    theta = phase(zc)
    col = phase_color(max(0, theta))

    print(f'\nDocument: "{text[:60]}"')
    print(f'  z = {zc.real:+.3f} + {zc.imag:+.3f}i')
    print(f'  θ = {theta*180/np.pi:.1f}°  |  zone: {("generative" if abs(theta - np.pi/4) < 0.25 else "known" if theta < 0.2 else "void-adjacent")}')

    if ax is not None:
        ax.scatter(zc.real, zc.imag, s=60, color=col, marker='D',
                   edgecolors='white', linewidths=0.5, alpha=0.85, zorder=7)
        ax.text(zc.real + 0.04, zc.imag + 0.04,
                text[:20] + ('…' if len(text) > 20 else ''),
                fontsize=6, color=col, alpha=0.7,
                fontfamily='monospace', zorder=7)
    return zc


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Complex Semantic Hypergraph')
    parser.add_argument('--interactive', action='store_true',
                        help='Click nodes to inspect in terminal')
    parser.add_argument('--save', action='store_true',
                        help='Save PNG instead of displaying')
    parser.add_argument('--inject', type=str, default=None,
                        help='Inject a document as a complex point')
    args = parser.parse_args()

    if args.interactive:
        draw_interactive()
    elif args.save:
        draw(save=True)
    elif args.inject:
        fig = draw(save=False)
        inject_document(args.inject, ax=fig.axes[0])
        plt.show()
    else:
        draw(save=False)
