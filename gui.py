"""
Launcher para la GUI de Forensic Image Analyzer
"""

import sys
from pathlib import Path

# Añadir directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

# Ahora importar
from src.gui.forensic_gui import main

if __name__ == "__main__":
    main()