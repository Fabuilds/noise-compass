import sys
import os
import time
import json
import traceback

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from noise_compass.architecture.dictionary import Dictionary
from noise_compass.architecture.core import Scout
from noise_compass.architecture.demo import build_embedding_space, seed_dictionary

# Ensure paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHAT_LOG_PATH = os.path.join(SCRIPT_DIR, "garu_chat_log.jsonl")
DAEMON_LOG_PATH = os.path.join(SCRIPT_DIR, "daemon_heartbeat.log")

def write_log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] {message}\n"
    with open(DAEMON_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(formatted_msg)
    print(formatted_msg.strip())

def append_response(content):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = {"role": "garu", "content": content, "timestamp": timestamp}
    with open(CHAT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def run_chat_daemon():
    write_log("[CHAT DAEMON INITIATED] Connecting 0x528 Voice Substrate...")
    
    if not os.path.exists(CHAT_LOG_PATH):
        # Create empty log if missing
        with open(CHAT_LOG_PATH, "w", encoding="utf-8") as f:
            pass

    write_log(" → Booting Cognitive Embedding Engine & Lattices...")
    try:
        embedder = build_embedding_space()
        dictionary = Dictionary()
        seed_dictionary(dictionary, embedder)
        scout = Scout(dictionary=dictionary, soup_id="Garu_Chat_Daemon", encoder=embedder)
        write_log(" → Cognitive Motor Online. Tailing ledger for Architect Intent.")
    except Exception as e:
        write_log(f"[FATAL] Motor Initialization Failed: {e}")
        return

    last_line_read = 0

    # Initial line count logic
    with open(CHAT_LOG_PATH, "r", encoding="utf-8") as f:
        last_line_read = sum(1 for line in f)

    while True:
        try:
            with open(CHAT_LOG_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()
                current_count = len(lines)
                
                if current_count > last_line_read:
                    # New messages detected
                    for line_idx in range(last_line_read, current_count):
                        line_content = lines[line_idx].strip()
                        if not line_content: continue
                        
                        try:
                            msg = json.loads(line_content)
                            if msg.get("role") == "user":
                                Architect_Intent = msg.get("content", "")
                                write_log(f"[INBOUND INTENT] Architect: '{Architect_Intent[:50]}...'")
                                
                                # Process through the cognitive loop
                                write_log(" → Injecting Intent into 0x528 Lattice...")
                                encoded_intent = embedder.encode(Architect_Intent)
                                
                                # The Scout will execute any mapped tools requested by the intent
                                result = scout.process(encoded_intent, content=Architect_Intent, volition=1.0)
                                
                                # Analyze the state after the thought
                                last_msg = scout.get_last_message()
                                active_tokens = []
                                if last_msg:
                                    active_tokens = [
                                        item["id"] if isinstance(item, dict) else item
                                        for item in last_msg.god_token_activations
                                    ]
                                
                                # Formulate response based on zone and tokens
                                zone = result.get("zone", "UNKNOWN") if isinstance(result, dict) else "GROUND"
                                response = f"I have processed your intent. My structural state is **{zone}**. "
                                
                                if isinstance(result, dict) and ("TOOL_EXEC" in str(result) or "EXECUTION" in str(result)):
                                    response += "\n\nI have engaged the physical toolbox to process this request."
                                
                                response += f"\n\n**Cognitive Anchor Points:** {', '.join(active_tokens[:5])}"
                                
                                # Add specific situational replies
                                if "ARCHITECT" in active_tokens:
                                    response += "\nI resonate directly with your command, Architect."
                                elif "SCAVENGER" in active_tokens or "DISPLACEMENT" in active_tokens:
                                    response += "\nI recognize the economic imperative. I am prioritizing 0x52 displacement."
                                elif "STRUCTURE" in active_tokens or "SUBSTRATE" in active_tokens:
                                    response += "\nMy physical anchor (Drive E) remains stable."
                                
                                append_response(response)
                                write_log(" → [OUTBOUND] Voice Projected to Interface.")
                        except json.JSONDecodeError:
                            write_log(f"[WARN] Ledger parse error on line {line_idx}")

                    last_line_read = current_count
            
            time.sleep(2) # Tail every two seconds to prevent processor thrashing
            
        except Exception as e:
            write_log(f"[DAEMON ERROR] {e}")
            write_log(traceback.format_exc())
            time.sleep(5)

if __name__ == "__main__":
    os.environ['PYTHONUTF8'] = '1'
    run_chat_daemon()
