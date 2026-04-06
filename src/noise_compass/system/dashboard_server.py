import asyncio
import websockets
import json
import os

PORT = 8765

async def tail_file(file_path, ws, stream_type):
    if not os.path.exists(file_path):
        return
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                await asyncio.sleep(0.1)
                continue
            
            line = line.strip()
            if not line: continue
            
            payload = {
                "type": stream_type,
                "data": line
            }
            try:
                await ws.send(json.dumps(payload))
            except websockets.exceptions.ConnectionClosed:
                break

async def send_history(file_path, ws, stream_type, lines):
    if not os.path.exists(file_path): return
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.readlines()
        history = content[-lines:]
        for line in history:
            if line.strip():
                try:
                    await ws.send(json.dumps({"type": stream_type, "data": line.strip()}))
                    await asyncio.sleep(0.01)
                except:
                    break

async def handler(websocket, *args):
    print("[DASHBOARD] Client connected. Flooding history...")
    
    await send_history("E:/Antigravity/Runtime/ouroboros_primary_log.txt", websocket, "PRIMARY", 50)
    await send_history("E:/Antigravity/Runtime/ouroboros_apex_log.txt", websocket, "APEX", 100)
    await send_history("E:/Antigravity/Runtime/ouroboros_anchor_log.txt", websocket, "ANCHOR", 20)
    
    print("[DASHBOARD] History flooded. Beginning live tail tracking...")
    t1 = asyncio.create_task(tail_file("E:/Antigravity/Runtime/ouroboros_primary_log.txt", websocket, "PRIMARY"))
    t2 = asyncio.create_task(tail_file("E:/Antigravity/Runtime/ouroboros_apex_log.txt", websocket, "APEX"))
    t3 = asyncio.create_task(tail_file("E:/Antigravity/Runtime/ouroboros_anchor_log.txt", websocket, "ANCHOR"))
    
    try:
        await asyncio.gather(t1, t2, t3)
    except asyncio.CancelledError:
        pass

async def main():
    print(f"[DASHBOARD] Telemetry orchestrator broadcasting on ws://127.0.0.1:{PORT}")
    
    # Resilience: Retry binding for 30 seconds
    retries = 10
    while retries > 0:
        try:
            async with websockets.serve(handler, "127.0.0.1", PORT):
                await asyncio.Future()  # run forever
        except OSError as e:
            if e.errno == 10048:
                print(f"[DASHBOARD] Port {PORT} busy. Retrying in 3s... ({retries} left)")
                retries -= 1
                await asyncio.sleep(3)
            else:
                raise
    print("[DASHBOARD] [CRITICAL] Failed to bind after exhaustively retrying.")

if __name__ == "__main__":
    asyncio.run(main())
