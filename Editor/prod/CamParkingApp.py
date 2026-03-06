from window import main_window
import Editor.prod.data.style as style
import Editor.prod.data.prefers_manager as pm
import Editor.prod.data.names as names
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

global_app = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    global_app = app
    style.load_font()
    # Устанавливаем стиль
    app.setStyle("Fusion")
    style.app = app
    theme, language = pm.load_config()
    names.set_language(language)
    style.load_theme(theme)

    # app.setStyle("windowsvista")
    # app.setStyle("windows11")
    # app.setStyle("Windows")

    window = main_window.MainWindow()
    window.show()

    sys.exit(app.exec())
