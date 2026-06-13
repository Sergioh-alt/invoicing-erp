"""
NotificationController - Maneja notificaciones y diálogos emergentes.
Mixin para MainWindow que gestiona la visualización y acciones de notificaciones.
"""
from PySide6 import QtWidgets
from app.views.notification_window import NotificationDialog
from app.services.snooze_manager import compute_snooze_until


class NotificationController:
    """
    Controlador de notificaciones.
    Se usa como mixin en MainWindow.
    
    Requiere que la clase que lo use tenga:
    - self.db: Database
    - self.refresh_table(): método
    """
    
    def show_notification(self, payload: dict):
        """
        Muestra una notificación emergente para una factura.
        
        Args:
            payload: Dict con datos de la factura a notificar
        """
        dlg = NotificationDialog(self, payload)
        
        # Conectar señales
        dlg.mark_paid_signal.connect(lambda fid: self._notif_mark_paid(fid))
        dlg.snooze_signal.connect(lambda fid, mins: self._notif_snooze(fid, mins))
        
        dlg.exec()
    
    def _notif_mark_paid(self, factura_id: int):
        """
        Marca factura como pagada desde notificación.
        
        Args:
            factura_id: ID de la factura a marcar como pagada
        """
        self.db.mark_pagada(factura_id)
        self.refresh_table()
    
    def _notif_snooze(self, factura_id: int, minutes: int):
        """
        Pospone recordatorio de una factura.
        
        Args:
            factura_id: ID de la factura
            minutes: Minutos para posponer
        """
        snooze_until_iso = compute_snooze_until(minutes)
        self.db.set_snooze_until(factura_id, snooze_until_iso)
        self.refresh_table()
