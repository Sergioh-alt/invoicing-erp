from PySide6 import QtCore, QtWidgets, QtGui

class NotificationDialog(QtWidgets.QDialog):
    action_mark_paid = QtCore.Signal(int)
    action_snooze = QtCore.Signal(int, int)

    def __init__(self, factura: dict, title: str, parent=None):
        super().__init__(parent)
        self.factura_id = int(factura["id"])
        
        # Reproducir beep de notificación (siempre)
        from app.utils.sound import play_notification_beep
        play_notification_beep(force=True)  # Force=True para que siempre suene

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(18, 18, 18, 18)

        card = QtWidgets.QFrame()
        card.setObjectName("Card")
        card.setStyleSheet("""
            QFrame#Card {
                background: rgba(15, 26, 47, 0.98);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 22px;
            }
        """)
        v = QtWidgets.QVBoxLayout(card)
        v.setContentsMargins(22, 20, 22, 18)
        v.setSpacing(12)

        h = QtWidgets.QHBoxLayout()
        badge = QtWidgets.QLabel("⚠️")
        badge.setStyleSheet("font-size: 20pt;")
        h.addWidget(badge, 0)

        lab_title = QtWidgets.QLabel(title)
        lab_title.setStyleSheet("font-size: 16pt; font-weight: 950;")
        h.addWidget(lab_title, 1)

        btn_close = QtWidgets.QPushButton("✕")
        btn_close.setFixedSize(40, 40)
        btn_close.setStyleSheet("""
            QPushButton { background: rgba(255,255,255,0.08); border-radius: 12px; font-weight: 900; }
            QPushButton:hover { background: rgba(255,255,255,0.12); }
        """)
        btn_close.clicked.connect(self.close)
        h.addWidget(btn_close, 0)
        v.addLayout(h)

        num = factura.get("numero_factura", "")
        prov = factura.get("proveedor") or "(sin proveedor)"
        notas = factura.get("notas") or "(sin notas)"
        venc = factura.get("pretty_due") or ""

        big = QtWidgets.QLabel(f"Factura #{num}")
        big.setStyleSheet("font-size: 22pt; font-weight: 980;")
        v.addWidget(big)

        row_meta = QtWidgets.QHBoxLayout()
        pill1 = QtWidgets.QLabel(f"Proveedor: {prov}")
        pill1.setStyleSheet("padding: 8px 10px; background: rgba(37,99,235,0.18); border-radius: 12px; font-weight: 900;")
        pill2 = QtWidgets.QLabel(f"Vence: {venc}")
        pill2.setStyleSheet("padding: 8px 10px; background: rgba(22,163,74,0.18); border-radius: 12px; font-weight: 900;")
        row_meta.addWidget(pill1, 1)
        row_meta.addWidget(pill2, 0)
        v.addLayout(row_meta)

        lab_notes_title = QtWidgets.QLabel("NOTAS")
        lab_notes_title.setStyleSheet("font-weight: 950; letter-spacing: 1px; color: rgba(229,231,235,0.70);")
        v.addWidget(lab_notes_title)

        notes_box = QtWidgets.QTextEdit()
        notes_box.setReadOnly(True)
        notes_box.setPlainText(notas)
        notes_box.setMinimumHeight(160)
        notes_box.setStyleSheet("""
            QTextEdit {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 14px;
                padding: 10px;
                font-size: 11pt;
            }
        """)
        v.addWidget(notes_box)

        actions = QtWidgets.QHBoxLayout()
        self.cmb_snooze = QtWidgets.QComboBox()
        self.cmb_snooze.addItem("Posponer 5 min", 5)
        self.cmb_snooze.addItem("Posponer 15 min", 15)
        self.cmb_snooze.addItem("Posponer 30 min", 30)
        self.cmb_snooze.addItem("Posponer 1 hora", 60)
        self.cmb_snooze.setMinimumWidth(210)

        btn_snooze = QtWidgets.QPushButton("Aplicar Snooze")
        btn_snooze.setObjectName("Secondary")
        btn_paid = QtWidgets.QPushButton("Marcar como pagada")

        btn_snooze.clicked.connect(self._do_snooze)
        btn_paid.clicked.connect(self._do_paid)

        actions.addWidget(self.cmb_snooze, 0)
        actions.addWidget(btn_snooze, 0)
        actions.addStretch(1)
        actions.addWidget(btn_paid, 0)
        v.addLayout(actions)

        outer.addWidget(card)

        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 14)
        shadow.setColor(QtGui.QColor(0, 0, 0, 175))
        card.setGraphicsEffect(shadow)

        self.resize(660, 500)
        self._move_bottom_right()
        try:
            QtWidgets.QApplication.beep()
        except Exception:
            pass

    def _move_bottom_right(self):
        screen = QtGui.QGuiApplication.primaryScreen()
        geo = screen.availableGeometry()
        x = geo.x() + geo.width() - self.width() - 28
        y = geo.y() + geo.height() - self.height() - 28
        self.move(x, y)

    def _do_paid(self):
        self.action_mark_paid.emit(self.factura_id)
        self.close()

    def _do_snooze(self):
        minutes = int(self.cmb_snooze.currentData())
        self.action_snooze.emit(self.factura_id, minutes)
        self.close()
