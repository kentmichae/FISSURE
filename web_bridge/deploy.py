#!/usr/bin/env python3
"""
Deploy FISSURE Web GUI Stack
- Starts FISSURE Server on ports 6100/6101
- Starts ZMQ-to-WebSocket Bridge on port 8765
- Serves Web UI with static files
- Monitors health
"""

import subprocess
import sys
import signal
import time
import os

FISSURE_DIR = "/home/nebulaone/spark-dev-workspace/FISSURE"
VENV = os.path.join(FISSURE_DIR, "fissure-venv")
BRIDGE_DIR = os.path.join(FISSURE_DIR, "web_bridge")
DISPLAY = ":99"

procs = []
running = True

def cleanup(signum, frame):
    global running
    running = False
    print("\n[deploy] Shutting down...")
    for p in procs:
        try:
            p.terminate()
        except Exception:
            pass
    time.sleep(2)
    for p in procs:
        try:
            p.kill()
        except Exception:
            pass
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)


def launch_server():
    """Launch FISSURE HIPRFISR Server."""
    print("[deploy] Starting FISSURE HIPRFISR Server...")
    env = os.environ.copy()
    env["DISPLAY"] = DISPLAY
    env["QT_API"] = "pyqt6"
    env["MPL_BACKEND"] = "qtagg"
    env["VIRTUAL_ENV"] = VENV
    env["PATH"] = f"{VENV}/bin:{os.environ.get('PATH','')}"

    p = subprocess.Popen(
        [f"{VENV}/bin/python", "-m", "fissure.Server"],
        cwd=FISSURE_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,
    )
    procs.append(p)

    # Stream output
    def stream():
        for line in iter(p.stdout.readline, b""):
            sys.stdout.buffer.write(line)
            sys.stdout.buffer.flush()
    import threading
    t = threading.Thread(target=stream, daemon=True)
    t.start()
    print(f"[deploy] Server started (PID {p.pid})")
    time.sleep(3)  # wait for ZMQ listeners


def launch_bridge():
    """Launch ZMQ-to-WebSocket Bridge."""
    print("[deploy] Starting ZMQ Bridge...")
    p = subprocess.Popen(
        ["python", "bridge.py"],
        cwd=BRIDGE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,
    )
    procs.append(p)

    def stream():
        for line in iter(p.stdout.readline, b""):
            sys.stdout.buffer.write(line)
            sys.stdout.buffer.flush()
    import threading
    t = threading.Thread(target=stream, daemon=True)
    t.start()
    print(f"[deploy] Bridge started (PID {p.pid})")
    time.sleep(2)


if __name__ == "__main__":
    print("=" * 60)
    print(" FISSURE Web GUI Deployment Stack")
    print("=" * 60)
    print("")
    print("  HIPRFISR Server:  tcp://0.0.0.0:6100 (HB)")
    print("                  tcp://0.0.0.0:6101 (MSG)")
    print("  ZMQ Bridge:      http://0.0.0.0:8765")
    print("  Web UI:          http://0.0.0.0:8765/index.html")
    print("")
    print(" Press Ctrl+C to stop")
    print("=" * 60)
    print("")

    launch_server()
    launch_bridge()

    print("")
    print("[deploy] Stack ready")
    print("[deploy] Open http://localhost:8765/index.html in your browser")
    print("")

    # Keep running
    while running:
        time.sleep(1)
        # Check if processes are alive
        for p in procs:
            if p.poll() is not None:
                print(f"[deploy] WARNING: Process exited with code {p.poll()}")
