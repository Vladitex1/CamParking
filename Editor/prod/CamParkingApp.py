import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QAction, QImage
from window import main_window
import numpy as np
import Editor.prod.data.style as style

if __name__ == "__main__":
    # Включить High DPI масштабирование (часто включено по умолчанию в Qt6)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # Использовать иконки высокого разрешения, если они есть
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    style.load_font()
    # Устанавливаем стиль
    app.setStyleSheet(style.STYLESHEET)

    #app.setStyle("Fusion")
    #app.setStyle("windowsvista")
    app.setStyle("windows11")
    #app.setStyle("Windows")

    window = main_window.MainWindow()
    window.show()

    sys.exit(app.exec())