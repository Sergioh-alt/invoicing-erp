"""
Diálogo de activación con diseño premium.
Incluye atajo Ctrl+Shift+D para modo desarrollador.
"""
from PySide6 import QtWidgets, QtCore, QtGui
import logging

logger = logging.getLogger("FacturasGanaTodo.activation_dialog")


class ActivationDialog(QtWidgets.QDialog):
    """Diálogo de activación de la aplicación."""
    
    # Señal para activar modo desarrollador
    dev_mode_requested = QtCore.Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("")
        self.setModal(True)
        self.setFixedSize(540, 380)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint)
        
        self._setup_ui()
        self._setup_shortcuts()
        
        logger.info("Diálogo de activación mostrado")
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Card principal
        card = QtWidgets.QFrame()
        card.setObjectName("ActivationCard")
        card.setStyleSheet("""
            QFrame#ActivationCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(15, 26, 47, 0.98),
                    stop:1 rgba(22, 33, 62, 0.98));
                border: 2px solid rgba(37,99,235,0.4);
                border-radius: 24px;
            }
        """)
        
        v = QtWidgets.QVBoxLayout(card)
        v.setContentsMargins(36, 32, 36, 32)
        v.setSpacing(20)
        
        # Header con icono
        header = QtWidgets.QHBoxLayout()
        icon = QtWidgets.QLabel("🔐")
        icon.setStyleSheet("font-size: 36pt;")
        header.addWidget(icon)
        
        title = QtWidgets.QLabel("Activación Requerida")
        title.setStyleSheet("font-size: 20pt; font-weight: 950; color: #f9fafb;")
        header.addWidget(title, 1)
        v.addLayout(header)
        
        # Descripción
        desc = QtWidgets.QLabel(
            "Para usar Facturas GanaTodo, ingresa el código de activación.\n"
            "Solo necesitas hacerlo una vez."
        )
        desc.setStyleSheet("color: rgba(229,231,235,0.75); font-size: 11pt; line-height: 1.5;")
        desc.setWordWrap(True)
        v.addWidget(desc)
        
        # Input de código
        self.code_input = QtWidgets.QLineEdit()
        self.code_input.setPlaceholderText("Ingresa el código de activación")
        self.code_input.setAlignment(QtCore.Qt.AlignCenter)
        self.code_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.08);
                border: 2px solid rgba(37,99,235,0.3);
                border-radius: 14px;
                padding: 16px 20px;
                font-size: 13pt;
                font-weight: 700;
                letter-spacing: 2px;
                color: #e5e7eb;
            }
            QLineEdit:focus {
                border: 2px solid rgba(37,99,235,0.7);
                background: rgba(255,255,255,0.12);
            }
        """)
        self.code_input.returnPressed.connect(self._try_activate)
        v.addWidget(self.code_input)
        
        # Mensaje de error
        self.error_label = QtWidgets.QLabel("")
        self.error_label.setAlignment(QtCore.Qt.AlignCenter)
        self.error_label.setStyleSheet(
            "color: rgba(239,68,68,0.95); font-weight: 800; font-size: 10pt;"
        )
        self.error_label.hide()
        v.addWidget(self.error_label)
        
        v.addStretch(1)
        
        # Botones
        buttons = QtWidgets.QHBoxLayout()
        buttons.setSpacing(12)
        buttons.addStretch(1)
        
        btn_activate = QtWidgets.QPushButton("Activar")
        btn_activate.setStyleSheet("""
            QPushButton {
                background: rgba(22,163,74,0.92);
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 12px;
                padding: 14px 36px;
                font-weight: 900;
                font-size: 11pt;
                color: white;
            }
            QPushButton:hover {
                background: rgba(34,197,94,0.95);
            }
            QPushButton:pressed {
                background: rgba(22,163,74,1.0);
            }
        """)
        btn_activate.clicked.connect(self._try_activate)
        btn_activate.setCursor(QtCore.Qt.PointingHandCursor)
        buttons.addWidget(btn_activate)
        
        btn_cancel = QtWidgets.QPushButton("Salir")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 12px;
                padding: 14px 28px;
                font-weight: 800;
                font-size: 11pt;
                color: rgba(229,231,235,0.85);
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.10);
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setCursor(QtCore.Qt.PointingHandCursor)
        buttons.addWidget(btn_cancel)
        
        v.addLayout(buttons)
        
        layout.addWidget(card)
        
        # Sombra dramática
        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(50)
        shadow.setOffset(0, 18)
        shadow.setColor(QtGui.QColor(0, 0, 0, 220))
        card.setGraphicsEffect(shadow)
    
    def _setup_shortcuts(self):
        """Configura atajos de teclado."""
        # Ctrl+Shift+D para modo desarrollador
        dev_shortcut = QtGui.QShortcut(
            QtGui.QKeySequence("Ctrl+Shift+D"), 
            self
        )
        dev_shortcut.activated.connect(self._activate_dev_mode)
        
        logger.debug("Atajos de teclado configurados")
    
    def _try_activate(self):
        """Intenta activar con el código ingresado."""
        code = self.code_input.text()
        
        logger.info(f"Intento de activación con código: {code[:4]}...")
        
        if code.strip().upper() == "SHEDULE-36-2":
            logger.info("✓ Código correcto - activando")
            self.accept()
        else:
            logger.warning("✗ Código incorrecto")
            self.error_label.setText("❌ Código incorrecto. Verifica e intenta de nuevo.")
            self.error_label.show()
            self.code_input.setFocus()
            self.code_input.selectAll()
            
            # Efecto de shake (opcional)
            self._shake_animation()
    
    def _activate_dev_mode(self):
        """Activa modo desarrollador con atajo de teclado."""
        logger.warning("[DEV] Modo desarrollador activado via atajo de teclado")
        
        # Mostrar confirmación
        reply = QtWidgets.QMessageBox.question(
            self,
            "Modo Desarrollador",
            "¿Activar modo desarrollador?\n\n"
            "Esto permitirá usar la app sin código de activación.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.dev_mode_requested.emit()
            self.accept()
    
    def _shake_animation(self):
        """Animación de shake cuando el código es incorrecto."""
        # Animación simple de movimiento horizontal
        animation = QtCore.QPropertyAnimation(self, b"pos")
        animation.setDuration(400)
        animation.setLoopCount(1)
        
        original_pos = self.pos()
        
        animation.setKeyValueAt(0, original_pos)
        animation.setKeyValueAt(0.25, original_pos + QtCore.QPoint(10, 0))
        animation.setKeyValueAt(0.5, original_pos - QtCore.QPoint(10, 0))
        animation.setKeyValueAt(0.75, original_pos + QtCore.QPoint(5, 0))
        animation.setKeyValueAt(1, original_pos)
        
        animation.start()
    
    def get_code(self) -> str:
        """Retorna el código ingresado."""
        return self.code_input.text()
    
    def showEvent(self, event: QtGui.QShowEvent):
        """Centra el diálogo en la pantalla al mostrarse."""
        super().showEvent(event)
        
        # Centrar en pantalla
        screen = QtGui.QGuiApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(screen_geometry.x() + x, screen_geometry.y() + y)
        
        # Focus en el input
        self.code_input.setFocus()
