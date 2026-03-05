# Add phase1 to path so "from src.fetch_dataset" works when running pytest from project root or phase1
import os
import sys
from pathlib import Path

phase1_root = Path(__file__).resolve().parent.parent
if str(phase1_root) not in sys.path:
    sys.path.insert(0, str(phase1_root))

# Use project-local HF cache so tests can run without writing to ~/.cache
_hf_cache = phase1_root / "data" / "hf_cache"
if "HF_HOME" not in os.environ:
    os.environ["HF_HOME"] = str(_hf_cache)
if "HF_HUB_CACHE" not in os.environ:
    os.environ["HF_HUB_CACHE"] = str(_hf_cache / "hub")
