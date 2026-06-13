"""
Sistema de activación con código de un solo uso.
Incluye modo bypass de desarrollador para prevenir bloqueos.
"""
import json
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger("FacturasGanaTodo.activation")

ACTIVATION_CODE = "SHEDULE-36-2"


class ActivationManager:
    """Gestiona la activación de la aplicación."""
    
    def __init__(self, app_dir: str):
        """
        Inicializa el gestor de activación.
        
        Args:
            app_dir: Directorio base de la aplicación
        """
        self.app_dir = Path(app_dir)
        self.activation_file = self.app_dir / ".activation"
        self.devmode_file = self.app_dir / ".devmode"
        
        logger.info(f"ActivationManager inicializado en: {app_dir}")
    
    def is_activated(self) -> bool:
        """
        Verifica si la app está activada.
        
        Returns:
            True si está activada o en modo desarrollador
        """
        # Verificar modo desarrollador primero
        if self.is_dev_mode():
            logger.info("Modo desarrollador activo - bypass de activación")
            return True
        
        # Verificar activación normal
        if not self.activation_file.exists():
            logger.debug("Archivo de activación no existe")
            return False
        
        try:
            with open(self.activation_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                activated = data.get('activated', False)
                
                if activated:
                    logger.info("Aplicación activada correctamente")
                else:
                    logger.warning("Archivo de activación existe pero activated=False")
                
                return activated
        
        except Exception as e:
            logger.error(f"Error al leer archivo de activación: {e}")
            return False
    
    def activate(self, code: str) -> bool:
        """
        Activa la app con el código proporcionado.
        
        Args:
            code: Código de activación ingresado por el usuario
            
        Returns:
            True si la activación fue exitosa
        """
        code_upper = code.strip().upper()
        
        if code_upper != ACTIVATION_CODE:
            logger.warning(f"Intento de activación con código incorrecto: {code}")
            return False
        
        try:
            # Asegurar que el directorio existe
            self.app_dir.mkdir(parents=True, exist_ok=True)
            
            import time
            activation_data = {
                'activated': True,
                'code': code_upper,
                'timestamp': str(time.time())  # Timestamp de activación
            }
            
            with open(self.activation_file, 'w', encoding='utf-8') as f:
                json.dump(activation_data, f, indent=2)
            
            logger.info("✓ Aplicación activada exitosamente")
            return True
        
        except Exception as e:
            logger.error(f"Error al guardar activación: {e}")
            return False
    
    def deactivate(self) -> None:
        """
        Desactiva la app (solo para testing/desarrollo).
        
        Warning:
            Esta función elimina el archivo de activación.
            Usar solo para pruebas.
        """
        if self.activation_file.exists():
            self.activation_file.unlink()
            logger.warning("Aplicación desactivada - archivo de activación eliminado")
    
    def is_dev_mode(self) -> bool:
        """
        Verifica si está activo el modo desarrollador.
        
        El modo desarrollador se activa de dos formas:
        1. Existencia del archivo .devmode en el directorio de la app
        2. Variable de entorno FACTURAS_DEV_MODE=1
        
        Returns:
            True si el modo desarrollador está activo
        """
        import os
        
        # Método 1: Archivo .devmode
        if self.devmode_file.exists():
            logger.debug("Modo desarrollador activo (archivo .devmode)")
            return True
        
        # Método 2: Variable de entorno
        if os.environ.get('FACTURAS_DEV_MODE', '0') == '1':
            logger.debug("Modo desarrollador activo (variable de entorno)")
            return True
        
        return False
    
    def enable_dev_mode(self) -> bool:
        """
        Habilita el modo desarrollador creando el archivo .devmode.
        
        Returns:
            True si se habilitó exitosamente
        """
        try:
            # Asegurar que el directorio existe
            self.app_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.devmode_file, 'w', encoding='utf-8') as f:
                f.write("# Archivo de modo desarrollador\n")
                f.write("# Elimina este archivo para requerir activación nuevamente\n")
            
            logger.info("✓ Modo desarrollador habilitado")
            return True
        
        except Exception as e:
            logger.error(f"Error al habilitar modo desarrollador: {e}")
            return False
    
    def disable_dev_mode(self) -> None:
        """Deshabilita el modo desarrollador eliminando el archivo .devmode."""
        if self.devmode_file.exists():
            self.devmode_file.unlink()
            logger.info("Modo desarrollador deshabilitado")
    
    def get_status(self) -> dict:
        """
        Obtiene el estado completo de la activación.
        
        Returns:
            Dict con información del estado
        """
        return {
            'is_activated': self.is_activated(),
            'is_dev_mode': self.is_dev_mode(),
            'activation_file_exists': self.activation_file.exists(),
            'devmode_file_exists': self.devmode_file.exists(),
        }
