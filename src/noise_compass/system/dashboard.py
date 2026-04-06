import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
import threading

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# State to hold the latest nodes and triangulations
geometry_state = {
    "nodes": [], # e.g. ["TIME", "EXISTENCE", "CAUSALITY"] -> to position on a ring
    "edges": [], # e.g. [{"source": "TIME", "target": "CAUSALITY", "tension": 0.8}]
    "status": "IDLE", # RESONANT, ASYMMETRIC, MAXIMUM_TENSION
    "spin": "CW",
    "chirality": "NORMAL",
    "variance": 0.0,
    "last_update": ""
}

# The frontend files will reside in System/static
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

@app.route('/')
def serve_index():
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(STATIC_DIR, path)

@app.route('/api/telemetry', methods=['POST'])
def receive_telemetry():
    """Endpoint for Ouroboros to broadcast its current geometric state."""
    global geometry_state
    data = request.json
    
    geometry_state.update(data)
    
    # Broadcast to all connected web clients
    socketio.emit('geometry_update', geometry_state)
    
    return jsonify({"status": "received"}), 200

@app.route('/api/state', methods=['GET'])
def get_state():
    return jsonify(geometry_state)

def run_dashboard(port=5285):
    print(f"[CORTEX] Visual Dashboard running at http://127.0.0.1:{port}")
    # Disable werkzeug logging to keep terminal clean
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    socketio.run(app, host='127.0.0.1', port=port, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    run_dashboard()
