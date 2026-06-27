import os
import sys
import http.server
import socketserver
import subprocess

# Start HTTP server on port 9080 (serving FISSURE Web GUI)
os.chdir("/home/nebulaone/spark-dev-workspace/FISSURE/web_bridge")

handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("0.0.0.0", 9080), handler)

print("FISSURE Web GUI serving on http://localhost:9080/index.html")
httpd.serve_forever()
