from PySide6 import QtWidgets, QtGui, QtCore

class TrayManager(QtCore.QObject):
    open_requested = QtCore.Signal()
    exit_requested = QtCore.Signal()

    def __init__(self, icon: QtGui.QIcon, parent=None):
        super().__init__(parent)
        self.tray = QtWidgets.QSystemTrayIcon()
        self.tray.setIcon(icon)
        self.tray.setToolTip("Facturas GanaTodo (segundo plano)")

        menu = QtWidgets.QMenu()
        act_open = menu.addAction("Abrir Facturas GanaTodo")
        act_exit = menu.addAction("Salir completamente")
        act_open.triggered.connect(self.open_requested.emit)
        act_exit.triggered.connect(self.exit_requested.emit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_activated)
        self.tray.show()

    def _on_activated(self, reason):
        if reason in (QtWidgets.QSystemTrayIcon.DoubleClick, QtWidgets.QSystemTrayIcon.Trigger):
            self.open_requested.emit()

    def show_info(self, title: str, message: str, timeout_ms: int = 2500):
        try:
            self.tray.showMessage(title, message, QtWidgets.QSystemTrayIcon.Information, timeout_ms)
        except Exception:
            pass
