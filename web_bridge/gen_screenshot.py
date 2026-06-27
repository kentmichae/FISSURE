#!/usr/bin/env python3
"""Generate a PNG screenshot of the FISSURE Web GUI using PyQt6 headless rendering."""
import sys
import os

# Set environment for headless Qt rendering
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['DISPLAY'] = ':99'

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWebEngineWidgets import QWebEngineView
import subprocess
import sys

# Create application
app = QApplication(sys.argv)

# Create web view
view = QWebEngineView()
page = view.page()

# Load the HTML file directly
page.load(QUrl('file:///home/nebulaone/spark-dev-workspace/FISSURE/web_bridge/index.html'))

def save_screenshot():
    """Wait for page to load, then render and save as PNG."""
    import time
    
    # Wait for page to load
    time.sleep(2)
    
    # Set the viewport size to match desktop view
    view.resize(1200, 800)  # Width, height
    
    # Render the page to a pixmap
    pixmap = view.grab()
    
    # Save as PNG
    output_path = '/home/nebulaone/spark-dev-workspace/FISSURE/web_gui_screenshot.png'
    pixmap.save(output_path, 'PNG')
    
    print(f"Screenshot saved to {output_path}")
    sys.exit(0)

# Connect to load finished signal
view.loadFinished.connect(save_screenshot)

# Execute the application
sys.exit(app.exec())