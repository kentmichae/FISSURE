#!/bin/bash
# Launch FISSURE ZMQ-to-WebSocket Bridge
export BRIDGE_PORT=8765

cd /home/nebulaone/spark-dev-workspace/FISSURE/web_bridge
source /home/nebulaone/spark-dev-workspace/FISSURE/fissure-venv/bin/activate
python bridge.py "$@"
