import tkinter as tk # Maybe not? The user asked for a web UI though, but 800x600 window. Wait, no, they said "maybe a 800x600 window with roboto font". I'll configure the Vite SPA to be limited to 800x600.
import os
import json
import asyncio
import socket
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import h5py
import bitnet_tools

app = FastAPI()

# Allow all CORS for the local Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bridge logic to connect to the internal proxy_bridge
PROXY_HOST = '127.0.0.1'
PROXY_PORT = 5283

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

def send_intent_to_ouroboros(intent_text: str):
    """Sends the command text down to Ouroboros via ProxyBridge TCP Socket."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((PROXY_HOST, PROXY_PORT))
            s.sendall(intent_text.encode('utf-8'))
            return True
    except ConnectionRefusedError:
        return False

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # UI sends intent
            payload = json.loads(data)
            msg_type = payload.get("type", "chat")
            
            if msg_type == "chat":
                intent = payload.get("content", "")
                success = send_intent_to_ouroboros(intent)
                ack = {"type": "system", "content": f"Intent forwarded to sovereign engine: {success}"}
                await manager.broadcast(json.dumps(ack))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def tail_log_file():
    log_path = "E:/Antigravity/Runtime/ouroboros_primary_log.txt"
    if not os.path.exists(log_path):
        return
        
    with open(log_path, "r", encoding="utf-8") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                await asyncio.sleep(0.5)
                continue
                
                # Filter for broadcast logic
                if line.strip():
                    if "[QWEN" in line or "[TRINITY" in line or "[EPIPHANY" in line:
                        msg = {"type": "agent", "content": line.strip()}
                        await manager.broadcast(json.dumps(msg))
                    elif "[TOPOLOGY]" in line:
                        msg = {"type": "topology", "content": line.strip()}
                        await manager.broadcast(json.dumps(msg))
                    elif "]" in line:
                        msg = {"type": "log", "content": line.strip()}
                        await manager.broadcast(json.dumps(msg))

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(tail_log_file())

@app.get("/api/files")
async def get_files():
    """Lists files loaded into the Sovereign space (the local workspace)."""
    # For simplicity, scanning E:/Antigravity/Qwen and System
    targets = ["E:/Antigravity/Runtime", "E:/Antigravity/Qwen"]
    files = []
    for t in targets:
        if os.path.exists(t):
            for f in os.listdir(t):
                if f.endswith(".py") or f.endswith(".md"):
                    files.append({"name": f, "path": os.path.join(t, f)})
    return {"files": files}

    return {"superpositions": superpositions}

@app.post("/api/scrutinize")
async def scrutinize_file(data: dict):
    """
    Trigger Phase 129 Volumetric Scrutiny on a file.
    Reads file content and dispatches to BitNet worker.
    """
    path = data.get("path")
    if not path or not os.path.exists(path):
        return {"error": "Invalid file path"}
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Dispatch to BitNet Worker via tools
        result = bitnet_tools.ask_bitnet("SCRUTINIZE", content)
        return result
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Wait for the UI connections
    uvicorn.run(app, host="0.0.0.0", port=5285)
