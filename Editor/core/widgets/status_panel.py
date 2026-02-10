from PySide6.QtWidgets import QWidget, QTextEdit, QVBoxLayout

class StatusPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        layout.addWidget(self.log)

    def add_message(self, text):
        self.log.append(text)
