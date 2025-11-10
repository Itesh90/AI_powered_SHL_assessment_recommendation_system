import sys
from pathlib import Path

# Add parent directory to path to import main
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the FastAPI app from main.py
from main import app

# Vercel expects the handler to be named 'handler' or the app itself
# For FastAPI, we can export the app directly

