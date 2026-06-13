"""
Utilidad para configurar auto-inicio en Windows.
"""
import os
import sys
import winreg


def get_startup_path():
    """Obtiene la ruta de la carpeta de inicio de Windows."""
    return os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')


def is_auto_start_enabled():
    """Verifica si el auto-inicio está habilitado."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\Run',
            0,
            winreg.KEY_READ
        )
        try:
            # Probar nombre nuevo
            try:
                winreg.QueryValueEx(key, 'FacturasGanaTodo')
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                pass
            
            # Probar nombre antiguo
            try:
                winreg.QueryValueEx(key, 'GanaTodoFacturas')
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                pass
                
            winreg.CloseKey(key)
            return False
        except Exception:
            winreg.CloseKey(key)
            return False
    except Exception:
        return False


def set_auto_start(enabled: bool):
    """Habilita o deshabilita el auto-inicio."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\Run',
            0,
            winreg.KEY_SET_VALUE
        )
        
        if enabled:
            # Obtener ruta del ejecutable o script
            if getattr(sys, 'frozen', False):
                # Si está empaquetado (exe)
                app_path = f'"{sys.executable}"'
            else:
                # Si es script de Python
                python_exe = sys.executable
                if python_exe.lower().endswith("python.exe"):
                    python_w = python_exe.lower().replace("python.exe", "pythonw.exe")
                    if os.path.exists(python_w):
                        python_exe = python_w
                
                script_path = os.path.abspath(sys.argv[0])
                app_path = f'"{python_exe}" "{script_path}"'
            
            # Usar un nombre consistente
            winreg.SetValueEx(key, 'FacturasGanaTodo', 0, winreg.REG_SZ, app_path)
            # Borrar el nombre antiguo por si acaso
            try:
                winreg.DeleteValue(key, 'GanaTodoFacturas')
            except FileNotFoundError:
                pass
        else:
            # Eliminar entrada
            try:
                winreg.DeleteValue(key, 'FacturasGanaTodo')
            except FileNotFoundError:
                pass
            try:
                winreg.DeleteValue(key, 'GanaTodoFacturas')
            except FileNotFoundError:
                pass
        
        winreg.CloseKey(key)
        return True
    except Exception:
        # print(f"Error setting auto-start: {e}")
        return False
