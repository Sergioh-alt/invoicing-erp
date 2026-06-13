"""
Sistema de logging centralizado para Facturas GanaTodo.
"""
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(app_dir: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configura el sistema de logging para la aplicación.
    
    Args:
        app_dir: Directorio base de la aplicación
        level: Nivel de logging (logging.INFO, logging.DEBUG, etc.)
        
    Returns:
        Logger configurado
    """
    log_dir = Path(app_dir) / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Archivo de log con fecha
    log_file = log_dir / f"facturas_{datetime.now():%Y%m%d}.log"
    
    # Formato de mensajes
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para archivo
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)  # Solo warnings/errors en consola
    
    # Configurar logger principal
    logger = logging.getLogger("FacturasGanaTodo")
    logger.setLevel(level)
    
    # Evitar duplicación si ya hay handlers
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    logger.info("=" * 60)
    logger.info("Sistema de logging iniciado")
    logger.info(f"Nivel de log: {logging.getLevelName(level)}")
    logger.info(f"Archivo de log: {log_file}")
    logger.info("=" * 60)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Obtiene un logger hijo del logger principal.
    
    Args:
        name: Nombre del módulo (opcional)
        
    Returns:
        Logger configurado
    """
    if name:
        return logging.getLogger(f"FacturasGanaTodo.{name}")
    return logging.getLogger("FacturasGanaTodo")
