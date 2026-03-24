from PySide6.QtCore import QObject, Signal


class SignalBus(QObject):
    changed = Signal(str)
    update_display = Signal()
    fast_nav_changed = Signal(bool)

    def __init__(self):  # ✅ Двойные подчёркивания!
        super().__init__()  # ✅ Двойные подчёркивания!


signal = SignalBus()