#!/bin/bash
# Launch FISSURE Server with proper environment
export DISPLAY=:99
export QT_API=pyqt6
export MPL_BACKEND=qtagg

cd /home/nebulaone/spark-dev-workspace/FISSURE
source fissure-venv/bin/activate
python -m fissure.Server "$@"
