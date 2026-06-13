"""
Diálogo de factura mejorado con vista previa de PDF integrada.
"""
from PySide6 import QtCore, QtWidgets, QtGui
from datetime import datetime
from pathlib import Path

# Importar el diálogo base
from app.views.dialog_invoice import InvoiceDialog


class InvoiceDialogWithPDFPreview(InvoiceDialog):
    """Diálogo de factura con vista previa del PDF al lado derecho."""
    
    def __init__(self, parent=None, *, title="Nueva factura desde PDF", data=None, pdf_path=None):
        # Guardar pdf_path antes de llamar al __init__ del padre
        self.pdf_path = pdf_path
        
        # Llamar al constructor del padre
        super().__init__(parent, title=title, data=data)
        
        # Redefinir tamaño mínimo para acomodar la vista previa
        self.setMinimumWidth(1000)
        self.setMinimumHeight(700)
        
        # Agregar vista previa del PDF si existe
        if self.pdf_path:
            self._add_pdf_preview()
    
    def _add_pdf_preview(self):
        """Agrega la vista previa del PDF al lado derecho del diálogo."""
        # Obtener el layout principal
        main_layout = self.layout()
        
        # Crear un layout horizontal para dividir formulario y vista previa
        h_layout = QtWidgets.QHBoxLayout()
        
        # El layout original del formulario ya existe, lo movemos a la izquierda
        # Primero, extraemos todos los widgets del layout actual
        form_widget = QtWidgets.QWidget()
        form_layout = QtWidgets.QVBoxLayout(form_widget)
        
        # Mover todo el contenido existente al nuevo widget de formulario
        while main_layout.count():
            item = main_layout.takeAt(0)
            if item.widget():
                form_layout.addWidget(item.widget())
            elif item.layout():
                form_layout.addLayout(item.layout())
        
        # Agregar el formulario al layout horizontal (lado izquierdo)
        h_layout.addWidget(form_widget, 1)
        
        # Crear widget de vista previa del PDF (lado derecho)
        preview_widget = self._create_pdf_preview_widget()
        h_layout.addWidget(preview_widget, 1)
        
        # Agregar el layout horizontal al layout principal
        main_layout.addLayout(h_layout)
    
    def _create_pdf_preview_widget(self) -> QtWidgets.QWidget:
        """Crea el widget de vista previa del PDF."""
        widget = QtWidgets.QWidget()
        widget.setStyleSheet("""
            QWidget {
                background: rgba(30, 41, 59, 0.5);
                border-radius: 12px;
                border: 1px solid rgba(71, 85, 105, 0.5);
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Título
        title = QtWidgets.QLabel("📄 Vista Previa del PDF")
        title.setStyleSheet("font-size: 12pt; font-weight: bold; color: rgba(226,232,240,0.95);")
        layout.addWidget(title)
        
        # Nombre del archivo
        filename = Path(self.pdf_path).name
        file_label = QtWidgets.QLabel(f"📎 {filename}")
        file_label.setStyleSheet("color: rgba(148,163,184,0.8); font-size: 9pt;")
        file_label.setWordWrap(True)
        layout.addWidget(file_label)
        
        # Label para mostrar la imagen del PDF
        self.pdf_preview_label = QtWidgets.QLabel()
        self.pdf_preview_label.setAlignment(QtCore.Qt.AlignCenter)
        self.pdf_preview_label.setStyleSheet("""
            QLabel {
                background: white;
                border: 2px solid rgba(71, 85, 105, 0.3);
                border-radius: 8px;
                padding: 10px;
            }
        """)
        self.pdf_preview_label.setMinimumSize(350, 450)
        self.pdf_preview_label.setScaledContents(False)
        
        # Cursor de lupa para indicar que se puede hacer zoom
        self.pdf_preview_label.setCursor(QtCore.Qt.CrossCursor)  # Cursor de cruz/lupa
        
        # Habilitar tracking de mouse para zoom hover
        self.pdf_preview_label.setMouseTracking(True)
        self.pdf_preview_label.mouseMoveEvent = lambda event: self._hover_zoom(event)
        self.pdf_preview_label.leaveEvent = lambda event: self._reset_zoom()
        self.pdf_preview_label.wheelEvent = lambda event: self._adjust_zoom_level(event)
        
        # Variables para almacenar pixmap original y nivel de zoom
        self.original_pdf_pixmap = None
        self.zoom_region_size = 150  # Tamaño inicial de región (aumentado de 100 a 150)
        self.min_zoom_region = 50    # Máximo zoom (región más pequeña)
        self.max_zoom_region = 600   # Mínimo zoom (región más grande) - aumentado de 300 a 600
        
        # Renderizar primera página del PDF
        self._render_pdf_preview()
        
        layout.addWidget(self.pdf_preview_label, 1)
        
        # Botón para abrir PDF completo
        btn_open_pdf = QtWidgets.QPushButton("🔍 Abrir PDF Completo")
        btn_open_pdf.setStyleSheet("""
            QPushButton {
                background: rgba(37,99,235,0.15);
                border: 1px solid rgba(37,99,235,0.4);
                border-radius: 6px;
                padding: 8px 16px;
                color: rgba(96,165,250,0.95);
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(37,99,235,0.25);
            }
        """)
        btn_open_pdf.clicked.connect(self._open_full_pdf)
        layout.addWidget(btn_open_pdf)
        
        return widget
    
    def _render_pdf_preview(self):
        """Renderiza la primera página del PDF como imagen en alta calidad."""
        try:
            import fitz  # PyMuPDF
            
            # Abrir PDF
            doc = fitz.open(self.pdf_path)
            
            # Obtener primera página
            page = doc[0]
            
            # Renderizar a imagen con ALTA CALIDAD (3x zoom para mejor resolución)
            zoom = 3.0  # Factor de zoom aumentado de 1.5 a 3.0 para mayor calidad
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)  # alpha=False para mejor rendimiento
            
            # Convertir a QImage
            img_data = pix.tobytes("png")
            qimage = QtGui.QImage.fromData(img_data)
            
            # Escalar imagen para que quepa en el label
            pixmap = QtGui.QPixmap.fromImage(qimage)
            
            # Guardar pixmap original de ALTA CALIDAD para zoom
            self.original_pdf_pixmap = pixmap
            
            scaled_pixmap = pixmap.scaled(
                self.pdf_preview_label.minimumWidth() - 20,
                self.pdf_preview_label.minimumHeight() - 20,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            
            self.pdf_preview_label.setPixmap(scaled_pixmap)
            
            doc.close()
            
        except ImportError:
            # Si PyMuPDF no está disponible
            self.pdf_preview_label.setText("⚠️ PyMuPDF no disponible\nNo se puede mostrar vista previa")
            self.pdf_preview_label.setStyleSheet("""
                QLabel {
                    background: rgba(254,226,226,0.1);
                    border: 2px dashed rgba(239,68,68,0.3);
                    color: rgba(239,68,68,0.8);
                }
            """)
        
        except Exception as e:
            # Error al renderizar
            self.pdf_preview_label.setText(f"❌ Error al cargar PDF:\n{str(e)}")
            self.pdf_preview_label.setStyleSheet("""
                QLabel {
                    background: rgba(254,226,226,0.1);
                    border: 2px dashed rgba(239,68,68,0.3);
                    color: rgba(239,68,68,0.8);
                }
            """)
    
    def _hover_zoom(self, event):
        """Muestra zoom en tiempo real siguiendo el cursor del mouse."""
        if not self.original_pdf_pixmap:
            return
        
        # Obtener posición del cursor relativa al label
        pos = event.pos()
        label_size = self.pdf_preview_label.size()
        
        # Calcular la posición correspondiente en la imagen original
        current_pixmap = self.pdf_preview_label.pixmap()
        if not current_pixmap:
            return
        
        # Escalar coordenadas del cursor a coordenadas de la imagen original
        scale_x = self.original_pdf_pixmap.width() / current_pixmap.width()
        scale_y = self.original_pdf_pixmap.height() / current_pixmap.height()
        
        orig_x = int(pos.x() * scale_x)
        orig_y = int(pos.y() * scale_y)
        
        # Usar el tamaño de región variable (ajustable con rueda del mouse)
        region_size = int(self.zoom_region_size)
        
        # Calcular rectángulo de la región a ampliar
        x1 = max(0, orig_x - region_size // 2)
        y1 = max(0, orig_y - region_size // 2)
        x2 = min(self.original_pdf_pixmap.width(), x1 + region_size)
        y2 = min(self.original_pdf_pixmap.height(), y1 + region_size)
        
        # Ajustar si estamos cerca de los bordes
        if x2 - x1 < region_size:
            x1 = max(0, x2 - region_size)
        if y2 - y1 < region_size:
            y1 = max(0, y2 - region_size)
        
        # Extraer región de la imagen original
        zoomed_region = self.original_pdf_pixmap.copy(x1, y1, x2 - x1, y2 - y1)
        
        # Escalar la región al tamaño del label para mostrar zoom
        zoomed_pixmap = zoomed_region.scaled(
            label_size.width(),
            label_size.height(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )
        
        # Mostrar imagen ampliada
        self.pdf_preview_label.setPixmap(zoomed_pixmap)
    
    def _reset_zoom(self):
        """Restaura la vista normal cuando el mouse sale del área."""
        if not self.original_pdf_pixmap:
            return
        
        # Volver a mostrar la imagen completa escalada
        scaled_pixmap = self.original_pdf_pixmap.scaled(
            self.pdf_preview_label.minimumWidth() - 20,
            self.pdf_preview_label.minimumHeight() - 20,
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )
        
        self.pdf_preview_label.setPixmap(scaled_pixmap)
    
    def _adjust_zoom_level(self, event):
        """Ajusta el nivel de zoom con la rueda del mouse."""
        if not self.original_pdf_pixmap:
            return
        
        # Obtener dirección del scroll
        delta = event.angleDelta().y()
        
        # Ajustar tamaño de región (scroll up = más zoom = región más pequeña)
        # Incremento aumentado de 10 a 15 para cambios más rápidos
        if delta > 0:
            # Scroll hacia arriba → Más zoom (región más pequeña)
            self.zoom_region_size = max(self.min_zoom_region, self.zoom_region_size - 15)
        else:
            # Scroll hacia abajo → Menos zoom (región más grande)
            self.zoom_region_size = min(self.max_zoom_region, self.zoom_region_size + 15)
        
        # Redibujar zoom con el nuevo nivel
        self._hover_zoom(event)
    
    def _open_full_pdf(self):
        """Abre el PDF completo en el visor del sistema."""
        import os
        import subprocess
        
        try:
            if os.path.exists(self.pdf_path):
                # Windows
                if os.name == 'nt':
                    os.startfile(self.pdf_path)
                # macOS
                elif os.name == 'posix' and os.uname().sysname == 'Darwin':
                    subprocess.call(['open', self.pdf_path])
                # Linux
                else:
                    subprocess.call(['xdg-open', self.pdf_path])
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "PDF no encontrado",
                    f"El archivo PDF no existe:\n{self.pdf_path}"
                )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"No se pudo abrir el PDF:\n{str(e)}"
            )
