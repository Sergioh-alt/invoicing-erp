"""
Diálogo oculto para activar/desactivar generador de comprobantes de pago.
Se accede mediante easter egg en el buscador.
"""
from PySide6 import QtWidgets, QtCore, QtGui


class HiddenFeatureDialog(QtWidgets.QDialog):
    """Diálogo para gestionar función oculta de comprobantes de pago."""
    
    # Señales
    feature_toggled = QtCore.Signal(bool)  # Emite True si activado, False si desactivado
    
    def __init__(self, parent=None, current_status: bool = False):
        """
        Inicializa el diálogo.
        
        Args:
            parent: Widget padre
            current_status: Estado actual de la función (True = activada)
        """
        super().__init__(parent)
        self.current_status = current_status
        self.new_status = current_status
        
        self.setWindowTitle("🔓 Función Oculta Detectada")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz del diálogo."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Título con icono
        title = QtWidgets.QLabel("🔓 Función Oculta Desbloqueada")
        title.setStyleSheet("""
            font-size: 18pt;
            font-weight: bold;
            color: rgba(59,130,246,0.9);
            margin-bottom: 10px;
        """)
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        # Mensaje descriptivo
        msg = QtWidgets.QLabel(
            "¡Has descubierto el <b>Generador de Comprobantes de Pago</b>!<br/><br/>"
            "Cuando esta función está activada, se genera automáticamente<br/>"
            "un comprobante en PDF cada vez que marcas una factura como pagada.<br/><br/>"
            "El comprobante incluye:<br/>"
            "• Número de factura<br/>"
            "• Proveedor y monto<br/>"
            "• Fechas de vencimiento y pago<br/>"
            "• Notas adicionales<br/><br/>"
            f"<b>Estado actual:</b> <span style='color: {'#22c55e' if self.current_status else '#ef4444'};'>"
            f"{'✓ ACTIVADO' if self.current_status else '✗ DESACTIVADO'}</span>"
        )
        msg.setWordWrap(True)
        msg.setStyleSheet("""
            QLabel {
                color: rgba(229,231,235,0.9);
                background-color: rgba(30,41,59,0.5);
                padding: 15px;
                border-radius: 8px;
                border: 1px solid rgba(71,85,105,0.5);
            }
        """)
        layout.addWidget(msg)
        
        # Botones
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(12)
        
        # Botón Activar
        self.btn_enable = QtWidgets.QPushButton("✅ Activar")
        self.btn_enable.setStyleSheet("""
            QPushButton {
                background-color: rgba(34,197,94,0.15);
                border: 2px solid rgba(34,197,94,0.4);
                color: rgba(34,197,94,1);
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: rgba(34,197,94,0.25);
                border-color: rgba(34,197,94,0.6);
            }
            QPushButton:disabled {
                background-color: rgba(71,85,105,0.2);
                border-color: rgba(71,85,105,0.3);
                color: rgba(148,163,184,0.5);
            }
        """)
        self.btn_enable.clicked.connect(lambda: self._toggle_feature(True))
        btn_layout.addWidget(self.btn_enable)
        
        # Botón Desactivar
        self.btn_disable = QtWidgets.QPushButton("❌ Desactivar")
        self.btn_disable.setStyleSheet("""
            QPushButton {
                background-color: rgba(239,68,68,0.15);
                border: 2px solid rgba(239,68,68,0.4);
                color: rgba(239,68,68,1);
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: rgba(239,68,68,0.25);
                border-color: rgba(239,68,68,0.6);
            }
            QPushButton:disabled {
                background-color: rgba(71,85,105,0.2);
                border-color: rgba(71,85,105,0.3);
                color: rgba(148,163,184,0.5);
            }
        """)
        self.btn_disable.clicked.connect(lambda: self._toggle_feature(False))
        btn_layout.addWidget(self.btn_disable)
        
        # Botón Cancelar
        self.btn_cancel = QtWidgets.QPushButton("Cancelar")
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: rgba(71,85,105,0.3);
                border: 2px solid rgba(100,116,139,0.4);
                color: rgba(229,231,235,0.9);
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: rgba(71,85,105,0.5);
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)
        
        # Desabilitar botón según estado actual
        self._update_buttons()
    
    def _update_buttons(self):
        """Actualiza el estado de los botones según el estado actual."""
        self.btn_enable.setEnabled(not self.new_status)
        self.btn_disable.setEnabled(self.new_status)
    
    def _toggle_feature(self, enable: bool):
        """
        Cambia el estado de la función.
        
        Args:
            enable: True para activar, False para desactivar
        """
        self.new_status = enable
        self.feature_toggled.emit(enable)
        self.accept ()
    
    def get_new_status(self) -> bool:
        """Retorna el nuevo estado seleccionado por el usuario."""
        return self.new_status
