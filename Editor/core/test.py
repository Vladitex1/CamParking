import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QAction, QImage
import numpy as np


class ImageDockWidget(QWidget):
    """Виджет для отображения изображения и расстановки точек"""

    def __init__(self):
        super().__init__()
        self.image_path = ""
        self.image = None
        self.points = []  # Список точек [(x, y), ...]
        self.current_point = None
        self.point_radius = 5

        # Создаем метку для отображения изображения
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 300)

        # Создаем кнопки
        self.load_btn = QPushButton("Загрузить изображение")
        self.clear_btn = QPushButton("Очистить точки")
        self.coords_label = QLabel("Точки: 0")

        # Layout
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.coords_label)

        layout.addLayout(button_layout)
        layout.addWidget(self.image_label, 1)

        # Информационная панель
        info_group = QGroupBox("Информация")
        info_layout = QVBoxLayout()
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(100)
        self.info_text.setReadOnly(True)
        info_layout.addWidget(QLabel("Координаты точек:"))
        info_layout.addWidget(self.info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        self.setLayout(layout)

        # Подключаем сигналы
        self.load_btn.clicked.connect(self.load_image)
        self.clear_btn.clicked.connect(self.clear_points)

        # Устанавливаем обработчик событий мыши для метки
        self.image_label.mousePressEvent = self.image_mouse_press
        self.image_label.mouseMoveEvent = self.image_mouse_move
        self.image_label.mouseReleaseEvent = self.image_mouse_release

        # Состояние перетаскивания
        self.dragging_point = -1

    def load_image(self):
        """Загрузка изображения"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if filename:
            self.image_path = filename
            self.image = QPixmap(filename)
            self.display_image()

    def display_image(self):
        """Отображение изображения с точками"""
        if self.image:
            # Создаем копию изображения для рисования
            pixmap = self.image.copy()

            # Рисуем на изображении
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)

            # Рисуем все точки
            for i, point in enumerate(self.points):
                # Выбираем цвет в зависимости от индекса
                colors = [Qt.red, Qt.blue, Qt.green, Qt.yellow, Qt.magenta, Qt.cyan]
                color = colors[i % len(colors)]

                # Рисуем круг
                painter.setPen(QPen(color, 2))
                painter.setBrush(QBrush(color))
                painter.drawEllipse(
                    QPoint(int(point[0]), int(point[1])),
                    self.point_radius,
                    self.point_radius
                )

                # Подписываем точку
                painter.drawText(
                    int(point[0]) + 10,
                    int(point[1]) - 10,
                    f"P{i + 1}"
                )

            painter.end()

            # Масштабируем изображение под размер виджета
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

            # Обновляем информацию
            self.update_info()

    def image_mouse_press(self, event):
        """Обработка клика по изображению"""
        if not self.image:
            return

        # Получаем координаты относительно оригинального изображения
        label_pos = event.position()
        pixmap = self.image_label.pixmap()

        if pixmap:
            # Масштабируем координаты
            label_size = self.image_label.size()
            pixmap_size = pixmap.size()

            scale_x = pixmap_size.width() / label_size.width()
            scale_y = pixmap_size.height() / label_size.height()

            # Вычисляем смещение (если изображение центрировано)
            offset_x = (label_size.width() - pixmap_size.width() / scale_x) / 2
            offset_y = (label_size.height() - pixmap_size.height() / scale_y) / 2

            x = (label_pos.x() - offset_x) * scale_x
            y = (label_pos.y() - offset_y) * scale_y

            # Проверяем, попали ли мы в существующую точку
            for i, point in enumerate(self.points):
                distance = np.sqrt((x - point[0]) ** 2 + (y - point[1]) ** 2)
                if distance < self.point_radius * 2:
                    self.dragging_point = i
                    return

            # Добавляем новую точку
            if event.button() == Qt.LeftButton:
                self.points.append((x, y))
                self.coords_label.setText(f"Точки: {len(self.points)}")
                self.display_image()

    def image_mouse_move(self, event):
        """Обработка перемещения мыши"""
        if self.dragging_point >= 0 and self.image:
            label_pos = event.position()
            pixmap = self.image_label.pixmap()

            if pixmap:
                # Масштабируем координаты
                label_size = self.image_label.size()
                pixmap_size = pixmap.size()

                scale_x = pixmap_size.width() / label_size.width()
                scale_y = pixmap_size.height() / label_size.height()

                # Вычисляем смещение
                offset_x = (label_size.width() - pixmap_size.width() / scale_x) / 2
                offset_y = (label_size.height() - pixmap_size.height() / scale_y) / 2

                x = (label_pos.x() - offset_x) * scale_x
                y = (label_pos.y() - offset_y) * scale_y

                # Обновляем точку
                self.points[self.dragging_point] = (x, y)
                self.display_image()

    def image_mouse_release(self, event):
        """Обработка отпускания кнопки мыши"""
        self.dragging_point = -1

    def clear_points(self):
        """Очистка всех точек"""
        self.points = []
        self.coords_label.setText("Точки: 0")
        if self.image:
            self.display_image()
        self.update_info()

    def update_info(self):
        """Обновление информации о точках"""
        if not self.points:
            self.info_text.setText("Нет точек")
            return

        info = ""
        for i, (x, y) in enumerate(self.points):
            info += f"Точка {i + 1}: X={x:.1f}, Y={y:.1f}\n"
        self.info_text.setText(info)

    def resizeEvent(self, event):
        """Обработка изменения размера окна"""
        super().resizeEvent(event)
        if self.image:
            self.display_image()


class TextPageWidget(QWidget):
    """Первая страница с текстом и кнопкой"""

    def __init__(self):
        super().__init__()

        # Создаем элементы
        title_label = QLabel("Добро пожаловать на первую страницу!")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        info_label = QLabel(
            "Это демонстрационное приложение с двумя страницами.\n\n"
            "На второй странице вы можете загрузить изображение и расставлять на нем точки.\n"
            "Точки можно перемещать, перетаскивая их мышью.\n\n"
            "Используйте меню вверху для переключения между страницами."
        )
        info_label.setWordWrap(True)

        # Создаем кнопку
        self.message_btn = QPushButton("Показать сообщение")
        self.message_btn.clicked.connect(self.show_message)

        # Создаем текстовое поле
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Введите текст здесь...")
        self.text_edit.setMaximumHeight(100)

        # Создаем список
        self.list_widget = QListWidget()
        self.list_widget.addItems(["Элемент 1", "Элемент 2", "Элемент 3"])

        # Создаем переключатели
        self.checkbox1 = QCheckBox("Опция 1")
        self.checkbox2 = QCheckBox("Опция 2")
        self.radio1 = QRadioButton("Вариант A")
        self.radio2 = QRadioButton("Вариант B")

        # Группируем переключатели
        options_group = QGroupBox("Настройки")
        options_layout = QVBoxLayout()
        options_layout.addWidget(self.checkbox1)
        options_layout.addWidget(self.checkbox2)
        options_layout.addWidget(self.radio1)
        options_layout.addWidget(self.radio2)
        options_group.setLayout(options_layout)

        # Создаем прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(50)

        # Создаем слайдер
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self.slider_changed)

        # Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(title_label)
        main_layout.addWidget(info_label)
        main_layout.addSpacing(20)

        # Верхняя часть с кнопкой и текстом
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.message_btn, 1)
        top_layout.addWidget(self.text_edit, 2)
        main_layout.addLayout(top_layout)

        # Средняя часть со списком и настройками
        middle_layout = QHBoxLayout()
        middle_layout.addWidget(self.list_widget, 1)
        middle_layout.addWidget(options_group, 1)
        main_layout.addLayout(middle_layout)

        # Нижняя часть с прогрессом
        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(QLabel("Прогресс:"))
        bottom_layout.addWidget(self.progress_bar)
        bottom_layout.addWidget(QLabel("Слайдер:"))
        bottom_layout.addWidget(self.slider)
        main_layout.addLayout(bottom_layout)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def show_message(self):
        """Показать сообщение из текстового поля"""
        text = self.text_edit.toPlainText()
        if text:
            QMessageBox.information(self, "Сообщение", text)
        else:
            QMessageBox.warning(self, "Внимание", "Введите текст в поле!")

    def slider_changed(self, value):
        """Обработчик изменения слайдера"""
        self.progress_bar.setValue(value)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Приложение с двумя страницами")
        self.setGeometry(100, 100, 900, 700)

        # Создаем центральный виджет для переключения страниц
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # Создаем страницы
        self.text_page = TextPageWidget()
        self.image_page = ImageDockWidget()

        # Добавляем страницы в StackedWidget
        self.central_widget.addWidget(self.text_page)
        self.central_widget.addWidget(self.image_page)

        # Создаем меню
        self.create_menu()

        # Создаем панель инструментов
        self.create_toolbar()

        # Создаем статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово. Текущая страница: Текстовая")

        # Докинг окно для дополнительной информации
        self.create_dock_widget()

    def create_menu(self):
        """Создание меню"""
        menubar = self.menuBar()

        # Меню "Файл"
        file_menu = menubar.addMenu("Файл")

        new_action = QAction("Новый", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)

        open_action = QAction("Открыть", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)

        save_action = QAction("Сохранить", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню "Страницы" для переключения
        pages_menu = menubar.addMenu("Страницы")

        text_page_action = QAction("Текстовая страница", self)
        text_page_action.setShortcut("F1")
        text_page_action.triggered.connect(lambda: self.switch_page(0))
        pages_menu.addAction(text_page_action)

        image_page_action = QAction("Страница с изображением", self)
        image_page_action.setShortcut("F2")
        image_page_action.triggered.connect(lambda: self.switch_page(1))
        pages_menu.addAction(image_page_action)

        # Меню "Справка"
        help_menu = menubar.addMenu("Справка")

        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """Создание панели инструментов"""
        toolbar = QToolBar("Панель инструментов")
        self.addToolBar(toolbar)

        # Кнопки для переключения страниц
        text_page_btn = QAction("📝 Текст", self)
        text_page_btn.triggered.connect(lambda: self.switch_page(0))
        toolbar.addAction(text_page_btn)

        image_page_btn = QAction("🖼️ Изображение", self)
        image_page_btn.triggered.connect(lambda: self.switch_page(1))
        toolbar.addAction(image_page_btn)

        toolbar.addSeparator()

        # Кнопка загрузки изображения (видна только на странице с изображением)
        self.load_image_action = QAction("📁 Загрузить", self)
        self.load_image_action.triggered.connect(self.load_image_from_toolbar)
        toolbar.addAction(self.load_image_action)

    def create_dock_widget(self):
        """Создание докинг окна"""
        dock = QDockWidget("Информация", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # Содержимое докинг окна
        dock_content = QWidget()
        layout = QVBoxLayout()

        info_label = QLabel(
            "<b>Инструкция:</b><br><br>"
            "1. Используйте меню 'Страницы' для переключения<br>"
            "2. На странице с изображением:<br>"
            "   - Нажмите 'Загрузить изображение'<br>"
            "   - Кликните на изображении чтобы добавить точку<br>"
            "   - Перетащите точку для перемещения<br>"
            "3. Координаты точек отображаются внизу"
        )
        info_label.setWordWrap(True)

        layout.addWidget(info_label)
        layout.addStretch()

        # Добавляем переключатель видимости докинга
        self.dock_visibility = QCheckBox("Показывать панель информации")
        self.dock_visibility.setChecked(True)
        self.dock_visibility.toggled.connect(dock.setVisible)
        layout.addWidget(self.dock_visibility)

        dock_content.setLayout(layout)
        dock.setWidget(dock_content)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def switch_page(self, index):
        """Переключение между страницами"""
        self.central_widget.setCurrentIndex(index)

        # Обновляем статус бар
        if index == 0:
            self.status_bar.showMessage("Текущая страница: Текстовая")
            self.load_image_action.setEnabled(False)
        else:
            self.status_bar.showMessage("Текущая страница: Работа с изображением")
            self.load_image_action.setEnabled(True)

    def load_image_from_toolbar(self):
        """Загрузка изображения из панели инструментов"""
        if self.central_widget.currentIndex() == 1:
            self.image_page.load_image()

    def show_about(self):
        """Показать окно 'О программе'"""
        QMessageBox.about(
            self,
            "О программе",
            "Приложение с двумя страницами\n\n"
            "Страница 1: Текстовая с элементами управления\n"
            "Страница 2: Работа с изображением и точками\n\n"
            "Создано с использованием PySide6"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Устанавливаем стиль
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())