import os
from pathlib import Path
import numpy as np
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QPoint, QSize, QTimer, QEvent,QThread, Signal
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QAction, QPolygon, QPainterPath
import qtawesome as qta
import logic.file as file
import logic.camera_control as camera_control
import Editor.prod.data.style as style
from Editor.prod.data.properties import DockTitleBar     # если в data
import Editor.prod.data.names as names
from Editor.prod.data.signal_bus import signal
import asyncio

class CaptureImageThread(QThread):
    image_ready = Signal(str)
    def __init__(self, capture_func):
        super().__init__()
        self.capture_func = capture_func   # функция, которая возвращает путь к файлу

    def run(self):
        try:
            # Вызываем синхронную функцию получения изображения
            # Если функция асинхронная, нужно запускать свой event loop
            path = self.capture_func()
            self.image_ready.emit(path)
        except Exception as e:
            print(f"Ошибка захвата: {e}")
            self.image_ready.emit(None)


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
        self.name = names.NAMES[names.get_language()]
        self.line_size = 3
        self.point_size = 7
        self.text_size = 25
        self.new_color = 4
        self.alpha = 80
        self.max_points_in_polygon: int = 9

        self.button_icon=[]
        self.widget_buttons=[]
        self.IsDebug = False
        self.checked_widgets = []

        self.image = None
        self.points = []  # Список точек [(x, y), ...]  👈 СТАРОЕ: использовалось и для текущих, и для сохраненных
        self.polygons = []  # Список полигонов, каждый полигон = список точек
        self.current_points = []  # 👈 НОВОЕ: точки текущего редактируемого полигона

        self.dragging_point = -1
        self.dragging_polygon = -1  # 👈 НОВОЕ: индекс полигона, точку которого тащим
        self.dragging_polygon_whole = -1  # 👈 НОВОЕ: индекс полигона, который тащим целиком
        self.drag_offset_x = 0  # 👈 НОВОЕ: смещение по X при захвате
        self.drag_offset_y = 0  # 👈 НОВОЕ: смещение по Y при захвате



        self.current_color = 0
        self.colors = [
            "#FF0000",  # красный
            "#FFA500",  # оранжевый
            "#FFFF00",  # жёлтый
            "#00FF00",  # зелёный
            "#00BFFF",  # голубой
            "#0000FF",  # синий
            "#EE82EE",  # фиолетовый
        ]


        self.image_path = ""
        self.project_root = str(Path(__file__).parent.parent.parent.parent.resolve())
        self.loaded_mask:str = ""
        # ===== ВАЖНО: СОЗДАЕМ ЦЕНТРАЛЬНЫЙ ВИДЖЕТ =====
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.capture_thread = None
        # Главный layout для центрального виджета
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignCenter)
        asd = central_widget.size()
        print(asd)
        # Создаем метку для отображения изображения
        self.image_label = QLabel()
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        #self.image_label.setAlignment(Qt.AlignCenter)  # ← Явное центрирование
        self.image_label.setProperty("window", "main")
        main_layout.addWidget(self.image_label, stretch=1)  # ← stretch=1 заставляет занимать всё место

        # Создаем кнопки

        self.create_toolbar()
        self.dock_editor()
        self.dock_help()
        self.create_statusbar()
        self.StatusBarLabelUpdate(coords=None,mask=None)


        # !!! Удалён локальный stylesheet для status_bar

        # Устанавливаем обработчик событий мыши для метки
        self.image_label.mousePressEvent = self.image_mouse_press
        self.image_label.mouseMoveEvent = self.image_mouse_move
        self.image_label.mouseReleaseEvent = self.image_mouse_release

        # ✅ Подключение сигнала
        signal.update_display.connect(self.update_display)
        signal.changed.connect(self.update_theme_buttons)
        self.update_theme_buttons()


    # Обработчик кнопки – показывает временное сообщение и меняет цвет индикатора


    def clear_display(self,is_img_del:bool=False):
        self.current_points:list = []
        self.points:list = []
        self.polygons:list = []
        self.del_polygon_from_widget(del_all=True)
        self.del_polygon_from_meta(del_all=True)
        if is_img_del:
            self.image = QPixmap(800, 600)
            self.image.fill(Qt.transparent)
            self.image_path: str = ""
        self.update_display()
        if is_img_del:
            self.image = None
        self.loaded_mask:str = ""
        self.remap_id()
        self.update_polygons_list_widget()

        self.StatusBarLabelUpdate(coords=None,mask=None)

    def capture_image(self):
        if self.capture_thread and self.capture_thread.isRunning():
            return
        self.capture_thread = CaptureImageThread(camera_control.get_img_sync)
        self.capture_thread.image_ready.connect(self.on_image_captured)
        self.capture_thread.start()

    def on_image_captured(self, image_path):
        if image_path and os.path.exists(image_path):
            self.manual_load_image(image_path, True)
        else:
            print("Не удалось получить фото с камеры")

    def create_toolbar(self):
        toolbar = QToolBar(self.name["editor.toolbar.title"])
        self.addToolBar(toolbar)
        toolbar.setProperty("toolbar", "toolbar")

        actions_data = [
            (self.name["editor.toolbar.load.file"], "mdi6.folder-download", self.load_mask,"Alt+1"),
            (self.name["editor.toolbar.load.mask"], "mdi6.vector-polygon", lambda: (self.load_mask(only_poly = True)),"Alt+4"),
            (self.name["editor.toolbar.load.image"], "mdi6.image", self.load_image,"Alt+2"),
            (self.name["editor.toolbar.save.as"], "mdi6.content-save-edit", self.new_save_mask,"Alt+S"),
            (self.name["editor.toolbar.save.fast"], "mdi6.content-save", self.fast_save_mask,"Alt+E"),
            (self.name["editor.toolbar.clear"], "mdi6.delete", lambda: (self.clear_display(True)),"Alt+Del"),
            (self.name["editor.toolbar.test.image"], "mdi6.flask", lambda: (self.manual_load_image(self.absolute_path("img/camphoto/camera_photo_2026-01-28.jpg"),True)),"Alt+3"),
            (self.name["editor.toolbar.capture.image"], "mdi6.camera-image", self.capture_image, "Ctrl+Alt+4"),
        ]
        for name, icon_path, slot,shortcut in actions_data:
            action = QAction(self)
            action.setToolTip(name+" / "+shortcut)
            action.setShortcut(shortcut)
            action.triggered.connect(slot)
            toolbar.addAction(action)
            self.button_icon.append([action,icon_path,1.1])

    def update_theme_buttons(self):
        for button,icon_path,scale in self.button_icon:
            icon = qta.icon(icon_path, color=style.STYLE[style.current_color]["text_color"],
                            options=[{'scale_factor': scale, }])
            button.setIcon(icon)

    def StatusBarLabelUpdate(self,coords:int=-1,mask:str="-1"):
        if coords != -1:
            if coords is None:
                self.coords_label.setText(f"📍 {self.name["editor.statusbar.point.false"]}")
            else:
                self.coords_label.setText(f"📍 {self.name["editor.statusbar.point.true"]}{coords}/{self.max_points_in_polygon+1}")
        if mask != "-1":
            if mask is None:
                self.mask_name_label.setText(f"📁 {self.name["editor.statusbar.mask.false"]}")
            else:
                self.mask_name_label.setText(f"📁 {self.name["editor.statusbar.mask.true"]}{mask}")

    def create_statusbar(self):
        self.status_bar = QStatusBar(self)
        self.status_bar.setProperty("statusbar", "statusbar")
        self.status_bar.setSizeGripEnabled(False)

        # ===== КОНТЕЙНЕР ДЛЯ ФИКСИРОВАННЫХ ДАННЫХ =====
        self.status_container = QWidget()  # ✅ Сохраняем ссылку на контейнер
        self.status_container.setProperty("statusbar", "container")  # ✅ Свойство для стилизации
        status_layout = QHBoxLayout(self.status_container)
        status_layout.setContentsMargins(10, 0, 10, 0)  # ✅ Отступы внутри контейнера
        status_layout.setSpacing(20)
        status_layout.addStretch()
        # Виджет 1: Счётчик точек
        self.coords_label = QLabel()
        self.coords_label.setProperty("statusbar", "label")  # ✅ Свойство для лейбла
        status_layout.addWidget(self.coords_label)

        # Разделитель
        separator = QLabel("│")
        separator.setProperty("statusbar", "separator")
        status_layout.addWidget(separator)

        # Виджет 2: Название маски
        self.mask_name_label = QLabel()
        self.mask_name_label.setProperty("statusbar", "label")
        status_layout.addWidget(self.mask_name_label)

        separator = QLabel(" ")
        separator.setProperty("statusbar", "separator")
        status_layout.addWidget(separator)


        self.status_bar.addPermanentWidget(self.status_container, stretch=0)
        self.setStatusBar(self.status_bar)


    def statusbar_show_temp_message(self, msg_type: str, success: bool, data=""):
        # Словарь с шаблонами сообщений
        templates = {
            "load_mask": {
                True: self.name["editor.statusbar.load.mask"],
                False: self.name["editor.statusbar.error"],
            },
            "load_image": {
                True: self.name["editor.statusbar.load.image"],
                False: self.name["editor.statusbar.error"],
            },
            "new_save": {
                True: self.name["editor.statusbar.save.as"],
                False: self.name["editor.statusbar.error"],
            },
            "fast_save": {
                True: self.name["editor.statusbar.save.fast"],
                False: self.name["editor.statusbar.error"],
            },
            "test_image": {
                True: self.name["editor.statusbar.test.image"],
                False: self.name["editor.statusbar.error"],
            },

        }

        if msg_type not in templates:
            return

        text = templates[msg_type][success]
        emoji = "🟢" if success else "🔴"
        full_text = f"   {emoji} - {text}"

        self.status_bar.showMessage(full_text+data, 3000)

    def on_dock_state_changed(self, *args):
        """Вызывается при изменении состояния дока (открепление/прикрепление/перемещение)"""
        # Откладываем обновление в конец очереди событий
        QTimer.singleShot(50, lambda: (self.update_display()) if self.image else None)

    def create_dock(self,name:str="",position:str="left",content=None,
                    min_width:int = 10,max_width: int = 3000,
                    min_height:int = 10,max_height: int = 3000):
        dock = QDockWidget(name, self)
        dock.setTitleBarWidget(DockTitleBar(name, dock))
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setProperty("dock", "main")

        dock.setWidget(content)
        dock.setStyleSheet(f"""
        QDockWidget{{
            min-width: {min_width}px;
            max-width: {max_width}px;
            min-height: {min_height}px;
            max-height: {max_height}px;
        }}
        """)

        # 🔵 ПОДКЛЮЧАЕМ СОБЫТИЯ
        dock.topLevelChanged.connect(self.on_dock_state_changed)
        dock.dockLocationChanged.connect(self.on_dock_state_changed)

        # 🔵 ВАЖНО: Устанавливаем eventFilter для перехвата resize
        dock.installEventFilter(self)
        dock.setProperty("dock_widget", "trackable")  # Метка для фильтрации

        match position:
            case "left":
                self.addDockWidget(Qt.LeftDockWidgetArea, dock)
            case "right":
                self.addDockWidget(Qt.RightDockWidgetArea, dock)
            case _:
                self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        # 🔵 Сохраняем ссылку на dock для доступа в eventFilter
        if not hasattr(self, 'tracked_docks'):
            self.tracked_docks = []
        self.tracked_docks.append(dock)

    def eventFilter(self, obj, event):
        """Перехват событий для dock-окон"""
        # 🔵 Проверяем, что это QDockWidget с нашей меткой
        if (hasattr(obj, 'property') and
                obj.property("dock_widget") == "trackable"):

            if event.type() == QEvent.Resize:
                # 🔵 Док изменил размер — обновляем дисплей
                QTimer.singleShot(0, lambda: (self.update_display()) if self.image else None)
                return False  # Пропускаем событие дальше

        return super().eventFilter(obj, event)

    def dock_help(self):
        # Содержимое докинг окна
        dock_content = QWidget()
        dock_content.setProperty("dock", "main")
        dock_content.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        layout = QVBoxLayout()
        mrg = 25
        layout.setContentsMargins(mrg, mrg, mrg, mrg)

        info_label = QLabel(self.name["editor.help.dock.name"])
        info_label.setProperty("dock", "main")
        info_label.setWordWrap(True)
        #info_label.setObjectName("dockMainContent")
        layout.addWidget(info_label)
        layout.addStretch()

        # Добавляем переключатель видимости докинга

        dock_content.setLayout(layout)

        self.create_dock(name =self.name["editor.help.dock.title"],
                    position ="right",
                    content = dock_content,
                    min_width = 300,
                    max_width = 350,
                    max_height=1000,
        )

    def dock_editor(self):

        # Содержимое док-окна
        dock_content = QWidget()
        dock_content.setProperty("dock", "main")
        dock_content.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(dock_content)
        mrg = 25
        layout.setContentsMargins(mrg, mrg, mrg, mrg)

        # Заголовок
        title_label = QLabel(self.name["editor.editor.dock.name"])
        title_label.setProperty("dock", "main")
        title_label.setStyleSheet(f"font-size: {style.STYLE["global"]["font_size_h2"]}; font-weight: bold;")
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
        scroll_QVBox.setAlignment(Qt.AlignCenter)
        self.scroll_QVBox = scroll_QVBox


        # Растяжка в конце списка
        scroll_QVBox.addStretch()

        # Область прокрутки
        scroll_area = QScrollArea()
        scroll_area.setWidget(scroll_QWidget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Задаём фон, рамку и скругление для всей области
        scroll_QWidget.setProperty("dock", "scroll")
        scroll_area.setWidget(scroll_QWidget)

        layout.addWidget(scroll_area)

        # Кнопки действий
        actions_data = [
            (self.name["editor.editor.dock.button.delete.all"], "mdi6.eraser", lambda: (self.del_polygon(), self.update_display(), self.debug())),
            (self.name["editor.editor.dock.button.select.all"], "mdi6.check-all", lambda: (self.select_all_in_widget(), self.debug())),
        ]
        for name, icon_path, slot in actions_data:
            button = QPushButton(name)
            self.button_icon.append([button, icon_path, 1.1])
            self.widget_buttons.append(button)
            if slot:
                button.clicked.connect(slot)
            button.setProperty("button", "st1")
            button.setVisible(False)
            layout.addWidget(button)

        #layout.addStretch()

        self.create_dock(
            name=self.name["editor.editor.dock.title"],
            position="left",
            content=dock_content,
            min_width=300,
            max_width=650,
            max_height=1000,
        )

    def relative_path(self, input_filepath: str) -> str:
        result = os.path.relpath(input_filepath, self.project_root).replace("\\","/")
        return str(result)

    def absolute_path(self, input_filepath: str) -> str:
        result = os.path.join(self.project_root, input_filepath).replace("\\","/")
        return str(result)


    def load_image(self):
        """Загрузка изображения"""

        filename, _ = QFileDialog.getOpenFileName(
            self, self.name["editor.toolbar.load.image.title"], "../../img",
            "(*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        print(filename)
        if filename != "":
            self.clear_display()
            self.manual_load_image(filename,True)



    def manual_load_image(self, path:str,statusbar:bool=False):
        """Загрузка изображения"""
        if path:
            if not os.path.exists(path):
                print("ошибка загрузки изображения: изображение не существует ",path)
                self.statusbar_show_temp_message("load_image", False, self.relative_path(path))
                return
            elif os.path.exists(path):
                print("успешная загрузка изображения ",path)
                if statusbar:
                    self.statusbar_show_temp_message("load_image", True, self.relative_path(path))
                self.image_path = path
                self.image = QPixmap(path)
                self.update_display()


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


    def update_display(self):
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
            text_font = painter.font()
            text_font.setPointSize(text_size)
            painter.setFont(text_font)

            if self.current_points:
                for num, point in enumerate(self.current_points):
                    painter.setPen(QPen(QColor(self.colors[new_color]), line_size))
                    painter.setBrush(QBrush(QColor(self.colors[new_color])))
                    pos_x = int(point[0])
                    pos_y = int(point[1])
                    painter.drawEllipse(QPoint(pos_x, pos_y), point_size, point_size)
                    painter.drawText(pos_x + 10, pos_y - 10, f"P{num + 1}")

                    points = self.current_points
                    if len(points) > 1:
                        painter.setPen(QPen(QColor(self.colors[new_color]), line_size))
                        for point_num in range(len(points) - 1):
                            point_start = QPoint(int(points[point_num][0]), int(points[point_num][1]))
                            point_end = QPoint(int(points[point_num + 1][0]), int(points[point_num + 1][1]))
                            painter.drawLine(point_start, point_end)

            if self.polygons:
                for i, data in enumerate(self.polygons):
                    num = i % len(self.colors)
                    points = data['points']
                    for point_num, point in enumerate(points):
                        painter.setPen(QPen(QColor(self.colors[num]), line_size))
                        painter.setBrush(QBrush(QColor(self.colors[num])))
                        pos_x = int(point[0])
                        pos_y = int(point[1])
                        painter.drawEllipse(QPoint(pos_x, pos_y), point_size, point_size)
                        painter.drawText(pos_x + 10, pos_y - 10, f"P{i + 1}-{point_num + 1}")

                    if len(points) >= 2:
                        polygon = QPolygon()
                        for pt in points:
                            polygon.append(QPoint(pt[0], pt[1]))

                        fill_color = QColor(self.colors[num])
                        fill_color.setAlpha(alpha)
                        painter.setBrush(QBrush(fill_color))
                        painter.drawPolygon(polygon)

            painter.end()

            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            #self.image_label.setPixmap(scaled_pixmap)
            radius = int(style.STYLE["global"]["style_border_radius"].replace("px",""))  # Радиус скругления в пикселях
            rounded_pixmap = QPixmap(scaled_pixmap.size())
            rounded_pixmap.fill(Qt.transparent)

            painter = QPainter(rounded_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)

            # Создаём скруглённый путь
            path = QPainterPath()
            path.addRoundedRect(0, 0, scaled_pixmap.width(), scaled_pixmap.height(), radius, radius)
            painter.setClipPath(path)

            # Рисуем изображение внутри скруглённой области
            painter.drawPixmap(0, 0, scaled_pixmap)
            painter.end()

            self.image_label.setPixmap(rounded_pixmap)


    def image_mouse_press(self, event):
        """Обработка клика по изображению"""
        if self.image == None:
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
                        # 👈 НОВОЕ: Проверяем, кликнули ли внутрь существующего полигона
                        for polygon_num, polygon in enumerate(self.polygons):
                            if self.image_is_point_inside_polygon(x, y, polygon['points']):
                                self.dragging_polygon_whole = polygon_num
                                # Запоминаем смещение между кликом и первым пунктом полигона
                                first_point = polygon['points'][0]
                                self.drag_offset_x = x - first_point[0]
                                self.drag_offset_y = y - first_point[1]
                                clicked = True
                                break
                    if not clicked:
                        self.current_points.append((x, y))
                        self.StatusBarLabelUpdate(coords=len(self.current_points))
                        if len(self.current_points) > self.max_points_in_polygon:
                            self.add_polygon_meta()
                            self.update_polygons_list_widget()
                            self.StatusBarLabelUpdate(coords=None)
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
                        self.StatusBarLabelUpdate(coords=None)
                    else:
                        self.current_points.clear()
                        self.StatusBarLabelUpdate(coords=None)


            self.update_display()


    def image_mouse_move(self, event):
        if not self.image:
            return

        x, y = self.get_image_coordinates(event)
        x = int(x)
        y = int(y)
        update = False

        # 👈 НОВОЕ: Перетаскивание всего полигона
        if self.dragging_polygon_whole >= 0:
            polygon = self.polygons[self.dragging_polygon_whole]
            new_points = []
            for px, py in polygon['points']:
                new_x = x - self.drag_offset_x + (px - polygon['points'][0][0])
                new_y = y - self.drag_offset_y + (py - polygon['points'][0][1])
                new_points.append((new_x, new_y))
            polygon['points'] = new_points
            update = True

        #"""Обработка перемещения мыши"""
        elif self.dragging_point >= 0 and self.image:
            if self.dragging_polygon >= 0:
                self.polygons[self.dragging_polygon]['points'][self.dragging_point] = (x, y)
            else:
                self.current_points[self.dragging_point] = (x, y)
            update = True

        if update:
            self.update_display()


    def image_mouse_release(self, event):
        """Обработка отпускания кнопки мыши"""
        self.dragging_point = -1
        self.dragging_polygon = -1
        self.dragging_polygon_whole = -1
        self.drag_offset_x = 0
        self.drag_offset_y = 0

    # В editor_window.py, новый метод
    def image_is_point_inside_polygon(self, x, y, polygon_points):
        """
        Алгоритм Ray Casting - проверяет, находится ли точка внутри полигона
        """
        inside = False
        n = len(polygon_points)

        j = n - 1
        for i in range(n):
            xi, yi = polygon_points[i]
            xj, yj = polygon_points[j]

            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside

            j = i

        return inside



    def resizeEvent(self, event):
        """Обработка изменения размера окна"""
        if self.image:
            super().resizeEvent(event)
            self.update_display()

    def dockEvent(self, event):
        if self.image:
            self.update_display()

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

    def select_all_in_widget(self):
        for i in range(self.scroll_QVBox.count()):
            item = self.scroll_QVBox.itemAt(i)
            if item and item.widget():
                checkbox = item.widget().findChild(QCheckBox)
                checkbox.setChecked(True)


    def load_mask(self,only_poly:bool=False):
        file_path, _ = QFileDialog.getOpenFileName(
            self, self.name["editor.toolbar.load.file.title"], "../../save",
            "(*.mask)"
        )
        if file_path != '':
            correct,saved_data, parent_file = file.load_data(file_path)
            if correct:
                self.loaded_mask = file_path
                self.statusbar_show_temp_message("load_mask", True, self.relative_path(self.loaded_mask))
                self.clear_display(not only_poly)
                for id, i in enumerate(saved_data):
                    self.add_polygon_meta(name=i['name'], points=i['points'])
                    self.add_polygon_widget(name=i['name'], id=id)
                if only_poly == False: ## Загрузка полной маски
                    self.manual_load_image(path=self.absolute_path(parent_file))
                else: ## Загрузка только полигонов
                    self.update_display()
                self.loaded_mask = file_path
                self.update_polygons_list_widget()
                self.StatusBarLabelUpdate(mask=self.relative_path(self.loaded_mask))
                print("_____")
                print(parent_file)
            else:
                self.statusbar_show_temp_message("load_mask", False, saved_data)


    def new_save_mask(self):
        self.loaded_mask, _ = QFileDialog.getSaveFileName(
            caption=self.name["editor.editor.dock.button.delete.all"],
            dir="../../save",
            filter="(*.mask)"
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

            path = self.relative_path(self.image_path)
            correct, error = file.save_data(saved_data, self.loaded_mask,  path)
            if correct:
                self.statusbar_show_temp_message("new_save", True, self.relative_path(self.loaded_mask))
            else:
                self.statusbar_show_temp_message("new_save", False, error)


            print(f"Маска сохранена: {self.loaded_mask}")


    def fast_save_mask(self):
        saved_data = []
        for polygon in self.polygons:
            saved_data.append({
                "name": polygon['name'],
                "points": polygon['points']
            })
        path = self.relative_path(self.image_path)
        correct,error = file.save_data(saved_data, self.loaded_mask, path)
        if correct:
            self.statusbar_show_temp_message("fast_save", True, self.relative_path(self.loaded_mask))
        else:
            self.statusbar_show_temp_message("fast_save", False, error)

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
        for button in self.widget_buttons:
            if len(self.polygons) == 0:
                button.setVisible(False)
            else:
                button.setVisible(True)


    def add_polygon_widget(self, name: str = 'error', id:int = -1):
        polygon_num = id
        num = id % len(self.colors)
        row_widget = QWidget()
        row_widget.setProperty("dock", "polygon_slot")

        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(1, 1, 1, 1)
        row_layout.setSpacing(2)
        print("цвет", self.colors[num])
        meta = QLabel(f"{id}")
        meta.setStyleSheet(f"""
        min-height: 20px;
        min-width: 20px;
        border-radius: {style.STYLE["global"]["style_border_radius"]};
        background-color: {self.colors[num]};
        """)    ########################################################################################################
        meta.setVisible(self.IsDebug)
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

        color_indicator = QLabel()
        color_indicator.setFixedSize(22,22)

        color_indicator.setProperty("element", "circle")
        color_indicator.setStyleSheet(f"""
        background-color: {self.colors[num]}
        """)

        row_layout.addWidget(meta)

        #row_layout.setStyleSheet(f"border-radius: 8px;")

        row_layout.addWidget(btn)
        row_layout.addWidget(text_edit)
        row_layout.addWidget(color_indicator)
        self.scroll_QVBox.insertWidget(self.scroll_QVBox.count() - 1, row_widget)


    def debug(self):
        print("==================")
        for i in self.polygons:
            print(f"{i['id']} | {i['name']} | {i['points']}")
        print(self.polygons)
        print(self.loaded_mask)
        self.update_display()

    def closeEvent(self, event):
        if self.capture_thread and self.capture_thread.isRunning():
            self.capture_thread.quit()
            self.capture_thread.wait(2000)
        event.accept()