"""Vista de configuración/ajustes de la aplicación - Simplificada."""
from PySide6 import QtWidgets, QtCore, QtGui
from app.config import get_settings


class SettingsView(QtWidgets.QWidget):
    """Vista de ajustes de la aplicación."""
    
    theme_changed = QtCore.Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = get_settings()
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de la vista."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(24)
        
        # Header
        header = QtWidgets.QLabel("⚙️ Ajustes")
        header.setObjectName("H1")
        headerStyles = """
            font-size: 24pt;
            font-weight: 900;
            color: rgba(248,250,252,0.98);
            padding-bottom: 8px;
        """
        header.setStyleSheet(headerStyles)
        layout.addWidget(header)
        
        # Scroll area para el contenido
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        
        content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setSpacing(16)
        
        # Secciones
        content_layout.addWidget(self._create_section_title("🔔 Notificaciones"))
        content_layout.addWidget(self._create_notification_settings())
        
        content_layout.addWidget(self._create_section_title("💻 Sistema"))
        content_layout.addWidget(self._create_system_settings())
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    def _create_section_title(self, text: str) -> QtWidgets.QLabel:
        """Crea un título de sección."""
        label = QtWidgets.QLabel(text)
        label.setStyleSheet("""
            QLabel {
                color: rgba(226,232,240,0.9);
                font-size: 14pt;
                font-weight: 800;
                padding-top: 12px;
            }
        """)
        return label
    
    def _create_notification_settings(self) -> QtWidgets.QWidget:
        """Crea configuración de notificaciones."""
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Toggle sonido
        toggle_layout = QtWidgets.QHBoxLayout()
        
        label = QtWidgets.QLabel("Sonido de Notificación")
        label.setStyleSheet("color: rgba(203,213,225,0.9); font-size: 11pt; font-weight: 600;")
        toggle_layout.addWidget(label)
        
        toggle_layout.addStretch()
        
        self.sound_toggle = QtWidgets.QCheckBox()
        self.sound_toggle.setChecked(self.settings.is_notification_sound_enabled())
        self.sound_toggle.setStyleSheet(self._toggle_style())
        self.sound_toggle.stateChanged.connect(self._on_sound_toggled)
        toggle_layout.addWidget(self.sound_toggle)
        
        layout.addLayout(toggle_layout)
        
        # Línea separadora
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setStyleSheet("background: rgba(71,85,105,0.3); max-height: 1px;")
        layout.addWidget(separator)
        
        # Botón de prueba
        test_btn = QtWidgets.QPushButton("🔊 Probar Sonido")
        test_btn.setStyleSheet("""
            QPushButton {
                background: rgba(37,99,235,0.8);
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                color: white;
                font-weight: 700;
                font-size: 10pt;
                margin-top: 8px;
            }
            QPushButton:hover {
                background: rgba(59,130,246,0.9);
            }
        """)
        test_btn.setCursor(QtCore.Qt.PointingHandCursor)
        test_btn.clicked.connect(self._test_sound)
        layout.addWidget(test_btn)
        
        # Descripción informativa
        desc = QtWidgets.QLabel(
            "💡 Para ajustar el volumen del beep, usa el mezclador de volumen de Windows "
            "(click derecho en el ícono de sonido de la barra de tareas)."
        )
        desc.setStyleSheet("color: rgba(148,163,184,0.7); font-size: 9pt; padding-top: 12px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        container.setStyleSheet("""
            QWidget {
                background: rgba(30,41,59,0.4);
                border: 1px solid rgba(71,85,105,0.3);
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        return container

    def _create_system_settings(self) -> QtWidgets.QWidget:
        """Crea configuración de sistema."""
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Toggle auto-inicio
        toggle_layout = QtWidgets.QHBoxLayout()
        
        label = QtWidgets.QLabel("Auto-inicio con Windows")
        label.setStyleSheet("color: rgba(203,213,225,0.9); font-size: 11pt; font-weight: 600;")
        toggle_layout.addWidget(label)
        
        toggle_layout.addStretch()
        
        self.autostart_toggle = QtWidgets.QCheckBox()
        self.autostart_toggle.setChecked(self.settings.is_auto_start_enabled())
        self.autostart_toggle.setStyleSheet(self._toggle_style())
        self.autostart_toggle.stateChanged.connect(self._on_autostart_toggled)
        toggle_layout.addWidget(self.autostart_toggle)
        
        layout.addLayout(toggle_layout)
        
        # Descripción informativa
        desc = QtWidgets.QLabel(
            "🚀 Inicia la aplicación automáticamente al encender el computador."
        )
        desc.setStyleSheet("color: rgba(148,163,184,0.7); font-size: 9pt; padding-top: 4px;")
        layout.addWidget(desc)

        container.setStyleSheet("""
            QWidget {
                background: rgba(30,41,59,0.4);
                border: 1px solid rgba(71,85,105,0.3);
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        return container

    def _on_autostart_toggled(self, state):
        """Maneja toggle de auto-inicio."""
        enabled = bool(state)
        # print(f"🚀 _on_autostart_toggled: state={state}, enabled={enabled}")
        self.settings.set_auto_start(enabled)
    
    def _toggle_style(self) -> str:
        """Estilo CSS para toggles."""
        return """
            QCheckBox {
                spacing: 0px;
            }
            QCheckBox::indicator {
                width: 48px;
                height: 24px;
                border-radius: 12px;
                background: rgba(71,85,105,0.5);
            }
            QCheckBox::indicator:checked {
                background: rgba(59,130,246,0.9);
            }
            QCheckBox::indicator:hover {
                background: rgba(71,85,105,0.7);
            }
            QCheckBox::indicator:checked:hover {
                background: rgba(37,99,235,0.95);
            }
        """
    
    def _on_sound_toggled(self, state):
        """Maneja toggle de sonido."""
        enabled = bool(state)
        # print(f"🔊 _on_sound_toggled: state={state}, enabled={enabled}")
        self.settings.set_notification_sound(enabled)
    
    def _test_sound(self):
        """Prueba el sonido de notificación."""
        from app.utils.sound import play_notification_beep
        # Siempre probar sonido, ignorando el toggle
        play_notification_beep(force=True)
