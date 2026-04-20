from window import main_window
import Editor.prod.data.style as style
import Editor.prod.data.prefers_manager as pm #load_config
import Editor.prod.data.names as names
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

global_app = None


if __name__ == "__main__":

    from PySide6.QtCore import qInstallMessageHandler, QtMsgType

    def silence_qthread_warning(mode, context, message):
        if "QThread: Destroyed while thread" in str(message):
            return  # подавляем
        # Остальные сообщения выводим
        sys.stderr.write(f"{message}\n")

    qInstallMessageHandler(silence_qthread_warning)

    app = QApplication(sys.argv)
    global_app = app
    style.load_font()
    # Устанавливаем стиль
    app.setStyle("Fusion")
    style.app = app
    preset = pm.load_config()
    names.set_language(preset["client_language"])

    # app.setStyle("windowsvista")
    # app.setStyle("windows11")
    # app.setStyle("Windows")

    window = main_window.MainWindow()
    window.show()

    sys.exit(app.exec())
