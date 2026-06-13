"""
Componente de Paginación para tablas
Mejora el rendimiento mostrando solo un subconjunto de datos por página
"""
from PySide6 import QtWidgets, QtCore, QtGui
from typing import List, Dict, Any, Callable


class PaginationWidget(QtWidgets.QWidget):
    """Widget de controles de paginación con botones y selector de página"""
    
    # Señal emitida cuando cambia la página
    page_changed = QtCore.Signal(int)  # Nueva página (0-indexed)
    
    def __init__(self, items_per_page: int = 50, parent=None):
        super().__init__(parent)
        self.items_per_page = items_per_page
        self.current_page = 0
        self.total_pages = 1
        self.total_items = 0
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Crea la interfaz de paginación"""
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)  # Ultra compacto: 2px arriba/abajo
        layout.setSpacing(6)  # Mínimo spacing
        
        # Stretch izquierdo para centrar controles
        layout.addStretch()
        
        # Botón Anterior
        self.btn_prev = QtWidgets.QPushButton("◄ Anterior")
        self.btn_prev.setFixedWidth(100)  # Reducido de 120
        self.btn_prev.setFixedHeight(26)  # Altura fija pequeña
        self.btn_prev.setStyleSheet("""
            QPushButton {
                background: rgba(71, 85, 105, 0.3);
                border: 1px solid rgba(100, 116, 139, 0.5);
                border-radius: 4px;
                color: rgba(226, 232, 240, 0.9);
                padding: 2px 8px;
                font-weight: 600;
                font-size: 10pt;
            }
            QPushButton:hover {
                background: rgba(71, 85, 105, 0.5);
                border: 1px solid rgba(100, 116, 139, 0.7);
            }
            QPushButton:disabled {
                background: rgba(51, 65, 85, 0.2);
                color: rgba(148, 163, 184, 0.4);
                border: 1px solid rgba(71, 85, 105, 0.3);
            }
        """)
        self.btn_prev.clicked.connect(self._on_prev_clicked)
        layout.addWidget(self.btn_prev)
        
        # Label de información (Página X de Y - Mostrando A-B de C)
        self.lbl_info = QtWidgets.QLabel("Página 1 de 1")
        self.lbl_info.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_info.setMinimumWidth(250)  # Reducido de 280
        self.lbl_info.setFixedHeight(26)  # Altura fija
        self.lbl_info.setStyleSheet("""
            QLabel {
                color: rgba(148, 163, 184, 0.9);
                font-size: 10pt;
                font-weight: 500;
                padding: 2px 8px;
            }
        """)
        layout.addWidget(self.lbl_info)
        
        # Botón Siguiente
        self.btn_next = QtWidgets.QPushButton("Siguiente ►")
        self.btn_next.setFixedWidth(100)  # Reducido de 120
        self.btn_next.setFixedHeight(26)  # Altura fija pequeña
        self.btn_next.setStyleSheet("""
            QPushButton {
                background: rgba(71, 85, 105, 0.3);
                border: 1px solid rgba(100, 116, 139, 0.5);
                border-radius: 4px;
                color: rgba(226, 232, 240, 0.9);
                padding: 2px 8px;
                font-weight: 600;
                font-size: 10pt;
            }
            QPushButton:hover {
                background: rgba(71, 85, 105, 0.5);
                border: 1px solid rgba(100, 116, 139, 0.7);
            }
            QPushButton:disabled {
                background: rgba(51, 65, 85, 0.2);
                color: rgba(148, 163, 184, 0.4);
                border: 1px solid rgba(71, 85, 105, 0.3);
            }
        """)
        self.btn_next.clicked.connect(self._on_next_clicked)
        layout.addWidget(self.btn_next)
        
        # Stretch derecho
        layout.addStretch()
        
        # Inicializar estado de botones
        self._update_buttons()
    
    def set_total_items(self, total: int):
        """Establece el total de items y recalcula páginas"""
        self.total_items = total
        self.total_pages = max(1, (total + self.items_per_page - 1) // self.items_per_page)
        
        # Si estamos en una página que ya no existe (ej: filtramos), volver a la primera
        if self.current_page >= self.total_pages:
            self.current_page = 0
        
        self._update_display()
    
    def _update_display(self):
        """Actualiza el label de información y estado de botones"""
        if self.total_items == 0:
            self.lbl_info.setText("Sin resultados")
        else:
            # Calcular rango de items mostrados
            start_item = self.current_page * self.items_per_page + 1
            end_item = min((self.current_page + 1) * self.items_per_page, self.total_items)
            
            # Texto: "Página X de Y - Mostrando A-B de C"
            page_text = f"Página {self.current_page + 1} de {self.total_pages}"
            items_text = f"Mostrando {start_item}-{end_item} de {self.total_items}"
            self.lbl_info.setText(f"{page_text}  •  {items_text}")
        
        self._update_buttons()
    
    def _update_buttons(self):
        """Actualiza el estado habilitado/deshabilitado de los botones"""
        self.btn_prev.setEnabled(self.current_page > 0)
        self.btn_next.setEnabled(self.current_page < self.total_pages - 1)
    
    def _on_prev_clicked(self):
        """Maneja click en botón Anterior"""
        if self.current_page > 0:
            self.current_page -= 1
            self._update_display()
            self.page_changed.emit(self.current_page)
    
    def _on_next_clicked(self):
        """Maneja click en botón Siguiente"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self._update_display()
            self.page_changed.emit(self.current_page)
    
    def reset(self):
        """Resetea la paginación a la primera página"""
        self.current_page = 0
        self._update_display()
    
    def get_page_slice(self, items: List[Any]) -> List[Any]:
        """
        Retorna el subconjunto de items correspondiente a la página actual
        
        Args:
            items: Lista completa de items
            
        Returns:
            Subconjunto de items para la página actual
        """
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        return items[start:end]


class PaginatedTableManager:
    """
    Manager que coordina tabla y paginación
    Simplifica el uso de paginación con QTableWidget
    """
    
    def __init__(self, table: QtWidgets.QTableWidget, pagination: PaginationWidget):
        self.table = table
        self.pagination = pagination
        self._all_items = []
        self._populate_callback = None
        
        # Conectar señal de cambio de página
        self.pagination.page_changed.connect(self._on_page_changed)
    
    def set_populate_callback(self, callback: Callable[[List[Any]], None]):
        """
        Establece la función que llena la tabla con items
        
        Args:
            callback: Función que recibe lista de items y llena la tabla
                     Debe tener firma: def populate(items: List[Dict]) -> None
        """
        self._populate_callback = callback
    
    def refresh(self, all_items: List[Any]):
        """
        Actualiza la tabla con todos los items, aplicando paginación
        
        Args:
            all_items: Lista completa de items (generalmente desde BD)
        """
        self._all_items = all_items
        
        # Actualizar información de paginación
        self.pagination.set_total_items(len(all_items))
        
        # Obtener items de la página actual
        page_items = self.pagination.get_page_slice(all_items)
        
        # Llenar tabla con items de la página
        if self._populate_callback:
            self._populate_callback(page_items)
    
    def _on_page_changed(self, new_page: int):
        """Maneja cambio de página - recarga la tabla"""
        page_items = self.pagination.get_page_slice(self._all_items)
        if self._populate_callback:
            self._populate_callback(page_items)
    
    def reset(self):
        """Resetea a la primera página"""
        self.pagination.reset()
