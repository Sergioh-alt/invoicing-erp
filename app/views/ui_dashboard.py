from PySide6 import QtWidgets

class KPIWidget(QtWidgets.QFrame):
    def __init__(self, label: str, number: str = "0", *, accent_qss: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("KPI")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        self.lbl_num = QtWidgets.QLabel(number)
        self.lbl_num.setObjectName("KpiNumber")
        if accent_qss:
            self.lbl_num.setStyleSheet(accent_qss)

        self.lbl_label = QtWidgets.QLabel(label)
        self.lbl_label.setObjectName("KpiLabel")

        layout.addWidget(self.lbl_num)
        layout.addWidget(self.lbl_label)
        layout.addStretch(1)

    def set_value(self, n: int):
        self.lbl_num.setText(str(n))
