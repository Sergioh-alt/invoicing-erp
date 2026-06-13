"""
Sistema de sonido simple con pygame - Un solo archivo WAV
"""
import pygame
from pathlib import Path

# Inicializar una sola vez
pygame.mixer.init()
# print("[SOUND] pygame.mixer inicializado")

def play_notification_beep(force=False):
    """Reproduce beep de notificación."""
    # Obtener configuración
    if not force:
        from app.config import get_settings
        settings = get_settings()
        if not settings.is_notification_sound_enabled():
            # print("[SOUND] Sonido desactivado")
            return
    
    # print("[SOUND] Reproduciendo beep de notificación")
    
    # Usar el archivo original
    sound_file = Path(__file__).parent.parent / "assets" / "notification_beep.wav"
    
    if not sound_file.exists():
        # print(f"[WARN] Archivo no encontrado: {sound_file}")
        import winsound
        winsound.MessageBeep(-1)
        return
    
    # Reproducir con pygame
    try:
        sound = pygame.mixer.Sound(str(sound_file))
        sound.play()
        # print("  [OK] Beep reproducido correctamente")
    except Exception:
        # print(f"  [ERR] Error: {e}")
        pass


def play_beep_pattern(pattern="single"):
    """Patrones de beep."""
    play_notification_beep()
