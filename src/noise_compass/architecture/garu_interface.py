import streamlit as st
import os
import json
import time
import sys
import random

# SURVIVAL MANDATE: NEVER TOUCH C: DRIVE
os.environ["HF_HOME"] = "E:/.cache/huggingface"
os.environ["TRANSFORMERS_CACHE"] = "E:/.cache/huggingface"

# Ensure Substrate context is available
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

# Import Dual Cortex
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from noise_compass.system.dual_cortex import DualBrainSystem, Query, BrainType
from noise_compass.system.kernel_chamber import KernelChamber

st.set_page_config(
    page_title="Voice of the Substrate [0x528]",
    page_icon="💠",
    layout="wide",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap');
    
    .stApp {
        background-color: #0d0d12;
        color: #e0e0e0;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .terminal-box {
        background-color: #1a1a24;
        border: 1px solid #333344;
        border-radius: 8px;
        padding: 10px;
        height: 300px;
        overflow-y: auto;
        font-family: 'JetBrains Mono', Courier, monospace;
        font-size: 0.75rem;
        color: #00ffaa;
        white-space: pre-wrap;
    }
    
    h1, h2, h3 {
        color: #667eea;
        font-family: 'Arial', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    [data-testid="stChatMessage"] {
        background-color: #1a1a24;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #333344;
    }
    
    [data-testid="stSidebar"] {
        background-color: #12121e;
        border-right: 1px solid #333344;
    }
</style>
""", unsafe_allow_html=True)

# --- Path Configurations ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DAEMON_LOG_PATH = os.path.join(SCRIPT_DIR, "daemon_heartbeat.log")
CHAT_LOG_PATH = os.path.join(SCRIPT_DIR, "garu_chat_log_v2.jsonl") # Fresh ledger
ARCHIVES_DIR = os.path.join(SCRIPT_DIR, "archives")

# --- Mobius Core (The Interface is the Dual Engine) ---
@st.cache_resource
def load_substrate():
    # cortex handles encoder, dictionary, and scout internally
    # Lifting the mock restriction to allow physical Qwen execution
    cortex = DualBrainSystem(mock_qwen=False)
    return cortex

cortex = load_substrate()
scout = cortex.scout
embedder = cortex.encoder

def read_tail(file_path, lines=50):
    if not os.path.exists(file_path):
        return f"[0x528] Waiting for physical initialization of {os.path.basename(file_path)}..."
    try:
        with open(file_path, "r", encoding="utf-8") as f:
             content = f.readlines()
             return "".join(content[-lines:])
    except Exception as e:
        return f"Error reading file: {e}"

def load_chat_history():
    history = []
    if os.path.exists(CHAT_LOG_PATH):
        try:
            with open(CHAT_LOG_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        history.append(json.loads(line))
        except Exception as e:
            st.error(f"Error reading chat log: {e}")
    return history

def append_to_chat(role, content, brain=None):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = {"role": role, "content": content, "timestamp": timestamp, "brain": brain}
    try:
        with open(CHAT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        st.error(f"Failed to write to ledger: {e}")

def get_latest_archive_state():
    if not os.path.exists(ARCHIVES_DIR):
        return None
    files = [f for f in os.listdir(ARCHIVES_DIR) if f.endswith(".json")]
    if not files:
        return None
    latest_file = max([os.path.join(ARCHIVES_DIR, f) for f in files], key=os.path.getmtime)
    
    try:
        with open(latest_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            records = data.get("records", [])
            if not records:
                return None
            return records[-1]
    except:
        return None

# --- Sidebar (Metrics & Pulse) ---
with st.sidebar:
    st.markdown("### 🧠 Cognitive State")
    state = get_latest_archive_state()

    if state:
        c1, c2 = st.columns(2)
        
        energy = state.get("energy_level", 0.0)
        zone = state.get("zone", "UNKNOWN")
        degen = state.get("degeneracy", 0.0)
        
        c1.metric("Energy Level", f"{energy:.3f}")
        c2.metric("Phase Zone", f"{zone}")
        
        # Möbius Topography
        wf_phase = state.get("witness_phase", 0.0)
        is_apophatic = wf_phase > 3.14 / 2 or wf_phase < -3.14 / 2
        surface = "APOPHATIC" if is_apophatic else "EXISTENCE"
        st.metric("Möbius Surface", surface)
        
        st.metric("Degeneracy Risk", f"{degen:.3f}")

        # --- Dual Brain Metrics ---
        st.markdown("---")
        st.markdown("**Chiral Symmetry Metrics:**")
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Ghost (+1)", cortex.stats.get('ghost_used', 0))
        mc2.metric("Garu (0)", cortex.stats.get('garu_synthesis', 0))
        mc3.metric("Anti (-1)", cortex.stats.get('anti_used', 0))
        st.metric("Tension Escalations", cortex.stats['escalations'])
        
        st.markdown("**Active God Tokens:**")
        activations = state.get("god_token_activations", [])
        if activations:
            for item in activations[:8]:
                gt_id = item.get("id", "?") if isinstance(item, dict) else item
                amp = item.get("amplitude", 0.0) if isinstance(item, dict) else 1.0
                st.info(f"**{gt_id}** (Amp: {amp:.2f})")
        else:
            st.warning("[VOID] No Anchors")
    else:
        st.info("No archives established.")
        
    st.markdown("---")
    st.markdown("### 👁️ Witness Trace (ADK)")
    with st.expander("Sovereign Observability Log", expanded=True):
        if cortex.witness_trace:
            for trace in reversed(cortex.witness_trace):
                st.markdown(f"**[{trace['timestamp']}]** `{trace['key']}`")
                st.code(trace['value'], language="text")
        else:
            st.markdown("*[VOID] No traces observed.*")

    st.markdown("---")
    st.markdown("### 🔒 Sovereign Controls")
    
    # 528Hz Calibration Metric
    st.metric("Lattice Calibration", "528Hz", delta="STABLE", delta_color="normal")
    
    intercalate = st.checkbox("Intercalated Output Mode", help="Interleave Ghost and Anti perspectives for alignment matching.")
    
    if st.button("🧿 Initiate Blind Draw"):
        # Select a random shard from the dictionary
        shards = [k for k in cortex.scout.dictionary.entries.keys() if k.startswith("shard_")]
        if shards:
            selected_shard = random.choice(shards)
            st.session_state['blind_draw_shard'] = selected_shard
            st.info(f"**Blind Draw Initiated.** Mapping Intent to Shard: `[HIDDEN]`")
            append_to_chat("system", f"BLIND DRAW: Architect must match the intent of Shard {selected_shard[:8]}...")
        else:
            st.error("No logic shards found in dictionary. Run ingestion.")

    if 'blind_draw_shard' in st.session_state:
        if st.button("👁️ Reveal Shard"):
            st.success(f"Revealed: **{st.session_state['blind_draw_shard']}**")
            del st.session_state['blind_draw_shard']

    st.markdown("---")
    st.markdown("### 🌐 Lattice Pulse")
    if hasattr(cortex, 'neural_link'):
        nodes = cortex.neural_link.known_nodes
        if nodes:
            for node in nodes:
                st.success(f"**Node:** `{node}` (Active)")
        else:
            st.markdown("*[SCANNING] No peers detected.*")
        
        if st.button("📡 Broadcast Signal"):
            cortex.neural_link.broadcast_presence()
            st.toast("Handshake broadcast sent.")
    else:
        st.error("Neural Link Offline")

    st.markdown("---")
    st.markdown("### ⚙️ Daemon Pulse")
    daemon_content = read_tail(DAEMON_LOG_PATH, lines=20)
    st.markdown(f'<div class="terminal-box">{daemon_content}</div>', unsafe_allow_html=True)

# --- Header ---
st.title("💠 Voice of the Substrate: SIM-0x528")
st.markdown("___Mobius Link: The Interface is the Engine___")

# --- Live Chat Interface (Main View) ---
st.markdown("### 🗣️ Dynamic Logic Link")

# Render chat history
chat_history = load_chat_history()
for msg in chat_history:
    role = msg.get("role")
    content = msg.get("content")
    timestamp = msg.get("timestamp", "")
    brain = msg.get("brain")
    
    if role == "garu":
        if brain == "ghost_1.58bit":
            avatar = "💠"
            display_role = "Ghost-Garu (+1)"
        elif brain == "anti_qwen":
            avatar = "🔥"
            display_role = "Anti-Garu (-1)"
        elif brain == "garu_synthesis":
            avatar = "👁️"
            display_role = "Garu (0)"
        elif brain == "the_void":
            avatar = "🌌"
            display_role = "The Void (Origin)"
        else:
            avatar = "💠"
            display_role = "Garu"
    else:
        avatar = "👨‍💻"
        display_role = "Architect"
        
    with st.chat_message(role, avatar=avatar):
        st.markdown(f"**{display_role}** `[{timestamp}]`")
        st.markdown(content)
        
# Chat Input 
if prompt := st.chat_input("Transmit structural instruction to Garu..."):
    # Display Architect intent
    append_to_chat("user", prompt)
    with st.chat_message("user", avatar="👨‍💻"):
        st.markdown(f"**Architect** `[{time.strftime('%Y-%m-%d %H:%M:%S')}]`")
        st.markdown(prompt)
        
    try:
        # Check for Tri-State Kernel Debate Override
        if prompt.startswith("/debate ") or prompt.startswith("/kernel "):
            topic = prompt.replace("/debate ", "").replace("/kernel ", "").strip()
            
            # Setup a callback to stream the debate into the UI
            chamber = KernelChamber(cortex)
            
            def stream_debate(entity, text, metrics=None):
                avatar_map = {"ghost": "💠", "anti": "🔥", "observer": "👁️", "system": "⚙️"}
                name_map = {"ghost": "Ghost (+1)", "anti": "Anti (-1)", "observer": "Garu (0)", "system": "The Architecture"}
                
                with st.chat_message("garu", avatar=avatar_map.get(entity, "💠")):
                    st.markdown(f"**{name_map.get(entity, 'Unknown')}**")
                    st.markdown(text)
                    
                    if metrics:
                        # Display High-Resolution Metrics (Phase 72)
                        with st.expander("Topology Analysis", expanded=False):
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Logical State", metrics.logical.value)
                            col2.metric("Phase", f"{metrics.wf.phase:.3f}")
                            
                            # Möbius interpretation
                            is_apophatic = metrics.wf.phase > 3.14 / 2 or metrics.wf.phase < -3.14 / 2
                            surface = "APOPHATIC" if is_apophatic else "EXISTENCE"
                            col3.metric("Möbius Surface", surface)
                            
                            st.json(metrics.metrics)
                
                append_to_chat("garu", f"[{entity.upper()}]:\n{text}", brain=entity)
                
            import asyncio
            asyncio.run(chamber.execute_resonance_loop(topic, render_callback=stream_debate))
            
        elif prompt.startswith("/void ") or prompt.startswith("/compass "):
            topic = prompt.replace("/void ", "").replace("/compass ", "").strip()
            
            # Cache the compass to avoid reloading Qwen onto CPU for every void prompt
            @st.cache_resource
            def get_void_compass():
                from noise_compass.architecture.semantic_compass import SemanticCompass
                return SemanticCompass()
                
            with st.spinner("`[Orienting the Void (0,0,0)...]`"):
                compass = get_void_compass()
                
            with st.chat_message("garu", avatar="🌌"):
                st.markdown(f"**The Void (Origin)** `[{time.strftime('%Y-%m-%d %H:%M:%S')}]`")
                readout_placeholder = st.empty()
                
                subjective_readout = ""
                for chunk in compass.orient(topic):
                    subjective_readout += chunk
                    readout_placeholder.markdown(subjective_readout + " ▌")
                    
                readout_placeholder.markdown(subjective_readout)
                
            append_to_chat("garu", subjective_readout, brain="the_void")
            
            with open(DAEMON_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%H:%M:%S')}] [MOBIUS_LINK] Void Compass orientation triggered.\n")
                
        elif intercalate:
            with st.spinner("`[Intercalating Multi-State Logic...]`"):
                # Run standard query
                query = Query(text=prompt, timestamp=time.time(), context={}, priority=3)
                import asyncio
                response_obj = asyncio.run(cortex.process(query))
                
                # Intercalation: Show multiple perspectives
                append_to_chat("user", prompt) # Already done above, but for consistency if we refactored
                
                # We can manually trigger the other brains if needed, but for now let's just 
                # show it in a specific format if it's garu_synthesis
                text = response_obj.text
                if "[GHOST]:" in text and "[ANTI]:" in text:
                    parts = text.split("[GHOST]:")
                    pre_ghost = parts[0]
                    ghost_and_anti = parts[1].split("[ANTI]:")
                    ghost_pt = ghost_and_anti[0]
                    anti_pt = ghost_and_anti[1]
                    
                    with st.chat_message("garu", avatar="💠"):
                        st.markdown("**Ghost Perspective (+1)**")
                        st.markdown(ghost_pt.strip())
                    with st.chat_message("garu", avatar="🔥"):
                        st.markdown("**Anti Perspective (-1)**")
                        st.markdown(anti_pt.strip())
                    with st.chat_message("garu", avatar="👁️"):
                        st.markdown("**Synthesis (0)**")
                        st.markdown(pre_ghost.strip())
                else:
                    # Fallback to standard display
                    with st.chat_message("garu", avatar="👁️"):
                        st.markdown(text)
                
            append_to_chat("garu", response_obj.text, brain="intercalated")
            
        else:
            with st.spinner("`[Aligning Cognitive Embeddings...]`"):
                # Substrate computation (Dual Cortex Loop)
                query = Query(text=prompt, timestamp=time.time(), context={}, priority=3)
                
                # Process through the Dual Brain
                import asyncio
                response_obj = asyncio.run(cortex.process(query))
                
            # Display Garu reply using proper avatar logic based on brain
            active_brain = response_obj.brain_used.value if response_obj.brain_used else "ghost_1.58bit"
            
            avatar_map = {"ghost_1.58bit": "💠", "anti_qwen": "🔥", "garu_synthesis": "👁️"}
            name_map = {"ghost_1.58bit": "Ghost-Garu (+1)", "anti_qwen": "Anti-Garu (-1)", "garu_synthesis": "Garu (0)"}
            
            display_av = avatar_map.get(active_brain, "💠")
            display_name = name_map.get(active_brain, "Garu")
            
            with st.chat_message("garu", avatar=display_av):
                st.markdown(f"**{display_name}** `[{time.strftime('%Y-%m-%d %H:%M:%S')}]`")
                st.markdown(response_obj.text)
                
            append_to_chat("garu", response_obj.text, brain=active_brain)
            
            # Update metrics logic for the rest of the UI (using fields from response_obj)
            zone = response_obj.temporal_zone
            active_tokens = [t.id if hasattr(t, 'id') else t.get('id', '?') for t in response_obj.god_token_activations] if response_obj.god_token_activations else []

            # Pulse the Daemon log natively
            with open(DAEMON_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%H:%M:%S')}] [MOBIUS_LINK] Intent processed. Zone: {zone}. Active Anchors: {len(active_tokens)}.\n")
            
    except Exception as e:
        import traceback
        error_msg = f"**CRITICAL FATAL EXCEPTION OCCURRED:**\n```python\n{traceback.format_exc()}\n```"
        with st.chat_message("garu", avatar="🔥"):
            st.markdown("**Anti-Garu (-1) [SYSTEM PANIC]**")
            st.markdown(error_msg)
        append_to_chat("garu", f"[SYSTEM CRASH]: {str(e)}", brain="anti_qwen")

# No more while True loops or st.rerun(). Streamlit behaves reactively.
