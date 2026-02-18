import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QPoint, QRect, QSize, QLine
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QAction, QImage, QIcon, QPolygon, QPolygonF
# import Editor.prod.data.names as names
import numpy as np
import logic.file as file
import os
from pathlib import Path
from PySide6.QtWidgets import QStatusBar, QLabel, QProgressBar, QPushButton
from PySide6.QtCore import QTimer, QDateTime
from PySide6.QtGui import QFont


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
        self.image_label.setStyleSheet("border: 1px solid gray;")
        main_layout.addWidget(self.image_label)

        # Создаем кнопки
        self.coords_label = QLabel("Точки: 0")

        self.create_toolbar()
        self.dock_editor()

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("""
                QStatusBar {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                      stop:0 #2c3e50, stop:1 #3498db);
                    color: white;
                    border-top: 1px solid #1a2632;
                    max-height: 30px;
                }
                QStatusBar QLabel {
                    color: white;
                    padding: 3px 10px;
                    border-radius: 3px;
                    background-color: rgba(0,0,0,0.2);
                    margin: 2px;
                }
                QStatusBar QProgressBar {
                    border: none;
                    border-radius: 3px;
                    background-color: rgba(255,255,255,0.2);
                    max-height: 16px;
                    min-width: 150px;
                    margin: 2px;
                }
                QStatusBar QProgressBar::chunk {
                    border-radius: 3px;
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                      stop:0 #f1c40f, stop:1 #e67e22);
                }
            """)


        # Устанавливаем обработчик событий мыши для метки
        self.image_label.mousePressEvent = self.image_mouse_press
        self.image_label.mouseMoveEvent = self.image_mouse_move
        self.image_label.mouseReleaseEvent = self.image_mouse_release

        # Обработчик кнопки – показывает временное сообщение и меняет цвет индикатора
    def show_temp_message(self, msg_type: str, success: bool, data=None):
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

        # Если тип не найден – ничего не делаем (или можно показать просто текст)
        if msg_type not in templates:
            return

        # Выбираем нужный текст
        text = templates[msg_type][success]

        # Добавляем эмодзи в начало
        emoji = "🟢" if success else "🔴"
        full_text = f"{emoji} | {text}"

        # Показываем в статус-баре (например, на 2 секунды)
        self.status_bar.showMessage(full_text, 5000)





    def clear_display(self):
        self.current_points:list = []
        self.points:list = []
        self.polygons:list = []
        self.del_polygon_from_widget(del_all=True)
        self.del_polygon_from_meta(del_all=True)
        self.image = QPixmap(800, 600)  # размер можно любой
        self.image.fill(Qt.transparent)  # заливаем белым
        self.display_image()
        self.image_path:str = ""
        self.loaded_mask:str = ""
        self.remap_id()
        self.update_polygons_list_widget()
        self.image = None


    def create_toolbar(self):
        """Создание панели инструментов"""
        toolbar = QToolBar("Панель инструментов2")

        self.addToolBar(toolbar)
        toolbar.setIconSize(QSize(32, 32))

        self.editor_load_mask_action = QAction(self)
        self.editor_load_mask_action.setIcon(QIcon("../icons/comedy_mask.png"))
        self.editor_load_mask_action.triggered.connect(self.load_mask)
        toolbar.addAction(self.editor_load_mask_action)

        self.editor_load_image_action = QAction(self)
        self.editor_load_image_action.setIcon(QIcon("../icons/load_image.png"))
        self.editor_load_image_action.triggered.connect(self.load_image)
        toolbar.addAction(self.editor_load_image_action)

        self.editor_save_mask_action = QAction(self)
        self.editor_save_mask_action.setIcon(QIcon("../icons/saveas.png"))
        self.editor_save_mask_action.triggered.connect(self.new_save_mask)
        toolbar.addAction(self.editor_save_mask_action)

        # Если хотите задать размер иконок для всей панели (рекомендуется)


        self.editor_fast_save_mask_action = QAction(self)
        self.editor_fast_save_mask_action.setIcon(QIcon("../icons/save.png"))
        self.editor_fast_save_mask_action.triggered.connect(self.fast_save_mask)
        toolbar.addAction(self.editor_fast_save_mask_action)

        self.editor_clear_display_action = QAction(self)
        self.editor_clear_display_action.setIcon(QIcon("../icons/clear.png"))
        self.editor_clear_display_action.triggered.connect(self.clear_display)
        toolbar.addAction(self.editor_clear_display_action)

        self.manual_load_action = QAction(self)
        self.manual_load_action.setIcon(QIcon("../icons/exp.png"))
        self.manual_load_action.triggered.connect(lambda: (self.manual_load_image("C:/MyPrograms/pycharm/CamParking_diplom/img/camphoto/camera_photo_2026-01-28.jpg"),
                                                           self.show_temp_message("test_image",False,"хуй")))
        toolbar.addAction(self.manual_load_action)

    def dock_editor(self):
        self.EditorDock = QDockWidget("Информация", self)
        self.EditorDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        dock_content = QWidget()
        layout = QVBoxLayout(dock_content)

        # === ГРУППА ПОЛИГОНОВ ===
        polygon_group = QGroupBox()
        polygon_group.setMinimumHeight(300)
        polygon_group.setMinimumWidth(50)

        title_label = QLabel("Полигоны:")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

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
        btn2.clicked.connect(lambda: (self.del_polygon(),
                                      self.display_image(),
                                      self.debug(),
        ))
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

    def relative_path(self,input_filepath: str) -> str:
        result = os.path.relpath(input_filepath, self.project_root)
        return str(result)
        # функция для воспросизведения патча входной Длинный -> Короткий -> Сохранение

    def absolute_path(self,input_filepath: str) -> str:
        result = os.path.join(self.project_root, input_filepath)
        return str(result)

    def load_image(self):
        """Загрузка изображения"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "../../img",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        print(filename)
        if filename:
            self.image_path = filename
            self.image = QPixmap(filename)
            self.display_image()

    def manual_load_image(self,path:str):
        """Загрузка изображения"""
        if path:
            self.image_path = path
            self.image = QPixmap(path)
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
            text_font.setPointSize(text_size)  # можно изменить цифру
            painter.setFont(text_font)

            if self.current_points:
                # 👇 ИСПРАВЛЕНО: рисуем ТОЛЬКО current_points, points больше не используем
                for num, point in enumerate(self.current_points):
                    painter.setPen(QPen(colors[new_color], line_size))  # <= размер линии уже в готовом полигоне
                    painter.setBrush(QBrush(colors[new_color])) # <= можно сделать прозрачные точки (на не готовом полигоне)
                    pos_x = int(point[0])
                    pos_y = int(point[1])
                    painter.drawEllipse(
                        QPoint(pos_x, pos_y),
                        point_size,
                        point_size
                    )

                    painter.drawText(
                        pos_x + 10,
                        pos_y - 10,
                        f"P{num + 1}"
                    )

                    points = self.current_points
                    if len(points) > 1:
                        painter.setPen(QPen(colors[new_color], line_size))
                        for point_num in range(len(points) - 1):
                            point_start = QPoint(int(points[point_num][0]), int(points[point_num][1]))
                            point_end = QPoint(int(points[point_num + 1][0]), int(points[point_num + 1][1]))
                            painter.drawLine(point_start, point_end)

                        # Замыкающая линия (последняя -> первая)



            # 👇 ИСПРАВЛЕНО: рисуем полигоны
            if self.polygons:
                for i, data in enumerate(self.polygons):
                    num = i % len(colors)
                    points = data['points']
                    # Рисуем точки полигона
                    for point_num, point in enumerate(points):
                        painter.setPen(QPen(colors[num], line_size)) # <= размер линии уже в готовом полигоне
                        painter.setBrush(QBrush(colors[num])) # <= можно сделать прозрачные точки (на уже готовом полигоне)
                        pos_x = int(point[0])
                        pos_y = int(point[1])
                        painter.drawEllipse(
                            QPoint(pos_x, pos_y),
                            point_size,     # <= размер точки
                            point_size      # <= размер точки
                        )
                        painter.drawText(
                            pos_x + 10,
                            pos_y - 10,
                            f"P{i + 1}-{point_num + 1}"
                        )

                    if len(points) >= 2:  # нужен хотя бы треугольник
                        polygon = QPolygon()
                        for pt in points:
                            polygon.append(QPoint(pt[0], pt[1]))

                        # 2. Сохраняем текущие настройки пера/кисти (если нужно)
                        # Устанавливаем полупрозрачную заливку
                        fill_color = QColor(colors[num])  # берём тот же цвет, что и для линий
                        fill_color.setAlpha(alpha)  # прозрачность (0-255)
                        painter.setBrush(QBrush(fill_color))
                        #painter.setPen(Qt.NoPen)  # без контура, чтобы не рисовать лишний слой

                        # 3. Рисуем залитый полигон
                        painter.drawPolygon(polygon)

                        # 4. Восстанавливаем перо для контура (если нужно рисовать линии)
                        # Здесь можно вернуть перо, которое использовалось для линий
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

        # 👇 ИСПРАВЛЕНО: используем новый метод для координат
        x, y = self.get_image_coordinates(event)
        x = int(x)
        y = int(y)
        pixmap = self.image_label.pixmap()

        if pixmap:
            # Добавляем новую точку
            match event.button():
                case Qt.LeftButton:
                    clicked = False
                    for i, point in enumerate(self.current_points):
                        distance = np.sqrt((x - point[0]) ** 2 + (y - point[1]) ** 2)
                        if distance < self.point_radius * 2:
                            self.dragging_point = i
                            self.dragging_polygon = -1  # 👈 НОВОЕ: тащим из current
                            clicked = True
                            break
                    if not clicked: # 👇 НОВОЕ: проверяем точки в полигонах
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
                                            # Ищем позицию для вставки
                                            for num in range(len(self.polygons[polygon_num]['points'])):
                                                if self.polygons[polygon_num]['points'][num] == start_point:
                                                    self.polygons[polygon_num]['points'].insert(num + 1, (x, y))
                                                    break
                                            # 👇 после вставки выходим из внутреннего цикла
                                            break
                            # если вставили, прерываем внутренний цикл (на случай, если break выше не сработал)
                    # 👇 после всех проверок, если точка была вставлена, обновляем картинку и выходим из метода

                case Qt.RightButton:
                    for polygon_num, polygon in enumerate(self.polygons):
                        for point_num, point in enumerate(polygon['points']):
                            distance = np.sqrt((x - point[0]) ** 2 + (y - point[1]) ** 2)
                            if distance < self.point_radius * 2:
                                self.polygons[polygon_num]['points'].pop(point_num)
                                break
                    # 👇 ИСПРАВЛЕНО: проверяем current_points, а не points
                    if len(self.current_points) > 3:  # Минимум 3 точки для полигона
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


    def resizeEvent(self, event):
        """Обработка изменения размера окна"""
        super().resizeEvent(event)
        if self.image:
            self.display_image()


    # 👇 НОВЫЙ МЕТОД: выбор полигона для редактирования

    def remap_id(self):
        data = self.polygons
        for num,i in enumerate(self.polygons):
            data[num]['id'] = num
        self.polygons = data

    def get_ids_from_widget(self):
        self.checked_widgets = []
        for i in range(self.scroll_layout.count()):  # идем с конца
            item = self.scroll_layout.itemAt(i)
            if item and item.widget():
                checkbox = item.widget().findChild(QCheckBox)
                a = item.widget().findChild(QLabel)
                if checkbox.isChecked():
                    self.checked_widgets.append(int(a.text()))
        #print(f"{self.checked_widgets}")
        return self.checked_widgets

    def load_mask(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите маску", "../../save",
            "Маски (*.mask)"
        )
        saved_data, parent_file = file.load_data(file_path)
        for id,i in enumerate(saved_data):
            self.add_polygon_meta(name=i['name'],points=i['points'])
            self.add_polygon_widget(name=i['name'],id=id)
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

            # Подготавливаем данные для сохранения
            saved_data = []
            for polygon in self.polygons:
                saved_data.append({
                    "name": polygon['name'],
                    "points": polygon['points']
                })

            # Сохраняем
            file.save_data(saved_data, self.loaded_mask,  self.relative_path(self.image_path))
            print(f"Маска сохранена: {self.loaded_mask}")

    def fast_save_mask(self):
        saved_data = []
        for polygon in self.polygons:
            saved_data.append({
                "name": polygon['name'],
                "points": polygon['points']
            })

        # Сохраняем
        file.save_data(saved_data, self.loaded_mask, self.relative_path(self.image_path))
        print(f"Быстрое сохранение: {self.loaded_mask}")

    def add_polygon_meta(self, name: str = 'noname',points=None):
        # 👇 ИСПРАВЛЕНО: добавляем КОПИЮ точек, а не ссылку
        if points is None:
            points = self.current_points
        print(points)
        new_polygon = {
            'id': len(self.polygons),
            'name': name,
            'points': points.copy(),
        }
        self.polygons.append(new_polygon)
        #print(self.polygons)
        print(f"Добавлен новый полигон: {new_polygon}")
        self.current_points.clear()


    def del_polygon(self):
        data = self.get_ids_from_widget()
        self.del_polygon_from_meta(data)
        self.del_polygon_from_widget(data)
        self.remap_id()
        self.update_polygons_list_widget()

    def rename_polygon(self, new_name: str,id:int):
        for i in self.polygons:
            if i['id'] == id:
                i['name'] = new_name


    def del_polygon_from_meta(self,id = None,del_all:bool = False):
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
            # Очищаем виджеты (оставляем только stretch)
            while self.scroll_layout.count() > 1:
                item = self.scroll_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        if isinstance(id, list):
            # Удаляем по списку имен
            for i in range(self.scroll_layout.count() - 1, -1, -1):  # идем с конца
                item = self.scroll_layout.itemAt(i)
                if item and item.widget():
                    label = item.widget().findChild(QLabel)
                    if label and label.text() in str(id):
                        item.widget().deleteLater()
                        self.scroll_layout.removeItem(item)
        else:
            # Удаляем виджет
            for i in range(self.scroll_layout.count()):
                item = self.scroll_layout.itemAt(i)
                if item and item.widget():
                    # Ищем QLineEdit с нужным текстом
                    label = item.widget().findChild(QLabel)
                    if label and label.text() == str(id):
                        item.widget().deleteLater()
                        self.scroll_layout.removeItem(item)
                        break

        #self.display_image()

    def update_polygons_list_widget(self):
        self.del_polygon_from_widget(del_all=True)
        for i in range(len(self.polygons)):
            self.add_polygon_widget(self.polygons[i]['name'],self.polygons[i]['id'])

    def add_polygon_widget(self, name: str = 'error',id:int = -1):
        polygon_num = id
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(1, 1, 1, 1)
        row_layout.setSpacing(5)

        # Кнопка

        meta = QLabel()
        meta.setText(str(id))
        meta.setFixedSize(30, 30)
        meta.setVisible(self.debugbool)
        meta.setStyleSheet("""QLabel {
                            font-size: 17px;
                            border-radius: 10px;
                            background-color: #2d2d2d;
                            color: white;
                        }""")
        meta.setAlignment(Qt.AlignCenter)
        btn = QCheckBox()
        btn.setCheckable(True)
        btn.setIcon(QIcon("../icons/edit"))   # Убедитесь, что путь верный
        btn.setIconSize(QSize(24, 24))        # Иконка чуть меньше кнопки
        btn.setFixedSize(30, 30)

        # Таблица стилей
        btn.setStyleSheet("""
            QCheckBox {
                font-size: 23px;
                border-radius: 10px;
                background-color: #2d2d2d;
                color: white;
                spacing: 8px;                /* отступ между индикатором и иконкой (если нужно) */
            }
            QCheckBox::indicator {
                left: -5px;          /* сдвигаем далеко влево */
                width: 0px;
                height: 0px;
            }
            QCheckBox::indicator:checked {
                background-color: #007acc;     /* цвет индикатора в состоянии checked */
                /* Если нужна галочка картинкой, можно добавить:
                image: url(:/icons/check.svg); */
            }
            QCheckBox:hover {
                background-color: #3d3d3d;
            }
            QCheckBox:checked {
                background-color: #007acc;     /* фон всей кнопки при checked */
            }
        """)

        # Сохраняем индекс полигона (polygon_num) и передаём в слот
        #btn.clicked.connect(lambda checked, idx=polygon_num: self.select_polygon(idx))

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
                            padding-left: 5px;  /* отступ текста от левого края */
                        }
                    """)
        text_edit.textChanged.connect(lambda text, idx=int(meta.text()): self.rename_polygon(text, idx))
        text_edit.setMinimumWidth(100)
        self.text_edits.append(text_edit)

        row_layout.addWidget(meta)
        row_layout.addWidget(btn)
        row_layout.addWidget(text_edit)

        # 👇 ИСПРАВЛЕНО: вставляем перед stretch
        self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, row_widget)

    def debug(self):
        print("==================")
        for i in self.polygons:
            print(f"{i['id']} | {i['name']} | {i['points']}")
        print(self.polygons)
        #self.display_image()
        print(self.loaded_mask)