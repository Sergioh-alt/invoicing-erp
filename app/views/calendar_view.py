"""
Vista de Calendario mejorada - Con dropdowns mes/año, navegación a dashboard, y filtros mejorados.
"""
from PySide6 import QtWidgets, QtCore, QtGui
from datetime import datetime, timedelta
from typing import List, Dict, Any


class CalendarDayWidget(QtWidgets.QWidget):
    """Widget para un día del calendario - estilo compacto."""
    
    day_clicked = QtCore.Signal(datetime)
    
    def __init__(self, date: datetime, facturas: List[Dict[str, Any]], is_current_month: bool = True, parent=None):
        super().__init__(parent)
        self.date = date
        self.facturas = facturas
        self.is_current_month = is_current_month
        self.is_today = date.date() == datetime.now().date()
        self.is_selected = False
        
        self.setMinimumSize(50, 50)
        self.setMaximumSize(80, 80)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la UI del día."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        # Número del día
        day_label = QtWidgets.QLabel(str(self.date.day))
        day_label.setAlignment(QtCore.Qt.AlignCenter)
        
        if not self.is_current_month:
            day_label.setStyleSheet("""
                QLabel {
                    color: rgba(100,116,139,0.4);
                    font-weight: 500;
                    font-size: 12pt;
                }
            """)
        else:
            day_label.setStyleSheet("""
                QLabel {
                    color: rgba(226,232,240,0.95);
                    font-weight: 600;
                    font-size: 12pt;
                }
            """)
        
        layout.addWidget(day_label)
        
        # Indicador de facturas (badge compacto)
        if self.facturas and self.is_current_month:
            count = len(self.facturas)
            badge = QtWidgets.QLabel(str(count))
            badge.setAlignment(QtCore.Qt.AlignCenter)
            
            # Color según el tipo de facturas
            color = self._get_badge_color()
            badge.setStyleSheet(f"""
                QLabel {{
                    background: {color};
                    color: white;
                    border-radius: 8px;
                    padding: 2px 6px;
                    font-size: 8pt;
                    font-weight: 700;
                    min-width: 16px;
                }}
            """)
            layout.addWidget(badge, alignment=QtCore.Qt.AlignCenter)
        
        layout.addStretch()
        self._update_style()
    
    def _get_badge_color(self) -> str:
        """Determina el color del badge según las facturas.
        
        Prioridad:
        1. ROJO: Si al menos una está vencida (aunque haya pagadas)
        2. AMARILLO: Si NO hay vencidas pero hay al menos una pendiente
        3. VERDE: Solo si TODAS están pagadas
        """
        if not self.facturas:
            return "rgba(59,130,246,0.9)"  # Azul si no hay facturas
        
        now = datetime.now()
        total_facturas = len(self.facturas)
        facturas_pagadas = 0
        tiene_vencida = False
        
        for f in self.facturas:
            estado = f.get("estado", "")
            fecha_venc = f.get("fecha_vencimiento", "")
            
            # Contar pagadas
            if estado == "Pagada":
                facturas_pagadas += 1
                continue  # No importa si está vencida si ya está pagada
            
            # Si NO está pagada, verificar si está vencida
            if fecha_venc:
                try:
                    fv = datetime.fromisoformat(fecha_venc.replace('Z', '+00:00'))
                    if fv.date() < now.date():
                        tiene_vencida = True
                except:
                    pass
        
        # Lógica de prioridad
        if tiene_vencida:
            return "rgba(239,68,68,0.9)"  # 🔴 ROJO: Al menos una vencida
        elif facturas_pagadas < total_facturas:
            return "rgba(234,179,8,0.9)"  # 🟡 AMARILLO: Hay pendientes (no todas pagadas)
        else:
            return "rgba(34,197,94,0.9)"  # 🟢 VERDE: Todas pagadas
    
    def _update_style(self):
        """Actualiza el estilo del widget."""
        if self.is_selected:
            bg = "rgba(30,58,138,0.9)"
            border = "rgba(59,130,246,0.8)"
        elif self.is_today:
            bg = "rgba(30,41,59,0.6)"
            border = "rgba(59,130,246,0.5)"
        elif not self.is_current_month:
            bg = "rgba(15,23,42,0.2)"
            border = "rgba(51,65,85,0.3)"
        else:
            bg = "rgba(15,23,42,0.5)"
            border = "rgba(51,65,85,0.4)"
        
        self.setStyleSheet(f"""
            CalendarDayWidget {{
                background: {bg};
                border: 1px solid {border};
                border-radius: 6px;
            }}
            CalendarDayWidget:hover {{
                background: rgba(30,41,59,0.7);
                border: 1px solid rgba(59,130,246,0.6);
            }}
        """)
    
    def set_selected(self, selected: bool):
        """Marca/desmarca el día como seleccionado."""
        self.is_selected = selected
        self._update_style()
    
    def mousePressEvent(self, event):
        """Maneja el click en el día."""
        if event.button() == QtCore.Qt.LeftButton and self.is_current_month:
            self.day_clicked.emit(self.date)
        super().mousePressEvent(event)


class CalendarView(QtWidgets.QWidget):
    """Vista principal del calendario con semanas, filtros y dropdowns mes/año."""
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.parent_window = parent
        self.current_date = datetime.now()
        self.selected_day_widget = None
        self._setup_ui()
        self._load_month()
    
    def _setup_ui(self):
        """Configura la interfaz principal."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(16)
        
        # Título
        title = QtWidgets.QLabel("Calendario")
        title.setStyleSheet("""
            QLabel {
                color: rgba(226,232,240,0.95);
                font-size: 18pt;
                font-weight: 900;
            }
        """)
        layout.addWidget(title)
        
        # Filtros
        filters = self._create_filters()
        layout.addWidget(filters)
        
        # Header con navegación de mes/año (CON DROPDOWNS)
        header = self._create_header()
        layout.addWidget(header)
        
        # Grid del calendario
        calendar_container = QtWidgets.QWidget()
        calendar_layout = QtWidgets.QVBoxLayout(calendar_container)
        calendar_layout.setContentsMargins(0, 0, 0, 0)
        calendar_layout.setSpacing(0)
        
        # Grid principal
        self.calendar_grid = QtWidgets.QGridLayout()
        self.calendar_grid.setSpacing(4)
        self.calendar_grid.setContentsMargins(0, 0, 0, 0)
        
        # Header de días de la semana
        days_header = QtWidgets.QWidget()
        days_header_layout = QtWidgets.QHBoxLayout(days_header)
        days_header_layout.setContentsMargins(0, 0, 0, 8)
        days_header_layout.setSpacing(4)
        
        # Espacio para columna de semanas
        week_spacer = QtWidgets.QLabel("Sem")
        week_spacer.setFixedWidth(40)
        week_spacer.setAlignment(QtCore.Qt.AlignCenter)
        week_spacer.setStyleSheet("""
            QLabel {
                color: rgba(100,116,139,0.7);
                font-weight: 700;
                font-size: 8pt;
                letter-spacing: 1px;
            }
        """)
        days_header_layout.addWidget(week_spacer)
        
        # Días de la semana
        days_of_week = ["dom", "lun", "mar", "mié", "jue", "vie", "sáb"]
        for day in days_of_week:
            label = QtWidgets.QLabel(day)
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    color: rgba(148,163,184,0.8);
                    font-weight: 700;
                    font-size: 9pt;
                    letter-spacing: 0.5px;
                }
            """)
            days_header_layout.addWidget(label)
        
        calendar_layout.addWidget(days_header)
        calendar_layout.addLayout(self.calendar_grid)
        
        layout.addWidget(calendar_container, 1)
    
    def _create_filters(self) -> QtWidgets.QWidget:
        """Crea la barra de filtros mejorados."""
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Filtro por ID/Factura
        id_label = QtWidgets.QLabel("ID/Factura:")
        id_label.setStyleSheet("color: rgba(148,163,184,0.9); font-size: 9pt; font-weight: 600;")
        layout.addWidget(id_label)
        
        self.id_filter = QtWidgets.QLineEdit()
        self.id_filter.setPlaceholderText("FVE, 11109...")
        self.id_filter.setMaximumWidth(150)
        self.id_filter.setStyleSheet(self._input_style())
        self.id_filter.textChanged.connect(self._on_filter_changed)
        layout.addWidget(self.id_filter)
        
        # Filtro por proveedor
        prov_label = QtWidgets.QLabel("Proveedor:")
        prov_label.setStyleSheet("color: rgba(148,163,184,0.9); font-size: 9pt; font-weight: 600;")
        layout.addWidget(prov_label)
        
        self.prov_filter = QtWidgets.QLineEdit()
        self.prov_filter.setPlaceholderText("Nombre...")
        self.prov_filter.setMaximumWidth(150)
        self.prov_filter.setStyleSheet(self._input_style())
        self.prov_filter.textChanged.connect(self._on_filter_changed)
        layout.addWidget(self.prov_filter)
        
        # Filtro por estado
        estado_label = QtWidgets.QLabel("Estado:")
        estado_label.setStyleSheet("color: rgba(148,163,184,0.9); font-size: 9pt; font-weight: 600;")
        layout.addWidget(estado_label)
        
        self.estado_filter = QtWidgets.QComboBox()
        self.estado_filter.addItems(["Todas", "Pendiente", "Pagada", "Vencida"])
        self.estado_filter.setStyleSheet(self._combo_style())
        self.estado_filter.currentTextChanged.connect(self._on_filter_changed)
        layout.addWidget(self.estado_filter)
        
        layout.addStretch()
        
        # Botón limpiar
        btn_clear = QtWidgets.QPushButton("Limpiar")
        btn_clear.setStyleSheet("""
            QPushButton {
                background: rgba(51,65,85,0.4);
                border: 1px solid rgba(71,85,105,0.5);
                border-radius: 6px;
                padding: 6px 14px;
                color: rgba(148,163,184,0.9);
                font-weight: 600;
                font-size: 9pt;
            }
            QPushButton:hover {
                background: rgba(51,65,85,0.6);
            }
        """)
        btn_clear.setCursor(QtCore.Qt.PointingHandCursor)
        btn_clear.clicked.connect(self._clear_filters)
        layout.addWidget(btn_clear)
        
        return container
    
    def _create_header(self) -> QtWidgets.QWidget:
        """Crea header con DROPDOWNS de mes y año."""
        header = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Navegación flechas
        btn_prev = QtWidgets.QPushButton("◀")
        btn_prev.setFixedSize(36, 36)
        btn_prev.setStyleSheet(self._nav_button_style())
        btn_prev.setCursor(QtCore.Qt.PointingHandCursor)
        btn_prev.clicked.connect(self._prev_month)
        
        # DROPDOWN DE MES
        self.month_combo = QtWidgets.QComboBox()
        month_names = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                       "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        self.month_combo.addItems(month_names)
        self.month_combo.setCurrentIndex(self.current_date.month - 1)
        self.month_combo.setStyleSheet(self._combo_style())
        self.month_combo.setCursor(QtCore.Qt.PointingHandCursor)
        self.month_combo.currentIndexChanged.connect(self._on_month_changed)
        
        # DROPDOWN DE AÑO (EDITABLE)
        self.year_combo = QtWidgets.QComboBox()
        self.year_combo.setEditable(True)  # Permite escribir
        self.year_combo.setInsertPolicy(QtWidgets.QComboBox.NoInsert)  # No inserta valores escritos
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 5, current_year + 6)]
        self.year_combo.addItems(years)
        self.year_combo.setCurrentIndex(5)  # Año actual
        self.year_combo.setStyleSheet(self._combo_style())
        self.year_combo.setCursor(QtCore.Qt.PointingHandCursor)
        
        # Validador para solo números de 4 dígitos
        year_validator = QtGui.QIntValidator(1900, 2100, self)
        self.year_combo.setValidator(year_validator)
        
        # Conectar tanto cambio de texto como selección
        self.year_combo.currentTextChanged.connect(self._on_year_changed)
        self.year_combo.lineEdit().returnPressed.connect(lambda: self._on_year_changed(self.year_combo.currentText()))
        
        btn_next = QtWidgets.QPushButton("▶")
        btn_next.setFixedSize(36, 36)
        btn_next.setStyleSheet(self._nav_button_style())
        btn_next.setCursor(QtCore.Qt.PointingHandCursor)
        btn_next.clicked.connect(self._next_month)
        
        btn_today = QtWidgets.QPushButton("Hoy")
        btn_today.setStyleSheet("""
            QPushButton {
                background: rgba(37,99,235,0.8);
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: white;
                font-weight: 700;
                font-size: 9pt;
            }
            QPushButton:hover {
                background: rgba(59,130,246,0.9);
            }
        """)
        btn_today.setCursor(QtCore.Qt.PointingHandCursor)
        btn_today.clicked.connect(self._go_to_today)
        
        layout.addWidget(btn_prev)
        layout.addSpacing(12)
        layout.addWidget(self.month_combo)
        layout.addWidget(QtWidgets.QLabel(","))
        layout.addWidget(self.year_combo)
        layout.addSpacing(12)
        layout.addWidget(btn_next)
        layout.addStretch()
        layout.addWidget(btn_today)
        
        return header
    
    def _input_style(self) -> str:
        """Estilo para inputs de texto."""
        return """
            QLineEdit {
                background: rgba(30,41,59,0.5);
                border: 1px solid rgba(71,85,105,0.5);
                border-radius: 6px;
                padding: 6px 12px;
                color: rgba(226,232,240,0.95);
                font-size: 9pt;
            }
            QLineEdit:focus {
                border: 1px solid rgba(59,130,246,0.6);
                background: rgba(30,41,59,0.7);
            }
        """
    
    def _combo_style(self) -> str:
        """Estilo para comboboxes."""
        return """
            QComboBox {
                background: rgba(30,41,59,0.5);
                border: 1px solid rgba(71,85,105,0.5);
                border-radius: 6px;
                padding: 6px 12px;
                color: rgba(226,232,240,0.95);
                font-size: 9pt;
                font-weight: 600;
                min-width: 100px;
            }
            QComboBox:hover {
                border: 1px solid rgba(59,130,246,0.4);
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid rgba(148,163,184,0.8);
                margin-right: 8px;
            }
        """
    
    def _nav_button_style(self) -> str:
        """Estilo para botones de navegación."""
        return """
            QPushButton {
                background: rgba(51,65,85,0.5);
                border: 1px solid rgba(71,85,105,0.5);
                border-radius: 6px;
                color: rgba(148,163,184,0.9);
                font-weight: 700;
                font-size: 11pt;
            }
            QPushButton:hover {
                background: rgba(51,65,85,0.7);
                border: 1px solid rgba(59,130,246,0.5);
                color: rgba(226,232,240,0.95);
            }
        """
    
    def _load_month(self):
        """Carga el mes con números de semana correctos (1-53)."""
        # Limpiar referencia al día seleccionado (se va a borrar)
        self.selected_day_widget = None
        
        # Limpiar grid
        for i in reversed(range(self.calendar_grid.count())):
            widget = self.calendar_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Actualizar dropdowns sin trigger
        self.month_combo.blockSignals(True)
        self.year_combo.blockSignals(True)
        self.month_combo.setCurrentIndex(self.current_date.month - 1)
        self.year_combo.setCurrentText(str(self.current_date.year))
        self.month_combo.blockSignals(False)
        self.year_combo.blockSignals(False)
        
        # Obtener facturas filtradas
        facturas = self._get_filtered_facturas()
        
        # Calcular inicio del calendario
        first_day = self.current_date.replace(day=1)
        weekday = (first_day.weekday() + 1) % 7  # Domingo = 0
        start_date = first_day - timedelta(days=weekday)
        
        # Generar 6 semanas
        current = start_date
        for week in range(6):
            # Número de semana ISO (1-53)
            week_num = current.isocalendar()[1]
            week_label = QtWidgets.QLabel(str(week_num))
            week_label.setFixedWidth(40)
            week_label.setAlignment(QtCore.Qt.AlignCenter)
            week_label.setStyleSheet("""
                QLabel {
                    color: rgba(100,116,139,0.6);
                    font-weight: 600;
                    font-size: 9pt;
                    background: rgba(15,23,42,0.3);
                    border-radius: 4px;
                    padding: 4px;
                }
            """)
            self.calendar_grid.addWidget(week_label, week, 0)
            
            # Días de la semana
            for day in range(7):
                day_facturas = self._get_facturas_for_day(current, facturas)
                is_current = current.month == self.current_date.month
                
                day_widget = CalendarDayWidget(current, day_facturas, is_current, self)
                day_widget.day_clicked.connect(self._on_day_clicked)
                
                self.calendar_grid.addWidget(day_widget, week, day + 1)
                current += timedelta(days=1)
    
    def _get_filtered_facturas(self) -> List[Dict[str, Any]]:
        """Obtiene facturas con filtros mejorados."""
        facturas = self.db.list_facturas()
        
        # Filtro de ID/Factura (busca en ambos campos)
        id_text = self.id_filter.text().strip().upper()
        if id_text:
            facturas = [f for f in facturas if 
                id_text in str(f.get("id", "")).upper() or 
                id_text in (f.get("numero_factura") or "").upper()]
        
        # Filtro de proveedor
        prov_text = self.prov_filter.text().strip().lower()
        if prov_text:
            facturas = [f for f in facturas if prov_text in (f.get("proveedor") or "").lower()]
        
        # Filtro de estado
        estado = self.estado_filter.currentText()
        if estado != "Todas":
            if estado == "Vencida":
                now = datetime.now()
                facturas = [f for f in facturas if f.get("estado") != "Pagada" and 
                           self._is_vencida(f, now)]
            else:
                facturas = [f for f in facturas if f.get("estado") == estado]
        
        return facturas
    
    def _is_vencida(self, factura: Dict[str, Any], now: datetime) -> bool:
        """Verifica si está vencida."""
        fecha_venc = factura.get("fecha_vencimiento", "")
        if not fecha_venc:
            return False
        try:
            fv = datetime.fromisoformat(fecha_venc.replace('Z', '+00:00'))
            return fv.date() < now.date()
        except:
            return False
    
    def _get_facturas_for_day(self, date: datetime, facturas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Obtiene facturas de un día."""
        result = []
        for f in facturas:
            fecha_venc = f.get("fecha_vencimiento", "")
            if not fecha_venc:
                continue
            try:
                fv = datetime.fromisoformat(fecha_venc.replace('Z', '+00:00'))
                if fv.date() == date.date():
                    result.append(f)
            except:
                continue
        return result
    
    def _on_day_clicked(self, date: datetime):
        """Al hacer click en día, filtra facturas que VENCEN ese día."""
        # Deseleccionar día anterior (verificar si sigue existiendo)
        if self.selected_day_widget:
            try:
                self.selected_day_widget.set_selected(False)
            except RuntimeError:
                # Widget ya fue borrado (cambio de mes)
                pass
        
        # Seleccionar nuevo día
        for i in range(self.calendar_grid.count()):
            widget = self.calendar_grid.itemAt(i).widget()
            if isinstance(widget, CalendarDayWidget) and widget.date.date() == date.date():
                widget.set_selected(True)
                self.selected_day_widget = widget
                break
        
        # NAVEGAR A DASHBOARD Y FILTRAR por fecha de vencimiento
        if self.parent_window and hasattr(self.parent_window, 'sidebar'):
            # Cambiar a vista dashboard
            self.parent_window.sidebar._on_nav_click("dashboard")
            
            # Aplicar filtro de fecha en dashboard
            if hasattr(self.parent_window, 'filter_by_date'):
                self.parent_window.filter_by_date(date)
    
    def _on_month_changed(self, index):
        """Cuando cambia el mes en dropdown."""
        self.current_date = self.current_date.replace(month=index + 1)
        self._load_month()
    
    def _on_year_changed(self, year_text):
        """Cuando cambia el año en dropdown."""
        try:
            year = int(year_text)
            self.current_date = self.current_date.replace(year=year)
            self._load_month()
        except:
            pass
    
    def _on_filter_changed(self):
        """Recarga cuando cambian filtros."""
        self._load_month()
    
    def _clear_filters(self):
        """Limpia filtros."""
        self.id_filter.clear()
        self.prov_filter.clear()
        self.estado_filter.setCurrentIndex(0)
        self._load_month()
    
    def _prev_month(self):
        """Mes anterior."""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self._load_month()
    
    def _next_month(self):
        """Mes siguiente."""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self._load_month()
    
    def _go_to_today(self):
        """Vuelve a hoy."""
        self.current_date = datetime.now()
        self._load_month()

    def refresh(self):
        """Refresca el calendario (actualiza los colores de los badges)."""
        self._load_month()

