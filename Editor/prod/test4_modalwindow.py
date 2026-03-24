from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt

class ModalWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Модальный виджет")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)  # блокирует всё приложение
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Dialog)  # чтобы вело себя как диалог
        layout = QVBoxLayout(self)
        btn = QPushButton("Закрыть")
        btn.clicked.connect(self.close)
        layout.addWidget(btn)
        self.resize(300, 200)

# Вызов:
mw = ModalWidget(parent)  # parent - главное окно
mw.show()  # не блокирует выполнение! нужно ждать закрытия