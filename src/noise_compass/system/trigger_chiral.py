import socket
import time

def trigger_chiral():
    intent = ("Synthesize a new chiral invariant connecting the node of OBLIGATION "
              "with the node of DOC_SHUTIL (high-level file operations) "
              "within the 384-D complex manifold.")
    
    print(f"--- TRIGGERING CHIRAL PULSE ---")
    print(f"INTENT: {intent}")
    
    # Acts as a one-shot server for the Ouroboros loop's get_proxy_intent()
    # It listens on 5284, Ouroboros connects TO IT.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 5284))
    server.listen(1)
    server.settimeout(60)
    
    try:
        client, addr = server.accept()
        data = client.recv(1024).decode('utf-8')
        if "GET_INTENT" in data:
            client.send(intent.encode('utf-8'))
            print("  [SUCCESS] Intent synchronized to loop.")
    except Exception as e:
        print(f"  [ERROR] Synchronisation failed: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    trigger_chiral()
