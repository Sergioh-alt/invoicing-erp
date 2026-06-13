"""
TableController - Maneja la lógica de la tabla de facturas.
Mixin para MainWindow que gestiona visualización, ordenamiento y actualización de la tabla.
"""
from PySide6 import QtWidgets, QtGui
from datetime import datetime
from app.views.helpers.formatting_helpers import (
    parse_iso, compute_counts, status_text, kind_color, remaining_text
)


class TableController:
    """
    Controlador de la tabla de facturas.
    Se usa como mixin en MainWindow.
    
    Requiere que la clase que lo use tenga:
    - self.table: QTableWidget
    - self.db: Database
    - self.kpi_*: KPIWidgets
    - self.pagination_manager: PaginatedTableManager
    - self._rows_cache: list de facturas filtradas
    - self._sort_ascending: bool
    - self._is_refreshing: bool
    - self._fecha_filtro_activa: datetime opcional
    - self.cmb_filter, self.id_input, self.prov_input: widgets de filtro
    """
    
    def pretty_dt(self, iso: str):
        """Formatea datetime ISO a string bonito."""
        d = parse_iso(iso)
        return d.strftime("%d/%m/%Y %H:%M") if d else "-"
    
    def _toggle_sort_order(self):
        """
        Alterna el orden de las facturas (ascendente/descendente).
        Actualiza el ícono en el header y refresca la tabla.
        """
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
        """
        Maneja click en headers de la tabla.
        Solo la columna de Factura (índice 1) es ordenable.
        """
        if column_index == 1:  # Columna "Factura"
            self._toggle_sort_order()
    
    def refresh_table(self, fecha_filtro=None):
        """
        Actualiza la tabla con filtros aplicados.
        
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
        
        self._rows_cache = all_rows
        
        # Actualizar KPIs
        p, t, o = compute_counts(all_rows)
        self.kpi_pending.set_value(p)
        self.kpi_today.set_value(t)
        self.kpi_overdue.set_value(o)
        self.kpi_total.set_value(len(all_rows))
        
        # Usar paginación para mostrar filas
        if hasattr(self, 'pagination_manager'):
            self.pagination_manager.set_data(all_rows)
        
        # Actualizar calendario con todas las fechas
        if hasattr(self, 'calendar_view'):
            try:
                fechas = []
                for r in all_rows:
                    if r.get("fecha_vencimiento"):
                        dt = parse_iso(r["fecha_vencimiento"])
                        if dt:
                            fechas.append(dt.date())
                self.calendar_view.mark_dates(fechas)
            except:
                pass
        
        self._update_filter_status()
        self._is_refreshing = False
    
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
            tiene_pdf = bool(r.get("pdf_path"))
            pdf_text = "Sí" if tiene_pdf else "No"
            
            
            # Indicador de Comprobante - FORZAR VALOR VISIBLE
            comprobante_path_value = r.get("comprobante_path")
            tiene_comprobante = bool(comprobante_path_value and str(comprobante_path_value).strip())
            comprobante_text = "✓ Sí" if tiene_comprobante else "✗ No"
            
            # DEBUG: Ver qué valores tiene
            # if r.get("estado") == "Pagada":
            #     print(f"DEBUG Factura {factura_id} ({r.get('numero_factura')}): comprobante_path = {comprobante_path_value!r}, tiene = {tiene_comprobante}, text = {comprobante_text!r}")
            
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
                comprobante_text,  # Nueva columna
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
                
                # Columna Comprobante (índice 11) con estilo especial si tiene comprobante
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
        """
        Actualiza solo las cuentas regresivas sin refrescar toda la tabla.
        Usado por timer para actualizar tiempos en tiempo real.
        """
        # Obtener filas visibles en la página actual
        visible_count = self.table.rowCount()
        
        if not hasattr(self, '_rows_cache') or not self._rows_cache:
            return
        
        # Obtener página actual
        if hasattr(self, 'pagination_manager'):
            current_page = self.pagination_manager.current_page
            items_per_page = self.pagination_manager.items_per_page
            start_idx = (current_page - 1) * items_per_page
            page_rows = self._rows_cache[start_idx:start_idx + items_per_page]
        else:
            page_rows = self._rows_cache
        
        for visual_row, r in enumerate(page_rows):
            if visual_row >= visible_count:
                break
            
            # Actualizar columna de tiempo restante (índice 5)
            remaining_item = self.table.item(visual_row, 5)
            if remaining_item:
                remaining_item.setText(remaining_text(r))
            
            # Actualizar columna de estado si hay snooze (índice 7)
            st_text, kind = status_text(r)
            status_item = self.table.item(visual_row, 7)
            if status_item:
                status_item.setText(st_text)
                col = kind_color(kind)
                # Actualizar color de toda la fila
                for c in range(self.table.columnCount()):
                    if c != 10:  # Excepto columna PDF
                        item = self.table.item(visual_row, c)
                        if item:
                            item.setForeground(col)
