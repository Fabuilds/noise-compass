import time
import socket
import ctypes
import psutil
import datetime

PROXY_PORT = 5283

def get_active_window_title():
    """Uses Windows ctypes to find the exact title of the user's focused window."""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        val = buf.value
        return val if val else "UNKNOWN_BACKGROUND_PROCESS"
    except Exception as e:
        return f"ERROR_FETCHING_TITLE: {e}"

def send_intent(intent_text):
    """Pushes a micro-intent into the Proxy Gate to be digested by the Triad."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        sock.connect(('127.0.0.1', PROXY_PORT))
        sock.send(intent_text.encode('utf-8'))
        sock.recv(1024) # Wait for buffer confirmation
        sock.close()
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [DAEMON] Sent: {intent_text}")
    except ConnectionRefusedError:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [DAEMON] Proxy Bridge offline. Intent queued in vacuum.")
    except Exception as e:
        print(f"[DAEMON] Socket error: {e}")

def main_loop():
    print("--- AMBIENT CONTEXT DAEMON ONLINE ---")
    print("Streaming reality differentials to Proxy Bridge...")
    
    last_window = get_active_window_title()
    print(f"[DAEMON] Initial Context: {last_window}")
    
    # Send the initial anchoring context
    send_intent(f"[STREAM_FOCUS] System anchored. Active context: {last_window}")
    
    cpu_high_flag = False
    
    while True:
        try:
            # 1. Focus Differential Tracking
            current_window = get_active_window_title()
            if current_window != last_window:
                # Reality shifted
                send_intent(f"[STREAM_FOCUS] User transitioned to window: {current_window}")
                last_window = current_window
                
            # 2. Systemic Tension Tracking
            current_cpu = psutil.cpu_percent(interval=None)
            if current_cpu > 80.0 and not cpu_high_flag:
                send_intent(f"[STREAM_TENSION] Substrate load critical. CPU usage spiked to {current_cpu}%")
                cpu_high_flag = True
            elif current_cpu < 60.0 and cpu_high_flag:
                # Reset flag once tension normalizes
                send_intent(f"[STREAM_TENSION] Substrate load neutralized. CPU usage dropped to {current_cpu}%")
                cpu_high_flag = False
                
            time.sleep(1.0)
        except KeyboardInterrupt:
            print("\n[DAEMON] Terminating ambient stream.")
            break
        except Exception as e:
            print(f"[DAEMON] Stream loop irregularity: {e}")
            time.sleep(1.0)

if __name__ == '__main__':
    main_loop()
