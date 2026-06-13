"""
FilterController - Maneja la lógica de filtros de la tabla.
Mixin para MainWindow que gestiona filtros de búsqueda y estado.
"""
from PySide6 import QtWidgets


class FilterController:
    """
    Controlador de filtros para la tabla de facturas.
    Se usa como mixin en MainWindow.
    
    Requiere que la clase que lo use tenga:
    - self.id_input: QLineEdit
    - self.prov_input: QLineEdit
    - self.cmb_filter: QComboBox
    - self.filter_status_label: QLabel
    - self._fecha_filtro_activa: datetime opcional
    - self.refresh_table(): método
    """
    
    def _on_text_filter_changed(self):
        """
        Maneja cambios en filtros de texto (limpia filtro de fecha).
        Se llama cuando el usuario escribe en campos de filtro.
        También detecta easter egg: código de activación en búsqueda.
        """
        # EASTER EGG: Detectar código de activación en filtro de búsqueda
        prov_text = self.prov_input.text().strip().upper()
        
        # DEBUG: Print para verificar
        # print(f"DEBUG FILTER: prov_text = '{prov_text}'")
        
        if prov_text == "SHEDULE-36-2":
            # print("DEBUG: ★★★ EASTER EGG DETECTED! ★★★")
            import logging
            logger = logging.getLogger("FacturasGanaTodo.filter")
            logger.info("Easter egg detected!")
            
            try:
                self._show_hidden_feature_dialog()
                self.prov_input.clear()  # Limpiar después de detectar
            except Exception as e:
                logger.exception(f"Error showing hidden feature dialog: {e}")
                from PySide6 import QtWidgets
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    f"Error al activar función oculta:\n{str(e)}"
                )
            return
        
        # Si el usuario escribe en filtros, limpiar filtro de fecha del calendario
        self._fecha_filtro_activa = None
        self._sort_ascending = True  # True = antiguas primero, False = recientes primero
        self._is_refreshing = False
        
        # Actualizar indicador de filtros
        self._update_filter_status()
        self.refresh_table()
    
    def _update_filter_status(self):
        """
        Actualiza el label de estado de filtros.
        Muestra qué filtros están activos.
        """
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
    
    def _clear_filters(self):
        """
        Limpia todos los filtros aplicados.
        Resetea campos de búsqueda, estado y fecha.
        """
        # Limpiar filtro de fecha del calendario
        self._fecha_filtro_activa = None
        self._sort_ascending = True  # True = antiguas primero, False = recientes primero
        self._is_refreshing = False
        
        # Actualizar indicador de filtros
        self._update_filter_status()
        
        # Limpiar filtros de texto
        if hasattr(self, 'id_input'):
            self.id_input.clear()
        
        if hasattr(self, 'prov_input'):
            self.prov_input.clear()
        
        self.cmb_filter.setCurrentIndex(0)  # "Todas"
        self.refresh_table()
    
    def _show_hidden_feature_dialog(self):
        """
        Muestra el diálogo de función oculta (generador de comprobantes).
        Se activa cuando el usuario escribe el código de activación.
        """
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
            from PySide6 import QtWidgets
            status_text = "activado" if new_status else "desactivado"
            QtWidgets.QMessageBox.information(
                self,
                "Configuración Actualizada",
                f"El generador de comprobantes de pago ha sido {status_text}."
            )
