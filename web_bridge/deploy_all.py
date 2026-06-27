#!/usr/bin/env python3
"""Deploy FISSURE Web GUI: Server + Bridge + serve index.html."""
import subprocess, sys, signal, time, os
from pathlib import Path

FISSURE_DIR = Path("/home/nebulaone/spark-dev-workspace/FISSURE")
BRIDGE_DIR = FISSURE_DIR / "web_bridge"
VENV_PY = FISSURE_DIR / "fissure-venv" / "bin" / "python"

procs = []

def cleanup(sig, frame):
    print("\n[deploy] Shutting down...")
    for p in procs:
        try: p.terminate()
        except: pass
    time.sleep(2)
    for p in procs:
        try: p.kill()
        except: pass
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

env = {**os.environ, "DISPLAY": ":99", "QT_API": "pyqt6", "MPL_BACKEND": "agg",
       "VIRTUAL_ENV": str(FISSURE_DIR / "fissure-venv")}
env["PATH"] = f"{FISSURE_DIR / 'fissure-venv' / 'bin'}:{env.get('PATH', '')}"

print("=" * 60)
print(" FISSURE Web GUI Deployment Stack")
print("=" * 60)

# ── Server ──────────────────────────────────
print("\n[deploy] Starting HIPRFISR Server...")
p = subprocess.Popen(
    [str(VENV_PY), "-m", "fissure.Server"],
    cwd=str(FISSURE_DIR), env=env,
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1,
)
procs.append(p)
print(f"[deploy] Server pid={p.pid}")

# ── Bridge ──────────────────────────────────────────
print("[deploy] Starting ZMQ-to-WebSocket Bridge...")
q = subprocess.Popen(
    [sys.executable, str(BRIDGE_DIR / "bridge.py")],
    cwd=str(BRIDGE_DIR),
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1,
)
procs.append(q)
print(f"[deploy] Bridge pid={q.pid}")
print("")

# Stream both
def pipe(stream, tag):
    for line in iter(stream.readline, b""):
        print(f"[{tag}] {line.decode('utf-8', errors='replace')}", end="")

# Give ports a moment to bind
time.sleep(2)

print("=" * 60)
print(" Stack deployed!")
print("  HIPRFISR:  tcp://0.0.0.0:6100 (HB), tcp://0.0.0.0:6101 (MSG)")
print("  Web GUI:   http://localhost:8765/index.html")
print("  WebSocket: ws://localhost:8765/ws")
print("=" * 60)

# Keep streaming
while True:
    time.sleep(0.1)
    if p.poll() is not None:
        print(f"[WARN] Server exited {p.poll()}")
        p.stdout.close()
    if q.poll() is not None:
        print(f"[WARN] Bridge exited {q.poll()}")
        q.stdout.close()
