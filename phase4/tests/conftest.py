# Add phase4 to path for "from src.*" when running pytest
import sys
from pathlib import Path

phase4_root = Path(__file__).resolve().parent.parent
if str(phase4_root) not in sys.path:
    sys.path.insert(0, str(phase4_root))
