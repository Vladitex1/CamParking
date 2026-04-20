import sys
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import QThread, QTimer
import qtawesome as qta

class AsyncIconThread(QThread):
    def run(self):
        # Эмулируем долгую загрузку иконок в фоне
        for i in range(5):
            time.sleep(1)
            # Просто дергаем библиотеку, чтобы создать нагрузку
            icon = qta.icon('mdi6.check-circle')
            print(f"Фоновая загрузка иконки... шаг {i+1}")
        print("Фоновая задача завершена, но поток продолжает висеть.")

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест с ошибкой (qtawesome)")
        self.setGeometry(100, 100, 300, 200)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        btn_start = QPushButton("Запустить фоновую загрузку")
        btn_start.clicked.connect(self.start_async_loading)
        layout.addWidget(btn_start)

    def start_async_loading(self):
        # Поток создается как локальная переменная, ссылка на него не сохраняется.
        # После завершения этого метода объект потока может быть удален,
        # а его рабочий поток продолжит работу, что и вызовет ошибку при закрытии окна.
        self.thread = AsyncIconThread()
        self.thread.start()
        print("Фоновая загрузка запущена, ссылка на поток сохранена.") # Обратите внимание, теперь ссылка есть!

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())