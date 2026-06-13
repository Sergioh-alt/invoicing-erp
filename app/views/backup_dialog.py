"""
Diálogo de Gestión de Backups.
Permite crear, restaurar y administrar backups de la base de datos.
"""
from PySide6 import QtWidgets, QtCore, QtGui
from datetime import datetime
from app.utils.windows_styles import apply_dark_title_bar
import os


class BackupDialog(QtWidgets.QDialog):
    """Diálogo para gestionar backups de la base de datos."""
    
    def __init__(self, parent, backup_manager):
        """
        Inicializa el diálogo de backups.
        
        Args:
            parent: Ventana padre
            backup_manager: Instancia de BackupManager
        """
        super().__init__(parent)
        self.backup_manager = backup_manager
        
        self.setWindowTitle("")
        self.setMinimumSize(700, 500)
        self.setModal(True)
        
        self._setup_ui()
        self._refresh_list()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Título
        title = QtWidgets.QLabel("💾 Gestión de Backups")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; color: rgba(59,130,246,0.9);")
        layout.addWidget(title)
        
        # Descripción
        desc = QtWidgets.QLabel(
            "Los backups protegen tus datos. Se recomienda crear backups regulares.\n"
            "Los backups automáticos se crean diariamente y se mantienen por 30 días."
        )
        desc.setStyleSheet("color: rgba(229,231,235,0.7); margin-bottom: 10px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Estadísticas
        self.stats_label = QtWidgets.QLabel()
        self.stats_label.setStyleSheet("""
            background-color: rgba(59,130,246,0.1);
            border: 1px solid rgba(59,130,246,0.3);
            border-radius: 8px;
            padding: 12px;
            color: rgba(229,231,235,0.9);
        """)
        layout.addWidget(self.stats_label)
        
        # Tabla de backups
        table_label = QtWidgets.QLabel("📋 Backups Disponibles")
        table_label.setStyleSheet("font-size: 12pt; font-weight: bold; margin-top: 10px;")
        layout.addWidget(table_label)
        
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Fecha", "Tipo", "Tamaño", "Nombre"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.table.setSelectionMode(QtWidgets.QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(30,41,59,0.5);
                border: 1px solid rgba(71,85,105,0.5);
                border-radius: 8px;
                gridline-color: rgba(71,85,105,0.3);
            }
            QHeaderView::section {
                background-color: rgba(51,65,85,0.8);
                color: rgba(229,231,235,0.9);
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)
        
        # Botones de acción
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(12)
        
        # Crear Backup
        btn_create = QtWidgets.QPushButton("✨ Crear Backup Ahora")
        btn_create.setStyleSheet("""
            QPushButton {
                background-color: rgba(34,197,94,0.15);
                border: 2px solid rgba(34,197,94,0.4);
                color: rgba(34,197,94,1);
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: rgba(34,197,94,0.25);
                border-color: rgba(34,197,94,0.6);
            }
        """)
        btn_create.clicked.connect(self._create_backup)
        btn_layout.addWidget(btn_create)
        
        # Restaurar
        btn_restore = QtWidgets.QPushButton("🔄 Restaurar Seleccionado")
        btn_restore.setStyleSheet("""
            QPushButton {
                background-color: rgba(251,191,36,0.15);
                border: 2px solid rgba(251,191,36,0.4);
                color: rgba(251,191,36,1);
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: rgba(251,191,36,0.25);
                border-color: rgba(251,191,36,0.6);
            }
        """)
        btn_restore.clicked.connect(self._restore_backup)
        btn_layout.addWidget(btn_restore)
        
        # Eliminar
        btn_delete = QtWidgets.QPushButton("🗑️ Eliminar Seleccionado")
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: rgba(239,68,68,0.15);
                border: 2px solid rgba(239,68,68,0.4);
                color: rgba(239,68,68,1);
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: rgba(239,68,68,0.25);
                border-color: rgba(239,68,68,0.6);
            }
        """)
        btn_delete.clicked.connect(self._delete_backup)
        btn_layout.addWidget(btn_delete)
        
        # Abrir carpeta
        btn_open = QtWidgets.QPushButton("📂 Abrir Carpeta")
        btn_open.setStyleSheet("""
            QPushButton {
                background-color: rgba(59,130,246,0.15);
                border: 2px solid rgba(59,130,246,0.4);
                color: rgba(59,130,246,1);
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: rgba(59,130,246,0.25);
                border-color: rgba(59,130,246,0.6);
            }
        """)
        btn_open.clicked.connect(self._open_folder)
        btn_layout.addWidget(btn_open)
        
        layout.addLayout(btn_layout)
        
        # Botón cerrar
        btn_close = QtWidgets.QPushButton("Cerrar")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: rgba(71,85,105,0.3);
                border: 2px solid rgba(100,116,139,0.4);
                color: rgba(229,231,235,0.9);
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(71,85,105,0.5);
            }
        """)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
    
    def _refresh_list(self):
        """Actualiza la lista de backups."""
        # Limpiar tabla
        self.table.setRowCount(0)
        
        # Obtener backups
        backups = self.backup_manager.list_backups()
        
        # Llenar tabla
        for backup in backups:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Fecha
            fecha_str = backup["date"].strftime("%d/%m/%Y %H:%M:%S")
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(fecha_str))
            
            # Tipo
            tipo_item = QtWidgets.QTableWidgetItem(backup["type"])
            if backup["type"] == "Automático":
                tipo_item.setForeground(QtGui.QColor(34, 197, 94))  # Verde
            else:
                tipo_item.setForeground(QtGui.QColor(59, 130, 246))  # Azul
            self.table.setItem(row, 1, tipo_item)
            
            # Tamaño
            size_str = f"{backup['size_kb']:.2f} KB"
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(size_str))
            
            # Nombre
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(backup["name"]))
            
            # Guardar ruta en item data
            self.table.item(row, 0).setData(QtCore.Qt.UserRole, backup["path"])
        
        self.table.resizeColumnsToContents()
        
        # Actualizar estadísticas
        stats = self.backup_manager.get_stats()
        stats_text = f"""📊 Estadísticas:  
Total: {stats['total_backups']} backups  |  Automáticos: {stats['automatic']}  |  Manuales: {stats['manual']}  |  Espacio: {stats['total_size_mb']:.2f} MB"""
        
        if stats['newest']:
            stats_text += f"  |  Último: {stats['newest'].strftime('%d/%m/%Y %H:%M')}"
        
        self.stats_label.setText(stats_text)
    
    def _create_backup(self):
        """Crea un nuevo backup manual."""
        result = self.backup_manager.create_backup(auto=False)
        
        if result:
            QtWidgets.QMessageBox.information(
                self,
                "Backup Creado",
                f"Backup creado exitosamente:\n{os.path.basename(result)}"
            )
            self._refresh_list()
        else:
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                "No se pudo crear el backup. Verifica los logs para más detalles."
            )
    
    def _restore_backup(self):
        """Restaura desde el backup seleccionado."""
        selected = self.table.selectedItems()
        if not selected:
            QtWidgets.QMessageBox.warning(
                self,
                "Sin Selección",
                "Por favor selecciona un backup para restaurar."
            )
            return
        
        backup_path = self.table.item(selected[0].row(), 0).data(QtCore.Qt.UserRole)
        backup_name = os.path.basename(backup_path)
        
        # Confirmación
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirmar Restauración",
            f"¿Restaurar desde este backup?\n\n{backup_name}\n\n"
            "⚠️ ADVERTENCIA: Esto reemplazará la base de datos actual.\n"
            "Se creará un backup de seguridad antes de restaurar.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            result = self.backup_manager.restore_backup(backup_path)
            
            if result:
                QtWidgets.QMessageBox.information(
                    self,
                    "Restauración Exitosa",
                    "Base de datos restaurada correctamente.\n\n"
                    "Se recomienda reiniciar la aplicación."
                )
                self.accept()  # Cerrar diálogo
            else:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    "No se pudo restaurar el backup. Verifica los logs."
                )
    
    def _delete_backup(self):
        """Elimina el backup seleccionado."""
        selected = self.table.selectedItems()
        if not selected:
            QtWidgets.QMessageBox.warning(
                self,
                "Sin Selección",
                "Por favor selecciona un backup para eliminar."
            )
            return
        
        backup_path = self.table.item(selected[0].row(), 0).data(QtCore.Qt.UserRole)
        backup_name = os.path.basename(backup_path)
        
        # Confirmación
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Eliminar este backup?\n\n{backup_name}",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                os.remove(backup_path)
                QtWidgets.QMessageBox.information(
                    self,
                    "Eliminado",
                    "Backup eliminado correctamente."
                )
                self._refresh_list()
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    f"No se pudo eliminar el backup:\n{str(e)}"
                )
    
    def _open_folder(self):
        """Abre la carpeta de backups en el explorador."""
        import subprocess
        backup_dir = str(self.backup_manager.backup_dir.absolute())
        
        try:
            if os.name == 'nt':  # Windows
                os.startfile(backup_dir)
            elif os.name == 'posix':  # macOS/Linux
                subprocess.call(['open' if os.uname().sysname == 'Darwin' else 'xdg-open', backup_dir])
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self,
                "Error",
                f"No se pudo abrir la carpeta:\n{str(e)}"
            )

    def showEvent(self, event: QtGui.QShowEvent):
        """Aplica barra de título oscura al mostrarse."""
        super().showEvent(event)
        apply_dark_title_bar(self)
