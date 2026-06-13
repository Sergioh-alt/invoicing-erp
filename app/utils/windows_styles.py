import sys
import ctypes

def apply_dark_title_bar(window):
    """
    Aplica el modo oscuro a la barra de título de Windows (DWM).
    Funciona en Windows 10 (17763+) y Windows 11.
    """
    if sys.platform != "win32":
        return

    try:
        # Obtener el HWND (identificador de ventana de Windows)
        hwnd = int(window.winId())
        
        # DWMWA_USE_IMMERSIVE_DARK_MODE
        # Windows 11 usa el atributo 20
        # Versiones más antiguas de Win 10 usaban el 19
        attribute = 20
        
        # Activar modo oscuro (1 = habilitado)
        dark_mode = ctypes.c_int(1)
        
        # Llamar a dwmapi para aplicar el estilo
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 
            attribute, 
            ctypes.byref(dark_mode), 
            ctypes.sizeof(dark_mode)
        )
        
        # Refrescar la ventana para que se vea el cambio inmediatamente
        window.hide()
        window.show()
        
    except Exception:
        # Fallback silencioso si falla (por ejemplo en versiones muy antiguas de Windows)
        pass
