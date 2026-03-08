from PySide6.QtCore import QObject, Signal


class SignalBus(QObject):
    changed = Signal(str)
    update_display = Signal()

    def __init__(self):  # ✅ Двойные подчёркивания!
        super().__init__()  # ✅ Двойные подчёркивания!


signal = SignalBus()