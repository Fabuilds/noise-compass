import argparse
import sys
import os
import time

# Ensure pathing (Removed sys.path.append for unified package)
from noise_compass.system.ouroboros_resonant import ResonantOuroboros
from noise_compass.system.initialize_h5_logic import initialize_h5_skeleton
from noise_compass.system.h5_manager import H5Manager

def main():
    parser = argparse.ArgumentParser(description="Antigravity: Sovereign Reasoning Engine CLI")
    subparsers = parser.add_subparsers(dest="command", help="Operational Commands")

    # Run Command
    run_parser = subparsers.add_parser("run", help="Start the Ouroboros Loop")
    run_parser.add_argument("--mode", default="primary", choices=["primary", "secondary", "background"], help="Loop mode")
    run_parser.add_argument("--port", type=int, help="Optional port for listener mode")
    run_parser.add_argument("--hours", type=float, default=-1.0, help="Duration of the run (default -1.0 = Perpetual)")

    # Init Command
    init_parser = subparsers.add_parser("init", help="Initialize the H5 Substrate")
    
    # Scan Command
    scan_parser = subparsers.add_parser("scan", help="Run a manifold tension scan")

    # View Command
    view_parser = subparsers.add_parser("view", help="Stream the Hidden Mind log")

    args = parser.parse_args()

    if args.command == "run":
        engine = ResonantOuroboros(mode=args.mode, port=args.port)
        engine.start(duration_hours=args.hours)
    
    elif args.command == "init":
        print("[CLI] Starting Substrate Initialization...")
        initialize_h5_skeleton()
        print("[CLI] Substrate Ready.")

    elif args.command == "scan":
        print("[CLI] Initiating Manifold Tension Scan...")
        # For now, we trigger a short Ouroboros test cycle as the scan
        engine = ResonantOuroboros(mode="test")
        engine.start(duration_hours=0.1)
    
    elif args.command == "view":
        log_path = "e:/Antigravity/Runtime/ouroboros_primary_hidden_mind.txt"
        if os.path.exists(log_path):
            print(f"[CLI] Streaming Hidden Mind from {log_path} (Ctrl+C to stop)...")
            try:
                with open(log_path, 'r') as f:
                    # Seek to end
                    f.seek(0, 2)
                    while True:
                        line = f.readline()
                        if not line:
                            time.sleep(0.5)
                            continue
                        print(line, end="")
            except KeyboardInterrupt:
                print("\n[CLI] View closed.")
        else:
            print(f"[ERROR] Log not found at {log_path}. Start a 'run' first.")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
