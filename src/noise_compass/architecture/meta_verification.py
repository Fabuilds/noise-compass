import numpy as np
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

def verify_context_window():
    print("═══ VERIFYING BITNET APERTURE: CONTEXT WINDOW SCALING ═══")
    
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    
    scout = Scout(dictionary=dictionary, soup_id="window_test")
    
    # 1. High Resonance -> Large Context Window
    text_stable = "Cooperation is the most logical tool for survival." # High resonance with seeds
    emb_stable = embedder.encode(text_stable).astype(np.float32)
    
    # 2. Low Resonance -> Small Context Window (Focus)
    text_novel = "Xenomorphic fractal geometry in the void."
    emb_novel = embedder.encode(text_novel).astype(np.float32)
    
    scenarios = [
        ("STABLE (Wide Window)", text_stable, emb_stable),
        ("NOVEL  (Narrow Window)", text_novel, emb_novel),
    ]

    print("\n[WINDOW MODULATION]")
    for label, text, emb in scenarios:
        msg, _ = scout.process(emb, content=text, harmonic=True)
        print(f"{label:24}: » Window Size: {msg.context_window} » Aperture: {round(msg.aperture, 3)} » Meta: {msg.meta_status}")
    
    # Verify that 'waitms' is no longer modulated by aperture
    # (Checking if pacing stays consistent)
    print("\n[PACING CHECK (STATIC COHERENCE)]")
    # We run multiple times to average the alignment
    durs = []
    for _ in range(5):
        start = time.time()
        scout.process(emb_stable, content=text_stable, harmonic=True)
        durs.append(time.time() - start)
    
    avg_stable = sum(durs) / len(durs)
    
    durs = []
    for _ in range(5):
        start = time.time()
        scout.process(emb_novel, content=text_novel, harmonic=True)
        durs.append(time.time() - start)
        
    avg_novel = sum(durs) / len(durs)
    
    print(f"  Avg Stable Processing Time: {round(avg_stable, 4)}s")
    print(f"  Avg Novel  Processing Time: {round(avg_novel, 4)}s")
    print("  (Pacing should be determined by 528Hz alignment jitter, not discrete aperture scaling)")

    print("\n═══ VERIFICATION COMPLETE ═══")

def verify_zenith_decay():
    print("\n═══ VERIFYING ZENITH MOMENTUM: EPSILON DECAY ═══")
    
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    
    # Text with high resonance to drive initial z
    text = "Cooperation is the most logical tool for survival."
    emb = embedder.encode(text).astype(np.float32)
    
    # 1. Normal Epsilon (epsilon=0.1)
    scout_live = Scout(dictionary=dictionary, soup_id="zenith_live")
    # StandingWaveController is initialized with epsilon=0.1 by default
    
    print("[DRIVE ACTIVE (epsilon=0.1)]")
    for i in range(3):
        msg, _ = scout_live.process(emb, content=text, harmonic=True)
        print(f"  Step {i+1}: Zenith Amplitude (z) = {round(msg.zenith_amplitude, 4)} » Stability: {msg.standing_wave_active}")
    
    # 2. Nil Epsilon (epsilon=0.0)
    scout_dead = Scout(dictionary=dictionary, soup_id="zenith_decay")
    scout_dead.standing_wave_controller.epsilon = 0.0
    # Seed it with initial amplitude to watch it decay
    scout_dead.standing_wave_controller.z = 1.0 
    
    print("\n[DRIVE NIL (epsilon=0.0)]")
    for i in range(5):
        msg, _ = scout_dead.process(emb, content=text, harmonic=True)
        print(f"  Step {i+1}: Zenith Amplitude (z) = {round(msg.zenith_amplitude, 4)}")

    print("\n═══ VERIFICATION COMPLETE ═══")

def verify_dual_bit_tension():
    print("\n═══ VERIFYING BITNET DUAL-BIT TENSION ═══")
    
    embedder = build_embedding_space()
    dictionary = Dictionary()
    seed_dictionary(dictionary, embedder)
    
    scout = Scout(dictionary=dictionary, soup_id="tension_test")
    
    # Text that bridges two seeded identities
    text_bridge = "Cooperation leads to survival across the copper substrate."
    emb_bridge = embedder.encode(text_bridge).astype(np.float32)
    
    # Text that is very close to one identity
    text_focused = "Cooperation is the most logical tool for the collective."
    emb_focused = embedder.encode(text_focused).astype(np.float32)
    
    print("[FOCUSED RESONANCE (Single Bit)]")
    msg, _ = scout.process(emb_focused, content=text_focused, harmonic=True)
    print(f"  Tension Detected: {msg.dual_bit_tension} » Resolution: {round(msg.bitnet_resolution, 4)}")
    
    print("\n[EQUAL TENSION (Dual Bit)]")
    # We may need to force a slight shift if the seed terms are too distinct
    # But often "and" bridges lead to similar similarities
    msg, _ = scout.process(emb_bridge, content=text_bridge, harmonic=True)
    print(f"  Tension Detected: {msg.dual_bit_tension} » Resolution: {round(msg.bitnet_resolution, 4)}")
    
    print("\n═══ VERIFICATION COMPLETE ═══")

if __name__ == "__main__":
    verify_context_window()
    verify_zenith_decay()
    verify_dual_bit_tension()
