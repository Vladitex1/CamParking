import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QAction, QImage
import Editor.prod.data.style as style
from Editor.prod.data.signal_bus import signal
import Editor.prod.data.global_var as global_var
from Editor.prod.data.names import NAMES,get_language,change_language
from Editor.prod.window import editor_window, connect_window, settings_window
import qtawesome as qta

class StartWindow(QWidget):
    """Первая страница с текстом и кнопкой"""

    def __init__(self):
        super().__init__()
        self.name = NAMES[get_language()]
        self.icons=[]
        # Создаем элементы
        self.create_layout()
        signal.theme_changed.connect(self.update_icons)
        self.update_icons()

    def update_icons(self):
        for button,icon_path,scale in self.icons:
            icon = qta.icon(icon_path, color=style.STYLE[style.current_color]["text_color"],
                            options=[{'scale_factor': scale, 'color_disabled': style.STYLE[style.current_color]["text_color"]}])
            button.setIcon(icon)

    def create_layout(self):
        # Заголовки
        top_labels_layout = QVBoxLayout()
        title_label = QLabel(f"{self.name['start.title']}"+"\n")
        title_label.setStyleSheet(f'font-size: {style.STYLE["global"]["font_size_h2"]}; font-weight: bold;')

        info_label = QLabel(f"{self.name['start.about']}"+"\n\n")
        info_label.setStyleSheet(f'font-size: {style.STYLE["global"]["font_size_h3"]};')
        top_labels_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        top_labels_layout.addWidget(info_label, alignment=Qt.AlignCenter)

        # Горизонтальное центрирование заголовков
        h_center_labels = QHBoxLayout()
        h_center_labels.addStretch()
        h_center_labels.addLayout(top_labels_layout)
        h_center_labels.addStretch()

        # Основной вертикальный layout
        main_layout = QVBoxLayout()
        main_layout.addSpacing(50)                     # фиксированный отступ сверху
        main_layout.addLayout(h_center_labels)         # заголовки по центру

        # --- Контейнер для кнопок с центрированием ---
        self.TopButtons_Layout = QHBoxLayout()
        self.TopButtons_Layout.setSpacing(30)          # расстояние между кнопками (не слева/справа)
        self.create_navigation_buttons()               # добавляем кнопки в self.TopButtons_Layout

        # Горизонтальная обёртка для центрирования блока кнопок
        buttons_wrapper = QHBoxLayout()
        buttons_wrapper.addStretch()
        buttons_wrapper.addLayout(self.TopButtons_Layout)
        buttons_wrapper.addStretch()

        main_layout.addLayout(buttons_wrapper)         # кнопки по центру

        down_layout = QHBoxLayout()
        version_num_label = QLabel(f"Ver.{global_var.program_version}")
        down_layout.addStretch()
        down_layout.addWidget(version_num_label)


        main_layout.addStretch()                       # пружина снизу
        main_layout.addLayout(down_layout)


        self.setLayout(main_layout)


    def create_navigation_buttons(self):
        self.menus = [
            [f"{self.name['menu.navigate.editor']}", lambda: signal.menu_switch_request.emit(1), "mdi6.image-edit", 1.1],
            [f"{self.name['menu.navigate.connect']}", lambda: signal.menu_switch_request.emit(2), "mdi6.camera-wireless", 1.1],
            [f"{self.name['menu.parameters.settings']}", lambda: signal.menu_switch_request.emit(3), "mdi6.cog", 1.1],
        ]

        for name, window, icon, size in self.menus:
            button = QToolButton()
            if name:
                button.setText(name)
                button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

            self.icons.append((button, icon, size))
            button.clicked.connect(window)
            button.setProperty("button", "st_start")
            self.TopButtons_Layout.addWidget(button)






if __name__ == "__main__":
    app = QApplication(sys.argv)
    global_app = app
    app.setStyle("Fusion")

    window = StartWindow()

    # --- Блок перемещения на второй монитор ---
    screens = app.screens()
    if len(screens) > 1:
        # Индекс 1 — это обычно второй монитор.
        # Если он слева от основного, попробуйте индекс 1 или 0 в зависимости от системных настроек.
        target_screen = screens[1]
        screen_geometry = target_screen.availableGeometry()

        # Перемещаем окно в верхний левый угол второго экрана
        window.move(screen_geometry.topLeft())
    # ------------------------------------------

    window.show()
    sys.exit(app.exec())





