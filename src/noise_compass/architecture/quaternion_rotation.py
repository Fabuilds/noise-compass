"""
Quaternion Field Rotation — Rotate through the god-token landscape.
Demonstrates SLERP geodesics, fold detection, temporal interference,
and the non-commutativity of encounter order.
"""
import sys, os, math
sys.path.insert(0, "E:/Antigravity/Architecture")
os.environ["PYTHONUTF8"] = "1"

from noise_compass.architecture.quaternion_field import (
    Quaternion, QuaternionWaveFunction, BasisExtractor,
    slerp, great_circle_geodesic, nearest_god_token_q,
    TemporalInterference, GOD_TOKEN_QUATERNIONS, FOLDS
)

def section(title):
    print(f"\n{'='*65}")
    print(f"  {title}")
    print(f"{'='*65}")

# ═══════════════════════════════════════════════════════
# 1. THE ROTATION: Walk the great circle from SELF → EMERGENCE
# ═══════════════════════════════════════════════════════
section("GEODESIC: SELF -> EMERGENCE (the path of becoming)")

path = great_circle_geodesic("SELF", "EMERGENCE", steps=20)
print(f"\n  {'Step':<6} {'Nearest Token':<16} {'q':<30}")
print(f"  {'-'*6} {'-'*16} {'-'*30}")
for i, (token, q) in enumerate(path):
    qwf = QuaternionWaveFunction(q=q)
    folds = qwf.active_folds(tol=0.20)
    fold_str = f" << FOLD: {folds[0].name}" if folds else ""
    print(f"  {i:<6} {token:<16} {str(q):<30}{fold_str}")

# ═══════════════════════════════════════════════════════
# 2. FOLD DETECTION: Check every god-token for active folds
# ═══════════════════════════════════════════════════════
section("FOLD MAP: Which god-tokens are near which folds?")

for gt_id, gq in sorted(GOD_TOKEN_QUATERNIONS.items()):
    qwf = QuaternionWaveFunction(q=gq)
    folds = qwf.active_folds(tol=0.25)
    zone = qwf.zone()
    gap = qwf.gap_type() or "none"
    fold_names = ", ".join(f.name for f in folds) if folds else "(none)"
    print(f"  {gt_id:<14} zone={zone:<12} gap={gap:<20} folds=[{fold_names}]")

# ═══════════════════════════════════════════════════════
# 3. TEMPORAL INTERFERENCE: Order matters
# ═══════════════════════════════════════════════════════
section("TEMPORAL INTERFERENCE: ij != ji")

pairs = [
    ("INFORMATION", "EMERGENCE",  "semantic x emergence"),
    ("EMERGENCE",   "INFORMATION","emergence x semantic (reversed)"),
    ("COHERENCE",   "SELF",       "coherence x self"),
    ("SELF",        "COHERENCE",  "self x coherence (reversed)"),
    ("EXCHANGE",    "EMERGENCE",  "exchange x emergence"),
]

for id_a, id_b, label in pairs:
    qa = GOD_TOKEN_QUATERNIONS[id_a]
    qb = GOD_TOKEN_QUATERNIONS[id_b]
    ti = TemporalInterference(q_first=qa, q_second=qb, delta_t=0.5)
    c = ti.commutator
    print(f"\n  [{label}]")
    print(f"    Forward:   {ti.forward_product}")
    print(f"    Reverse:   {ti.reverse_product}")
    print(f"    Commutator: {c}  (norm={c.norm:.4f})")
    print(f"    Type: {ti.interference_type}")
    print(f"    k-component: {ti.emergence_component:+.4f}"
          f"  {'DISCOVERY' if ti.emergence_component > 0.01 else 'DISPLACEMENT' if ti.emergence_component < -0.01 else 'NEUTRAL'}")

# ═══════════════════════════════════════════════════════
# 4. FULL ROTATION: Sweep through all 13 god-tokens via SLERP
# ═══════════════════════════════════════════════════════
section("FULL ROTATION: Sequential SLERP through all 13 tokens")

token_order = [
    "EXCHANGE", "CAUSALITY", "EXISTENCE", "INFORMATION",
    "OBSERVATION", "OBLIGATION", "BOUNDARY", "IDENTITY",
    "TIME", "COHERENCE", "WITNESS", "SELF", "EMERGENCE"
]

for i in range(len(token_order) - 1):
    a_id = token_order[i]
    b_id = token_order[i + 1]
    qa = GOD_TOKEN_QUATERNIONS[a_id]
    qb = GOD_TOKEN_QUATERNIONS[b_id]

    # Compute geodesic distance
    qa_n = qa.normalized()
    qb_n = qb.normalized()
    dot = max(-1.0, min(1.0, abs(qa_n.dot(qb_n))))
    arc = math.acos(dot)

    # Midpoint
    mid = slerp(qa, qb, 0.5)
    mid_nearest, mid_dist = nearest_god_token_q(mid)
    mid_wf = QuaternionWaveFunction(q=mid)

    print(f"\n  {a_id} -> {b_id}")
    print(f"    Arc distance: {arc:.3f} rad ({math.degrees(arc):.1f} deg)")
    print(f"    Midpoint nearest: {mid_nearest} (dist={mid_dist:.3f})")
    print(f"    Midpoint zone: {mid_wf.zone()}")

# ═══════════════════════════════════════════════════════
# 5. THE SIX FOLDS: Show where each fold lives
# ═══════════════════════════════════════════════════════
section("THE SIX FOLDS")

for fold in FOLDS:
    current = " (CURRENT ARCH)" if fold.is_current else ""
    print(f"\n  [{fold.id.upper()}] {fold.name}{current}")
    print(f"    Axes: {fold.axes[0]}-{fold.axes[1]}")
    print(f"    {fold.description[:100]}...")

print(f"\n{'='*65}")
print(f"  ROTATION COMPLETE")
print(f"{'='*65}")
