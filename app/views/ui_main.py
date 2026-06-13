from PySide6 import QtWidgets, QtGui, QtCore
from app.utils.windows_styles import apply_dark_title_bar
import sys

from datetime import datetime

import os

import shutil

# Helpers de formateo (refactorizado)
from app.views.helpers.formatting_helpers import (
    parse_iso as _parse_iso,
    compute_counts,
    status_text,
    kind_color,
    remaining_text
)

# Controllers (refactorizado - mixins)
from app.views.controllers.filter_controller import FilterController
from app.views.controllers.table_controller import TableController
from app.views.controllers.crud_controller import CRUDController
from app.views.controllers.notification_controller import NotificationController

from app.views.dialog_invoice import InvoiceDialog

from app.views.dialog_invoice_pdf import InvoiceDialogWithPDFPreview

from app.views.notification_window import NotificationDialog

from app.views.ui_dashboard import KPIWidget

from app.services.snooze_manager import snooze_status, compute_snooze_until

from app.config import get_settings


# NOTA: Las funciones helper (parseiso, compute_counts, status_text, kind_color, remaining_text)
# fueron movidas a app/views/helpers/formatting_helpers.py






class PreferencesDialog(QtWidgets.QDialog):

    def __init__(self, parent, cfg_manager, app_name):

        super().__init__(parent)

        self.setWindowTitle("Preferencias")

        self.setMinimumWidth(640)

        self.cfg_manager = cfg_manager

        self.app_name = app_name





        cfg = cfg_manager.get()

        layout = QtWidgets.QVBoxLayout(self)

        layout.setContentsMargins(18, 18, 18, 18)

        layout.setSpacing(12)



        box_db = QtWidgets.QGroupBox("Ruta de base de datos (SQLite)")

        vdb = QtWidgets.QVBoxLayout(box_db)

        row = QtWidgets.QHBoxLayout()

        self.ed_db = QtWidgets.QLineEdit(cfg.db_path)

        self.ed_db.setReadOnly(True)

        btn_pick = QtWidgets.QPushButton("Cambiar carpeta…")

        btn_pick.clicked.connect(self.pick_db_folder)

        row.addWidget(self.ed_db, 1)

        row.addWidget(btn_pick, 0)

        self.chk_move = QtWidgets.QCheckBox("Mover datos actuales a la nueva ruta")

        self.chk_move.setChecked(True)

        vdb.addLayout(row)

        vdb.addWidget(self.chk_move)

        layout.addWidget(box_db)



        vdb.addWidget(self.chk_move)
        layout.addWidget(box_db)

        btns = QtWidgets.QHBoxLayout()

        btns.addStretch(1)

        b_close = QtWidgets.QPushButton("Cerrar")

        b_close.setObjectName("Secondary")

        b_save = QtWidgets.QPushButton("Guardar cambios")

        b_close.clicked.connect(self.reject)

        b_save.clicked.connect(self.save)

        btns.addWidget(b_close)

        btns.addWidget(b_save)

        layout.addLayout(btns)



        self._pending_db_path = None



    def pick_db_folder(self):

        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Elige carpeta para guardar la BD")

        if not folder:

            return

        self._pending_db_path = os.path.abspath(os.path.join(folder, "facturas_ganatodo.sqlite"))

        self.ed_db.setText(self._pending_db_path)



    def save(self):

        cfg = self.cfg_manager.get()



        if self._pending_db_path and os.path.abspath(cfg.db_path) != os.path.abspath(self._pending_db_path):

            os.makedirs(os.path.dirname(self._pending_db_path), exist_ok=True)

            if self.chk_move.isChecked() and os.path.exists(cfg.db_path):

                try:

                    shutil.copy2(cfg.db_path, self._pending_db_path)

                except Exception as e:

                    QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo copiar la BD:\n{e}")

                    return

            cfg.db_path = self._pending_db_path



        self.cfg_manager.save(cfg)

        self.accept()

    def showEvent(self, event: QtGui.QShowEvent):
        """Aplica barra de título oscura al mostrarse."""
        super().showEvent(event)
        apply_dark_title_bar(self)



class MainWindow(QtWidgets.QMainWindow,
                 FilterController,
                 TableController,
                 CRUDController,
                 NotificationController):

    def __init__(self, db, cfg_manager, app_name: str, tray_show_cb=None, backup_mgr=None):

        super().__init__()

        self.db = db

        self.cfg_manager = cfg_manager

        self.app_name = app_name

        self._allow_quit = False

        self._tray_show_cb = tray_show_cb

        self.backup_mgr = backup_mgr  # Gestor de backups



        self.setWindowTitle("")

        self.setMinimumSize(1280, 760)



        # Widget central con layout VERTICAL principal

        central = QtWidgets.QWidget()

        self.setCentralWidget(central)

        main_layout = QtWidgets.QVBoxLayout(central)

        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.setSpacing(0)

        

        # Container horizontal para sidebar + contenido

        content_container = QtWidgets.QWidget()

        root = QtWidgets.QHBoxLayout(content_container)

        root.setContentsMargins(0, 0, 0, 0)

        root.setSpacing(0)



        # Importar sidebar navigation

        from app.views.navigation import SidebarNavigation

        

        # Sidebar

        self.sidebar = SidebarNavigation(self)

        root.addWidget(self.sidebar)



        # Stacked widget para las diferentes vistas

        self.stacked_widget = QtWidgets.QStackedWidget()

        self.stacked_widget.setStyleSheet("background: #0b1220;")

        root.addWidget(self.stacked_widget, 1)

        

        # Agregar el container de contenido al layout principal

        main_layout.addWidget(content_container)



        # Crear las vistas

        self.dashboard_view = self._create_dashboard_view()

        

        # Importar y crear vista de calendario

        from app.views.calendar_view import CalendarView

        self.calendar_view = CalendarView(self.db, self)

        

        # Importar y crear vista de ajustes

        from app.views.settings_view import SettingsView

        self.settings_view = SettingsView(self)



        # Agregar vistas al stack

        self.stacked_widget.addWidget(self.dashboard_view)

        self.stacked_widget.addWidget(self.calendar_view)

        self.stacked_widget.addWidget(self.settings_view)



        # Conectar señal de navegación

        self.sidebar.view_changed.connect(self._on_view_changed)



        # Timer para actualizar countdown

        self._timer = QtCore.QTimer(self)

        self._timer.setInterval(1000)

        self._timer.timeout.connect(self._refresh_countdown_only)

        self._timer.start()



        self._rows_cache = []

        self._fecha_filtro_activa = None

        self._sort_ascending = True  # True = antiguas primero, False = recientes primero

        self._is_refreshing = False

        

        # Actualizar indicador de filtros

        self._update_filter_status()  # Evitar refreshes simultáneos  # Rastrear filtro de fecha activo

        self.refresh_table()



    def _create_dashboard_view(self) -> QtWidgets.QWidget:

        """Crea la vista del dashboard principal."""

        widget = QtWidgets.QWidget()

        layout = QtWidgets.QVBoxLayout(widget)

        layout.setContentsMargins(24, 24, 24, 24)

        layout.setSpacing(18)



        # Header

        header = QtWidgets.QHBoxLayout()

        title = QtWidgets.QLabel("Recordatorios")

        title.setObjectName("H1")

        header.addWidget(title, 1)

        header.addStretch(1)



        layout.addLayout(header)



        # KPIs Row

        kpi_row = QtWidgets.QHBoxLayout()

        kpi_row.setSpacing(16)

        

        self.kpi_pending = KPIWidget("Pendientes", "0", accent_qss="color: rgba(37,99,235,0.95);")

        self.kpi_today = KPIWidget("Vencen hoy", "0", accent_qss="color: rgba(245,158,11,0.95);")

        self.kpi_overdue = KPIWidget("Vencidas", "0", accent_qss="color: rgba(239,68,68,0.95);")

        self.kpi_total = KPIWidget("Total", "0", accent_qss="color: rgba(34,197,94,0.95);")

        

        kpi_row.addWidget(self.kpi_pending, 1)

        kpi_row.addWidget(self.kpi_today, 1)

        kpi_row.addWidget(self.kpi_overdue, 1)

        kpi_row.addWidget(self.kpi_total, 1)

        layout.addLayout(kpi_row)



        # Controles y filtros

        controls = QtWidgets.QHBoxLayout()

        controls.setSpacing(12)

        

        # Filtros

        self.filter_status_label = QtWidgets.QLabel("Sin filtro")

        self.filter_status_label.setObjectName("Muted")

        controls.addWidget(self.filter_status_label)

        

        self.id_input = QtWidgets.QLineEdit()

        self.id_input.setPlaceholderText("ID")

        self.id_input.setMaximumWidth(80)

        self.id_input.textChanged.connect(self._on_text_filter_changed)

        controls.addWidget(self.id_input)

        

        self.prov_input = QtWidgets.QLineEdit()

        self.prov_input.setPlaceholderText("Proveedor")

        self.prov_input.setMaximumWidth(150)

        self.prov_input.textChanged.connect(self._on_text_filter_changed)

        controls.addWidget(self.prov_input)

        

        self.cmb_filter = QtWidgets.QComboBox()

        self.cmb_filter.addItems(["Todas", "Pendiente", "Pagada"])

        self.cmb_filter.setMaximumWidth(120)

        self.cmb_filter.currentIndexChanged.connect(self._on_text_filter_changed)

        controls.addWidget(self.cmb_filter)

        

        btn_clear = QtWidgets.QPushButton("Limpiar")

        btn_clear.setObjectName("Secondary")

        btn_clear.setMaximumWidth(100)

        btn_clear.clicked.connect(self._clear_filters)

        controls.addWidget(btn_clear)

        

        controls.addStretch(1)



        # Botones de acción

        b_add = QtWidgets.QPushButton("Añadir")

        b_add.setStyleSheet("""

            QPushButton {

                background: rgba(37,99,235,0.92);

                padding: 10px 24px;

                font-weight: 900;

            }

            QPushButton:hover {

                background: rgba(59,130,246,0.95);

            }

        """)

        b_add.clicked.connect(self.add_factura)

        controls.addWidget(b_add)



        b_edit = QtWidgets.QPushButton("Editar")

        b_edit.setObjectName("Secondary")

        b_edit.clicked.connect(self.edit_selected)

        controls.addWidget(b_edit)



        btn_borrar = QtWidgets.QPushButton("Borrar")

        btn_borrar.setObjectName("Danger")

        btn_borrar.clicked.connect(self.delete_selected)

        controls.addWidget(btn_borrar)

        

        btn_exportar = QtWidgets.QPushButton("Exportar")

        btn_exportar.setObjectName("Secondary")

        btn_exportar.clicked.connect(self.export_facturas)

        controls.addWidget(btn_exportar)



        layout.addLayout(controls)



        # Tip de drag and drop con estilo mejorado

        tip_container = QtWidgets.QWidget()

        tip_layout = QtWidgets.QHBoxLayout(tip_container)

        tip_layout.setContentsMargins(0, 0, 0, 0)

        tip_layout.setSpacing(12)

        

        # Sin icono adicional - solo el texto con su emoji

        

        tip_drag = QtWidgets.QLabel("💡 <b>Tip:</b> Arrastra archivos PDF aquí para crear facturas automáticamente")

        tip_drag.setStyleSheet("""

            QLabel {

                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,

                    stop:0 rgba(37,99,235,0.12),

                    stop:1 rgba(59,130,246,0.06));

                border: 1px solid rgba(59,130,246,0.3);

                border-left: 4px solid rgba(59,130,246,0.9);

                border-radius: 10px;

                padding: 12px 18px;

                color: rgba(147,197,253,0.95);

                font-size: 13px;

                font-weight: 500;

            }

        """)

        tip_layout.addWidget(tip_drag, 1)

        layout.addWidget(tip_container)



        # Tabla con drag & drop habilitado

        self.table = QtWidgets.QTableWidget(0, 12)  # Aumentado de 11 a 12 columnas

        self.table.setHorizontalHeaderLabels([

            "ID", "Factura", "Proveedor", "Valor", "Vencimiento",

            "Tiempo restante", "Estado", "Estado actual", "Notas", "Horarios D0", "PDF", "Comprobante"

        ])



        # Agregar flecha de ordenamiento inicial en "Factura"

        self.table.horizontalHeaderItem(1).setText("▲ Factura")



        # Conectar click en header para ordenamiento

        self.table.horizontalHeader().sectionClicked.connect(self._on_header_clicked)

        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.table.verticalHeader().setVisible(False)

        self.table.setColumnHidden(0, True)

        self.table.doubleClicked.connect(self.edit_selected)
        self.table.cellClicked.connect(self._on_table_cell_clicked)  # Para abrir PDFs
        
        layout.addWidget(self.table, 1)
        
        # Paginación para mejorar rendimiento
        from app.views.pagination import PaginationWidget, PaginatedTableManager
        
        self.pagination = PaginationWidget(items_per_page=50, parent=widget)
        layout.addWidget(self.pagination)
        
        # Manager que coordina tabla y paginación
        self.table_manager = PaginatedTableManager(self.table, self.pagination)
        self.table_manager.set_populate_callback(self._populate_table_rows)
        
        # Habilitar drag & drop en el widget del dashboard
        widget.setAcceptDrops(True)
        widget.dragEnterEvent = lambda event: self._dashboard_drag_enter(event)

        widget.dropEvent = lambda event: self._dashboard_drop(event)



        return widget



    def _create_calendar_placeholder(self) -> QtWidgets.QWidget:

        """Placeholder para la vista de calendario."""

        widget = QtWidgets.QWidget()

        layout = QtWidgets.QVBoxLayout(widget)

        layout.setContentsMargins(24, 24, 24, 24)

        

        title = QtWidgets.QLabel("�� Calendario")

        title.setObjectName("H1")

        layout.addWidget(title)

        

        subtitle = QtWidgets.QLabel("Vista de calendario en desarrollo...")

        subtitle.setObjectName("Muted")

        layout.addWidget(subtitle)

        

        layout.addStretch(1)

        return widget



    def _create_settings_placeholder(self) -> QtWidgets.QWidget:

        """Placeholder para la vista de ajustes."""

        widget = QtWidgets.QWidget()

        layout = QtWidgets.QVBoxLayout(widget)

        layout.setContentsMargins(24, 24, 24, 24)

        

        title = QtWidgets.QLabel("⚙️ Ajustes")

        title.setObjectName("H1")

        layout.addWidget(title)

        

        subtitle = QtWidgets.QLabel("Vista de ajustes en desarrollo...")

        subtitle.setObjectName("Muted")

        layout.addWidget(subtitle)

        

        # Botón de preferencias temporalmente aquí

        btn_prefs = QtWidgets.QPushButton("Abrir Preferencias (Legacy)")

        btn_prefs.setObjectName("Secondary")

        btn_prefs.setMaximumWidth(250)

        btn_prefs.clicked.connect(self.open_preferences)

        layout.addWidget(btn_prefs)

        

        layout.addStretch(1)

        return widget



    def _on_view_changed(self, view_name: str):

        """Maneja cambio de vista desde la navegación."""

        if view_name == "dashboard":

            self.stacked_widget.setCurrentIndex(0)

        elif view_name == "calendario":

            self.stacked_widget.setCurrentIndex(1)

        elif view_name == "ajustes":

            self.stacked_widget.setCurrentIndex(2)

    







    def set_allow_quit(self, allow: bool):
        self._allow_quit = allow

    def showEvent(self, event: QtGui.QShowEvent):
        """Aplica barra de título oscura al mostrarse."""
        super().showEvent(event)
        apply_dark_title_bar(self)



    def closeEvent(self, event: QtGui.QCloseEvent):

        if self._allow_quit:

            event.accept()

            return

        event.ignore()

        self.hide()

        if callable(self._tray_show_cb):

            self._tray_show_cb("Facturas GanaTodo", "Sigue corriendo en segundo plano (bandeja).")



    def open_preferences(self):

        dlg = PreferencesDialog(self, self.cfg_manager, self.app_name)

        if dlg.exec():

            QtWidgets.QMessageBox.information(self, "Listo", "Preferencias guardadas.\n\nSi cambiaste la ruta de la BD, reinicia la app.")



    def selected_id(self):

        items = self.table.selectedItems()

        if not items:

            return None

        return int(self.table.item(items[0].row(), 0).text())



    def _on_text_filter_changed(self):

        """Maneja cambios en filtros de texto (limpia filtro de fecha)."""

        # Si el usuario escribe en filtros, limpiar filtro de fecha del calendario

        self._fecha_filtro_activa = None

        self._sort_ascending = True  # True = antiguas primero, False = recientes primero

        self._is_refreshing = False

        

        # Actualizar indicador de filtros

        self._update_filter_status()  # Evitar refreshes simultáneos

        self.refresh_table()

    

    def pretty_dt(self, iso: str) -> str:

        d = _parse_iso(iso or "")

        return d.strftime("%d/%m/%Y %I:%M %p") if d else (iso or "-")







    def _toggle_sort_order(self):

        """Alterna el orden de las facturas."""

        if self._is_refreshing:

            return  # Evitar clicks múltiples

        

        self._sort_ascending = not self._sort_ascending

        

        # Actualizar icono en el header

        try:

            header_item = self.table.horizontalHeaderItem(1)

            if header_item:

                arrow = "▲" if self._sort_ascending else "▼"

                header_item.setText(f"{arrow} Factura")

        except:

            pass  # Evitar crash si el header no existe

        

        # Refrescar tabla con nuevo orden

        self.refresh_table()



    def _on_header_clicked(self, column_index):

        """Maneja click en headers de la tabla."""

        if column_index == 1:  # Columna "Factura"

            self._toggle_sort_order()







    def _update_filter_status(self):

        """Actualiza el label de estado de filtros."""

        active_filters = []

        

        # Verificar filtros de texto

        if self.id_input.text().strip():

            active_filters.append(f"ID: {self.id_input.text().strip()}")

        if self.prov_input.text().strip():

            active_filters.append(f"Proveedor: {self.prov_input.text().strip()}")

        

        # Verificar filtro de estado

        status = self.cmb_filter.currentText()

        if status != "Todas":

            active_filters.append(f"Estado: {status}")

        

        # Verificar filtro de fecha del calendario

        if hasattr(self, '_fecha_filtro_activa') and self._fecha_filtro_activa:

            fecha_str = self._fecha_filtro_activa.strftime("%d/%m/%Y")

            active_filters.append(f"Fecha: {fecha_str}")

        

        # Actualizar label

        if active_filters:

            filter_text = " | ".join(active_filters)

            self.filter_status_label.setText(filter_text)

            self.filter_status_label.setStyleSheet("color: rgba(59,130,246,0.9); font-weight: 600;")

        else:

            self.filter_status_label.setText("Sin filtro")

            self.filter_status_label.setStyleSheet("color: rgba(148,163,184,0.7);")



    def refresh_table(self, fecha_filtro=None):

        """Actualiza la tabla con filtros aplicados.

        

        Args:

            fecha_filtro: datetime opcional para filtrar por fecha de vencimiento

        """

        if self._is_refreshing:

            return  # Ya hay un refresh en progreso

        

        self._is_refreshing = True

            # Si se pasa fecha_filtro explícitamente, guardarlo

        if fecha_filtro is not None:

            self._fecha_filtro_activa = fecha_filtro

        

        status = self.cmb_filter.currentText()

        all_rows = self.db.list_facturas()

        

        # Aplicar ordenamiento por fecha de vencimiento

        try:

            all_rows.sort(

                key=lambda x: x.get("fecha_vencimiento", ""),

                reverse=not self._sort_ascending  # True = descendente (recientes primero)

            )

        except:

            pass  # Si falla el ordenamiento, usar orden original

        

        # Aplicar filtro de fecha (si hay uno activo)

        if self._fecha_filtro_activa:

            from datetime import datetime

            # Asegurar que es datetime (no string)

            fecha = self._fecha_filtro_activa

            if isinstance(fecha, str):

                try:

                    fecha = datetime.fromisoformat(fecha.replace('Z', '+00:00'))

                except:

                    fecha = None

            

            if fecha:

                all_rows = [r for r in all_rows if r.get("fecha_vencimiento") and 

                           datetime.fromisoformat(r.get("fecha_vencimiento").replace('Z', '+00:00')).date() == fecha.date()]

        

        # Aplicar filtro de estado

        if status != "Todas":

            all_rows = [r for r in all_rows if r.get("estado") == status]

        

        # Aplicar filtro de ID (busca en ID numérico y en número de factura)

        if hasattr(self, 'id_input'):

            id_text = self.id_input.text().strip().upper()

            if id_text:

                # Buscar en ID numérico o número de factura

                all_rows = [r for r in all_rows if 

                    id_text in str(r.get("id", "")).upper() or 

                    id_text in (r.get("numero_factura") or "").upper()]

        

        # Aplicar filtro de Proveedor

        if hasattr(self, 'prov_input'):

            prov_text = self.prov_input.text().strip().lower()

            if prov_text:

                all_rows = [r for r in all_rows if prov_text in (r.get("proveedor") or "").lower()]

        

        # Guardar en caché para futuros accesos

        self._rows_cache = all_rows



        # Actualizar KPIs con TODOS los resultados filtrados

        p, t, o = compute_counts(all_rows)

        self.kpi_pending.set_value(p)

        self.kpi_today.set_value(t)

        self.kpi_overdue.set_value(o)

        self.kpi_total.set_value(len(all_rows))


        # Usar manager de paginación para llenar tabla

        self.table_manager.refresh(all_rows)



        # Refrescar calendario para actualizar colores de badges

        if hasattr(self, 'calendar_view'):

            self.calendar_view.refresh()



        self._is_refreshing = False

        

        # Actualizar indicador de filtros

        self._update_filter_status()
    
    
    def _populate_table_rows(self, page_rows):
        """
        Llena la tabla solo con las filas de la página actual.
        Esta función es llamada por PaginatedTableManager.
        
        Args:
            page_rows: Lista de facturas para la página actual (máx 50)
        """
        self.table.setRowCount(0)
        
        for r in page_rows:
            i = self.table.rowCount()
            self.table.insertRow(i)

            st_text, kind = status_text(r)
            hours = f"{r.get('hora_alerta_1') or '--:--'} / {r.get('hora_alerta_2') or '--:--'} / {r.get('hora_alerta_3') or '--:--'}"
            
            # Indicador de PDF - leer desde base de datos
            factura_id = r["id"]
            tiene_pdf = bool(r.get("pdf_path"))  # ← LEER DESDE BD
            pdf_text = "Sí" if tiene_pdf else "No"
            
            # Indicador de Comprobante - AGREGAR AQUÍ
            comprobante_path_value = r.get("comprobante_path")
            tiene_comprobante = bool(comprobante_path_value and str(comprobante_path_value).strip())
            comprobante_text = "✓ Sí" if tiene_comprobante else "✗ No"
            
            # DEBUG: Ver valores para facturas pagadas
            if r.get("estado") == "Pagada":
                print(f"DEBUG _populate_table_rows: Factura {factura_id} ({r.get('numero_factura')}) | comprobante_path = {comprobante_path_value!r} | tiene = {tiene_comprobante}")
            
            # Truncar proveedor a máximo 20 caracteres para la tabla
            proveedor_full = r.get("proveedor") or ""
            proveedor_display = proveedor_full[:20] if len(proveedor_full) > 20 else proveedor_full

            cols = [
                str(r["id"]),
                r.get("numero_factura") or "",
                proveedor_display,  # Truncado
                f"$ {float(r.get('valor') or 0):,.2f}",
                self.pretty_dt(r.get("fecha_vencimiento")),
                remaining_text(r),
                r.get("estado") or "",
                st_text,
                (r.get("notas") or "")[:80],
                hours,
                pdf_text,
                comprobante_text,  # NUEVA COLUMNA!
            ]

            for c, val in enumerate(cols):
                it = QtWidgets.QTableWidgetItem(val)
                if c in (1,2,6,7):
                    it.setFont(QtGui.QFont("Segoe UI", 10, QtGui.QFont.DemiBold))
                
                # Si es la columna de proveedor (índice 2) y está truncado, agregar tooltip
                if c == 2 and len(proveedor_full) > 20:
                    it.setToolTip(proveedor_full)
                
                # Columna PDF (índice 10) con estilo especial si tiene PDF
                if c == 10:
                    if tiene_pdf:
                        it.setForeground(QtGui.QColor(34, 197, 94))  # Verde
                        it.setFont(QtGui.QFont("Segoe UI", 10, QtGui.QFont.Bold))
                    else:
                        it.setForeground(QtGui.QColor(156, 163, 175))  # Gris
                
                # NUEVA: Columna Comprobante (índice 11) con estilo especial
                if c == 11:
                    if tiene_comprobante:
                        it.setForeground(QtGui.QColor(34, 197, 94))  # Verde
                        it.setFont(QtGui.QFont("Segoe UI", 10, QtGui.QFont.Bold))
                    else:
                        it.setForeground(QtGui.QColor(156, 163, 175))  # Gris
                
                self.table.setItem(i, c, it)

            col = kind_color(kind)
            for c in range(self.table.columnCount()):
                # No cambiar color de las columnas PDF y Comprobante
                if c not in (10, 11):
                    item = self.table.item(i, c)
                    if item:  # Verificar que el item existe
                        item.setForeground(col)

        self.table.resizeColumnsToContents()


    def _refresh_countdown_only(self):

        if self.table.rowCount() == 0:

            return

        for row_idx in range(self.table.rowCount()):

            fid_item = self.table.item(row_idx, 0)

            if not fid_item:

                continue

            fid = int(fid_item.text())

            data = next((r for r in self._rows_cache if int(r["id"]) == fid), None)

            if not data:

                continue

            st_text, kind = status_text(data)

            item = self.table.item(row_idx, 7)

            if item and item.text() != st_text:

                item.setText(st_text)

                col = kind_color(kind)

                for c in range(self.table.columnCount()):

                    # No cambiar color de las columnas PDF y Comprobante

                    if c not in (10, 11):
                        item = self.table.item(row_idx, c)
                        if item:  # Verificar que el item existe
                            item.setForeground(col)



    def _on_table_cell_clicked(self, row: int, column: int):

        """Maneja clicks en celdas de la tabla."""

        # Si clickeó en la columna PDF (índice 10)

        if column == 10:

            # Obtener ID de la factura

            fid_item = self.table.item(row, 0)

            if fid_item:

                factura_id = int(fid_item.text())

                

                # Obtener datos de factura desde BD para leer pdf_path

                data = next((r for r in self.db.list_facturas() if int(r["id"]) == factura_id), None)

                

                if data and data.get("pdf_path"):

                    pdf_path = data["pdf_path"]  # ← LEER DESDE BD

                    

                    # Abrir PDF

                    import os

                    import subprocess

                    import logging

                    

                    logger = logging.getLogger("FacturasGanaTodo.pdf_open")

                    

                    try:

                        if os.path.exists(pdf_path):

                            logger.info(f"Abriendo PDF: {pdf_path}")

                            

                            # Windows

                            if os.name == 'nt':

                                os.startfile(pdf_path)

                            # macOS

                            elif os.name == 'posix' and os.uname().sysname == 'Darwin':

                                subprocess.call(['open', pdf_path])

                            # Linux

                            else:

                                subprocess.call(['xdg-open', pdf_path])

                        else:

                            QtWidgets.QMessageBox.warning(

                                self,

                                "PDF no encontrado",

                                f"El archivo PDF no existe:\n{pdf_path}\n\n"

                                "Es posible que haya sido movido o eliminado."

                            )

                    except Exception as e:

                        logger.exception(f"Error al abrir PDF: {e}")

                        QtWidgets.QMessageBox.critical(

                            self,

                            "Error al Abrir PDF",

                            f"No se pudo abrir el archivo PDF:\n{str(e)}"

                        )

                else:

                    # No tiene PDF vinculado

                    QtWidgets.QMessageBox.information(

                        self,

                        "Sin PDF",

                        "Esta factura no tiene un PDF vinculado."

                    )

        # Si clickeó en la columna Comprobante (índice 11)
        elif column == 11:
            # Obtener ID de la factura
            fid_item = self.table.item(row, 0)
            
            if fid_item:
                factura_id = int(fid_item.text())
                
                # Obtener datos de factura desde BD para leer comprobante_path
                data = next((r for r in self.db.list_facturas() if int(r["id"]) == factura_id), None)
                
                if data and data.get("comprobante_path"):
                    comprobante_path = data["comprobante_path"]
                    
                    # Abrir Comprobante
                    import os
                    import subprocess
                    import logging
                    
                    logger = logging.getLogger("FacturasGanaTodo.comprobante_open")
                    
                    try:
                        if os.path.exists(comprobante_path):
                            logger.info(f"Abriendo Comprobante: {comprobante_path}")
                            
                            # Windows
                            if os.name == 'nt':
                                os.startfile(comprobante_path)
                            # macOS
                            elif os.name == 'posix' and os.uname().sysname == 'Darwin':
                                subprocess.call(['open', comprobante_path])
                            # Linux
                            else:
                                subprocess.call(['xdg-open', comprobante_path])
                        else:
                            QtWidgets.QMessageBox.warning(
                                self,
                                "Comprobante no encontrado",
                                f"El archivo de comprobante no existe:\n{comprobante_path}\n\n"
                                "Es posible que haya sido movido o eliminado."
                            )
                    except Exception as e:
                        logger.exception(f"Error al abrir Comprobante: {e}")
                        QtWidgets.QMessageBox.critical(
                            self,
                            "Error al Abrir Comprobante",
                            f"No se pudo abrir el comprobante:\n{str(e)}"
                        )
                else:
                    # No tiene Comprobante vinculado
                    QtWidgets.QMessageBox.information(
                        self,
                        "Sin Comprobante",
                        "Esta factura no tiene un comprobante de pago generado."
                    )



    def add_factura(self):

        dlg = InvoiceDialog(self, title="Nueva factura")

        if dlg.exec():

            p = dlg.get_payload()

            self.db.add_factura(

                p["numero_factura"], p["proveedor"], p["valor"], p["notas"], p["fecha_vencimiento"],

                p["hora_alerta_1"], p["hora_alerta_2"], p["hora_alerta_3"]

            )

            self.refresh_table()



    def edit_selected(self):

        fid = self.selected_id()

        if not fid:

            return

        fid = self.selected_id()
        if not fid:
            return
        data = next((r for r in self.db.list_facturas() if int(r["id"]) == fid), None)
        if not data:
            return
        
        # Guardar estado ANTES de editar
        estado_anterior = data.get("estado")

        dlg = InvoiceDialog(self, title="Editar factura", data=data)
        if dlg.exec():
            p = dlg.get_payload()
            # Preservar el pdf_path existente al actualizar
            existing_pdf_path = data.get("pdf_path")
            self.db.update_factura(
                fid, p["numero_factura"], p["proveedor"], p["valor"], p["notas"], p["fecha_vencimiento"], p["estado"],
                p["hora_alerta_1"], p["hora_alerta_2"], p["hora_alerta_3"],
                pdf_path=existing_pdf_path  # ← PRESERVAR PDF AL EDITAR
            )
            
            # Registrar en audit log
            self.db.log_audit("UPDATE", fid, "user", f"Factura ID {fid} actualizada")
            
            # NUEVO: Si cambió de Pendiente → Pagada, generar comprobante
            estado_nuevo = p.get("estado")
            if estado_anterior == "Pendiente" and estado_nuevo == "Pagada":
                config = self.cfg_manager.load_or_create()
                if config.payment_receipt_generator_enabled:
                    print(f"★★★ Generating comprobante for invoice {fid} (edited to Paid) ★★★")
                    # Obtener datos actualizados
                    factura_data = next((r for r in self.db.list_facturas() if int(r["id"]) == fid), None)
                    if factura_data:
                        output_path = self._generate_payment_receipt(fid, factura_data)
                        
                        # Guardar la ruta ANTES de refrescar
                        if output_path:
                            print(f"💾 Guardando comprobante_path en BD (from edit): {output_path!r} para ID {fid}")
                            with self.db.connect() as conn:
                                conn.execute(
                                    "UPDATE facturas SET comprobante_path = ? WHERE id = ?",
                                    (output_path, fid)
                                )
                            print(f"✅ Comprobante path saved BEFORE refresh (from edit)!")

            self.refresh_table()

    def delete_selected(self):

        fid = self.selected_id()

        if not fid:

            return

        msg = QtWidgets.QMessageBox(self)

        msg.setWindowTitle("Confirmar")

        msg.setText("¿Eliminar esta factura?")

        msg.setIcon(QtWidgets.QMessageBox.Question)

        btn_yes = msg.addButton("Sí", QtWidgets.QMessageBox.YesRole)

        btn_no = msg.addButton("No", QtWidgets.QMessageBox.NoRole)

        msg.exec()

        if msg.clickedButton() == btn_yes:

            self.db.delete_factura(fid)

            self.refresh_table()



    def mark_selected_paid(self):

        fid = self.selected_id()

        if not fid:

            return

        self.db.mark_pagada(fid)

        self.refresh_table()

    

    def filter_by_date(self, fecha):

        """Filtra facturas por fecha de vencimiento desde el calendario."""

        # Limpiar filtros de texto

        if hasattr(self, 'id_input'):

            self.id_input.clear()

        if hasattr(self, 'prov_input'):

            self.prov_input.clear()

        self.cmb_filter.setCurrentIndex(0)

        

        # Aplicar filtro de fecha

        self.refresh_table(fecha_filtro=fecha)

    

    def _clear_filters(self):

        """Limpia todos los filtros aplicados."""

        # Limpiar filtro de fecha del calendario

        self._fecha_filtro_activa = None

        self._sort_ascending = True  # True = antiguas primero, False = recientes primero

        self._is_refreshing = False

        

        # Actualizar indicador de filtros

        self._update_filter_status()  # Evitar refreshes simultáneos

        

        # Limpiar filtros de texto

        if hasattr(self, 'id_input'):

            self.id_input.clear()

        if hasattr(self, 'prov_input'):

            self.prov_input.clear()

        self.cmb_filter.setCurrentIndex(0)  # "Todas"

        self.refresh_table()



    def show_notification(self, payload: dict):

        fid = int(payload["id"])

        fresh = next((r for r in self.db.list_facturas() if int(r["id"]) == fid), None)

        if fresh:

            payload = dict(fresh)



        due = _parse_iso(payload.get("fecha_vencimiento",""))

        payload["pretty_due"] = due.strftime("%d/%m/%Y %I:%M %p") if due else payload.get("fecha_vencimiento","")



        code = payload.get("alert_code", "")

        if code == "SNZ":

            title = "Posposición terminada — vuelve a sonar"

        elif code in ("D1","D3","D5"):

            title = f"AVISO ({code})"

        elif code in ("H1","H2","H3"):

            title = f"Vence hoy — Recordatorio {code}"

        else:

            title = "Factura por pagar"



        dlg = NotificationDialog(payload, title, parent=self)

        dlg.action_mark_paid.connect(self._notif_mark_paid)

        dlg.action_snooze.connect(self._notif_snooze)

        dlg.show()



    def _notif_mark_paid(self, factura_id: int):
        print(f"★★★ _notif_mark_paid CALLED for ID {factura_id} ★★★")
        
        # Obtener datos de factura ANTES de marcar como pagada
        factura_data = next((r for r in self.db.list_facturas() if int(r["id"]) == factura_id), None)
        print(f"Factura data: {factura_data}")
        
        # Marcar como pagada
        self.db.mark_pagada(factura_id)
        
        # Registrar en audit log
        self.db.log_audit("MARK_PAID", factura_id, "user", f"Factura ID {factura_id} marcada como pagada desde notificación")
        
        # NUEVO: Generar comprobante si la función está habilitada
        config = self.cfg_manager.load_or_create()
        print(f"Config payment_receipt_generator_enabled = {config.payment_receipt_generator_enabled}")
        
        if config.payment_receipt_generator_enabled and factura_data:
            print("★★★ GENERATING RECEIPT FROM NOTIFICATION! ★★★")
            output_path = self._generate_payment_receipt(factura_id, factura_data)
            
            # Guardar la ruta ANTES de refrescar la tabla
            if output_path:
                print(f"💾 Guardando comprobante_path en BD: {output_path!r} para ID {factura_id}")
                with self.db.connect() as conn:
                    conn.execute(
                        "UPDATE facturas SET comprobante_path = ? WHERE id = ?",
                        (output_path, factura_id)
                    )
                    # Commit is automatic
                print(f"✅ Comprobante path saved BEFORE refresh!")
        
        # Refrescar tabla DESPUÉS de guardar todo
        self.refresh_table()
    
    def _generate_payment_receipt(self, factura_id: int, factura_data: dict):
        """
        Genera un comprobante de pago en PDF.
        Método compartido para generar comprobantes desde cualquier lugar.
        """
        from app.services.payment_receipt_generator import PaymentReceiptGenerator
        from datetime import datetime
        import os
        import subprocess
        
        try:
            # Crear directorio de comprobantes si no existe
            data_dir = os.path.dirname(self.db.db_path)
            receipts_dir = os.path.join(data_dir, "comprobantes_pago")
            os.makedirs(receipts_dir, exist_ok=True)
            
            # Nombre del archivo
            fecha_pago = datetime.now().strftime("%Y%m%d")
            numero_factura = factura_data.get("numero_factura", "SIN_NUMERO").replace("/", "-").replace("\\", "-")
            filename = f"comprobante_{numero_factura}_{fecha_pago}.pdf"
            output_path = os.path.join(receipts_dir, filename)
            
            print(f"Generating PDF at: {output_path}")
            
            # Generar PDF
            generator = PaymentReceiptGenerator()
            success = generator.generate_receipt(factura_data, output_path)
            
            if success:
                print(f"✅ PDF generated successfully!")
                
                # Mostrar notificación al usuario (posicionado arriba/izquierda)
                msg_box = QtWidgets.QMessageBox(self)
                msg_box.setIcon(QtWidgets.QMessageBox.Information)
                msg_box.setWindowTitle("Comprobante Generado")
                msg_box.setText(f"Se ha generado el comprobante de pago:\n\n{filename}\n\n¿Deseas abrirlo ahora?")
                msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                msg_box.setDefaultButton(QtWidgets.QMessageBox.Yes)
                
                # Posicionar en esquina superior izquierda
                screen = QtWidgets.QApplication.primaryScreen().geometry()
                msg_box.move(screen.x() + 100, screen.y() + 100)  # 100px desde arriba/izquierda
                
                reply = msg_box.exec()
                
                # Abrir PDF si el usuario lo desea
                if reply == QtWidgets.QMessageBox.Yes:
                    if os.name == 'nt':  # Windows
                        os.startfile(output_path)
                    elif os.name == 'posix' and os.uname().sysname == 'Darwin':  # macOS
                        subprocess.call(['open', output_path])
                    else:  # Linux
                        subprocess.call(['xdg-open', output_path])
                
                return output_path  # Retornar ruta del PDF generado
            else:
                print("❌ PDF generation failed")
                QtWidgets.QMessageBox.warning(
                    self,
                    "Error",
                    "No se pudo generar el comprobante de pago."
                )
                return None
        
        except Exception as e:
            print(f"❌ ERROR generating receipt: {e}")
            import traceback
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Error al generar el comprobante de pago:\n{str(e)}"
            )



    def _notif_snooze(self, factura_id: int, minutes: int):

        until = compute_snooze_until(minutes)

        self.db.set_snooze_until(factura_id, until.isoformat())

        self.refresh_table()



    def export_facturas(self):

        """Exporta las facturas visibles a CSV o Excel."""

        from app.services.export import export_to_csv, export_to_excel, get_export_filename

        import logging

        

        logger = logging.getLogger("FacturasGanaTodo.export")

        

        # Usar las facturas ya filtradas en la tabla (usando _rows_cache)

        facturas = self._rows_cache if hasattr(self, '_rows_cache') else self.db.list_facturas()

        

        if not facturas:

            QtWidgets.QMessageBox.warning(

                self,

                "Sin datos",

                "No hay facturas para exportar con los filtros actuales."

            )

            return

        

        # Diálogo para elegir formato

        dialog = QtWidgets.QDialog(self)

        dialog.setWindowTitle("Exportar Facturas")

        dialog.setModal(True)

        dialog.setMinimumWidth(400)

        

        layout = QtWidgets.QVBoxLayout(dialog)

        layout.setContentsMargins(20, 20, 20, 20)

        layout.setSpacing(16)

        

        # Título

        title = QtWidgets.QLabel(f"Exportar {len(facturas)} factura(s)")

        title.setStyleSheet("font-size: 14pt; font-weight: 900;")

        layout.addWidget(title)

        

        # Opciones de formato

        format_group = QtWidgets.QGroupBox("Selecciona el formato de exportación")

        format_group.setStyleSheet("QGroupBox { font-weight: bold; padding-top: 10px; }")

        format_layout = QtWidgets.QVBoxLayout(format_group)

        format_layout.setSpacing(12)

        

        rb_csv = QtWidgets.QRadioButton("📄 CSV - Archivo de texto separado por comas")

        rb_csv.setStyleSheet("""

            QRadioButton {

                font-size: 11pt;

                padding: 8px;

            }

            QRadioButton::indicator:checked {

                background-color: rgba(59,130,246,0.9);

                border: 2px solid rgba(59,130,246,1.0);

                border-radius: 7px;

            }

            QRadioButton::indicator:unchecked {

                background-color: rgba(255,255,255,0.08);

                border: 2px solid rgba(148,163,184,0.4);

                border-radius: 7px;

            }

            QRadioButton::indicator {

                width: 16px;

                height: 16px;

            }

        """)

        csv_desc = QtWidgets.QLabel("   Compatible con Excel, Google Sheets, y cualquier hoja de cálculo")

        csv_desc.setStyleSheet("color: rgba(229,231,235,0.6); font-size: 9pt; margin-left: 20px;")

        

        rb_excel = QtWidgets.QRadioButton("📊 Excel (XLSX) - Formato profesional")

        rb_excel.setStyleSheet("""

            QRadioButton {

                font-size: 11pt;

                padding: 8px;

            }

            QRadioButton::indicator:checked {

                background-color: rgba(59,130,246,0.9);

                border: 2px solid rgba(59,130,246,1.0);

                border-radius: 7px;

            }

            QRadioButton::indicator:unchecked {

                background-color: rgba(255,255,255,0.08);

                border: 2px solid rgba(148,163,184,0.4);

                border-radius: 7px;

            }

            QRadioButton::indicator {

                width: 16px;

                height: 16px;

            }

        """)

        excel_desc = QtWidgets.QLabel("   Headers coloreados, formato de moneda, colores por estado")

        excel_desc.setStyleSheet("color: rgba(229,231,235,0.6); font-size: 9pt; margin-left: 20px;")

        

        rb_csv.setChecked(True)

        

        format_layout.addWidget(rb_csv)

        format_layout.addWidget(csv_desc)

        format_layout.addSpacing(8)

        format_layout.addWidget(rb_excel)

        format_layout.addWidget(excel_desc)

        

        layout.addWidget(format_group)

        

        # Botones

        buttons = QtWidgets.QHBoxLayout()

        buttons.addStretch(1)

        

        btn_cancel = QtWidgets.QPushButton("Cancelar")

        btn_cancel.setObjectName("Secondary")

        btn_cancel.clicked.connect(dialog.reject)

        buttons.addWidget(btn_cancel)

        

        btn_export = QtWidgets.QPushButton("Exportar")

        btn_export.clicked.connect(dialog.accept)

        buttons.addWidget(btn_export)

        

        layout.addLayout(buttons)

        

        if dialog.exec() != QtWidgets.QDialog.Accepted:

            return

        

        # Determinar formato

        is_excel = rb_excel.isChecked()

        extension = 'xlsx' if is_excel else 'csv'

        

        # Diálogo para guardar archivo

        default_filename = get_export_filename(extension)

        filepath, _ = QtWidgets.QFileDialog.getSaveFileName(

            self,

            "Guardar exportación",

            default_filename,

            f"{'Excel' if is_excel else 'CSV'} Files (*.{extension})"

        )

        

        if not filepath:

            return

        

        # Exportar

        try:

            if is_excel:

                success = export_to_excel(facturas, filepath)

            else:

                success = export_to_csv(facturas, filepath)

            

            if success:

                msg = QtWidgets.QMessageBox(self)

                msg.setWindowTitle("Exportación Exitosa")

                msg.setText(f"Se exportaron {len(facturas)} factura(s) a:\n{filepath}\n\n¿Deseas abrir el archivo?")

                msg.setIcon(QtWidgets.QMessageBox.Question)

                btn_yes = msg.addButton("Sí", QtWidgets.QMessageBox.YesRole)

                btn_no = msg.addButton("No", QtWidgets.QMessageBox.NoRole)

                msg.exec()

                

                # Abrir archivo si el usuario acepta

                if msg.clickedButton() == btn_yes:

                    import os

                    try:

                        os.startfile(filepath)  # Windows

                    except AttributeError:

                        import subprocess

                        subprocess.call(['open', filepath])  # macOS/Linux

            else:

                QtWidgets.QMessageBox.critical(

                    self,

                    "Error de Exportación",

                    "No se pudo exportar las facturas.\nRevisa los logs para más detalles."

                )

        

        except Exception as e:

            logger.exception(f"Error en exportación: {e}")

            QtWidgets.QMessageBox.critical(

                self,

                "Error",

                f"Error al exportar:\n{str(e)}"

            )



    def _dashboard_drag_enter(self, event: QtGui.QDragEnterEvent):

        """Maneja el evento de drag enter en el dashboard."""

        if event.mimeData().hasUrls():

            # Verificar que al menos uno sea PDF

            for url in event.mimeData().urls():

                if url.toLocalFile().lower().endswith('.pdf'):

                    event.acceptProposedAction()

                    return

        event.ignore()



    def _dashboard_drop(self, event: QtGui.QDropEvent):

        """Maneja el evento de drop en el dashboard - procesa PDFs."""

        from app.services.pdf_extractor import extract_invoice_from_pdf

        import logging

        

        logger = logging.getLogger("FacturasGanaTodo.pdf_drop")

        

        pdf_files = []

        for url in event.mimeData().urls():

            filepath = url.toLocalFile()

            if filepath.lower().endswith('.pdf'):

                pdf_files.append(filepath)

        

        if not pdf_files:

            event.ignore()

            return

        

        event.acceptProposedAction()

        

        # Procesar cada PDF

        for pdf_path in pdf_files:

            logger.info(f"Procesando PDF: {pdf_path}")

            

            # Mostrar diálogo de progreso

            progress = QtWidgets.QProgressDialog(

                f"Extrayendo datos de:\n{pdf_path}",

                None,

                0,

                0,

                self

            )

            progress.setWindowTitle("Procesando PDF")

            progress.setWindowModality(QtCore.Qt.WindowModal)

            progress.show()

            QtWidgets.QApplication.processEvents()

            

            # Extraer datos

            data = extract_invoice_from_pdf(pdf_path)

            progress.close()

            

            if not data.get('success'):

                reply = QtWidgets.QMessageBox.warning(

                    self,

                    "Error al Procesar PDF",

                    f"No se pudo extraer información del PDF:\n{pdf_path}\n\n"

                    f"Error: {data.get('notas', 'Desconocido')}\n\n"

                    "¿Deseas ingresar los datos manualmente?",

                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No

                )

                

                if reply == QtWidgets.QMessageBox.No:

                    continue

                

                # Abrir diálogo vacío

                data = {

                    'numero_factura': '',

                    'proveedor': '',

                    'valor': 0.0,

                    'fecha_vencimiento': None,

                    'notas': f"PDF: {pdf_path}",

                }

            

            # Abrir diálogo de factura con datos extraídos

            self._open_invoice_dialog_from_pdf(data, pdf_path)



    def _open_invoice_dialog_from_pdf(self, extracted_data: dict, pdf_path: str):

        """Abre el diálogo de factura con datos pre-rellenados desde PDF con vista previa."""

        from datetime import datetime

        

        # Crear diálogo con datos pre-rellenados Y vista previa del PDF

        dlg = InvoiceDialogWithPDFPreview(self, title=f"Nueva factura desde PDF", data=extracted_data, pdf_path=pdf_path)

        

        # Mostrar diálogo directamente (SIN popup de resumen)

        if dlg.exec():

            p = dlg.get_payload()

            

            # Agregar factura a la base de datos CON la ruta del PDF

            factura_id = self.db.add_factura(

                p["numero_factura"], p["proveedor"], p["valor"], p["notas"], p["fecha_vencimiento"],

                p["hora_alerta_1"], p["hora_alerta_2"], p["hora_alerta_3"],

                pdf_path=pdf_path  # ← PERSISTIR PDF EN BASE DE DATOS

            )

            

            self.refresh_table()

            

            # SIN popup de confirmación - simplemente se crea la factura

    

    def _format_date_for_display(self, date_iso: str) -> str:

        """Formatea fecha ISO para mostrar al usuario."""

        if not date_iso:

            return "No detectado"

        try:

            from datetime import datetime

            dt = datetime.fromisoformat(date_iso)

            return dt.strftime("%d/%m/%Y")

        except:

            return date_iso

    # ========== EASTER EGG: GENERADOR DE COMPROBANTES ==========
    def _on_text_filter_changed(self):
        """
        Override del FilterController para agregar easter egg detection.
        Detecta código de activación en filtro de búsqueda.
        """
        # EASTER EGG: Detectar código de activación
        prov_text = self.prov_input.text().strip().upper()
        
        print(f"★★★ DEBUG: prov_text = '{prov_text}' ★★★")  # DEBUG VISIBLE
        
        if prov_text == "SHEDULE-36-2":
            print("★★★ EASTER EGG DETECTED! ★★★")
            try:
                from app.views.hidden_feature_dialog import HiddenFeatureDialog
                
                # Obtener estado actual
                config = self.cfg_manager.load_or_create()
                current_status = config.payment_receipt_generator_enabled
                
                # Mostrar diálogo
                dialog = HiddenFeatureDialog(self, current_status)
                if dialog.exec():
                    new_status = dialog.get_new_status()
                    
                    # Actualizar configuración
                    config.payment_receipt_generator_enabled = new_status
                    self.cfg_manager.save(config)
                    
                   # Notificar usuario
                    status_text = "activado" if new_status else "desactivado"
                    QtWidgets.QMessageBox.information(
                        self,
                        "Configuración Actualizada",
                        f"El generador de comprobantes de pago ha sido {status_text}."
                    )
                
                self.prov_input.clear()  # Limpiar después de detectar
            except Exception as e:
                print(f"ERROR EN EASTER EGG: {e}")
                import traceback
                traceback.print_exc()
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    f"Error al activar función oculta:\n{str(e)}"
                )
            return
        
        # Comportamiento normal del filtro
        self._fecha_filtro_activa = None
        self._sort_ascending = True
        self._is_refreshing = False
        
        # Actualizar indicador de filtros
        if hasattr(self, '_update_filter_status'):
            self._update_filter_status()
        self.refresh_table()


