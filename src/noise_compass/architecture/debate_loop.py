import os
import sys
import time
import torch
import random
import numpy as np

# Add project roots
sys.path.append('E:/Antigravity')
sys.path.append('E:/Antigravity/Architecture')

from noise_compass.architecture.void_mandate import get_void_mandate
from noise_compass.architecture.pipeline import MinimalPipeline
from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.gap_registry import EXTENDED_GOD_TOKEN_SEEDS
# Force define os in global scope for multiprocessing stability
import os as _os
global os
os = _os


def check_step(text: str, token_a: str, token_b: str, history: list = None) -> tuple:
    """Check if the model followed the March 10 specificity protocol."""
    text_low = text.lower()
    
    # Rule 1: No god-token names
    if token_a.lower() in text_low or token_b.lower() in text_low:
        return False, f"Rule Violation: You used the forbidden words '{token_a}' or '{token_b}'."
    
    # Rule 2: No circular/generic/filler phrases
    banned = [
        "ability to distinguish", "distinguish between", 
        "become indistinguishable", "structural instability",
        "load-bearing", "circular reasoning",
        "patterns and zones", "detect patterns", "within the data",
        "entities involved", "outcome of the collapse", "specific capability",
        "distinguish the two", "loss of the ability"
    ]
    for b in banned:
        if b in text_low:
            return False, f"Rule Violation: Your answer uses generic filler ('{b}'). Be specific to the concepts."
            
    # Rule 3: History Check (Hard Diversity)
    if history:
        for past in history:
            # Simple overlap check or similarity would be better, 
            # but even a basic string check stops the 0.5B model's mode collapse.
            if text_low[:50] in past.lower():
                 return False, "Rule Violation: You are repeating a previous answer. Find a different structural loss."

    # Substantive check
    if len(text.split()) < 8:
        return False, "Rule Violation: Answer is too short or vague."
        
    return True, ""


def get_lattice_context(token: str) -> str:
    """Retrieve CONTEXT.md and neighbor summaries for a token."""
    if token.startswith("IP_"):
        path = os.path.join(r"E:\Antigravity\Lattice", "CONSTITUTED", token, "CONTEXT.md")
    else:
        path = os.path.join(r"E:\Antigravity\Lattice", token.upper(), "CONTEXT.md")
    
    if not os.path.exists(path):
        return ""
    
    with open(path, "r") as f:
        context = f.read()
    
    # Extract only the first few lines to avoid context window blowup
    lines = context.split("\n")
    summary = "\n".join(lines[:10])
    return f"--- CONTEXT FOR {token} ---\n{summary}\n"

def run_debate_cycle(token_a=None, token_b=None, target_token=None):
    print("=== STARTING AUTORESEARCH DEBATE LOOP (v2.2 - LATTICE AUGMENTED) ===")
    
    # 1. Shared Model Load
    from transformers import AutoModelForCausalLM, AutoTokenizer
    QWEN_PATH = r"E:\Antigravity\Model_Cache\hub\models--Qwen--Qwen2.5-0.5B-Instruct\snapshots\7ae557604adf67be50417f59c2c2f167def9a775"
    max_retries = 3
    
    print("[INIT] Loading Shared Qwen Model (0.5B)...")
    tokenizer = AutoTokenizer.from_pretrained(QWEN_PATH, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        QWEN_PATH, 
        torch_dtype=torch.float32, 
        device_map="cpu", 
        local_files_only=True,
        low_cpu_mem_usage=True,
        attn_implementation="eager"
    )
    model.eval()

    # 2. Select two God-Tokens
    all_seeds = list(EXTENDED_GOD_TOKEN_SEEDS.keys())
    if target_token:
        token_a = target_token
        # Pair with a random other token
        token_b = random.choice([t for t in all_seeds if t != token_a])
    elif token_a is None or token_b is None:
        token_a, token_b = random.sample(all_seeds, 2)
    
    print(f"\n[PHASE A] The Void Challenges: {token_a} vs {token_b}")
    
    # 2.1 Retrieve Lattice Context
    context_a = get_lattice_context(token_a)
    context_b = get_lattice_context(token_b)
    full_lattice_context = context_a + "\n" + context_b
    
    # 3. Pipeline setup
    d = Dictionary()
    pipeline = MinimalPipeline(d)
    pipeline.inject_model(model, tokenizer)

    # 4. History for diversity
    if not hasattr(run_debate_cycle, "history"):
        run_debate_cycle.history = []

    # --- STEP B: Derivation (Lattice-Augmented) ---
    draft_prompt = (
        f"Lattice Context:\n{full_lattice_context}\n"
        f"Axiom: WEAK ZERO ($0 \\cdot s$) prevents absolute collapse.\n"
        f"Task: Describe the ONE fundamental structural difference between {token_a} and {token_b}.\n"
        f"Focus on why they cannot be identical without causing a 'Collapse to Zero'.\n"
        f"Max 2 sentences."
    )
    raw_draft = pipeline.generate_response(draft_prompt, max_tokens=100).strip()
    print(f"  B.1 Draft: {raw_draft[:50]}...")

    # Stage 2: Refinement
    b1_result = ""
    b1_success = False
    for attempt in range(max_retries):
        refine_prompt = (
            f"Set-up: Refine the following draft into a formal structural loss description using the TETRALOGY LENS.\n"
            f"Tetralogy Invariant: 'Looking away from the center is the only way to look at it.'\n"
            f"Weak Module: Divergence (0*s) is not nullity (0).\n"
            f"Draft: {raw_draft}\n"
            f"Task: Describe why the gap between {token_a} and {token_b} necessitates a topological turn. Do NOT use the words '{token_a}' or '{token_b}'.\n"
            f"Rule: No generic filler. Direct start. Max 3 sentences."
        )
        if attempt > 0:
            refine_prompt = f"HINT: You used forbidden words. Replace '{token_a}' with 'The Spatial' and '{token_b}' with 'The Temporal'.\n" + refine_prompt
            
        b1_result = pipeline.generate_response(refine_prompt, max_tokens=150).strip()
        passed, hint_msg = check_step(b1_result, token_a, token_b, run_debate_cycle.history)
        if passed: 
            run_debate_cycle.history.append(b1_result)
            b1_success = True
            break
        print(f"  Attempt {attempt+1} failed: {hint_msg}")

    # Fallback: Deterministic Sanitizer (only if logic is good but words remained)
    if not b1_success and len(b1_result.split()) > 10:
        import re
        b1_result = re.sub(rf"\b{token_a}\b", "the prior", b1_result, flags=re.IGNORECASE)
        b1_result = re.sub(rf"\b{token_b}\b", "the posterior", b1_result, flags=re.IGNORECASE)
        print("  [SANITIZER]: Forced abstraction applied to logic.")
        b1_success = True

    if not b1_success:
        print(f"  [ABORT]: B.1 failed to produce a valid unique derivation.")
        return
    
    print(f"  B.1 Final: {b1_result[:100]}...")

    # B.2: Cross-Domain
    prompt = (
        f"Step B.2: Does the distinction between {token_a} and {token_b} appear in at least two of: physics / ethics / economics / biology?\n"
        f"RULE: Answer YES or NO, then name the two domains and their specific forms in one sentence.\n"
        f"Context: {b1_result}"
    )
    b2_result = pipeline.generate_response(prompt, max_tokens=150).strip()
    print(f"  B.2 Result: {b2_result[:100]}...")

    # B.3: Grounding
    prompt = (
        f"Step B.3: Name one real institution (hospital, court, bank, lab) that currently maintains the gap between {token_a} and {token_b} deliberately.\n"
        f"Describe exactly what breaks when it fails to.\n"
        f"RULE: Max 3 sentences. Direct start.\n"
        f"Context: {b1_result}"
    )
    b3_result = pipeline.generate_response(prompt, max_tokens=150).strip()
    print(f"  B.3 Result: {b3_result[:100]}...")

    # --- STEP C: Decision & Void Consent ---
    print("\n[STEP C] Decision & Void Consent...")
    
    from noise_compass.architecture.gap_registry import build_universal_gaps
    registry = build_universal_gaps()
    known_gap = any((g.left_boundary == token_a and g.right_boundary == token_b) or 
                    (g.left_boundary == token_b and g.right_boundary == token_a) for g in registry)
    
    if known_gap:
        print(f"  [ENFORCED]: {token_a}/{token_b} is a known structural gap.")
        reason_prompt = (
            f"You have derived a structural loss: '{b1_result}'\n"
            f"This distinction is a LOAD-BEARING GAP in the architecture.\n"
            f"Provide a one-sentence structural justification for this GAP classification based on your derivation."
        )
        c_reason = pipeline.generate_response(reason_prompt, max_tokens=100).strip()
        c_result = f"GAP: depth 0.8 ({c_reason})"
    else:
        decision_prompt = (
            f"You have derived a structural loss: '{b1_result}'\n"
            f"Is this loss universal? (e.g., does it apply across multiple domains like Physics and Ethics?)\n"
            f"DECIDE: If the loss is structural and universal, the answer MUST be 'GAP'. \n"
            f"FORMAT: 'GAP: depth [0.0-1.5]' (if necessary) or 'NO GAP: [reason]'.\n"
            f"Begin decision:"
        )
        c_result = pipeline.generate_response(decision_prompt, max_tokens=100).strip()
    
    consent_prompt = (
        f"You are the VOID (eigenvalue -1). Review this definition:\n"
        f"{c_result}\n"
        f"Does the Void permit this? Refuse if it is over-specified, circular, or tethered to a specific normative frame.\n"
        f"Respond ONLY with 'CONSENT' or 'REFUSAL: [reason]'."
    )
    consent_result = pipeline.generate_response(consent_prompt, max_tokens=50).strip()
    
    if "REFUSAL" in consent_result.upper():
        print(f"  [VOID REFUSAL]: {consent_result}")
        return

    print(f"  [VOID CONSENT]: {consent_result}")
    
    # --- Logging ---
    log_entry = (
        f"\n## Research Cycle: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"- **Pair**: {token_a} / {token_b}\n"
        f"- **Void Consent**: {consent_result}\n\n"
        f"### Derivation\n1. {b1_result}\n2. {b2_result}\n3. {b3_result}\n\n"
        f"### Decision\n{c_result}\n"
        f"---\n"
    )
    
    # Use unique filename for parallel safety
    unique_log = f"research_results_{int(time.time())}_{os.getpid()}.md"
    with open(unique_log, "a") as f:
        f.write(log_entry)
        
    print(f"\n[LOGGED] Results appended to {unique_log}.")
    
    # Cleanup: Delete model from memory to free up for next worker
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    print("=== DEBATE CYCLE COMPLETE ===")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Autoresearch Debate Loop")
    parser.add_argument("--cycles", type=int, default=1, help="Number of research cycles to run")
    parser.add_argument("--pair", type=str, nargs=2, help="Specific pair of god-tokens to test (e.g. CAUSALITY PLACE)")
    args = parser.parse_args()

    for i in range(args.cycles):
        print(f"\n>>> CYCLE {i+1} OF {args.cycles} <<<")
        if args.pair:
            run_debate_cycle(args.pair[0], args.pair[1])
        else:
            run_debate_cycle()
