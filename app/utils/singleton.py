from PySide6 import QtCore

class SingleInstance:
    def __init__(self, key: str):
        self.key = key
        self.shared = QtCore.QSharedMemory(self.key)

    def try_lock(self) -> bool:
        if self.shared.attach():
            self.shared.detach()
            return False
        if not self.shared.create(1):
            return False
        return True
