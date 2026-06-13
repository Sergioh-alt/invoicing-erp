"""
Sistema de Configuración de la Aplicación.
Maneja persistencia de preferencias del usuario.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict


class AppSettings:
    """Gestor de configuración de la aplicación."""
    
    DEFAULT_SETTINGS = {
        "theme": "dark",  # Always dark theme
        "multi_currency": False,  # Feature removed - not in use
        "default_currency": "COP",  # Peso colombiano
        "notification_sound": True,
        "notification_volume": 0.8,  # 0.0 a 1.0
        "auto_start": False,
    }
    
    def __init__(self):
        self.config_dir = Path.home() / ".ganatodo"
        self.config_file = self.config_dir / "settings.json"
        self._settings = {}
        self._load()
    
    def _load(self):
        """Carga configuración desde archivo."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._settings = json.load(f)
            else:
                self._settings = self.DEFAULT_SETTINGS.copy()
                self._save()
        except Exception:
            self._settings = self.DEFAULT_SETTINGS.copy()
    
    def _save(self):
        """Guarda configuración en archivo."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2)
        except Exception:
            pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor de configuración."""
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Establece un valor de configuración."""
        self._settings[key] = value
        self._save()
    
    def get_theme(self) -> str:
        """Obtiene el tema actual."""
        return "dark"  # Always dark theme
    
    def set_theme(self, theme: str):
        """Establece el tema - siempre oscuro."""
        pass  # Feature removed
    
    def is_multi_currency_enabled(self) -> bool:
        """Verifica si multi-moneda está habilitado."""
        return False  # Feature removed
    
    def set_multi_currency(self, enabled: bool):
        """Habilita/deshabilita multi-moneda."""
        pass  # Feature removed
    
    def get_default_currency(self) -> str:
        """Obtiene la moneda por defecto."""
        return self.get("default_currency", "COP")
    
    def set_default_currency(self, currency: str):
        """Establece la moneda por defecto."""
        self.set("default_currency", currency)
    
    def is_notification_sound_enabled(self) -> bool:
        """Verifica si el sonido está habilitado."""
        return self.get("notification_sound", True)
    
    def set_notification_sound(self, enabled: bool):
        """Habilita/deshabilita sonido de notificación."""
        self.set("notification_sound", enabled)
    
    def get_notification_volume(self) -> float:
        """Obtiene el volumen de notificación."""
        return self.get("notification_volume", 0.8)
    
    def set_notification_volume(self, volume: float):
        """Establece el volumen de notificación (0.0 - 1.0)."""
        volume = max(0.0, min(1.0, volume))
        self.set("notification_volume", volume)

    def is_auto_start_enabled(self) -> bool:
        """Verifica si el auto-inicio está habilitado en la configuración."""
        return self.get("auto_start", False)
    
    def set_auto_start(self, enabled: bool):
        """Habilita/deshabilita el auto-inicio en la configuración."""
        self.set("auto_start", enabled)
        # Aplicar el cambio al registro/sistema
        from app.utils.startup import set_auto_start as sys_set_auto_start
        sys_set_auto_start(enabled)


# Instancia global
_settings_instance = None

def get_settings() -> AppSettings:
    """Obtiene la instancia singleton de configuración."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = AppSettings()
    return _settings_instance
