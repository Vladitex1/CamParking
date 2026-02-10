from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

class ToolsPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        layout.addWidget(QPushButton("Режим маски"))
        layout.addWidget(QPushButton("Детекция"))
        layout.addWidget(QPushButton("Очистить"))
        layout.addStretch()
