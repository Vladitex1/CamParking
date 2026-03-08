
import qtawesome as qta
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QPalette, QColor
from ..data import style  # путь к твоему style.py (возможно, надо скорректировать)
from Editor.prod.data.signal_bus import signal




class DockTitleBar(QWidget):
    """
    Кастомный заголовок для QDockWidget.
    Содержит:
    - надпись с названием
    - кнопку "плавать/закрепить" (иконка mdi.chevron-down)
    - кнопку "закрыть" (иконка mdi.close)
    Иконки меняют цвет в зависимости от текущей темы (style.current_color).
    """

    def __init__(self, title: str, dock_widget):
        super().__init__(dock_widget)
        self.dock = dock_widget
        self.toggle_float_bool = False

        # Главный layout для всего заголовка (без отступов)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, int(style.STYLE["global"]["style_margin"].replace("px","")), 0, 0)
        main_layout.setSpacing(0)

        # Виджет, который будет фоном и содержать кнопки
        texture = QWidget(self)  # родитель — сам заголовок
        texture.setProperty("dock", "title")  # ключевое свойство для стиля
        main_layout.addWidget(texture)

        # Layout для содержимого texture
        layout = QHBoxLayout(texture)
        layout.setContentsMargins(20, 4, 8, 4)  # отступы: слева 20, справа 8
        layout.setSpacing(4)

        # Заголовок слева
        label = QLabel(title)
        label.setProperty("dock", "title")
        label.setStyleSheet(f"font-size: {style.STYLE["global"]["font_size_h2"]}; font-weight: bold;")
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(label)

        # Растяжка, прижимающая кнопки вправо
        layout.addStretch()

        # Кнопки
        self.buttons = [
            ("Открепить окно", self.on_toggle_clicked, "mdi6.dock-window"),
            ("Закрыть окно", self.on_close_clicked, "mdi6.window-close"),
        ]
        self.button_icons = []
        for name, action, icon in self.buttons:
            button = QPushButton()
            button.clicked.connect(action)
            button.setToolTip(name)
            button.setProperty("button", "dock")  # свойство для стилизации кнопок
            layout.addWidget(button)
            self.button_icons.append([button, icon])

        # Устанавливаем иконки
        signal.changed.connect(self.update_theme)
        self.update_theme()

    def on_toggle_clicked(self):
        print("🟡 on_toggle_clicked вызван")
        self.toggle_float()
        QTimer.singleShot(50, lambda: (
            print("⏰ Тест эмиссии через 1 секунду"),
            signal.update_display.emit()
        ))
        print("🟡 signal.update_display.emit() выполнен")

    def on_close_clicked(self):
        self.dock.close()
        print("🟡 on_close_clicked вызван")
        QTimer.singleShot(50, lambda: (
            print("⏰ Тест эмиссии через 1 секунду"),
            signal.update_display.emit()
        ))
        #signal.update_display.emit()
        print("🟡 signal.update_display.emit() выполнен")


    def toggle_float(self):
        """Переключает плавающий/закреплённый режим."""
        self.dock.setFloating(not self.dock.isFloating())

    def update_theme(self):
        color_hex = style.STYLE[style.current_color]["text_color"]
        for i in range(len(self.button_icons)):
            x = self.button_icons[i]
            x[0].setIcon(qta.icon(x[1], color=color_hex))


