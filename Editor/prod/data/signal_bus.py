from PySide6.QtCore import QObject, Signal


class SignalBus(QObject):
    theme_changed = Signal(str)
    update_display = Signal()
    fast_nav_changed = Signal(bool)
    menu_switch_request = Signal(int)
    camera_thread_end_request = Signal(bool)
    camera_ready = Signal(bool)


    def __init__(self):  # ✅ Двойные подчёркивания!
        super().__init__()  # ✅ Двойные подчёркивания!


signal = SignalBus()