"""
Servicio de Backup Automático para Facturas GanaTodo.
Crea backups automáticos de la base de datos con rotación y compresión.
"""
import os
import shutil
import zipfile
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger("FacturasGanaTodo.backup")


class BackupManager:
    """
    Gestiona backups automáticos de la base de datos.
    
    Features:
    - Backups automáticos diarios/semanales
    - Rotación automática (mantiene últimos N backups)
    - Compresión ZIP para ahorrar espacio
    - Restauración desde backup
    - Limpieza de backups antiguos
    """
    
    def __init__(self, db_path: str, backup_dir: str = "backups", keep_days: int = 30):
        """
        Inicializa el gestor de backups.
        
        Args:
            db_path: Ruta a la base de datos principal
            backup_dir: Directorio donde guardar backups (default: "backups")
            keep_days: Días de retención de backups (default: 30)
        """
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.keep_days = keep_days
        
        # Crear directorio de backups si no existe
        self.backup_dir.mkdir(exist_ok=True)
        
        logger.info(f"BackupManager inicializado: {self.backup_dir}, retención {keep_days} días")
    
    def create_backup(self, auto: bool = False) -> Optional[str]:
        """
        Crea un backup de la base de datos.
        
        Args:
            auto: Si es backup automático (para logging)
            
        Returns:
            Ruta del archivo de backup creado, o None si falla
        """
        try:
            # Verificar que BD existe
            if not self.db_path.exists():
                logger.error(f"BD no existe: {self.db_path}")
                return None
            
            # Nombre del backup con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = "auto" if auto else "manual"
            backup_name = f"backup_{prefix}_{timestamp}.zip"
            backup_path = self.backup_dir / backup_name
            
            # Crear ZIP con BD
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(self.db_path, self.db_path.name)
                
                # Agregar metadatos
                metadata = f"""Backup Facturas GanaTodo
Fecha: {datetime.now().isoformat()}
Tipo: {'Automático' if auto else 'Manual'}
BD Original: {self.db_path}
Tamaño BD: {self.db_path.stat().st_size / 1024:.2f} KB
"""
                zipf.writestr("backup_info.txt", metadata)
            
            # Verificar tamaño
            size_kb = backup_path.stat().st_size / 1024
            
            tipo = "automático" if auto else "manual"
            logger.info(f"Backup {tipo} creado: {backup_name} ({size_kb:.2f} KB)")
            
            return str(backup_path)
            
        except Exception as e:
            logger.exception(f"Error creando backup: {e}")
            return None
    
    def restore_backup(self, backup_path: str) -> bool:
        """
        Restaura base de datos desde un backup.
        
        Args:
            backup_path: Ruta al archivo de backup ZIP
            
        Returns:
            True si exitoso, False si falla
        """
        try:
            backup_file = Path(backup_path)
            
            if not backup_file.exists():
                logger.error(f"Backup no existe: {backup_path}")
                return False
            
            # Crear backup de BD actual antes de restaurar
            current_backup = self.backup_dir / f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(self.db_path, current_backup)
            logger.info(f"BD actual respaldada en: {current_backup}")
            
            # Extraer BD del ZIP
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                # Buscar archivo .db en el ZIP
                db_files = [f for f in zipf.namelist() if f.endswith('.db') or f.endswith('.sqlite')]
                
                if not db_files:
                    logger.error("No se encontró BD en el backup")
                    return False
                
                # Extraer a temporal
                temp_db = self.backup_dir / "temp_restore.db"
                zipf.extract(db_files[0], self.backup_dir)
                extracted = self.backup_dir / db_files[0]
                
                # Mover a ubicación final
                shutil.move(str(extracted), str(temp_db))
            
            # Reemplazar BD actual
            shutil.move(str(temp_db), str(self.db_path))
            
            logger.info(f"BD restaurada desde: {backup_path}")
            return True
            
        except Exception as e:
            logger.exception(f"Error restaurando backup: {e}")
            return False
    
    def cleanup_old_backups(self) -> int:
        """
        Elimina backups más antiguos que keep_days.
        
        Returns:
            Número de backups eliminados
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=self.keep_days)
            deleted = 0
            
            for backup_file in self.backup_dir.glob("backup_*.zip"):
                # Obtener timestamp del nombre
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                
                if file_time < cutoff_date:
                    backup_file.unlink()
                    deleted += 1
                    logger.info(f"Backup antiguo eliminado: {backup_file.name}")
            
            if deleted > 0:
                logger.info(f"Limpieza completada: {deleted} backups eliminados")
            
            return deleted
            
        except Exception as e:
            logger.exception(f"Error limpiando backups: {e}")
            return 0
    
    def list_backups(self) -> List[dict]:
        """
        Lista todos los backups disponibles.
        
        Returns:
            Lista de dicts con info de cada backup
        """
        backups = []
        
        for backup_file in sorted(self.backup_dir.glob("backup_*.zip"), reverse=True):
            try:
                stat = backup_file.stat()
                
                # Determinar tipo desde nombre
                is_auto = "_auto_" in backup_file.name
                
                backups.append({
                    "path": str(backup_file),
                    "name": backup_file.name,
                    "size_kb": stat.st_size / 1024,
                    "date": datetime.fromtimestamp(stat.st_mtime),
                    "type": "Automático" if is_auto else "Manual"
                })
            except Exception as e:
                logger.warning(f"Error leyendo backup {backup_file}: {e}")
                continue
        
        return backups
    
    def get_stats(self) -> dict:
        """
        Obtiene estadísticas de backups.
        
        Returns:
            Dict con estadísticas
        """
        backups = self.list_backups()
        
        total_size = sum(b["size_kb"] for b in backups)
        auto_count = sum(1 for b in backups if b["type"] == "Automático")
        manual_count = len(backups) - auto_count
        
        return {
            "total_backups": len(backups),
            "automatic": auto_count,
            "manual": manual_count,
            "total_size_mb": total_size / 1024,
            "oldest": backups[-1]["date"] if backups else None,
            "newest": backups[0]["date"] if backups else None,
        }
    
    def should_create_daily_backup(self) -> bool:
        """
        Determina si se debe crear backup diario.
        
        Returns:
            True si hace más de 24h del último backup automático
        """
        try:
            # Buscar último backup automático
            auto_backups = [b for b in self.list_backups() if b["type"] == "Automático"]
            
            if not auto_backups:
                return True  # No hay backups, crear uno
            
            # Verificar si último fue hace más de 24h
            last_backup_date = auto_backups[0]["date"]
            hours_since = (datetime.now() - last_backup_date).total_seconds() / 3600
            
            return hours_since >= 24
            
        except Exception as e:
            logger.exception(f"Error verificando backup diario: {e}")
            return True  # En caso de error, crear backup por seguridad
