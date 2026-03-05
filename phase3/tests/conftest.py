# Add phase3 to path for "from src.*" when running pytest from project root or phase3
import sys
from pathlib import Path

phase3_root = Path(__file__).resolve().parent.parent
if str(phase3_root) not in sys.path:
    sys.path.insert(0, str(phase3_root))
