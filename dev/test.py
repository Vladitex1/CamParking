import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QWidget, QVBoxLayout,
    QLabel, QPushButton, QHBoxLayout, QTextEdit
)
from PySide6.QtCore import Qt
import qtawesome as qta

# ---------- Кастомный заголовок для док-окна ----------
class DockTitleBar(QWidget):
    def __init__(self, title, dock_widget):
        super().__init__(dock_widget)
        self.dock = dock_widget
        self.setObjectName("dockTitleBar")
        self.setFixedHeight(32)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(4)

        self.label = QLabel(title)
        self.label.setObjectName("dockTitleLabel")
        layout.addWidget(self.label)
        layout.addStretch()

        self.float_btn = QPushButton()
        self.float_btn.setObjectName("dockFloatBtn")
        self.float_btn.setFixedSize(24, 24)
        self.float_btn.clicked.connect(self.toggle_float)
        layout.addWidget(self.float_btn)

        self.close_btn = QPushButton()
        self.close_btn.setObjectName("dockCloseBtn")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.clicked.connect(self.dock.close)
        layout.addWidget(self.close_btn)

        # Изначально установим иконки (цвет будет обновлён позже)
        self.update_theme("#CCD0CF")  # цвет по умолчанию

    def toggle_float(self):
        self.dock.setFloating(not self.dock.isFloating())

    def update_theme(self, color_hex):
        self.float_btn.setIcon(qta.icon('mdi.chevron-down', color=color_hex))
        self.close_btn.setIcon(qta.icon('mdi.close', color=color_hex))

# ---------- Главное окно ----------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест кастомных док-окон")
        self.resize(800, 600)

        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.addWidget(QLabel("Центральная область"))
        layout.addWidget(QTextEdit("Здесь можно писать текст..."))

        # Создаём два док-окна
        self.create_dock("Инструменты", Qt.LeftDockWidgetArea)
        self.create_dock("Свойства", Qt.RightDockWidgetArea)

        # Кнопка переключения темы
        theme_btn = QPushButton("Переключить тему")
        theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(theme_btn)

        # Начальная тема (тёмная)
        self.current_theme = "dark"
        self.apply_theme()

    def create_dock(self, title, area):
        dock = QDockWidget(title, self)   # стандартный заголовок будет скрыт
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # Содержимое док-окна
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.addWidget(QLabel(f"Содержимое {title}"))
        dock.setWidget(content)

        # Устанавливаем кастомный заголовок
        dock.setTitleBarWidget(DockTitleBar(title, dock))

        self.addDockWidget(area, dock)

    def toggle_theme(self):
        if self.current_theme == "dark":
            self.current_theme = "light"
        else:
            self.current_theme = "dark"
        self.apply_theme()

    def apply_theme(self):
        # Определяем цвета для темы
        if self.current_theme == "dark":
            main_bg = "#1e1e1e"
            dock_bg = "#2d2d2d"
            text_color = "#ffffff"
        else:
            main_bg = "#f0f0f0"
            dock_bg = "#ffffff"
            text_color = "#000000"

        # Глобальный стиль для виджетов
        style = f"""
        QMainWindow {{
            background-color: {main_bg};
        }}
        QDockWidget {{
            background-color: {dock_bg};
        }}
        #dockTitleBar {{
            background-color: {dock_bg};
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
        }}
        #dockTitleLabel {{
            color: {text_color};
            font-weight: bold;
        }}
        #dockFloatBtn, #dockCloseBtn {{
            background-color: transparent;
            border: none;
            border-radius: 4px;
            qproperty-iconSize: 20px 20px;
        }}
        #dockFloatBtn:hover, #dockCloseBtn:hover {{
            background-color: rgba(128, 128, 128, 0.3);
        }}
        #dockFloatBtn:pressed, #dockCloseBtn:pressed {{
            background-color: rgba(128, 128, 128, 0.5);
        }}
        QLabel {{
            color: {text_color};
        }}
        QPushButton {{
            background-color: {dock_bg};
            color: {text_color};
            border: 1px solid #aaa;
            border-radius: 4px;
            padding: 4px 8px;
        }}
        """
        self.setStyleSheet(style)

        # Обновляем иконки в заголовках док-окон
        for dock in self.findChildren(QDockWidget):
            title_bar = dock.titleBarWidget()
            if isinstance(title_bar, DockTitleBar):
                title_bar.update_theme(text_color)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())