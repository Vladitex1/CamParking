import sys
import numpy as np
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtMultimedia import *
from PySide6.QtCharts import *
import colorsys


class Canvas(QWidget):
    """Холст для рисования"""

    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)

        self.image = QImage(self.size(), QImage.Format_ARGB32)
        self.image.fill(Qt.white)

        self.drawing = False
        self.last_point = QPoint()

        # Настройки кисти
        self.brush_size = 5
        self.brush_color = Qt.black
        self.current_tool = "brush"  # brush, eraser, fill, text, shape

        # История действий для undo/redo
        self.history = []
        self.history_index = -1
        self.max_history = 20

        # Для фигур
        self.start_point = QPoint()
        self.current_shape = "rectangle"  # rectangle, ellipse, line

        # Для текста
        self.text_to_draw = ""
        self.font = QFont("Arial", 24)

        # Эффекты
        self.effect = None

        # Сетка
        self.show_grid = False
        self.grid_size = 20

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Рисуем изображение
        painter.drawImage(self.rect(), self.image, self.image.rect())

        # Рисуем сетку если включена
        if self.show_grid:
            self.draw_grid(painter)

        # Рисуем временную фигуру при рисовании
        if self.drawing and self.current_tool in ["rectangle", "ellipse", "line"]:
            painter.setPen(QPen(self.brush_color, self.brush_size, Qt.SolidLine))
            painter.setBrush(Qt.NoBrush if self.current_tool == "line" else Qt.transparent)

            rect = QRect(self.start_point, self.last_point).normalized()
            if self.current_shape == "rectangle":
                painter.drawRect(rect)
            elif self.current_shape == "ellipse":
                painter.drawEllipse(rect)
            elif self.current_shape == "line":
                painter.drawLine(self.start_point, self.last_point)

    def draw_grid(self, painter):
        """Рисование сетки"""
        painter.setPen(QPen(QColor(200, 200, 200, 50), 1))

        # Вертикальные линии
        for x in range(0, self.width(), self.grid_size):
            painter.drawLine(x, 0, x, self.height())

        # Горизонтальные линии
        for y in range(0, self.height(), self.grid_size):
            painter.drawLine(0, y, self.width(), y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.position().toPoint()
            self.start_point = event.position().toPoint()

            # Сохраняем состояние для undo перед изменением
            if self.current_tool not in ["rectangle", "ellipse", "line"]:
                self.save_to_history()

            # Для заливки
            if self.current_tool == "fill":
                self.flood_fill(self.last_point, self.brush_color)
                self.update()

            # Для текста
            elif self.current_tool == "text":
                text, ok = QInputDialog.getText(self, "Введите текст", "Текст:")
                if ok and text:
                    self.text_to_draw = text
                    painter = QPainter(self.image)
                    painter.setFont(self.font)
                    painter.setPen(QPen(self.brush_color, 1))
                    painter.drawText(self.last_point, self.text_to_draw)
                    painter.end()
                    self.update()

    def mouseMoveEvent(self, event):
        if self.drawing and self.current_tool in ["brush", "eraser"]:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brush_color if self.current_tool == "brush" else Qt.white,
                                self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.last_point, event.position().toPoint())
            painter.end()

            self.last_point = event.position().toPoint()
            self.update()

        elif self.drawing and self.current_tool in ["rectangle", "ellipse", "line"]:
            self.last_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            # Завершаем рисование фигур
            if self.current_tool in ["rectangle", "ellipse", "line"]:
                self.save_to_history()
                painter = QPainter(self.image)
                painter.setPen(QPen(self.brush_color, self.brush_size, Qt.SolidLine))
                painter.setBrush(Qt.NoBrush if self.current_tool == "line" else Qt.transparent)

                rect = QRect(self.start_point, self.last_point).normalized()
                if self.current_shape == "rectangle":
                    painter.drawRect(rect)
                elif self.current_shape == "ellipse":
                    painter.drawEllipse(rect)
                elif self.current_shape == "line":
                    painter.drawLine(self.start_point, self.last_point)

                painter.end()
                self.update()

            self.drawing = False

    def flood_fill(self, point, color):
        """Заливка области"""
        target_color = self.image.pixelColor(point)
        if target_color == color:
            return

        # Простая реализация заливки
        pixels = [point]
        while pixels:
            p = pixels.pop()
            if p.x() < 0 or p.y() < 0 or p.x() >= self.width() or p.y() >= self.height():
                continue

            if self.image.pixelColor(p) == target_color:
                self.image.setPixelColor(p, color)
                pixels.append(QPoint(p.x() + 1, p.y()))
                pixels.append(QPoint(p.x() - 1, p.y()))
                pixels.append(QPoint(p.x(), p.y() + 1))
                pixels.append(QPoint(p.x(), p.y() - 1))

    def save_to_history(self):
        """Сохранение состояния в историю"""
        # Удаляем всё после текущего индекса
        if self.history_index + 1 < len(self.history):
            self.history = self.history[:self.history_index + 1]

        # Сохраняем копию изображения
        image_copy = self.image.copy()
        self.history.append(image_copy)
        self.history_index += 1

        # Ограничиваем размер истории
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.history_index -= 1

    def undo(self):
        """Отмена последнего действия"""
        if self.history_index > 0:
            self.history_index -= 1
            self.image = self.history[self.history_index].copy()
            self.update()

    def redo(self):
        """Повтор последнего действия"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.image = self.history[self.history_index].copy()
            self.update()

    def clear(self):
        """Очистка холста"""
        self.save_to_history()
        self.image.fill(Qt.white)
        self.update()

    def set_background(self, color):
        """Установка фона"""
        self.save_to_history()
        self.image.fill(color)
        self.update()

    def apply_filter(self, filter_type):
        """Применение фильтров к изображению"""
        self.save_to_history()

        # Конвертируем QImage в numpy array
        width = self.image.width()
        height = self.image.height()

        # Создаем временное изображение для обработки
        temp_image = self.image.copy()

        if filter_type == "grayscale":
            for y in range(height):
                for x in range(width):
                    color = temp_image.pixelColor(x, y)
                    gray = int(color.red() * 0.299 + color.green() * 0.587 + color.blue() * 0.114)
                    temp_image.setPixelColor(x, y, QColor(gray, gray, gray))

        elif filter_type == "invert":
            for y in range(height):
                for x in range(width):
                    color = temp_image.pixelColor(x, y)
                    temp_image.setPixelColor(x, y,
                                             QColor(255 - color.red(), 255 - color.green(), 255 - color.blue()))

        elif filter_type == "sepia":
            for y in range(height):
                for x in range(width):
                    color = temp_image.pixelColor(x, y)
                    r = color.red()
                    g = color.green()
                    b = color.blue()

                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)

                    tr = min(255, tr)
                    tg = min(255, tg)
                    tb = min(255, tb)

                    temp_image.setPixelColor(x, y, QColor(tr, tg, tb))

        elif filter_type == "blur":
            # Простой blur 3x3
            blurred = temp_image.copy()
            kernel = [1, 2, 1, 2, 4, 2, 1, 2, 1]
            kernel_sum = sum(kernel)

            for y in range(1, height - 1):
                for x in range(1, width - 1):
                    r = g = b = 0
                    idx = 0
                    for ky in range(-1, 2):
                        for kx in range(-1, 2):
                            color = temp_image.pixelColor(x + kx, y + ky)
                            r += color.red() * kernel[idx]
                            g += color.green() * kernel[idx]
                            b += color.blue() * kernel[idx]
                            idx += 1

                    r = min(255, max(0, r // kernel_sum))
                    g = min(255, max(0, g // kernel_sum))
                    b = min(255, max(0, b // kernel_sum))

                    blurred.setPixelColor(x, y, QColor(r, g, b))

            temp_image = blurred

        self.image = temp_image
        self.update()


class ColorPicker(QWidget):
    """Виджет выбора цвета"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_color = Qt.black
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Палитра цветов
        colors_layout = QGridLayout()

        colors = [
            Qt.black, Qt.white, Qt.red, Qt.green, Qt.blue,
            Qt.yellow, Qt.magenta, Qt.cyan, Qt.darkRed, Qt.darkGreen,
            Qt.darkBlue, Qt.darkYellow, Qt.darkMagenta, Qt.darkCyan,
            Qt.gray, Qt.darkGray, Qt.lightGray
        ]

        row, col = 0, 0
        for color in colors:
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"background-color: ; border: 1px solid #ccc;")
            btn.clicked.connect(lambda checked, c=color: self.select_color(c))
            colors_layout.addWidget(btn, row, col)
            col += 1
            if col > 5:
                col = 0
                row += 1

        layout.addLayout(colors_layout)

        # Пользовательский выбор цвета
        custom_color_btn = QPushButton("🎨 Другой цвет...")
        custom_color_btn.clicked.connect(self.pick_custom_color)
        layout.addWidget(custom_color_btn)

        # Отображение выбранного цвета
        self.color_display = QLabel()
        self.color_display.setFixedHeight(30)
        self.color_display.setStyleSheet(f"background-color:  border: 2px solid #000;")
        layout.addWidget(self.color_display)

        self.setLayout(layout)

    def select_color(self, color):
        self.selected_color = color
        self.color_display.setStyleSheet(f"background-color: {color.name()}; border: 2px solid #000;")
        self.color_selected.emit(color)

    def pick_custom_color(self):
        color = QColorDialog.getColor(self.selected_color, self)
        if color.isValid():
            self.select_color(color)

    color_selected = Signal(QColor)


class BrushSettings(QWidget):
    """Настройки кисти"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Размер кисти
        layout.addWidget(QLabel("Размер кисти:"))
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(1, 50)
        self.size_slider.setValue(5)
        self.size_slider.valueChanged.connect(self.size_changed)
        layout.addWidget(self.size_slider)

        self.size_label = QLabel("5 px")
        layout.addWidget(self.size_label)

        # Стиль кисти
        layout.addWidget(QLabel("Стиль:"))
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Круглая", "Квадратная", "Изображение"])
        layout.addWidget(self.style_combo)

        # Прозрачность
        layout.addWidget(QLabel("Прозрачность:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(1, 100)
        self.opacity_slider.setValue(100)
        layout.addWidget(self.opacity_slider)

        self.setLayout(layout)

    def size_changed(self, value):
        self.size_label.setText(f"{value} px")
        self.settings_changed.emit()

    settings_changed = Signal()


class LayerWidget(QWidget):
    """Виджет для работы со слоями"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layers = []
        self.current_layer = 0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Кнопки управления слоями
        btn_layout = QHBoxLayout()

        add_btn = QPushButton("+")
        add_btn.clicked.connect(self.add_layer)
        btn_layout.addWidget(add_btn)

        remove_btn = QPushButton("-")
        remove_btn.clicked.connect(self.remove_layer)
        btn_layout.addWidget(remove_btn)

        up_btn = QPushButton("↑")
        up_btn.clicked.connect(self.move_layer_up)
        btn_layout.addWidget(up_btn)

        down_btn = QPushButton("↓")
        down_btn.clicked.connect(self.move_layer_down)
        btn_layout.addWidget(down_btn)

        layout.addLayout(btn_layout)

        # Список слоев
        self.layer_list = QListWidget()
        self.layer_list.itemClicked.connect(self.select_layer)
        layout.addWidget(self.layer_list)

        # Добавляем первый слой
        self.add_layer()

        self.setLayout(layout)

    def add_layer(self):
        layer_name = f"Слой {len(self.layers) + 1}"
        self.layers.append(layer_name)
        self.layer_list.addItem(layer_name)
        self.layer_list.setCurrentRow(len(self.layers) - 1)
        self.current_layer = len(self.layers) - 1

    def remove_layer(self):
        if len(self.layers) > 1:
            self.layers.pop(self.current_layer)
            self.layer_list.takeItem(self.current_layer)
            self.current_layer = max(0, self.current_layer - 1)
            self.layer_list.setCurrentRow(self.current_layer)

    def move_layer_up(self):
        if self.current_layer > 0:
            self.layers[self.current_layer], self.layers[self.current_layer - 1] = \
                self.layers[self.current_layer - 1], self.layers[self.current_layer]
            item = self.layer_list.takeItem(self.current_layer)
            self.layer_list.insertItem(self.current_layer - 1, item)
            self.current_layer -= 1
            self.layer_list.setCurrentRow(self.current_layer)

    def move_layer_down(self):
        if self.current_layer < len(self.layers) - 1:
            self.layers[self.current_layer], self.layers[self.current_layer + 1] = \
                self.layers[self.current_layer + 1], self.layers[self.current_layer]
            item = self.layer_list.takeItem(self.current_layer)
            self.layer_list.insertItem(self.current_layer + 1, item)
            self.current_layer += 1
            self.layer_list.setCurrentRow(self.current_layer)

    def select_layer(self, item):
        self.current_layer = self.layer_list.row(item)


class EffectPreview(QWidget):
    """Предпросмотр эффектов в реальном времени"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.effects = [
            "Нет", "Размытие", "Резкость", "Шум", "Сепия",
            "Негатив", "Акварель", "Масло", "Карандаш"
        ]
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Слайдеры для параметров эффектов
        self.intensity_slider = QSlider(Qt.Horizontal)
        self.intensity_slider.setRange(0, 100)
        self.intensity_slider.setValue(50)
        layout.addWidget(QLabel("Интенсивность:"))
        layout.addWidget(self.intensity_slider)

        # Список эффектов
        self.effect_combo = QComboBox()
        self.effect_combo.addItems(self.effects)
        layout.addWidget(QLabel("Эффект:"))
        layout.addWidget(self.effect_combo)

        # Предпросмотр
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(200, 200)
        self.preview_label.setStyleSheet("border: 2px solid #ccc; background-color: #f0f0f0;")
        layout.addWidget(self.preview_label)

        self.setLayout(layout)


class ImageEditor(QMainWindow):
    """Главное окно редактора изображений"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArtStudio Pro - Редактор изображений")
        self.setGeometry(100, 100, 1400, 900)

        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()

        # Левая панель инструментов
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel)

        # Центральная область с холстом
        center_area = self.create_center_area()
        main_layout.addWidget(center_area, 1)

        # Правая панель свойств
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel)

        central_widget.setLayout(main_layout)

        # Создаем меню
        self.create_menu()

        # Статус бар
        self.statusBar().showMessage("Готово")

        # Переменные
        self.current_file = None

    def create_left_panel(self):
        """Создание левой панели с инструментами"""
        panel = QWidget()
        panel.setMinimumWidth(80)
        panel.setMaximumWidth(120)

        layout = QVBoxLayout()

        # Инструменты рисования
        tools = [
            ("🖌️", "Кисть", "brush"),
            ("🧽", "Ластик", "eraser"),
            ("🎨", "Заливка", "fill"),
            ("📐", "Прямоугольник", "rectangle"),
            ("⚪", "Эллипс", "ellipse"),
            ("📏", "Линия", "line"),
            ("🔤", "Текст", "text"),
            ("✋", "Выделение", "select"),
            ("🔍", "Лупа", "zoom"),
            ("🎯", "Пипетка", "dropper")
        ]

        self.tool_buttons = []
        for icon, tooltip, tool_id in tools:
            btn = QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.setFixedSize(60, 60)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, tid=tool_id: self.select_tool(tid))

            # Стилизация
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 24px;
                    border-radius: 10px;
                    background-color: #2d2d2d;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #3d3d3d;
                }
                QPushButton:checked {
                    background-color: #007acc;
                }
            """)

            layout.addWidget(btn)
            self.tool_buttons.append((btn, tool_id))

        layout.addStretch()

        # Кнопка сохранения
        save_btn = QPushButton("💾")
        save_btn.setToolTip("Сохранить")
        save_btn.setFixedSize(60, 60)
        save_btn.clicked.connect(self.save_image)
        save_btn.setStyleSheet("""
            QPushButton {
                font-size: 24px;
                border-radius: 10px;
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(save_btn)

        panel.setLayout(layout)
        return panel

    def create_center_area(self):
        """Создание центральной области с холстом"""
        container = QWidget()
        layout = QVBoxLayout()

        # Панель инструментов над холстом
        top_panel = QWidget()
        top_layout = QHBoxLayout()

        # Кнопки файловых операций
        file_buttons = [
            ("📄", "Новый", self.new_image),
            ("📂", "Открыть", self.open_image),
            ("💾", "Сохранить", self.save_image),
            ("📤", "Экспорт", self.export_image)
        ]

        for icon, tooltip, callback in file_buttons:
            btn = QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.clicked.connect(callback)
            top_layout.addWidget(btn)

        top_layout.addStretch()

        # Инструменты редактирования
        edit_buttons = [
            ("↶", "Отменить", self.undo),
            ("↷", "Повторить", self.redo),
            ("🗑️", "Очистить", self.clear_canvas),
            ("🔲", "Сетка", self.toggle_grid)
        ]

        for icon, tooltip, callback in edit_buttons:
            btn = QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.clicked.connect(callback)
            top_layout.addWidget(btn)

        top_panel.setLayout(top_layout)
        layout.addWidget(top_panel)

        # Холст
        self.canvas = Canvas()
        layout.addWidget(self.canvas, 1)

        # Панель статуса холста
        status_panel = QWidget()
        status_layout = QHBoxLayout()

        self.position_label = QLabel("X: 0, Y: 0")
        status_layout.addWidget(self.position_label)

        self.zoom_label = QLabel("100%")
        status_layout.addWidget(self.zoom_label)

        self.color_label = QLabel("Цвет: #000000")
        status_layout.addWidget(self.color_label)

        status_panel.setLayout(status_layout)
        layout.addWidget(status_panel)

        container.setLayout(layout)
        return container

    def create_right_panel(self):
        """Создание правой панели свойств"""
        panel = QTabWidget()
        panel.setMaximumWidth(300)

        # Вкладка с цветом
        color_tab = ColorPicker()
        color_tab.color_selected.connect(self.set_brush_color)
        panel.addTab(color_tab, "🎨 Цвет")

        # Вкладка с кистями
        brush_tab = BrushSettings()
        brush_tab.settings_changed.connect(self.update_brush_settings)
        panel.addTab(brush_tab, "🖌️ Кисти")

        # Вкладка со слоями
        layer_tab = LayerWidget()
        panel.addTab(layer_tab, "📄 Слои")

        # Вкладка с эффектами
        effect_tab = EffectPreview()
        panel.addTab(effect_tab, "✨ Эффекты")

        # Вкладка с фильтрами
        filter_tab = self.create_filter_tab()
        panel.addTab(filter_tab, "🔧 Фильтры")

        return panel

    def create_filter_tab(self):
        """Создание вкладки с фильтрами"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Кнопки фильтров
        filters = [
            ("Черно-белый", "grayscale"),
            ("Негатив", "invert"),
            ("Сепия", "sepia"),
            ("Размытие", "blur"),
            ("Яркость", "brightness"),
            ("Контраст", "contrast"),
            ("Теплее", "warm"),
            ("Холоднее", "cool"),
            ("Винтаж", "vintage"),
            ("Поп-арт", "popart")
        ]

        for name, filter_id in filters:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, fid=filter_id: self.apply_filter(fid))
            layout.addWidget(btn)

        # Слайдеры для настройки
        layout.addWidget(QLabel("Яркость:"))
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        layout.addWidget(self.brightness_slider)

        layout.addWidget(QLabel("Контраст:"))
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(-100, 100)
        self.contrast_slider.setValue(0)
        layout.addWidget(self.contrast_slider)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_menu(self):
        """Создание меню"""
        menubar = self.menuBar()

        # Меню Файл
        file_menu = menubar.addMenu("📁 Файл")

        new_action = QAction("📄 Новый", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_image)
        file_menu.addAction(new_action)

        open_action = QAction("📂 Открыть", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)

        save_action = QAction("💾 Сохранить", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_image)
        file_menu.addAction(save_action)

        save_as_action = QAction("💾 Сохранить как...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_as_image)
        file_menu.addAction(save_as_action)

        export_action = QAction("📤 Экспорт", self)
        export_action.triggered.connect(self.export_image)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("🚪 Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню Правка
        edit_menu = menubar.addMenu("✏️ Правка")

        undo_action = QAction("↶ Отменить", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("↷ Повторить", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        clear_action = QAction("🗑️ Очистить", self)
        clear_action.setShortcut("Ctrl+Shift+N")
        clear_action.triggered.connect(self.clear_canvas)
        edit_menu.addAction(clear_action)

        # Меню Изображение
        image_menu = menubar.addMenu("🖼️ Изображение")

        resize_action = QAction("📏 Изменить размер", self)
        resize_action.triggered.connect(self.resize_image)
        image_menu.addAction(resize_action)

        rotate_action = QAction("🔄 Повернуть", self)
        rotate_action.triggered.connect(self.rotate_image)
        image_menu.addAction(rotate_action)

        crop_action = QAction("✂️ Обрезать", self)
        crop_action.triggered.connect(self.crop_image)
        image_menu.addAction(crop_action)

        # Меню Вид
        view_menu = menubar.addMenu("👁️ Вид")

        grid_action = QAction("🔲 Сетка", self, checkable=True)
        grid_action.triggered.connect(self.toggle_grid)
        view_menu.addAction(grid_action)

        zoom_in_action = QAction("➕ Увеличить", self)
        zoom_in_action.setShortcut("Ctrl++")
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("➖ Уменьшить", self)
        zoom_out_action.setShortcut("Ctrl+-")
        view_menu.addAction(zoom_out_action)

        # Меню Справка
        help_menu = menubar.addMenu("❓ Справка")

        about_action = QAction("ℹ️ О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def select_tool(self, tool_id):
        """Выбор инструмента"""
        # Сбрасываем выделение всех кнопок
        for btn, tid in self.tool_buttons:
            btn.setChecked(tid == tool_id)

        # Устанавливаем инструмент на холсте
        self.canvas.current_tool = tool_id

        # Для фигур устанавливаем соответствующую форму
        if tool_id in ["rectangle", "ellipse", "line"]:
            self.canvas.current_shape = tool_id

        self.statusBar().showMessage(f"Инструмент: {tool_id}")

    def set_brush_color(self, color):
        """Установка цвета кисти"""
        self.canvas.brush_color = color
        self.color_label.setText(f"Цвет: {color.name()}")

    def update_brush_settings(self):
        """Обновление настроек кисти"""
        # Здесь можно добавить получение настроек из виджета

    def apply_filter(self, filter_type):
        """Применение фильтра"""
        self.canvas.apply_filter(filter_type)

    def new_image(self):
        """Создание нового изображения"""
        dialog = NewImageDialog(self)
        if dialog.exec():
            width, height, color = dialog.get_values()
            self.canvas.image = QImage(width, height, QImage.Format_ARGB32)
            self.canvas.image.fill(color)
            self.canvas.setFixedSize(width, height)
            self.canvas.update()
            self.current_file = None

    def open_image(self):
        """Открытие изображения"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Открыть изображение", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All files (*.*)"
        )

        if filename:
            image = QImage(filename)
            if not image.isNull():
                self.canvas.image = image
                self.canvas.setFixedSize(image.size())
                self.canvas.update()
                self.current_file = filename
                self.statusBar().showMessage(f"Открыто: {filename}")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось загрузить изображение")

    def save_image(self):
        """Сохранение изображения"""
        if not self.current_file:
            self.save_as_image()
        else:
            self.canvas.image.save(self.current_file)
            self.statusBar().showMessage(f"Сохранено: {self.current_file}")

    def save_as_image(self):
        """Сохранение изображения как"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить изображение", "",
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp);;All files (*.*)"
        )

        if filename:
            self.canvas.image.save(filename)
            self.current_file = filename
            self.statusBar().showMessage(f"Сохранено: {filename}")

    def export_image(self):
        """Экспорт изображения в разные форматы"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Экспорт изображения")
        dialog.setFixedSize(300, 200)

        layout = QVBoxLayout()

        # Выбор формата
        format_label = QLabel("Формат:")
        format_combo = QComboBox()
        format_combo.addItems(["PNG", "JPEG", "BMP", "WebP"])
        layout.addWidget(format_label)
        layout.addWidget(format_combo)

        # Качество (для JPEG)
        quality_label = QLabel("Качество:")
        quality_slider = QSlider(Qt.Horizontal)
        quality_slider.setRange(1, 100)
        quality_slider.setValue(90)
        layout.addWidget(quality_label)
        layout.addWidget(quality_slider)

        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        if dialog.exec():
            # Здесь будет логика экспорта
            QMessageBox.information(self, "Экспорт", "Изображение экспортировано")

    def undo(self):
        """Отмена действия"""
        self.canvas.undo()

    def redo(self):
        """Повтор действия"""
        self.canvas.redo()

    def clear_canvas(self):
        """Очистка холста"""
        reply = QMessageBox.question(self, "Очистка",
                                     "Очистить холст? Все несохраненные изменения будут потеряны.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.canvas.clear()

    def toggle_grid(self):
        """Переключение сетки"""
        self.canvas.show_grid = not self.canvas.show_grid
        self.canvas.update()

    def resize_image(self):
        """Изменение размера изображения"""
        dialog = ResizeDialog(self.canvas.image.size(), self)
        if dialog.exec():
            new_size = dialog.get_size()
            self.canvas.image = self.canvas.image.scaled(new_size)
            self.canvas.setFixedSize(new_size)
            self.canvas.update()

    def rotate_image(self):
        """Поворот изображения"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Повернуть изображение")
        dialog.setFixedSize(250, 150)

        layout = QVBoxLayout()

        angle_label = QLabel("Угол поворота:")
        angle_spin = QSpinBox()
        angle_spin.setRange(-360, 360)
        angle_spin.setValue(90)
        angle_spin.setSuffix("°")

        layout.addWidget(angle_label)
        layout.addWidget(angle_spin)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        if dialog.exec():
            transform = QTransform().rotate(angle_spin.value())
            self.canvas.image = self.canvas.image.transformed(transform)
            self.canvas.update()

    def crop_image(self):
        """Обрезка изображения"""
        QMessageBox.information(self, "Обрезка",
                                "Выделите область для обрезки инструментом выделения")
        # Здесь можно добавить логику для обрезки

    def show_about(self):
        """Показать информацию о программе"""
        about_text = """
        <h2>🎨 ArtStudio Pro</h2>
        <p><b>Версия:</b> 1.0.0</p>
        <p><b>Описание:</b> Профессиональный редактор изображений</p>

        <h3>Возможности:</h3>
        <ul>
            <li>Рисование различными кистями</li>
            <li>Работа со слоями</li>
            <li>Фильтры и эффекты</li>
            <li>Инструменты для работы с фигурами</li>
            <li>Добавление текста</li>
            <li>История действий (Undo/Redo)</li>
        </ul>

        <p><i>Создано с использованием PySide6</i></p>
        """

        QMessageBox.about(self, "О программе", about_text)


class NewImageDialog(QDialog):
    """Диалог создания нового изображения"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новое изображение")
        self.setFixedSize(300, 250)

        layout = QVBoxLayout()

        # Размеры
        size_group = QGroupBox("Размер")
        size_layout = QFormLayout()

        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 5000)
        self.width_spin.setValue(800)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 5000)
        self.height_spin.setValue(600)

        size_layout.addRow("Ширина:", self.width_spin)
        size_layout.addRow("Высота:", self.height_spin)

        size_group.setLayout(size_layout)
        layout.addWidget(size_group)

        # Цвет фона
        color_group = QGroupBox("Цвет фона")
        color_layout = QVBoxLayout()

        self.bg_color = Qt.white
        self.color_button = QPushButton()
        self.color_button.setStyleSheet(f"background-color: {self.bg_color.name()};")
        self.color_button.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_button)

        # Пресеты цветов
        presets_layout = QHBoxLayout()
        for color in [Qt.white, Qt.black, Qt.transparent]:
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
            btn.clicked.connect(lambda checked, c=color: self.set_color(c))
            presets_layout.addWidget(btn)

        color_layout.addLayout(presets_layout)
        color_group.setLayout(color_layout)
        layout.addWidget(color_group)

        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def choose_color(self):
        color = QColorDialog.getColor(self.bg_color, self)
        if color.isValid():
            self.set_color(color)

    def set_color(self, color):
        self.bg_color = color
        self.color_button.setStyleSheet(f"background-color: {color.name()};")

    def get_values(self):
        return self.width_spin.value(), self.height_spin.value(), self.bg_color


class ResizeDialog(QDialog):
    """Диалог изменения размера"""

    def __init__(self, current_size, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Изменить размер")
        self.setFixedSize(300, 200)

        self.original_size = current_size
        self.keep_aspect = True

        layout = QVBoxLayout()

        # Текущий размер
        current_label = QLabel(f"Текущий размер: {current_size.width()} × {current_size.height()}")
        layout.addWidget(current_label)

        # Новый размер
        size_layout = QFormLayout()

        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 5000)
        self.width_spin.setValue(current_size.width())
        self.width_spin.valueChanged.connect(self.on_width_changed)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 5000)
        self.height_spin.setValue(current_size.height())
        self.height_spin.valueChanged.connect(self.on_height_changed)

        size_layout.addRow("Ширина:", self.width_spin)
        size_layout.addRow("Высота:", self.height_spin)

        layout.addLayout(size_layout)

        # Сохранять пропорции
        self.aspect_check = QCheckBox("Сохранять пропорции")
        self.aspect_check.setChecked(True)
        layout.addWidget(self.aspect_check)

        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def on_width_changed(self, value):
        if self.aspect_check.isChecked():
            ratio = value / self.original_size.width()
            new_height = int(self.original_size.height() * ratio)
            self.height_spin.blockSignals(True)
            self.height_spin.setValue(new_height)
            self.height_spin.blockSignals(False)

    def on_height_changed(self, value):
        if self.aspect_check.isChecked():
            ratio = value / self.original_size.height()
            new_width = int(self.original_size.width() * ratio)
            self.width_spin.blockSignals(True)
            self.width_spin.setValue(new_width)
            self.width_spin.blockSignals(False)

    def get_size(self):
        return QSize(self.width_spin.value(), self.height_spin.value())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Темная тема
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    # Устанавливаем иконку приложения
    app.setWindowIcon(QIcon.fromTheme("applications-graphics"))

    window = ImageEditor()
    window.show()

    sys.exit(app.exec())