"""
Widget de navegación lateral (sidebar) para Facturas GanaTodo.
"""
from PySide6 import QtWidgets, QtCore, QtGui


class NavigationButton(QtWidgets.QPushButton):
    """Botón de navegación personalizado con estilo moderno."""
    
    def __init__(self, text: str, icon_text: str, parent=None):
        super().__init__(parent)
        self.setText(f"{icon_text}  {text}")
        self.setCheckable(True)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setMinimumHeight(52)
        self.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.04);
                border: none;
                border-radius: 14px;
                padding: 14px 20px;
                text-align: left;
                font-size: 11pt;
                font-weight: 800;
                color: rgba(229,231,235,0.70);
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.08);
                color: rgba(229,231,235,0.95);
            }
            QPushButton:checked {
                background: rgba(37,99,235,0.20);
                color: #60a5fa;
                font-weight: 900;
                border-left: 3px solid #60a5fa;
            }
        """)


class SidebarNavigation(QtWidgets.QFrame):
    """Barra lateral de navegación con botones de vista."""
    
    view_changed = QtCore.Signal(str)  # Emite: "dashboard", "calendario", "ajustes"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(200)
        # Styles controlled by global theme
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de la sidebar."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 22, 16, 22)
        layout.setSpacing(10)
        
        # Logo/Título
        title_container = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel("Facturas\nGanaTodo")
        title.setStyleSheet("""
            font-size: 15pt;
            font-weight: 950;
            color: #f9fafb;
            padding: 12px 8px;
            line-height: 1.2;
        """)
        title.setAlignment(QtCore.Qt.AlignLeft)
        title_container.addWidget(title)
        
        layout.addLayout(title_container)
        layout.addSpacing(24)
        
        # Botones de navegación (sin label NAVEGACIÓN)
        
        # Botones de navegación
        self.btn_dashboard = NavigationButton("Recordatorios", "📊", self)
        self.btn_calendario = NavigationButton("Calendario", "📅", self)
        self.btn_ajustes = NavigationButton("Ajustes", "⚙️", self)
        
        self.btn_dashboard.setChecked(True)
        
        self.btn_dashboard.clicked.connect(lambda: self._on_nav_click("dashboard"))
        self.btn_calendario.clicked.connect(lambda: self._on_nav_click("calendario"))
        self.btn_ajustes.clicked.connect(lambda: self._on_nav_click("ajustes"))
        
        layout.addWidget(self.btn_dashboard)
        layout.addWidget(self.btn_calendario)
        layout.addWidget(self.btn_ajustes)
        
        layout.addStretch(1)
        
        # Separador
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setStyleSheet("background: rgba(255,255,255,0.08); max-height: 1px;")
        layout.addWidget(separator)
        
        # Info de la app
        info_layout = QtWidgets.QVBoxLayout()
        info_layout.setSpacing(4)
        
        app_status = QtWidgets.QLabel("● Activo")
        app_status.setStyleSheet("""
            color: rgba(34,197,94,0.85);
            font-size: 9pt;
            font-weight: 800;
            padding: 4px 8px;
        """)
        info_layout.addWidget(app_status)
        
        copyright_label = QtWidgets.QLabel("© 2026 GanaTodo")
        copyright_label.setStyleSheet("""
            color: rgba(229,231,235,0.35);
            font-size: 8pt;
            padding: 4px 8px;
        """)
        info_layout.addWidget(copyright_label)
        
        layout.addLayout(info_layout)
    
    def _on_nav_click(self, view_name: str):
        """Maneja clicks en botones de navegación."""
        # Desmarcar todos los botones
        for btn in [self.btn_dashboard, self.btn_calendario, self.btn_ajustes]:
            btn.setChecked(False)
        
        # Marcar el clickeado
        if view_name == "dashboard":
            self.btn_dashboard.setChecked(True)
        elif view_name == "calendario":
            self.btn_calendario.setChecked(True)
        elif view_name == "ajustes":
            self.btn_ajustes.setChecked(True)
        
        self.view_changed.emit(view_name)
    
    def set_active_view(self, view_name: str):
        """Establece la vista activa programáticamente."""
        self._on_nav_click(view_name)
