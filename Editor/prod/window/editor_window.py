import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QPoint, QRect, QSize, QLine
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QAction, QImage, QIcon
# import Editor.prod.data.names as names
import numpy as np


class ImageDockWidget(QMainWindow):
    """Виджет для отображения изображения и расстановки точек"""

    def __init__(self):
        super().__init__()
        self.image_path = ""
        self.image = None
        self.points = []  # Список точек [(x, y), ...]  👈 СТАРОЕ: использовалось и для текущих, и для сохраненных
        self.polygons = []  # Список полигонов, каждый полигон = список точек
        self.current_points = []  # 👈 НОВОЕ: точки текущего редактируемого полигона

        self.dragging_point = -1
        self.dragging_polygon = -1  # 👈 НОВОЕ: индекс полигона, точку которого тащим
        self.current_color = 1
        self.selected_polygon_widget = []

        # ===== ВАЖНО: СОЗДАЕМ ЦЕНТРАЛЬНЫЙ ВИДЖЕТ =====
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Главный layout для центрального виджета
        main_layout = QVBoxLayout(central_widget)

        # Создаем метку для отображения изображения
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setStyleSheet("border: 1px solid gray;")
        main_layout.addWidget(self.image_label)

        # Создаем кнопки
        self.coords_label = QLabel("Точки: 0")

        self.create_toolbar()
        self.dock_editor()

        # Устанавливаем обработчик событий мыши для метки
        self.image_label.mousePressEvent = self.image_mouse_press
        self.image_label.mouseMoveEvent = self.image_mouse_move
        self.image_label.mouseReleaseEvent = self.image_mouse_release

    def create_toolbar(self):
        """Создание панели инструментов"""
        toolbar = QToolBar("Панель инструментов2")
        self.addToolBar(toolbar)

        self.editor_load_mask_action = QAction("📁 Загрузить маску", self)
        #self.editor_load_mask_action.triggered.connect(self.load_mask)
        toolbar.addAction(self.editor_load_mask_action)

        self.editor_load_image_action = QAction("📁 Загрузить Изображение", self)
        self.editor_load_image_action.triggered.connect(self.load_image)
        toolbar.addAction(self.editor_load_image_action)

    def dock_editor(self):
        self.EditorDock = QDockWidget("Информация", self)
        self.EditorDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        dock_content = QWidget()
        layout = QVBoxLayout(dock_content)

        # === ГРУППА ПОЛИГОНОВ ===
        polygon_group = QGroupBox("Полигоны:")
        polygon_group.setMinimumHeight(300)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(2, 2, 2, 2)
        scroll_layout.setSpacing(2)
        scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_layout = scroll_layout

        scroll_area = QScrollArea()
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.text_edits = []
        scroll_layout.addStretch()

        group_layout = QVBoxLayout(polygon_group)
        group_layout.setContentsMargins(0, 0, 0, 0)
        group_layout.addWidget(scroll_area)

        layout.addWidget(polygon_group)

        btn2 = QPushButton("Удалить выбранные")
        btn2.setIcon(QIcon("../icons/delete"))
        btn2.clicked.connect(lambda: (
                                      self.del_polygon_from_meta(self.selected_polygon_widget),
                                      self.del_polygon_from_widget(self.selected_polygon_widget),
                                      self.display_image(),
                                      self.debug))
        btn3 = QPushButton("Скрыть всё")
        btn3.setIcon(QIcon("../icons/visabilityoff"))
        btn4 = QPushButton("Показать все")
        btn4.setIcon(QIcon("../icons/visabilityon"))
        btn5 = QPushButton("дебаг")
        btn5.setIcon(QIcon("../icons/renew"))
        btn5.clicked.connect(lambda: self.debug())

        for i in [btn2, btn3, btn4, btn5]:
            i.setIconSize(QSize(32, 32))
            i.setStyleSheet("""
                QPushButton {
                    font-size: 17px;
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
            layout.addWidget(i)

        layout.addStretch()

        self.EditorDock.setWidget(dock_content)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.EditorDock)

    def load_image(self):
        """Загрузка изображения"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "../../img",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if filename:
            self.image_path = filename
            self.image = QPixmap(filename)
            self.display_image()

    # 👇 НОВЫЙ МЕТОД: преобразование координат мыши в координаты изображения
    def get_image_coordinates(self, event):
        """Преобразует координаты клика в координаты изображения"""
        if not self.image_label.pixmap():
            return (0, 0)

        # Получаем позицию клика
        label_pos = event.position()

        # Получаем размеры
        label_rect = self.image_label.rect()
        pixmap_rect = self.image_label.pixmap().rect()
        image_size = self.image.size()

        # Смещение для центрирования
        offset_x = max(0, (label_rect.width() - pixmap_rect.width()) / 2)
        offset_y = max(0, (label_rect.height() - pixmap_rect.height()) / 2)

        # Масштаб
        scale_x = image_size.width() / pixmap_rect.width()
        scale_y = image_size.height() / pixmap_rect.height()

        # Итоговые координаты
        x = (label_pos.x() - offset_x) * scale_x
        y = (label_pos.y() - offset_y) * scale_y

        return (x, y)

    def display_image(self):
        """Отображение изображения с точками"""
        self.point_radius = 10
        if self.image:
            pixmap = self.image.copy()
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            colors = [Qt.red, Qt.blue, Qt.green, Qt.yellow, Qt.magenta, Qt.cyan]

            # 👇 ИСПРАВЛЕНО: рисуем ТОЛЬКО current_points, points больше не используем
            for num, point in enumerate(self.current_points):
                color = colors[self.current_color % len(colors)]
                painter.setPen(QPen(color, 2))
                painter.setBrush(QBrush(color))
                pos_x = int(point[0])
                pos_y = int(point[1])
                painter.drawEllipse(
                    QPoint(pos_x, pos_y),
                    self.point_radius,
                    self.point_radius
                )
                painter.drawText(
                    pos_x + 10,
                    pos_y - 10,
                    f"P{num + 1}"
                )

            # 👇 ИСПРАВЛЕНО: рисуем полигоны
            if self.polygons:
                for i, data in enumerate(self.polygons):
                    #print(self.polygons)
                    j = i % len(colors)
                    points = data['points']
                    # Рисуем точки полигона
                    for point_num, point in enumerate(points):
                        painter.setPen(QPen(colors[j], 10))
                        painter.setBrush(QBrush(colors[j]))
                        pos_x = int(point[0])
                        pos_y = int(point[1])
                        painter.drawEllipse(
                            QPoint(pos_x, pos_y),
                            self.point_radius,
                            self.point_radius
                        )
                        painter.drawText(
                            pos_x + 10,
                            pos_y - 10,
                            f"P{i + 1}-{point_num + 1}"
                        )

                    # 👇 ИСПРАВЛЕНО: рисуем линии между точками полигона
                    if len(points) > 1:
                        painter.setPen(QPen(colors[j], 2))
                        for point_num in range(len(points) - 1):
                            point_start = QPoint(int(points[point_num][0]), int(points[point_num][1]))
                            point_end = QPoint(int(points[point_num + 1][0]), int(points[point_num + 1][1]))
                            painter.drawLine(point_start, point_end)

                        # Замыкающая линия (последняя -> первая)
                        painter.drawLine(
                            QPoint(int(points[-1][0]), int(points[-1][1])),
                            QPoint(int(points[0][0]), int(points[0][1]))
                        )

            painter.end()

            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

            # 👇 ДОБАВЛЕНО: обновляем информацию
            self.update_info()

    def image_mouse_press(self, event):
        """Обработка клика по изображению"""
        if not self.image:
            return

        # 👇 ИСПРАВЛЕНО: используем новый метод для координат
        x, y = self.get_image_coordinates(event)
        pixmap = self.image_label.pixmap()

        if pixmap:
            # 👇 ИСПРАВЛЕНО: проверяем точки в current_points
            for i, point in enumerate(self.current_points):
                distance = np.sqrt((x - point[0]) ** 2 + (y - point[1]) ** 2)
                if distance < self.point_radius * 2:
                    self.dragging_point = i
                    self.dragging_polygon = -1  # 👈 НОВОЕ: тащим из current
                    return

            # 👇 НОВОЕ: проверяем точки в полигонах
            for polygon_num, polygon in enumerate(self.polygons):
                for point_num, point in enumerate(polygon['points']):
                    distance = np.sqrt((x - point[0]) ** 2 + (y - point[1]) ** 2)
                    if distance < self.point_radius * 2:
                        self.dragging_polygon = polygon_num
                        self.dragging_point = point_num
                        return

            # Добавляем новую точку
            if event.button() == Qt.LeftButton:
                self.current_points.append((x, y))
                # 👇 УДАЛЕНО: self.points больше не используем
                # self.points.append((x, y))
                self.coords_label.setText(f"Точки: {len(self.current_points)}")
                self.display_image()

            elif event.button() == Qt.RightButton:
                # 👇 ИСПРАВЛЕНО: проверяем current_points, а не points
                if len(self.current_points) > 2:  # Минимум 3 точки для полигона
                    self.add_polygon_meta()
                self.display_image()
                self.update_polygons_list_widget()

    def image_mouse_move(self, event):
        """Обработка перемещения мыши"""
        if self.dragging_point >= 0 and self.image:
            x, y = self.get_image_coordinates(event)

            if self.dragging_polygon >= 0:
                # ✅ ПРАВИЛЬНО: тащим из сохраненного полигона
                self.polygons[self.dragging_polygon]['points'][self.dragging_point] = (x, y)
            else:
                # Тащим из текущего полигона
                self.current_points[self.dragging_point] = (x, y)

            self.display_image()

    def image_mouse_release(self, event):
        """Обработка отпускания кнопки мыши"""
        self.dragging_point = -1
        self.dragging_polygon = -1  # 👈 НОВОЕ: сбрасываем

    def clear_points(self):
        """Очистка всех точек"""
        # 👇 ИСПРАВЛЕНО: очищаем current_points, а не points
        self.current_points = []
        self.coords_label.setText("Точки: 0")
        if self.image:
            self.display_image()
        self.update_info()

    def update_info(self):
        """Добавляет только новые полигоны"""
        # 👇 СТАРЫЙ КОД (закомментирован):
        # current_count = self.scroll_layout.count() - 1
        # if len(self.current_points)>3:
        # self.coords_label.setText(f"Точки: {len(self.points)}")

        # 👇 НОВОЕ: обновляем счетчик точек
        self.coords_label.setText(f"Точки текущего полигона: {len(self.current_points)}")

    def resizeEvent(self, event):
        """Обработка изменения размера окна"""
        super().resizeEvent(event)
        if self.image:
            self.display_image()


    # 👇 НОВЫЙ МЕТОД: выбор полигона для редактирования
    def select_polygon(self, name:str):
        self.selected_polygon_widget.append(name)
    def clear_select_polygon(self):
        self.selected_polygon_widget.clear()

    def add_polygon_meta(self, name: str = 'noname'):
        # 👇 ИСПРАВЛЕНО: добавляем КОПИЮ точек, а не ссылку

        if name == 'noname':
            name = f'noname {str(len(self.polygons)+1)}'
        new_polygon = {
            'name': name,
            'points': self.current_points.copy(),
        }
        self.polygons.append(new_polygon)
        #print(self.polygons)
        print(f"Добавлен новый полигон: {new_polygon}")
        self.current_points.clear()
        self.current_color += 1


    def del_polygon_from_meta(self,name = 'error',del_all:bool = False):
        if del_all:
            self.polygons.clear()
        if isinstance(name, list):
            new_polygons = []

            for polygon in self.polygons:
                if polygon['name'] not in name:
                    new_polygons.append(polygon)

            self.polygons = new_polygons
        else:
            for i in self.polygons:
                if i['name'] == name:
                    self.polygons.remove(i)

    def del_polygon_from_widget(self, name = 'error', del_all: bool = False):
        """Удаление полигона из виджета по имени"""
        if del_all:
            # Очищаем виджеты (оставляем только stretch)
            while self.scroll_layout.count() > 1:
                item = self.scroll_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        if isinstance(name, list):
            # Удаляем по списку имен
            for i in range(self.scroll_layout.count() - 1, -1, -1):  # идем с конца
                item = self.scroll_layout.itemAt(i)
                if item and item.widget():
                    text_edit = item.widget().findChild(QLineEdit)
                    if text_edit and text_edit.text() in name:
                        item.widget().deleteLater()
                        self.scroll_layout.removeItem(item)
        else:
            # Удаляем виджет
            for i in range(self.scroll_layout.count()):
                item = self.scroll_layout.itemAt(i)
                if item and item.widget():
                    # Ищем QLineEdit с нужным текстом
                    text_edit = item.widget().findChild(QLineEdit)
                    if text_edit and text_edit.text() == name:
                        item.widget().deleteLater()
                        self.scroll_layout.removeItem(item)
                        break

        #self.display_image()

    def update_polygons_list_widget(self):
        self.del_polygon_from_widget(del_all=True)
        for i in range(len(self.polygons)):
            self.add_polygon_widget(self.polygons[i]['name'])

    def add_polygon_widget(self, name: str = 'error'):
        polygon_num = len(self.polygons)
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(1, 1, 1, 1)
        row_layout.setSpacing(5)

        # Кнопка
        btn = QPushButton()
        btn.setIcon(QIcon("../icons/edit"))
        btn.setIconSize(QSize(32, 32))
        btn.setFixedSize(30, 30)
        btn.setCheckable(True)
        btn.setStyleSheet("""
                        QPushButton {
                            font-size: 23px;
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

        # 👇 НОВОЕ: сохраняем индекс полигона в кнопке
        btn.clicked.connect(lambda checked, idx=polygon_num: self.select_polygon(name))

        # Текстовое поле
        text_edit = QLineEdit()
        text_edit.setFixedHeight(28)
        text_edit.setText(name)
        text_edit.setReadOnly(False)
        text_edit.setStyleSheet("""
                        QLineEdit {
                            font-size: 17px;
                            border-radius: 10px;
                            background-color: #2d2d2d;
                            color: white;
                        }
                    """)
        text_edit.setMinimumWidth(100)
        self.text_edits.append(text_edit)

        row_layout.addWidget(btn)
        row_layout.addWidget(text_edit)

        # 👇 ИСПРАВЛЕНО: вставляем перед stretch
        self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, row_widget)

    def debug(self):
        print(self.polygons)