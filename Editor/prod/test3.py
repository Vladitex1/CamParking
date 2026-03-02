import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtGui import QUndoCommand, QUndoStack

class ChangeTextCommand(QUndoCommand):
    def __init__(self, label, new_text):
        super().__init__()
        self.label = label
        self.new_text = new_text
        self.old_text = label.text()

    def redo(self):
        self.label.setText(self.new_text)

    def undo(self):
        self.label.setText(self.old_text)

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Undo/Redo Test")
        layout = QVBoxLayout(self)

        self.label = QLabel("Исходный текст")
        layout.addWidget(self.label)

        self.undo_stack = QUndoStack(self)

        btn_change = QPushButton("Изменить текст")
        btn_change.clicked.connect(self.change_text)
        layout.addWidget(btn_change)

        btn_undo = QPushButton("Undo")
        btn_undo.clicked.connect(self.undo_stack.undo)
        layout.addWidget(btn_undo)

        btn_redo = QPushButton("Redo")
        btn_redo.clicked.connect(self.undo_stack.redo)
        layout.addWidget(btn_redo)

    def change_text(self):
        cmd = ChangeTextCommand(self.label, "Новый текст")
        self.undo_stack.push(cmd)

if __name__ == "__main__":
    app = QApplication(sys.argv)          # ← обязательно сначала
    window = TestWindow()                  # ← потом создаём окно
    window.show()
    sys.exit(app.exec())