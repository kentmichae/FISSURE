#!/usr/bin/env python3
"""Quick server to serve the FISSURE Web GUI."""
import http.server, threading, os
from pathlib import Path

BRIDGE = Path("/home/nebulaone/spark-dev-workspace/FISSURE/web_bridge")
PORT = 8765

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(BRIDGE), **k)
    def log_message(self, fmt, *args):
        pass  # quiet

server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
t = threading.Thread(target=server.serve_forever, daemon=True)
t.start()
print(f"FISSURE Web GUI served at http://localhost:{PORT}/index.html")
print("Press Ctrl+C to stop")

try:
    while True:
        import time
        time.sleep(1)
except KeyboardInterrupt:
    server.shutdown()
