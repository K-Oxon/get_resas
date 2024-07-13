import os
from pathlib import Path

API_KEY = os.getenv("RESAS_API_KEY")
EXPORT_DATA_DIR = Path(__file__).parents[2] / "data"
