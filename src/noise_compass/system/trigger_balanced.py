import socket

def trigger_balanced():
    intent = "Reflect on the identity of existence within the non-orientable manifold."
    print(f"--- TRIGGERING BALANCED PULSE ---")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 5284))
    server.listen(1)
    server.settimeout(60)
    try:
        client, addr = server.accept()
        data = client.recv(1024).decode('utf-8')
        if "GET_INTENT" in data:
            client.send(intent.encode('utf-8'))
            print("  [SUCCESS] Balanced intent synchronized.")
    except Exception as e:
        print(f"  [ERROR] Synchronisation failed: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    trigger_balanced()
