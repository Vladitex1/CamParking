import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QPoint, QRect, QSize, QLine
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QAction, QImage, QIcon, QPolygon, QPolygonF
import numpy as np
import logic.file as file
import os
from PySide6 import QtGui
import qtawesome as qta
from pathlib import Path
from PySide6.QtWidgets import QStatusBar, QLabel, QProgressBar, QPushButton
from PySide6.QtCore import QTimer, QDateTime
from PySide6.QtGui import QFont
import Editor.prod.data.style as style
from Editor.prod.data.properties import DockTitleBar     # если в data


class ImageDockWidget(QMainWindow):
    """Виджет для отображения изображения и расстановки точек"""

    def __init__(self):
        super().__init__()
        '''
            line_size = толщина линий
            point_size = размер точек
            text_size = размер текста у точек
            new_color = цвет, при новом полигоне
            alpha = прозрачность заполнения 0 - 255
        '''
        self.line_size = 3
        self.point_size = 7
        self.text_size = 25
        self.new_color = 4
        self.alpha = 80

        self.debugbool = False
        self.checked_widgets = []

        self.image = None
        self.points = []  # Список точек [(x, y), ...]  👈 СТАРОЕ: использовалось и для текущих, и для сохраненных
        self.polygons = []  # Список полигонов, каждый полигон = список точек
        self.current_points = []  # 👈 НОВОЕ: точки текущего редактируемого полигона

        self.dragging_point = -1
        self.dragging_polygon = -1  # 👈 НОВОЕ: индекс полигона, точку которого тащим
        self.current_color = 0

        self.image_path = ""
        self.project_root = str(Path(__file__).parent.parent.parent.parent.resolve())
        self.loaded_mask:str = ""
        # ===== ВАЖНО: СОЗДАЕМ ЦЕНТРАЛЬНЫЙ ВИДЖЕТ =====
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Главный layout для центрального виджета
        main_layout = QVBoxLayout(central_widget)

        # Создаем метку для отображения изображения
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setStyleSheet("border: 1px solid gray;")  # оставляем локально (можно перенести в общий стиль при желании)
        main_layout.addWidget(self.image_label)

        # Создаем кнопки
        self.coords_label = QLabel("Точки: 0")
        self.create_statusbar()
        self.create_toolbar()
        self.dock_editor()
        self.dock_help()



        # !!! Удалён локальный stylesheet для status_bar

        # Устанавливаем обработчик событий мыши для метки
        self.image_label.mousePressEvent = self.image_mouse_press
        self.image_label.mouseMoveEvent = self.image_mouse_move
        self.image_label.mouseReleaseEvent = self.image_mouse_release

        # ========== ПРИМЕНЯЕМ ЕДИНЫЙ СТИЛЬ КО ВСЕМУ ОКНУ ==========
        #self.setStyleSheet(style.STYLESHEET_GREEN)

    # Обработчик кнопки – показывает временное сообщение и меняет цвет индикатора


    def clear_display(self):
        self.current_points:list = []
        self.points:list = []
        self.polygons:list = []
        self.del_polygon_from_widget(del_all=True)
        self.del_polygon_from_meta(del_all=True)
        self.image = QPixmap(800, 600)
        self.image.fill(Qt.transparent)
        self.display_image()
        self.image_path:str = ""
        self.loaded_mask:str = ""
        self.remap_id()
        self.update_polygons_list_widget()
        self.image = None

    def create_toolbar(self):


        toolbar = QToolBar("Панель инструментов")
        self.addToolBar(toolbar)
        toolbar.setProperty("toolbar", "toolbar")

        actions_data = [
            ("load_mask", "mdi6.vector-polygon", self.load_mask),
            ("load_image", "mdi6.image", self.load_image),
            ("save_mask", "mdi6.content-save-edit", self.new_save_mask),
            ("fast_save", "mdi6.content-save", self.fast_save_mask),
            ("clear", "mdi6.eraser", self.clear_display),
            ("manual", "mdi.flask", lambda: (
                self.manual_load_image(self.absolute_path("img/camphoto/camera_photo_2026-01-28.jpg")),)),
        ]

        for name, icon_path, slot in actions_data:
            action = QAction(self)
            action.setIcon(qta.icon(icon_path, color=style.STYLE[style.current_color]["text_color"]))
            action.triggered.connect(slot)
            toolbar.addAction(action)


    def create_statusbar(self):
        self.status_bar = QStatusBar(self)
        self.status_bar.setProperty("statusbar", "statusbar")
        self.setStatusBar(self.status_bar)

    def statusbar_show_temp_message(self, msg_type: str, success: bool, data=None):
        # Словарь с шаблонами сообщений
        templates = {
            "new_save": {
                True: f"Новое сохранение {data} создано успешно",
                False: "Ошибка создания сохранения"
            },
            "fast_save": {
                True: f"Быстрое сохранение {data} выполнено успешно",
                False: "Ошибка выполнения быстрого сохранения"
            },
            "load_image": {
                True: f"Изображение {data} создано успешно",
                False: "Ошибка создания изображения"
            },
            "load_mask": {
                True: f"Маска {data} загружена",
                False: "Ошибка загрузки маски"
            },
            "test_image": {
                True: f"Тестовое изображение {data} загружено",
                False: "Ошибка загрузки тестового изображения"
            }
        }

        if msg_type not in templates:
            return

        text = templates[msg_type][success]
        emoji = "🟢" if success else "🔴"
        full_text = f"{emoji} - {text}"
        self.status_bar.showMessage(full_text, 5000)


    def dock_help(self):
        dock = QDockWidget("Помощь", self)
        dock.setTitleBarWidget(DockTitleBar("Помощь", dock))
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setProperty("dock", "help")

        # Содержимое докинг окна
        dock_content = QWidget()
        #dock_content.setObjectName("dockMainContent")
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 15, 0)

        info_label = QLabel(
            """
            <h2>🤿 Редактор масок</h2>

            <h3>Управление:</h3>
            <ul>
                <li>ЛКМ - Создание новой точки</li>
                <li>СКМ - Добавление точки в маску</li>
                <li>ПКМ - Завершить полигон</li>
            </ul>
            <p><i>Создано с использованием PySide6</i></p>
            """
        )
        info_label.setWordWrap(True)
        #info_label.setObjectName("dockMainContent")
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



    def dock_editor(self):
        EditorDock = QDockWidget("Полигоны", self)
        EditorDock.setTitleBarWidget(DockTitleBar("Полигоны", EditorDock))
        EditorDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        EditorDock.setProperty("dock", "main")

        dock_content = QWidget()
        #dock_content.setObjectName("dockMainContent")

        layout = QVBoxLayout(dock_content)

        # === ГРУППА ПОЛИГОНОВ ===
        polygon_group = QGroupBox()
        polygon_group.setMinimumHeight(300)
        polygon_group.setMinimumWidth(50)

        title_label = QLabel("Полигоны:")
        #title_label.setObjectName("dockMainContent")
        title_label.setStyleSheet(
            "font-size: 18px; font-weight: bold;")  # оставляем локальный стиль (можно заменить на объектное имя)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        scroll_content = QWidget()
        #scroll_content.setObjectName("dock_main_scroll_widget")
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

        actions_data = [
            ("Удалить выбранные", "mdi6.delete", (lambda: (self.del_polygon(),
                                      self.display_image(),
                                      self.debug()))),
            ("Скрыть всё", "mdi6.eye", None),
            ("Показать все", "mdi6.eye-off", None),
            ("Дебаг", "mdi.access-point", lambda: (self.debug(),)),
        ]
        for name, icon_path, slot in actions_data:
            button=QPushButton(name)
            button.setIcon(qta.icon(icon_path, color=style.STYLE[style.current_color]["text_color"]))
            if slot != None:
                button.clicked.connect(slot)
            button.setProperty("button", "st1")
            layout.addWidget(button)

        layout.addStretch()

        EditorDock.setWidget(dock_content)
        EditorDock.setProperty("dock", "main")


        self.addDockWidget(Qt.LeftDockWidgetArea, EditorDock)

    def relative_path(self, input_filepath: str) -> str:
        result = os.path.relpath(input_filepath, self.project_root)
        return str(result)

    def absolute_path(self, input_filepath: str) -> str:
        result = os.path.join(self.project_root, input_filepath)
        return str(result)


    def load_image(self):
        """Загрузка изображения"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "../../img",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        print(filename)
        self.manual_load_image(filename)


    def manual_load_image(self, path:str):
        """Загрузка изображения"""
        if path:
            if not os.path.exists(path):
                print("ошибка загрузки изображения: изображение не существует ",path)
                self.statusbar_show_temp_message("load_image", False, path)
                return
            elif os.path.exists(path):
                print("успешная загрузка изображения ",path)
                self.statusbar_show_temp_message("load_image", True, path)
                self.image_path = path
                self.image = QPixmap(path)
                self.display_image()


    def get_image_coordinates(self, event):
        """Преобразует координаты клика в координаты изображения"""
        if not self.image_label.pixmap():
            return (0, 0)

        label_pos = event.position()
        label_rect = self.image_label.rect()
        pixmap_rect = self.image_label.pixmap().rect()
        image_size = self.image.size()

        offset_x = max(0, (label_rect.width() - pixmap_rect.width()) / 2)
        offset_y = max(0, (label_rect.height() - pixmap_rect.height()) / 2)

        scale_x = image_size.width() / pixmap_rect.width()
        scale_y = image_size.height() / pixmap_rect.height()

        x = (label_pos.x() - offset_x) * scale_x
        y = (label_pos.y() - offset_y) * scale_y

        return (x, y)


    def check_polygons_is_correct(self):
        for num,i in enumerate(self.polygons):
            if len(self.polygons[num]['points']) <= 1:
                self.polygons.pop(num)
        self.update_polygons_list_widget()


    def display_image(self):
        line_size = self.line_size
        point_size = self.point_size
        text_size = self.text_size
        new_color = self.new_color
        alpha = self.alpha

        self.point_radius = point_size

        self.check_polygons_is_correct()
        """Отображение изображения с точками"""

        if self.image != None:
            pixmap = self.image.copy()
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            colors = [
                QColor(255, 0, 0),  # красный
                QColor(255, 165, 0),  # оранжевый
                QColor(255, 255, 0),  # жёлтый
                QColor(0, 255, 0),  # зелёный
                QColor(0, 191, 255),  # голубой (deep sky blue)
                QColor(0, 0, 255),  # синий
                QColor(238, 130, 238)  # фиолетовый (violet)
            ]
            text_font = painter.font()
            text_font.setPointSize(text_size)
            painter.setFont(text_font)

            if self.current_points:
                for num, point in enumerate(self.current_points):
                    painter.setPen(QPen(colors[new_color], line_size))
                    painter.setBrush(QBrush(colors[new_color]))
                    pos_x = int(point[0])
                    pos_y = int(point[1])
                    painter.drawEllipse(QPoint(pos_x, pos_y), point_size, point_size)
                    painter.drawText(pos_x + 10, pos_y - 10, f"P{num + 1}")

                    points = self.current_points
                    if len(points) > 1:
                        painter.setPen(QPen(colors[new_color], line_size))
                        for point_num in range(len(points) - 1):
                            point_start = QPoint(int(points[point_num][0]), int(points[point_num][1]))
                            point_end = QPoint(int(points[point_num + 1][0]), int(points[point_num + 1][1]))
                            painter.drawLine(point_start, point_end)

            if self.polygons:
                for i, data in enumerate(self.polygons):
                    num = i % len(colors)
                    points = data['points']
                    for point_num, point in enumerate(points):
                        painter.setPen(QPen(colors[num], line_size))
                        painter.setBrush(QBrush(colors[num]))
                        pos_x = int(point[0])
                        pos_y = int(point[1])
                        painter.drawEllipse(QPoint(pos_x, pos_y), point_size, point_size)
                        painter.drawText(pos_x + 10, pos_y - 10, f"P{i + 1}-{point_num + 1}")

                    if len(points) >= 2:
                        polygon = QPolygon()
                        for pt in points:
                            polygon.append(QPoint(pt[0], pt[1]))

                        fill_color = QColor(colors[num])
                        fill_color.setAlpha(alpha)
                        painter.setBrush(QBrush(fill_color))
                        painter.drawPolygon(polygon)

            painter.end()

            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)


    def image_mouse_press(self, event):
        """Обработка клика по изображению"""
        if not self.image:
            return

        x, y = self.get_image_coordinates(event)
        x = int(x)
        y = int(y)
        pixmap = self.image_label.pixmap()

        if pixmap:
            match event.button():
                case Qt.LeftButton:
                    clicked = False
                    for i, point in enumerate(self.current_points):
                        distance = np.sqrt((x - point[0]) ** 2 + (y - point[1]) ** 2)
                        if distance < self.point_radius * 2:
                            self.dragging_point = i
                            self.dragging_polygon = -1
                            clicked = True
                            break
                    if not clicked:
                        for polygon_num, polygon in enumerate(self.polygons):
                            for point_num, point in enumerate(polygon['points']):
                                distance = np.sqrt((x - point[0]) ** 2 + (y - point[1]) ** 2)
                                if distance < self.point_radius * 2:
                                    self.dragging_polygon = polygon_num
                                    self.dragging_point = point_num
                                    clicked = True
                                    break
                    if not clicked:
                        self.current_points.append((x, y))
                        self.coords_label.setText(f"Точки: {len(self.current_points)}")
                case Qt.MiddleButton:
                    for polygon_num, polygon in enumerate(self.polygons):
                        points = polygon['points']
                        for i in range(len(points)):
                            if i + 1 < len(points):
                                end_point = points[i + 1]
                            else:
                                end_point = points[0]
                            start_point = points[i]

                            x1, y1 = start_point
                            x2, y2 = end_point

                            cross = abs((y - y1) * (x2 - x1) - (y2 - y1) * (x - x1))
                            line_length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

                            if line_length > 0:
                                distance_to_line = cross / line_length
                                dot_product = (x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)
                                squared_length = line_length ** 2

                                if squared_length > 0:
                                    t = dot_product / squared_length
                                    if -0.1 <= t <= 1.1:
                                        if distance_to_line < self.point_radius * 2:
                                            print(f"точка x,y лежит между {self.polygons[polygon_num]['name']}")
                                            for num in range(len(self.polygons[polygon_num]['points'])):
                                                if self.polygons[polygon_num]['points'][num] == start_point:
                                                    self.polygons[polygon_num]['points'].insert(num + 1, (x, y))
                                                    break
                case Qt.RightButton:
                    for polygon_num, polygon in enumerate(self.polygons):
                        for point_num, point in enumerate(polygon['points']):
                            distance = np.sqrt((x - point[0]) ** 2 + (y - point[1]) ** 2)
                            if distance < self.point_radius * 2:
                                self.polygons[polygon_num]['points'].pop(point_num)
                                break
                    if len(self.current_points) > 3:
                        self.add_polygon_meta()

            self.update_polygons_list_widget()
            self.display_image()


    def image_mouse_move(self, event):
        """Обработка перемещения мыши"""
        if self.dragging_point >= 0 and self.image:
            x, y = self.get_image_coordinates(event)
            x = int(x)
            y = int(y)
            if self.dragging_polygon >= 0:
                self.polygons[self.dragging_polygon]['points'][self.dragging_point] = (x, y)
            else:
                self.current_points[self.dragging_point] = (x, y)

            self.display_image()


    def image_mouse_release(self, event):
        """Обработка отпускания кнопки мыши"""
        self.dragging_point = -1
        self.dragging_polygon = -1


    def clear_points(self):
        """Очистка всех точек"""
        self.current_points = []
        self.coords_label.setText("Точки: 0")
        if self.image:
            self.display_image()


    def resizeEvent(self, event):
        """Обработка изменения размера окна"""
        super().resizeEvent(event)
        if self.image:
            self.display_image()


    def remap_id(self):
        data = self.polygons
        for num,i in enumerate(self.polygons):
            data[num]['id'] = num
        self.polygons = data


    def get_ids_from_widget(self):
        self.checked_widgets = []
        for i in range(self.scroll_layout.count()):
            item = self.scroll_layout.itemAt(i)
            if item and item.widget():
                checkbox = item.widget().findChild(QCheckBox)
                a = item.widget().findChild(QLabel)
                if checkbox.isChecked():
                    self.checked_widgets.append(int(a.text()))
        return self.checked_widgets


    def load_mask(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите маску", "../../save",
            "Маски (*.mask)"
        )
        saved_data, parent_file = file.load_data(file_path)
        for id,i in enumerate(saved_data):
            self.add_polygon_meta(name=i['name'], points=i['points'])
            self.add_polygon_widget(name=i['name'], id=id)
        self.manual_load_image(path=self.absolute_path(parent_file))
        self.loaded_mask = file_path
        print("_____")
        print(parent_file)


    def new_save_mask(self):
        self.loaded_mask, _ = QFileDialog.getSaveFileName(
            caption="Сохранить маску",
            dir="../../save",
            filter="Маски (*.mask)"
        )

        if self.loaded_mask:
            if not self.loaded_mask.endswith('.mask'):
                self.loaded_mask += '.mask'

            saved_data = []
            for polygon in self.polygons:
                saved_data.append({
                    "name": polygon['name'],
                    "points": polygon['points']
                })
            print(self.relative_path(self.image_path),"хуй",self.image_path)
            file.save_data(saved_data, self.loaded_mask,  self.relative_path(self.image_path))
            print(f"Маска сохранена: {self.loaded_mask}")


    def fast_save_mask(self):
        saved_data = []
        for polygon in self.polygons:
            saved_data.append({
                "name": polygon['name'],
                "points": polygon['points']
            })
        correct: bool = False
        file.save_data(saved_data, self.loaded_mask, self.relative_path(self.image_path))
        print(f"Быстрое сохранение: {self.loaded_mask}")


    def add_polygon_meta(self, name: str = 'noname', points=None):
        if points is None:
            points = self.current_points
        print(points)
        new_polygon = {
            'id': len(self.polygons),
            'name': name,
            'points': points.copy(),
        }
        self.polygons.append(new_polygon)
        print(f"Добавлен новый полигон: {new_polygon}")
        self.current_points.clear()


    def del_polygon(self):
        data = self.get_ids_from_widget()
        self.del_polygon_from_meta(data)
        self.del_polygon_from_widget(data)
        self.remap_id()
        self.update_polygons_list_widget()


    def rename_polygon(self, new_name: str, id:int):
        for i in self.polygons:
            if i['id'] == id:
                i['name'] = new_name


    def del_polygon_from_meta(self, id = None, del_all:bool = False):
        if del_all:
            self.polygons.clear()
        if isinstance(id, list):
            new_polygons = []
            for polygon in self.polygons:
                if polygon['id'] not in id:
                    new_polygons.append(polygon)
            self.polygons = new_polygons
        else:
            for i in self.polygons:
                if i['id'] == id:
                    self.polygons.remove(i)


    def del_polygon_from_widget(self, id = None, del_all: bool = False):
        """Удаление полигона из виджета по имени"""
        if del_all:
            while self.scroll_layout.count() > 1:
                item = self.scroll_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        if isinstance(id, list):
            for i in range(self.scroll_layout.count() - 1, -1, -1):
                item = self.scroll_layout.itemAt(i)
                if item and item.widget():
                    label = item.widget().findChild(QLabel)
                    if label and label.text() in str(id):
                        item.widget().deleteLater()
                        self.scroll_layout.removeItem(item)
        else:
            for i in range(self.scroll_layout.count()):
                item = self.scroll_layout.itemAt(i)
                if item and item.widget():
                    label = item.widget().findChild(QLabel)
                    if label and label.text() == str(id):
                        item.widget().deleteLater()
                        self.scroll_layout.removeItem(item)
                        break


    def update_polygons_list_widget(self):
        self.del_polygon_from_widget(del_all=True)
        for i in range(len(self.polygons)):
            self.add_polygon_widget(self.polygons[i]['name'], self.polygons[i]['id'])


    def add_polygon_widget(self, name: str = 'error', id:int = -1):
        polygon_num = id
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(1, 1, 1, 1)
        row_layout.setSpacing(5)

        meta = QLabel()
        meta.setText(str(id))
        meta.setFixedSize(30, 30)
        meta.setVisible(self.debugbool)
        # !!! Удалён локальный stylesheet для meta

        meta.setAlignment(Qt.AlignCenter)
        btn = QCheckBox()
        btn.setCheckable(True)
        btn.setIcon(QIcon("../icons/edit"))
        btn.setIconSize(QSize(24, 24))
        btn.setFixedSize(30, 30)
        # !!! Удалён локальный stylesheet для btn

        text_edit = QLineEdit()
        text_edit.setFixedHeight(28)
        text_edit.setText(name)
        text_edit.setReadOnly(False)
        # !!! Удалён локальный stylesheet для text_edit

        text_edit.textChanged.connect(lambda text, idx=int(meta.text()): self.rename_polygon(text, idx))
        text_edit.setMinimumWidth(100)
        self.text_edits.append(text_edit)

        row_layout.addWidget(meta)
        row_layout.addWidget(btn)
        row_layout.addWidget(text_edit)

        self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, row_widget)


    def debug(self):
        print("==================")
        for i in self.polygons:
            print(f"{i['id']} | {i['name']} | {i['points']}")
        print(self.polygons)
        print(self.loaded_mask)