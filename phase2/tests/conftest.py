# Add phase2 to path so "from src.*" works when running pytest from project root or phase2
import sys
from pathlib import Path

phase2_root = Path(__file__).resolve().parent.parent
if str(phase2_root) not in sys.path:
    sys.path.insert(0, str(phase2_root))
