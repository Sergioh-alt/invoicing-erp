from PySide6 import QtCore, QtWidgets, QtGui
from datetime import datetime
from app.utils.windows_styles import apply_dark_title_bar

class InvoiceDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, *, title="Nueva factura", data=None):
        super().__init__(parent)
        self.setWindowTitle("")
        self.setModal(True)
        self.setMinimumWidth(600)

        self._data = data or {}

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        form = QtWidgets.QFormLayout()
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)

        self.in_num = QtWidgets.QLineEdit(self._data.get("numero_factura", ""))
        
        # Proveedor con limitación visual
        self.in_prov = QtWidgets.QLineEdit(self._data.get("proveedor", "") or "")
        self.in_prov.setMaxLength(100)  # Límite de caracteres
        
        # Crear una fuente más pequeña para proveedor si es muy largo
        proveedor_text = self._data.get("proveedor", "") or ""
        if len(proveedor_text) > 30:
            # Si es muy largo, mostrarlo en tooltip
            self.in_prov.setToolTip(proveedor_text)
            # Mostrar solo primeros 30 caracteres + "..."
            self.in_prov.setText(proveedor_text[:30] + "...")
            # Al hacer foco, mostrar todo
            self.in_prov.focusInEvent = lambda e: (self.in_prov.setText(proveedor_text), QtWidgets.QLineEdit.focusInEvent(self.in_prov, e))
            self.in_prov.focusOutEvent = lambda e: (self.in_prov.setText(proveedor_text[:30] + "..." if len(self.in_prov.text()) > 30 else self.in_prov.text()), QtWidgets.QLineEdit.focusOutEvent(self.in_prov, e))

        self.in_val = QtWidgets.QDoubleSpinBox()
        self.in_val.setMaximum(10_000_000_000)
        self.in_val.setDecimals(2)
        self.in_val.setValue(float(self._data.get("valor") or 0.0))
        self.in_val.setPrefix("$ ")

        # Notas con altura fija más pequeña
        self.in_notes = QtWidgets.QTextEdit(self._data.get("notas", "") or "")
        self.in_notes.setFixedHeight(60)  # Reducido de 110 a 60
        self.in_notes.setPlaceholderText("Notas adicionales (opcionales)...")

        self.dt = QtWidgets.QDateTimeEdit()
        self.dt.setCalendarPopup(True)
        self.dt.setDisplayFormat("dd/MM/yyyy hh:mm AP")
        self.dt.setTimeSpec(QtCore.Qt.LocalTime)

        if self._data.get("fecha_vencimiento"):
            try:
                d = datetime.fromisoformat(self._data["fecha_vencimiento"])
                self.dt.setDateTime(QtCore.QDateTime(d))
            except Exception:
                self.dt.setDateTime(QtCore.QDateTime.currentDateTime())
        else:
            self.dt.setDateTime(QtCore.QDateTime.currentDateTime().addDays(1))

        self.cmb_estado = QtWidgets.QComboBox()
        self.cmb_estado.addItems(["Pendiente", "Pagada"])
        self.cmb_estado.setCurrentText(self._data.get("estado", "Pendiente"))

        self.t1 = QtWidgets.QTimeEdit()
        self.t2 = QtWidgets.QTimeEdit()
        self.t3 = QtWidgets.QTimeEdit()
        for t in (self.t1, self.t2, self.t3):
            t.setDisplayFormat("HH:mm")

        self.t1.setTime(QtCore.QTime(9, 0))
        self.t2.setTime(QtCore.QTime(14, 0))
        self.t3.setTime(QtCore.QTime(18, 0))

        if self._data.get("hora_alerta_1"):
            self.t1.setTime(QtCore.QTime.fromString(self._data["hora_alerta_1"], "HH:mm"))
        if self._data.get("hora_alerta_2"):
            self.t2.setTime(QtCore.QTime.fromString(self._data["hora_alerta_2"], "HH:mm"))
        if self._data.get("hora_alerta_3"):
            self.t3.setTime(QtCore.QTime.fromString(self._data["hora_alerta_3"], "HH:mm"))

        hours_row = QtWidgets.QHBoxLayout()
        hours_row.addWidget(QtWidgets.QLabel("H1"))
        hours_row.addWidget(self.t1)
        hours_row.addSpacing(10)
        hours_row.addWidget(QtWidgets.QLabel("H2"))
        hours_row.addWidget(self.t2)
        hours_row.addSpacing(10)
        hours_row.addWidget(QtWidgets.QLabel("H3"))
        hours_row.addWidget(self.t3)
        hours_wrap = QtWidgets.QWidget()
        hours_wrap.setLayout(hours_row)

        form.addRow("Número de factura *", self.in_num)
        form.addRow("Proveedor", self.in_prov)
        form.addRow("Valor", self.in_val)
        form.addRow("Vencimiento (fecha y hora) *", self.dt)
        form.addRow("Horarios (Día 0) — 3 avisos", hours_wrap)
        form.addRow("Estado", self.cmb_estado)
        form.addRow("Notas", self.in_notes)

        layout.addLayout(form)

        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch(1)
        b_cancel = QtWidgets.QPushButton("Cancelar")
        b_cancel.setObjectName("Secondary")
        b_ok = QtWidgets.QPushButton("Guardar")
        b_ok.clicked.connect(self._validate_accept)
        b_cancel.clicked.connect(self.reject)
        buttons.addWidget(b_cancel)
        buttons.addWidget(b_ok)
        layout.addLayout(buttons)

    def _validate_accept(self):
        """Valida todos los campos antes de aceptar el diálogo."""
        # 1. Validar número de factura no vacío
        numero = self.in_num.text().strip()
        if not numero:
            QtWidgets.QMessageBox.warning(
                self, 
                "Falta información", 
                "Debes ingresar el número de factura."
            )
            return
        
        # 2. Validar largo del número de factura (no más de 50 caracteres)
        if len(numero) > 50:
            QtWidgets.QMessageBox.warning(
                self, 
                "Número muy largo", 
                "El número de factura no puede exceder 50 caracteres."
            )
            return
        
        # 3. Detectar duplicados
        if hasattr(self.parent(), 'db'):
            db = self.parent().db
            # Si estamos editando, excluir el ID actual de la búsqueda de duplicados
            exclude_id = self._data.get("id") if self._data else None
            
            if db.check_duplicate_invoice(numero, exclude_id):
                reply = QtWidgets.QMessageBox.warning(
                    self,
                    "Factura Duplicada",
                    f"Ya existe una factura con el número '{numero}'.\n\n"
                    "¿Deseas continuar de todas formas?",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.No
                )
                if reply == QtWidgets.QMessageBox.No:
                    return
        
        # 4. Validar valor (debe ser positivo)
        valor = self.in_val.value()
        if valor <= 0:
            QtWidgets.QMessageBox.warning(
                self,
                "Valor inválido",
                "El valor de la factura debe ser mayor a cero."
            )
            return
        
        # 5. Validar valor no sea excesivo (límite razonable: 1 billón)
        if valor > 1_000_000_000:
            reply = QtWidgets.QMessageBox.warning(
                self,
                "Valor muy alto",
                f"El valor de ${valor:,.2f} parece inusualmente alto.\n\n"
                "¿Es correcto este monto?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            if reply == QtWidgets.QMessageBox.No:
                return
        
        # 6. Validar fecha no esté muy lejos en el futuro (máx 10 años)
        fecha = self.dt.dateTime().toPython()
        max_fecha = datetime.now().replace(year=datetime.now().year + 10)
        
        if fecha > max_fecha:
            QtWidgets.QMessageBox.warning(
                self,
                "Fecha inválida",
                "La fecha de vencimiento no puede ser más de 10 años en el futuro."
            )
            return
        
        # 7. Advertir si fecha está en el pasado (permitir pero advertir)
        if fecha < datetime.now():
            reply = QtWidgets.QMessageBox.question(
                self,
                "Fecha en el pasado",
                "La fecha de vencimiento está en el pasado.\n\n"
                "¿Deseas continuar?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.Yes
            )
            if reply == QtWidgets.QMessageBox.No:
                return
        
        # 8. Validar proveedor (si está presente, no exceder 100 caracteres)
        proveedor = self.in_prov.text().strip()
        if len(proveedor) > 100:
            QtWidgets.QMessageBox.warning(
                self,
                "Proveedor muy largo",
                "El nombre del proveedor no puede exceder 100 caracteres."
            )
            return
        
        # Todas las validaciones pasaron
        self.accept()

    def get_payload(self) -> dict:
        """Retorna los datos del formulario, con sanitización de inputs."""
        dt = self.dt.dateTime().toPython().replace(microsecond=0)
        
        # Sanitizar textos (remover espacios extras, caracteres de control)
        def sanitize_text(text: str) -> str:
            """Limpia texto removiendo caracteres de control y espacios extras."""
            if not text:
                return ""
            # Remover caracteres de control
            cleaned = ''.join(char for char in text if char.isprintable() or char in '\n\r\t')
            # Normalizar espacios
            cleaned = ' '.join(cleaned.split())
            return cleaned.strip()
        
        return {
            "numero_factura": sanitize_text(self.in_num.text()),
            "proveedor": sanitize_text(self.in_prov.text()),
            "valor": float(self.in_val.value()),
            "notas": sanitize_text(self.in_notes.toPlainText()),
            "fecha_vencimiento": dt.isoformat(),
            "estado": self.cmb_estado.currentText(),
            "hora_alerta_1": self.t1.time().toString("HH:mm"),
            "hora_alerta_2": self.t2.time().toString("HH:mm"),
            "hora_alerta_3": self.t3.time().toString("HH:mm"),
        }

    def showEvent(self, event: QtGui.QShowEvent):
        """Aplica barra de título oscura al mostrarse."""
        super().showEvent(event)
        apply_dark_title_bar(self)
