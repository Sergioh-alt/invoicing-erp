import os
import sys

def resource_path(*parts: str) -> str:
    """
    Rutas seguras en fuente y en .exe (PyInstaller).
    - Fuente: base = carpeta del proyecto
    - .exe: base = sys._MEIPASS
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, *parts)
