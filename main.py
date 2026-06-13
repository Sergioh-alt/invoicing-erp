import os
import sys
from PySide6 import QtWidgets, QtGui

from app.services.config import ConfigManager
from app.services.activation import ActivationManager
from app.model.database import Database
from app.services.scheduler import SchedulerThread
from app.services.backup_manager import BackupManager
from app.views.ui_main import MainWindow
from app.views.ui_tray import TrayManager
from app.views.activation_dialog import ActivationDialog
from app.views.ui_styles import qss_dark_premium
from app.utils.singleton import SingleInstance
from app.utils.paths import resource_path
from app.utils.logger import setup_logger
from app.utils.startup import is_auto_start_enabled, set_auto_start
from app.utils.windows_styles import apply_dark_title_bar

APP_NAME = "FacturasGanaTodo"

def get_app_dir() -> str:
    """
    Retorna el directorio donde se guardarán los datos de la aplicación.
    Versión 100% Portable: Siempre usa el directorio donde reside el programa.
    """
    if getattr(sys, "frozen", False):
        # Directorio del archivo .exe
        return os.path.dirname(os.path.abspath(sys.executable))
    # Directorio del script (modo desarrollo)
    return os.path.dirname(os.path.abspath(__file__))

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)  # CRÍTICO: no matar proceso si se oculta la ventana
    # Cargar tema guardado
    from app.config import get_settings
    settings = get_settings()
    theme = settings.get_theme()
    if theme == "dark":
        from app.views.ui_styles import qss_dark_premium
        app.setStyleSheet(qss_dark_premium())
    else:
        from app.views.ui_styles import qss_light_premium
        app.setStyleSheet(qss_light_premium())

    # Configurar logging
    app_dir = get_app_dir()
    logger = setup_logger(app_dir)
    logger.info(f"Iniciando {APP_NAME}")
    logger.info(f"Directorio de aplicación: {app_dir}")

    # Verificar instancia única
    lock = SingleInstance(APP_NAME + "_lock")
    if not lock.try_lock():
        logger.warning("Ya hay una instancia ejecutándose")
        QtWidgets.QMessageBox.information(None, "Ya está abierto", "Facturas GanaTodo ya está ejecutándose.")
        return

    # Verificar activación
    activation_mgr = ActivationManager(app_dir)
    if not activation_mgr.is_activated():
        logger.info("Aplicación no activada - mostrando diálogo")
        
        activation_dialog = ActivationDialog()
        apply_dark_title_bar(activation_dialog)
        
        # Conectar señal de modo desarrollador
        def on_dev_mode_requested():
            if activation_mgr.enable_dev_mode():
                logger.info("✓ Modo desarrollador habilitado")
                QtWidgets.QMessageBox.information(
                    None,
                    "Modo Desarrollador",
                    "Modo desarrollador habilitado.\n\n"
                    "La app ya no requerirá código de activación.\n"
                    "Elimina el archivo .devmode para requerir activación nuevamente."
                )
        
        activation_dialog.dev_mode_requested.connect(on_dev_mode_requested)
        
        result = activation_dialog.exec()
        
        if result == QtWidgets.QDialog.Accepted:
            code = activation_dialog.get_code()
            
            # Si no es modo dev, validar código
            if not activation_mgr.is_dev_mode():
                if activation_mgr.activate(code):
                    logger.info("✓ Aplicación activada exitosamente")
                    QtWidgets.QMessageBox.information(
                        None,
                        "Activación Exitosa",
                        "¡Bienvenido a Facturas GanaTodo!\n\nLa aplicación ha sido activada correctamente."
                    )
                else:
                    logger.error("Error al activar - código incorrecto")
                    QtWidgets.QMessageBox.critical(
                        None,
                        "Error de Activación",
                        "No se pudo activar la aplicación.\nVerifica el código e intenta nuevamente."
                    )
                    return
        else:
            logger.info("Usuario canceló la activación")
            return

    logger.info("Aplicación activada - continuando con inicialización")

    # Cargar icono
    ico = resource_path("assets", "app.ico")
    svg = resource_path("assets", "app_icon.svg")
    icon_path = ico if os.path.exists(ico) else svg
    icon = QtGui.QIcon(icon_path) if os.path.exists(icon_path) else QtGui.QIcon()
    if not icon.isNull():
        app.setWindowIcon(icon)
    else:
        logger.warning("No se encontró icono de la aplicación")

    # Configuración
    cfg_mgr = ConfigManager(app_dir)
    cfg = cfg_mgr.load_or_create()
    logger.info(f"Configuración cargada: {cfg.db_path}")

    # Base de datos
    db = Database(cfg.db_path)
    db.initialize()
    logger.info("Base de datos inicializada")

    # Sistema de Backups Automáticos
    backup_dir = os.path.join(app_dir, "backups")
    backup_mgr = BackupManager(cfg.db_path, backup_dir, keep_days=30)
    logger.info(f"BackupManager inicialalizado: {backup_dir}")
    
    # Crear backup automático si es necesario (cada 24h)
    if backup_mgr.should_create_daily_backup():
        logger.info("Creando backup automático diario...")
        backup_file = backup_mgr.create_backup(auto=True)
        if backup_file:
            logger.info(f"✓ Backup automático creado: {os.path.basename(backup_file)}")
        else:
            logger.warning("⚠️ No se pudo crear backup automático")
    
    # Limpiar backups antiguos (>30 días)
    deleted = backup_mgr.cleanup_old_backups()
    if deleted > 0:
        logger.info(f"Limpieza de backups: {deleted} archivos antiguos eliminados")


    # Sincronizar estado de auto-inicio con la configuración
    try:
        set_auto_start(settings.is_auto_start_enabled())
    except Exception:
        pass


    tray = TrayManager(icon)
    win = MainWindow(
        db, cfg_mgr, APP_NAME,
        tray_show_cb=lambda t, m: tray.show_info(t, m),
        backup_mgr=backup_mgr
    )

    def open_window():
        win.showNormal()
        win.raise_()
        win.activateWindow()

    def exit_app():
        win.set_allow_quit(True)
        try:
            win.close()
        except Exception:
            pass
        QtWidgets.QApplication.quit()

    tray.open_requested.connect(open_window)
    tray.exit_requested.connect(exit_app)

    win.show()
    apply_dark_title_bar(win)

    sched = SchedulerThread(db)
    sched.alert_needed.connect(lambda payload: on_alert(db, win, payload))
    sched.start()

    rc = app.exec()

    sched.stop()
    sched.wait(1200)
    sys.exit(rc)

def on_alert(db: Database, win: MainWindow, payload: dict):
    code = payload.get("alert_code")
    now_iso = payload.get("now_iso") or ""
    try:
        if code in ("D5","D3","D1"):
            db.set_last_day_alert(int(payload["id"]), now_iso, code)
        elif code in ("H1","H2","H3"):
            slot = int(payload.get("day0_slot", 0) or 0)
            if slot in (1,2,3):
                db.set_day0_slot_fired(int(payload["id"]), slot, now_iso)
    except Exception:
        pass

    win.show_notification(payload)

if __name__ == "__main__":
    main()

