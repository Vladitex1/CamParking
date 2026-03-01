import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFrame, QColorDialog
from PySide6.QtCore import Qt

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Выбор цвета")
window.resize(300, 200)

layout = QVBoxLayout(window)

# Квадрат для отображения цвета
color_box = QFrame()
color_box.setFixedSize(100, 100)
color_box.setStyleSheet("background-color: #000000;")
layout.addWidget(color_box, alignment=Qt.AlignCenter)

# Текущий цвет храним как атрибут окна
window.current_color = "#000000"

def choose_color(event):
    color = QColorDialog.getColor()
    if color.isValid():
        window.current_color = color.name()
        color_box.setStyleSheet(f"background-color: {window.current_color};")

# Клик по квадрату открывает диалог
color_box.mousePressEvent = choose_color

# Кнопка копирования
copy_btn = QPushButton("Копировать цвет")
def copy_color():
    QApplication.clipboard().setText(window.current_color)
copy_btn.clicked.connect(copy_color)
layout.addWidget(copy_btn)

window.show()
sys.exit(app.exec())