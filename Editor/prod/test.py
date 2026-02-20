from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, QPoint

class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(40)  # высота заголовка

        # Layout для заголовка
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)

        # Заголовок (можно использовать QLabel)
        self.title_label = QLabel("Моё приложение")
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.title_label)

        layout.addStretch()  # растяжка, чтобы кнопки были справа

        # Кнопка "Свернуть"
        self.minimize_btn = QPushButton("—")
        self.minimize_btn.setFixedSize(40, 30)
        self.minimize_btn.clicked.connect(self.parent.showMinimized)
        layout.addWidget(self.minimize_btn)

        # Кнопка "Развернуть/Восстановить"
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setFixedSize(40, 30)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        layout.addWidget(self.maximize_btn)

        # Кнопка "Закрыть"
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(40, 30)
        self.close_btn.clicked.connect(self.parent.close)
        layout.addWidget(self.close_btn)

        # Переменные для перетаскивания окна
        self.drag_pos = QPoint()

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.maximize_btn.setText("□")
        else:
            self.parent.showMaximized()
            self.maximize_btn.setText("❐")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.parent.move(self.parent.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()

    def mouseDoubleClickEvent(self, event):
        self.toggle_maximize()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)  # убираем системную рамку

        # Создаём свой заголовок
        self.title_bar = CustomTitleBar(self)

        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)

        # Layout для всего окна (заголовок + содержимое)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Добавляем заголовок
        main_layout.addWidget(self.title_bar)

        # Содержимое окна (ваш интерфейс)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.addWidget(QLabel("Основной контент"))
        main_layout.addWidget(content)

        # Применяем тему (например, ваш STYLESHEET_STUDY)
        self.setStyleSheet(style.STYLESHEET_STUDY)