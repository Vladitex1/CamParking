import os
from pathlib import Path
import numpy as np
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QPoint, QSize,QTimer
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QAction,QPolygon
import qtawesome as qta
import logic.file as file
import Editor.prod.data.style as style
from Editor.prod.data.properties import DockTitleBar     # если в data


class EditorWindow(QMainWindow):
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
        self.button_icon=[]
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
        self.image_label.setMinimumSize(100, 400)
        self.image_label.setProperty("window", "main")
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




        style.theme_signals.changed.connect(self.update_theme_buttons)
        self.update_theme_buttons()


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
        desired_size = style.STYLE["global"]["toolbar_icon_size_toolbar"]  # 16 * 1.5
        toolbar.setIconSize(QSize(desired_size, desired_size))


        actions_data = [
            ("Загрузить файл маски", "mdi6.folder-download", self.load_mask,"Alt+1"),
            ("Загрузить только полигоны маски", "mdi6.vector-polygon", lambda: (self.load_mask(only_poly = True)),"Alt+4"),
            ("Загрузить только изображение", "mdi6.image", self.load_image,"Alt+2"),
            ("Сохранить маску", "mdi6.content-save-edit", self.new_save_mask,"Alt+S"),
            ("Быстрое сохранение", "mdi6.content-save", self.fast_save_mask,"Alt+E"),
            ("Очистить рабочую область", "mdi6.eraser", self.clear_display,"Alt+Del"),
            ("Загрузить тестовое изображение", "mdi.flask", lambda: (
                self.manual_load_image(self.absolute_path("img/camphoto/camera_photo_2026-01-28.jpg")),),"Alt+3"),
        ]
        for name, icon_path, slot,shortcut in actions_data:
            action = QAction(self)
            action.setToolTip(name+" / "+shortcut)
            action.setShortcut(shortcut)
            action.triggered.connect(slot)
            toolbar.addAction(action)
            self.button_icon.append([action,icon_path,1.35])

    def update_theme_buttons(self):
        for button,icon_path,scale in self.button_icon:
            icon = qta.icon(icon_path, color=style.STYLE[style.current_color]["text_color"],
                            options=[{'scale_factor': scale, }])
            button.setIcon(icon)


    def create_statusbar(self):
        self.status_bar = QStatusBar(self)
        self.status_bar.setProperty("statusbar", "statusbar")
        self.status_bar.setSizeGripEnabled(False)
        self.setStatusBar(self.status_bar)

    def statusbar_show_temp_message(self, msg_type: str, success: bool, data=""):
        # Словарь с шаблонами сообщений
        templates = {
            "new_save": {
                True: f"Новое сохранение {data} создано успешно",
                False: f"Ошибка создания сохранения: {data}"
            },
            "fast_save": {
                True: f"Быстрое сохранение {data} выполнено успешно",
                False: f"Ошибка выполнения быстрого сохранения: {data}"
            },
            "load_image": {
                True: f"Изображение {data} создано успешно",
                False: f"Ошибка создания изображения: {data}"
            },
            "load_mask": {
                True: f"Маска {data} загружена",
                False: f"Ошибка загрузки маски: {data}"
            },
            "test_image": {
                True: f"Тестовое изображение {data} загружено",
                False: f"Ошибка загрузки тестового изображения: {data}"
            }
        }

        if msg_type not in templates:
            return

        text = templates[msg_type][success]
        emoji = "🟢" if success else "🔴"
        full_text = f"{emoji} - {text}"
        self.status_bar.showMessage(full_text, 5000)

    def on_dock_state_changed(self, *args):
        """Вызывается при изменении состояния дока (открепление/прикрепление/перемещение)"""
        # Откладываем обновление в конец очереди событий
        QTimer.singleShot(0, self.delayed_display)

    def delayed_display(self):
        """Отложенное обновление изображения"""
        if self.image:
            self.display_image()

    def create_dock(self,name:str="",position:str="left",content=None,
                    min_width:int = 100,max_width: int = 1000,
                    min_height:int = 100,max_height: int = 1000):
        dock = QDockWidget(name, self)
        dock.setTitleBarWidget(DockTitleBar(name, dock))
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setProperty("dock", "main")  # свойство для самого дока (опционально)

        # Содержимое док-окна

        dock.setWidget(content)
        dock.setStyleSheet(f"""
        QDockWidget{{
            min-width: {min_width}px;
            max-width: {max_width}px;
            min-height: {min_height}px;
            max-height: {max_height}px;
        }}
        """)
        dock.topLevelChanged.connect(self.on_dock_state_changed)
        dock.dockLocationChanged.connect(self.on_dock_state_changed)
        match position:
            case "left":
                self.addDockWidget(Qt.LeftDockWidgetArea, dock)
            case "right":
                self.addDockWidget(Qt.RightDockWidgetArea, dock)
            case _:
                self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def dock_help(self):
        # Содержимое докинг окна
        dock_content = QWidget()
        dock_content.setProperty("dock", "main")
        dock_content.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
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
        info_label.setProperty("dock", "main")
        info_label.setWordWrap(True)
        #info_label.setObjectName("dockMainContent")
        layout.addWidget(info_label)
        layout.addStretch()

        # Добавляем переключатель видимости докинга

        dock_content.setLayout(layout)

        self.create_dock(name ="Помощь",
                    position ="right",
                    content = dock_content,
                    min_width = 300,
                    max_width = 350,
                    min_height= 400,
                    max_height=1000,
        )

    def dock_editor(self):

        # Содержимое док-окна
        dock_content = QWidget()
        dock_content.setProperty("dock", "main")
        dock_content.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(dock_content)
        layout.setContentsMargins(30, 20, 15, 0)

        # Заголовок
        title_label = QLabel("Полигоны:")
        title_label.setProperty("dock", "main")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Виджет для прокручиваемого списка (внутренний)
        scroll_QWidget = QWidget()
        scroll_QWidget.setProperty("dock", "scroll")
        # Локально убираем фон и рамку у внутреннего виджета


        # Лейаут для списка полигонов
        scroll_QVBox = QVBoxLayout(scroll_QWidget)
        scroll_QVBox.setContentsMargins(5, 5, 5, 5)
        scroll_QVBox.setSpacing(5)
        scroll_QVBox.setAlignment(Qt.AlignTop)
        self.scroll_QVBox = scroll_QVBox

        # Растяжка в конце списка
        scroll_QVBox.addStretch()

        # Область прокрутки
        scroll_area = QScrollArea()
        scroll_area.setWidget(scroll_QWidget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Задаём фон, рамку и скругление для всей области
        scroll_QWidget.setProperty("dock", "scroll")
        scroll_area.setWidget(scroll_QWidget)

        layout.addWidget(scroll_area)

        # Кнопки действий
        actions_data = [
            ("Удалить выбранные", "mdi6.delete", lambda: (self.del_polygon(), self.display_image(), self.debug())),
        ]
        for name, icon_path, slot in actions_data:
            button = QPushButton(name)
            self.button_icon.append([button, icon_path, 1.0])
            if slot:
                button.clicked.connect(slot)
            button.setProperty("button", "st1")
            layout.addWidget(button)

        layout.addStretch()

        self.create_dock(
            name="Редактор",
            position="left",
            content=dock_content,
            min_width=300,
            max_width=650,
            min_height=400,
            max_height=1000,
        )
    def relative_path(self, input_filepath: str) -> str:
        result = os.path.relpath(input_filepath, self.project_root)
        return str(result)

    def absolute_path(self, input_filepath: str) -> str:
        result = os.path.join(self.project_root, input_filepath)
        return str(result)


    def load_image(self):
        """Загрузка изображения"""
        self.clear_display()
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
                        if len(self.current_points) > 9:
                            self.add_polygon_meta()
                            self.update_polygons_list_widget()
                case Qt.MiddleButton:
                    # Перебираем все полигоны
                    for polygon_num, polygon in enumerate(self.polygons):
                        points = polygon['points']  # список точек текущего полигона

                        # Перебираем все рёбра полигона (каждая точка соединяется со следующей)
                        for i in range(len(points)):
                            # Определяем конец ребра: если i последняя точка, то конец - первая точка (замыкаем полигон)
                            if i + 1 < len(points):
                                end_point = points[i + 1]  # следующая точка
                            else:
                                end_point = points[0]  # для последней точки конец - первая точка

                            start_point = points[i]  # начало ребра - текущая точка

                            x1, y1 = start_point  # координаты начала ребра
                            x2, y2 = end_point  # координаты конца ребра

                            # Вычисляем расстояние от точки (x,y) до прямой, проходящей через ребро
                            # cross - это площадь параллелограмма, образованного векторами ребра и вектором от начала до точки
                            cross = abs((y - y1) * (x2 - x1) - (y2 - y1) * (x - x1))
                            line_length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)  # длина ребра

                            if line_length > 0:  # защита от деления на ноль (ребро не нулевой длины)
                                # расстояние от точки до прямой = площадь / длину основания
                                distance_to_line = cross / line_length

                                # Скалярное произведение вектора (от начала до точки) и вектора ребра
                                dot_product = (x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)
                                squared_length = line_length ** 2  # квадрат длины ребра

                                if squared_length > 0:
                                    # параметр t показывает, где проекция точки падает на ребро:
                                    # t=0 - проекция на начало, t=1 - на конец, 0<t<1 - между ними
                                    t = dot_product / squared_length

                                    # Проверяем, что проекция точки попадает на ребро (с небольшим запасом -0.1..1.1)
                                    if -0.1 <= t <= 1.1:
                                        # Проверяем, что расстояние до прямой меньше порога (точка достаточно близка к ребру)
                                        if distance_to_line < self.point_radius * 2:
                                            # Проверяем, не совпадает ли точка с существующей вершиной полигона
                                            vertex_found = False
                                            for point in polygon['points']:  # перебираем все вершины
                                                # если координаты совпадают с точностью до 1 пикселя
                                                if abs(x - point[0]) < 1 and abs(y - point[1]) < 1:
                                                    vertex_found = True  # нашли совпадение
                                                    break

                                            if not vertex_found:  # если точка не совпадает ни с одной вершиной
                                                print(f"точка x,y лежит между {self.polygons[polygon_num]['name']}")
                                                # Ищем позицию, куда вставить новую точку
                                                for num in range(len(self.polygons[polygon_num]['points'])):
                                                    # Вставляем после start_point
                                                    if self.polygons[polygon_num]['points'][num] == start_point:
                                                        self.polygons[polygon_num]['points'].insert(num + 1, (x, y))
                                                        break
                                            break  # выходим из цикла по рёбрам, если нашли подходящее
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

    def dockEvent(self, event):
        self.display_image()

    def remap_id(self):
        data = self.polygons
        for num,i in enumerate(self.polygons):
            data[num]['id'] = num
        self.polygons = data


    def get_ids_from_widget(self):
        self.checked_widgets = []
        for i in range(self.scroll_QVBox.count()):
            item = self.scroll_QVBox.itemAt(i)
            if item and item.widget():
                checkbox = item.widget().findChild(QCheckBox)
                a = item.widget().findChild(QLabel)
                if checkbox.isChecked():
                    self.checked_widgets.append(int(a.text()))
        return self.checked_widgets


    def load_mask(self,only_poly:bool=False):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите маску", "../../save",
            "Маски (*.mask)"
        )
        if file_path != '':
            saved_data, parent_file = file.load_data(file_path)
            if only_poly == False:
                self.clear_display()
                for id, i in enumerate(saved_data):
                    self.add_polygon_meta(name=i['name'], points=i['points'])
                    self.add_polygon_widget(name=i['name'], id=id)
                self.manual_load_image(path=self.absolute_path(parent_file))
            else:
                for id, i in enumerate(saved_data):
                    self.add_polygon_meta(name=i['name'], points=i['points'])
                    self.add_polygon_widget(name=i['name'], id=id)
                self.display_image()


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
        try:
            path = self.relative_path(self.image_path)
            correct,error = file.save_data(saved_data, self.loaded_mask, path)
            if correct:
                self.statusbar_show_temp_message("fast_save", True, path)
            else:
                self.statusbar_show_temp_message("fast_save", False, error)

            print(f"Быстрое сохранение: {self.loaded_mask}")
        except Exception as error:
            e = str(error)
            self.statusbar_show_temp_message("fast_save", False, e)


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
            while self.scroll_QVBox.count() > 1:
                item = self.scroll_QVBox.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        if isinstance(id, list):
            for i in range(self.scroll_QVBox.count() - 1, -1, -1):
                item = self.scroll_QVBox.itemAt(i)
                if item and item.widget():
                    label = item.widget().findChild(QLabel)
                    if label and label.text() in str(id):
                        item.widget().deleteLater()
                        self.scroll_QVBox.removeItem(item)
        else:
            for i in range(self.scroll_QVBox.count()):
                item = self.scroll_QVBox.itemAt(i)
                if item and item.widget():
                    label = item.widget().findChild(QLabel)
                    if label and label.text() == str(id):
                        item.widget().deleteLater()
                        self.scroll_QVBox.removeItem(item)
                        break


    def update_polygons_list_widget(self):
        self.del_polygon_from_widget(del_all=True)
        for i in range(len(self.polygons)):
            self.add_polygon_widget(self.polygons[i]['name'], self.polygons[i]['id'])


    def add_polygon_widget(self, name: str = 'error', id:int = -1):
        polygon_num = id
        row_widget = QWidget()
        row_widget.setProperty("dock", "polygon_slot")
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(1, 1, 1, 1)
        row_layout.setSpacing(2)

        meta = QLabel(f"{id}")
        meta.setStyleSheet(f"""
        min-height: 20px;
        min-width: 20px;
        border-radius: {style.STYLE["global"]["style_border_radius"]};
        """)
        meta.setVisible(self.debugbool)
        # !!! Удалён локальный stylesheet для meta

        meta.setAlignment(Qt.AlignCenter)

        btn = QCheckBox()

        # !!! Удалён локальный stylesheet для btn

        text_edit = QLineEdit()
        text_edit.setFixedHeight(28)
        text_edit.setText(name)
        text_edit.setReadOnly(False)
        # !!! Удалён локальный stylesheet для text_edit

        text_edit.textChanged.connect(lambda text, idx=int(meta.text()): self.rename_polygon(text, idx))
        text_edit.setMinimumWidth(100)



        row_layout.addWidget(meta)
        #spacer.setStyleSheet(f"pading: 8px; background-color: {style.STYLE["global"]["accent_color"]};")
        #row_layout.addWidget(spacer)
        #row_layout.setStyleSheet(f"border-radius: 8px;")

        row_layout.addWidget(btn)
        row_layout.addWidget(text_edit)

        self.scroll_QVBox.insertWidget(self.scroll_QVBox.count() - 1, row_widget)


    def debug(self):
        print("==================")
        for i in self.polygons:
            print(f"{i['id']} | {i['name']} | {i['points']}")
        print(self.polygons)
        print(self.loaded_mask)
        self.display_image()