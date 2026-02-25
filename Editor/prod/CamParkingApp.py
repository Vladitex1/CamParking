from window import main_window
import Editor.prod.data.style as style
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

if __name__ == "__main__":

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