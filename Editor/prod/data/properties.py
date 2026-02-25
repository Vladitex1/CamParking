
import qtawesome as qta
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPalette, QColor
from ..data import style  # путь к твоему style.py (возможно, надо скорректировать)


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
        self.toggle_float_bool: bool = False
        self.setObjectName("dockTitleBar") #Назначение стиля для объекта
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True) # Разрешаем рисование фона через стили

        # Основной layout (Панель где располагаются лейбл и кнопки)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 8, 0)
        layout.setSpacing(4)

        # Заголовок слева
        self.label = QLabel(title)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.label)

        # Растяжка, прижимающая кнопки вправо
        layout.addStretch()

        self.buttons = [
            ("dock_float_button",self.toggle_float,"mdi.chevron-down"),
            ("dock_close_button",self.dock.close,"mdi.close"),
        ]

        self.button_icons= []
        for name,action,icon in self.buttons:
            button = QPushButton()
            button.clicked.connect(action)
            button.setProperty("button", "dock")
            layout.addWidget(button)

            self.button_icons.append([button,icon])

        # Устанавливаем иконки в соответствии с текущей темой

        self.update_theme()

    def toggle_float(self):
        """Переключает плавающий/закреплённый режим."""
        self.dock.setFloating(not self.dock.isFloating())
        color_hex = style.STYLE[style.current_color]["text_color"]
        x = self.button_icons[0][0]
        match self.toggle_float_bool:
            case True:
                x.setIcon(qta.icon("mdi.chevron-down", color=color_hex))
            case False:
                x.setIcon(qta.icon("mdi.chevron-up", color=color_hex))

        self.toggle_float_bool = not self.toggle_float_bool

    def update_theme(self):
        color_hex = style.STYLE[style.current_color]["text_color"]
        for i in range(len(self.button_icons)):
            x = self.button_icons[i]
            x[0].setIcon(qta.icon(x[1], color=color_hex))
            x[0].setIconSize(QSize(5, 5))