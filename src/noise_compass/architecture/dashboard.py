"""
dashboard.py — Streamlit dashboard for the Architecture Scout + Archiver.
Provides visual access to god-token profiles, gap violations, zone distributions,
and structural overlap networks from persisted archive JSON files.

Run:  streamlit run dashboard.py
"""

import json
import os
import sys
import math
import streamlit as st

# ── Page Config ──
st.set_page_config(
    page_title="Architecture Scout Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paths ──
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVES_DIR = os.path.join(SCRIPT_DIR, "archives")

# ── Styling ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e0e0ff !important;
    }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #2a2a4e;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(100, 100, 255, 0.15);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #8888aa;
        margin-top: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .god-token-bar {
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 4px;
        height: 24px;
        transition: width 0.5s ease;
    }
    .gap-badge {
        background: rgba(255, 100, 100, 0.15);
        border: 1px solid rgba(255, 100, 100, 0.3);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        display: inline-block;
        margin: 0.2rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
    }
    h1 { font-weight: 700 !important; }
    h2 { font-weight: 600 !important; color: #667eea !important; }
    h3 { font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)


def load_archive(path: str) -> dict:
    """Load an archive JSON and compute derived analytics."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("records", [])

    # God-token profile
    gt_counts = {}
    for r in records:
        cluster = r.get("god_token_activations", [])
        for item in cluster:
            gt_id = item["id"] if isinstance(item, dict) else item
            gt_counts[gt_id] = gt_counts.get(gt_id, 0) + 1
    gt_profile = dict(sorted(gt_counts.items(), key=lambda x: -x[1]))

    # Zone distribution
    zones = {}
    for r in records:
        z = r.get("zone", "UNKNOWN")
        zones[z] = zones.get(z, 0) + 1

    # Gap violations
    gap_violations = {}
    for r in records:
        gs = r.get("gap_structure", {})
        for gap_id in gs.get("violated", []):
            gap_violations[gap_id] = gap_violations.get(gap_id, 0) + 1
    gap_violations = dict(sorted(gap_violations.items(), key=lambda x: -x[1]))

    # Energies
    energies = [r.get("energy_level", 0) for r in records]
    mean_energy = sum(energies) / max(len(energies), 1)

    # Causal types
    causal_types = {}
    for r in records:
        ct = r.get("causal_type", "unknown")
        causal_types[ct] = causal_types.get(ct, 0) + 1

    # Degeneracy
    degeneracies = [r.get("degeneracy", 0) for r in records]
    high_degen = sum(1 for d in degeneracies if d > 0.6)

    return {
        "session_id": data.get("session_id", "unknown"),
        "records": records,
        "record_count": len(records),
        "gt_profile": gt_profile,
        "zones": zones,
        "gap_violations": gap_violations,
        "mean_energy": mean_energy,
        "energies": energies,
        "causal_types": causal_types,
        "high_degen_count": high_degen,
        "degeneracies": degeneracies,
    }


def render_metric(value, label):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_god_token_profile(gt_profile, total):
    st.markdown("### 🔱 God-Token Activation Profile")
    if not gt_profile:
        st.info("No god-token activations found.")
        return

    max_count = max(gt_profile.values())
    for gt_id, count in gt_profile.items():
        pct = count / total * 100
        bar_width = count / max_count * 100
        col1, col2, col3 = st.columns([2, 5, 1])
        with col1:
            st.markdown(f"**`{gt_id}`**")
        with col2:
            st.markdown(f"""
            <div style="background: rgba(100,126,234,0.1); border-radius: 4px; overflow: hidden;">
                <div class="god-token-bar" style="width: {bar_width}%;"></div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"**{count}** ({pct:.0f}%)")


def render_zone_distribution(zones):
    st.markdown("### 🌊 Phase Zone Distribution")
    if not zones:
        st.info("No zone data.")
        return

    zone_colors = {
        "GROUND": "#4ade80",
        "CONVERGENT": "#60a5fa",
        "GENERATIVE": "#a78bfa",
        "DIVERGENT": "#fb923c",
        "TURBULENT": "#f87171",
    }
    total = sum(zones.values())
    cols = st.columns(len(zones))
    for i, (zone, count) in enumerate(zones.items()):
        color = zone_colors.get(zone, "#888")
        with cols[i]:
            st.markdown(f"""
            <div style="text-align:center; padding: 1rem; background: {color}15;
                        border: 1px solid {color}40; border-radius: 10px;">
                <div style="font-size: 1.8rem; font-weight: 700; color: {color};
                            font-family: 'JetBrains Mono';">{count}</div>
                <div style="font-size: 0.75rem; color: {color}; text-transform: uppercase;
                            letter-spacing: 1px; margin-top: 0.3rem;">{zone}</div>
                <div style="font-size: 0.7rem; color: #888; margin-top: 0.2rem;">
                    {count/total*100:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)


def render_gap_violations(gap_violations):
    st.markdown("### ⚠️ Gap Violations")
    if not gap_violations:
        st.success("No gap violations detected — structural boundaries intact.")
        return

    for gap_id, count in gap_violations.items():
        st.markdown(f"""
        <div class="gap-badge">
            ⚠ <strong>{gap_id}</strong> — {count}x violated
        </div>
        """, unsafe_allow_html=True)


def render_structural_overlap(records):
    st.markdown("### 🕸️ Structural Overlap Matrix")
    if len(records) < 2:
        st.info("Need at least 2 records for overlap analysis.")
        return

    def extract_ids(cluster):
        ids = set()
        for item in cluster:
            if isinstance(item, str):
                ids.add(item)
            elif isinstance(item, dict):
                ids.add(item.get("id", ""))
        return ids

    # Show first 15 records for performance
    subset = records[:15]
    n = len(subset)

    # Build overlap matrix
    clusters = [extract_ids(r.get("god_token_activations", [])) for r in subset]
    matrix = []
    for i in range(n):
        row = []
        for j in range(n):
            a, b = clusters[i], clusters[j]
            if not a and not b:
                row.append(1.0)
            elif not a or not b:
                row.append(0.0)
            else:
                row.append(len(a & b) / len(a | b))
        matrix.append(row)

    # Display as table
    labels = [f"[{i}]" for i in range(n)]
    header = "| |" + "|".join(labels) + "|"
    sep = "|---|" + "|".join(["---"] * n) + "|"
    rows = []
    for i in range(n):
        cells = []
        for j in range(n):
            v = matrix[i][j]
            if i == j:
                cells.append("—")
            elif v >= 0.8:
                cells.append(f"**{v:.2f}**")
            elif v >= 0.5:
                cells.append(f"{v:.2f}")
            elif v > 0:
                cells.append(f"{v:.2f}")
            else:
                cells.append("·")
        rows.append(f"|{labels[i]}|" + "|".join(cells) + "|")

    md = "\n".join([header, sep] + rows)
    st.markdown(md)


def render_energy_histogram(energies):
    st.markdown("### ⚡ Energy Distribution")
    if not energies:
        return

    # Simple histogram using streamlit
    import collections
    buckets = collections.Counter()
    for e in energies:
        bucket = round(e * 5) / 5  # 0.2 width buckets
        buckets[bucket] += 1

    sorted_buckets = dict(sorted(buckets.items()))
    st.bar_chart(sorted_buckets)


def render_record_table(records):
    st.markdown("### 📋 Record Browser")
    if not records:
        return

    table_data = []
    for i, r in enumerate(records):
        cluster = r.get("god_token_activations", [])
        gt_ids = []
        for item in cluster:
            if isinstance(item, str):
                gt_ids.append(item)
            elif isinstance(item, dict):
                gt_ids.append(item.get("id", "?"))
        table_data.append({
            "#": i,
            "Zone": r.get("zone", "?"),
            "Energy": round(r.get("energy_level", 0), 3),
            "Causal": r.get("causal_type", "?"),
            "God-Tokens": ", ".join(gt_ids),
            "Degen": round(r.get("degeneracy", 0), 3),
            "Preview": (r.get("content_preview", ""))[:60],
        })
    st.dataframe(table_data, use_container_width=True, hide_index=True)


def main():
    # ── Sidebar ──
    st.sidebar.markdown("# 🔬 Scout Dashboard")
    st.sidebar.markdown("---")

    # Find available archives
    archive_files = []
    if os.path.isdir(ARCHIVES_DIR):
        archive_files = [f for f in os.listdir(ARCHIVES_DIR) if f.endswith(".json")]

    if not archive_files:
        st.error(f"No archive files found in `{ARCHIVES_DIR}`")
        return

    selected = st.sidebar.selectbox("📂 Select Archive", archive_files)
    archive_path = os.path.join(ARCHIVES_DIR, selected)
    data = load_archive(archive_path)

    st.sidebar.markdown(f"""
    **Session:** `{data['session_id']}`

    **Records:** {data['record_count']}

    **God-Tokens:** {len(data['gt_profile'])}

    **Mean Energy:** {data['mean_energy']:.3f}
    """)

    # ── Header ──
    st.markdown(f"""
    # 🔬 Architecture Scout Dashboard
    > **F(x) = known(x) + i·Δ(x)** — Structural memory analysis for `{data['session_id']}`
    """)

    # ── Top metrics ──
    cols = st.columns(5)
    with cols[0]:
        render_metric(data["record_count"], "Records")
    with cols[1]:
        render_metric(len(data["gt_profile"]), "God-Tokens")
    with cols[2]:
        render_metric(len(data["gap_violations"]), "Gap Types")
    with cols[3]:
        render_metric(f"{data['mean_energy']:.2f}", "Mean Energy")
    with cols[4]:
        render_metric(data["high_degen_count"], "High Degen")

    st.markdown("---")

    # ── Main content ──
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔱 God-Tokens", "🌊 Zones", "⚠️ Gaps", "🕸️ Overlap", "📋 Records"
    ])

    with tab1:
        render_god_token_profile(data["gt_profile"], data["record_count"])
        st.markdown("---")
        render_energy_histogram(data["energies"])

    with tab2:
        render_zone_distribution(data["zones"])
        st.markdown("---")
        st.markdown("### 🧬 Causal Type Distribution")
        if data["causal_types"]:
            st.bar_chart(data["causal_types"])

    with tab3:
        render_gap_violations(data["gap_violations"])

    with tab4:
        render_structural_overlap(data["records"])

    with tab5:
        render_record_table(data["records"])


if __name__ == "__main__":
    main()
