import sys
import os
from pathlib import Path
import cv2
import numpy as np
import logic.detector as detector
import av
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QPoint, QSize, QTimer, QEvent, QUrl, QRectF, QPointF, QThread, Signal
from PySide6.QtGui import (
    QPixmap, QPainter, QPen, QBrush, QColor, QAction,
    QPolygon, QPainterPath, QImage, QWheelEvent,QPolygonF
)
import asyncio
import qtawesome as qta
import logic.file as file
import logic.logic as logic
import Editor.prod.data.style as style
from Editor.prod.data.properties import DockTitleBar
import Editor.prod.data.names as names
from Editor.prod.data.signal_bus import signal


# ----------------------------------------------------------------------
# Поток для захвата видео с RTSP камеры через OpenCV
# ----------------------------------------------------------------------
class CameraThread(QThread):
    change_pixmap_signal = Signal(QImage)

    def __init__(self, url, target_size):
        super().__init__()
        self.url = url
        self.target_size = target_size  # кортеж (width, height)
        self._run_flag = True

    def run(self):
        # Опции для стабильности RTSP
        options = {
            'rtsp_transport': 'tcp',      # принудительно TCP
            'buffer_size': '1024000',      # размер буфера
            'max_delay': '500000',         # максимальная задержка
            'stimeout': '5000000',         # таймаут сокета (5 секунд)
            'flags': 'low_delay',          # низкая задержка
        }

        while self._run_flag:
            container = None
            try:
                # Открываем RTSP поток
                container = av.open(self.url, options=options)
                # Берём первый видеопоток
                stream = container.streams.video[0]
                stream.thread_type = 'AUTO'   # автоматическое распараллеливание

                # Декодируем кадры
                for packet in container.demux(stream):
                    for frame in packet.decode():
                        if not self._run_flag:
                            break

                        # Получаем numpy массив в RGB (height, width, 3)
                        img = frame.to_ndarray(format='rgb24')

                        # Масштабируем до целевого размера, если необходимо
                        if (img.shape[1], img.shape[0]) != self.target_size:
                            img = cv2.resize(img, self.target_size, interpolation=cv2.INTER_LINEAR)

                        # Конвертируем в QImage
                        h, w, ch = img.shape
                        bytes_per_line = ch * w
                        qt_image = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)

                        # Отправляем сигнал
                        self.change_pixmap_signal.emit(qt_image)

                    if not self._run_flag:
                        break

            except Exception as e:
                print(f"❌ Ошибка в потоке PyAV: {e}")
                # Пауза перед переподключением
                self.msleep(1000)

            finally:
                if container is not None:
                    container.close()

        print("✅ Поток PyAV завершён")

    def stop(self):
        self._run_flag = False
        self.wait()


# ----------------------------------------------------------------------
# GraphicsView с масштабированием (без изменений)
# ----------------------------------------------------------------------
class GraphicsView(QGraphicsView):
    """Класс представления с поддержкой масштабирования колесиком мыши"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(self.renderHints())
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    '''
    def wheelEvent(self, event: QWheelEvent):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        old_pos = self.mapToScene(event.position().toPoint())

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.scale(zoom_factor, zoom_factor)

        new_pos = self.mapToScene(event.position().toPoint())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())
    '''
    def fit_to_view(self):
        """Масштабирует сцену под размер окна"""
        self.fitInView(self.scene().itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)


# ----------------------------------------------------------------------
# Главное окно подключения к камере
# ----------------------------------------------------------------------
class ConnectWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.name = names.NAMES[names.get_language()]
        self.line_size = 3
        self.point_size = 7
        self.text_size = 25
        self.new_color = 4
        self.alpha = 80
        self.max_points_in_polygon = 9
        self.button_icon = []
        self.polygons = []
        self.points = []
        self.current_color = 0
        self.colors = [
            "#FF0000", "#FFA500", "#FFFF00", "#00FF00",
            "#00BFFF", "#0000FF", "#EE82EE",
        ]
        self.img = None
        self.project_root = str(Path(__file__).parent.parent.parent.parent.resolve())
        # Центральный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        # Панель управления RTSP
        self.create_upper_string()
        self.create_viewport()
        self.create_toolbar()
        self.create_resolution_controls()
        self.create_statusbar()
        # Статус бар
        self.update_theme_buttons()
        signal.changed.connect(self.update_theme_buttons)
        # Поток камеры (будет создан при подключении)
        self.camera_thread = None

        # Целевой размер для масштабирования кадров
        self.target_size = QSize(1920,1080)

    # ----------------------------------------------------------------------
    # Панель URL и кнопки подключения
    # ----------------------------------------------------------------------
    def create_upper_string(self):
        control_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Введите RTSP URL (например, rtsp://admin:pass@192.168.1.100:554/stream)")
        self.url_input.setText("rtsp://admin:@192.168.0.27:554/stream1")
        self.connect_btn = QPushButton("Подключиться")
        self.stop_btn = QPushButton("Остановить")
        self.stop_btn.setEnabled(False)

        control_layout.addWidget(QLabel("RTSP URL:"))
        control_layout.addWidget(self.url_input)
        control_layout.addWidget(self.connect_btn)
        control_layout.addWidget(self.stop_btn)

        self.connect_btn.clicked.connect(self.connect_rtsp)
        self.stop_btn.clicked.connect(self.stop_rtsp)

        self.main_layout.addLayout(control_layout)

    # ----------------------------------------------------------------------
    # Панель выбора разрешения
    # ----------------------------------------------------------------------
    def create_resolution_controls(self):
        res_layout = QHBoxLayout()
        res_layout.addWidget(QLabel("Целевое разрешение:"))

        self.res_combo = QComboBox()
        self.res_combo.addItems(["1920x1080", "1280x720" , "1024x768","800x600","640x480", "Пользовательское"])
        self.res_combo.currentIndexChanged.connect(self.on_resolution_selected)
        res_layout.addWidget(self.res_combo)

        self.custom_width = QLineEdit()
        self.custom_width.setPlaceholderText("ширина")
        self.custom_width.setEnabled(False)
        self.custom_width.setFixedWidth(70)
        res_layout.addWidget(self.custom_width)

        self.custom_height = QLineEdit()
        self.custom_height.setPlaceholderText("высота")
        self.custom_height.setEnabled(False)
        self.custom_height.setFixedWidth(70)
        res_layout.addWidget(self.custom_height)

        self.apply_res_btn = QPushButton("Применить")
        self.apply_res_btn.clicked.connect(self.change_resolution)
        res_layout.addWidget(self.apply_res_btn)

        res_layout.addStretch()
        self.main_layout.addLayout(res_layout)

    def on_resolution_selected(self, index):
        if index == self.res_combo.count() - 1:  # "Пользовательское"
            self.custom_width.setEnabled(True)
            self.custom_height.setEnabled(True)
        else:
            self.custom_width.setEnabled(False)
            self.custom_height.setEnabled(False)
            text = self.res_combo.currentText()
            w, h = map(int, text.split('x'))
            self.target_size = QSize(w, h)

    def change_resolution(self):
        if self.res_combo.currentIndex() == self.res_combo.count() - 1:
            try:
                w = int(self.custom_width.text())
                h = int(self.custom_height.text())
                if w <= 0 or h <= 0:
                    raise ValueError
                self.target_size = QSize(w, h)
            except:
                QMessageBox.warning(self, "Ошибка", "Введите корректные положительные числа для ширины и высоты")
                return
        else:
            text = self.res_combo.currentText()
            w, h = map(int, text.split('x'))
            self.target_size = QSize(w, h)

        # Если поток уже запущен, обновим размер в потоке (перезапустим с новым размером)
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.target_size = (self.target_size.width(), self.target_size.height())



    # ----------------------------------------------------------------------
    # Видео-область (GraphicsView + PixmapItem)
    # ----------------------------------------------------------------------
    def create_viewport(self):
        self.view = GraphicsView()
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.main_layout.addWidget(self.view)

        # Элемент для отображения кадров
        self.pixmap_item = QGraphicsPixmapItem()
        self.pixmap_item.setZValue(0)          # чтобы точки (z=1) были сверху
        self.scene.addItem(self.pixmap_item)

        # Включаем отслеживание мыши
        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

    def update_frame(self, qimage):
        """Слот для обновления pixmap_item новым кадром"""
        pixmap = QPixmap.fromImage(qimage)
        self.pixmap_item.setPixmap(pixmap)

        # При первом кадре подогнать размер сцены
        if not hasattr(self, '_first_frame_done'):
            self._first_frame_done = True
            self.view.fit_to_view()

        ptr = qimage.bits()
        # Преобразуем memoryview в numpy array напрямую
        arr = np.frombuffer(ptr, dtype=np.uint8).reshape(qimage.height(), qimage.width(), 3)
        self.img = arr.copy()  # сохраняем копию для детекции

    # ----------------------------------------------------------------------
    # Тулбар (загрузка масок, очистка точек)
    # ----------------------------------------------------------------------
    def create_toolbar(self):
        toolbar = QToolBar("Заглушка")
        self.addToolBar(toolbar)
        toolbar.setProperty("toolbar", "toolbar")

        actions_data = [
            (self.name["editor.toolbar.load.mask"], "mdi6.vector-polygon", lambda: self.load_mask(only_poly=True), "Alt+4"),
            (self.name["editor.toolbar.clear"], "mdi6.delete", lambda: self.clear_display(), "Alt+Del"),
            ("дебаг", "mdi.flask", lambda: asyncio.create_task(self.debug(self.img,"confwn")), "Alt+V"),
        ]
        for name, icon_path, slot, shortcut in actions_data:
            action = QAction(self)
            action.setToolTip(name + " / " + shortcut)
            action.setShortcut(shortcut)
            action.triggered.connect(slot)
            toolbar.addAction(action)
            self.button_icon.append([action, icon_path, 1.1])

    def update_theme_buttons(self):
        for button, icon_path, scale in self.button_icon:
            icon = qta.icon(icon_path, color=style.STYLE[style.current_color]["text_color"],
                            options=[{'scale_factor': scale}])
            button.setIcon(icon)

    # ----------------------------------------------------------------------
    # Загрузка маски (из вашего проекта)
    # ----------------------------------------------------------------------
    def load_mask(self, only_poly: bool = False):
        file_path, _ = QFileDialog.getOpenFileName(
            self, self.name["editor.toolbar.load.file.title"], "../../save", "(*.mask)"
        )
        if file_path != '':
            self.fit_view()
            self.polygons.clear()
            correct, saved_data, parent_file = file.load_data(file_path)
            if correct:
                for i in saved_data:
                    self.add_polygon_meta(name=i['name'], points=i['points'])
                self.update_display()
                self.status_bar_label_update(mask=self.relative_path(file_path))
                self.statusbar_show_temp_message("load_mask", True, self.relative_path(file_path))
                print("_____")
                print(parent_file)

    # ----------------------------------------------------------------------
    # Методы для работы с полигонами (пока не адаптированы под новую сцену)
    # ----------------------------------------------------------------------
    def add_polygon_meta(self, name: str = 'noname', points=None):
        new_polygon = {
            'id': len(self.polygons),
            'name': name,
            'points': points.copy(),
        }
        self.polygons.append(new_polygon)
        print(f"Добавлен новый полигон: {new_polygon}")

    def relative_path(self, input_filepath: str) -> str:
        result = os.path.relpath(input_filepath, self.project_root).replace("\\","/")
        return str(result)

    def absolute_path(self, input_filepath: str) -> str:
        result = os.path.join(self.project_root, input_filepath).replace("\\","/")
        return str(result)

    def update_display(self,detect_data=None):
        """Удаляет все старые полигоны из сцены и рисует новые из self.polygons"""
        # Если у нас есть список элементов полигонов, удаляем их из сцены
        self.clear_display()
        # Проходим по всем сохранённым полигонам
        if detect_data == None:
            for num, poly_data in enumerate(self.polygons):
                self.add_polygon(num,poly_data["points"])
        else:
            for num, poly_data in enumerate(self.polygons):
                if poly_data["name"] in detect_data[0]:
                    self.add_polygon(0, self.polygons[num]["points"]) #da
                else:
                    self.add_polygon(3, self.polygons[num]["points"]) #net


    def debug(self,img,config_name):
        detected_car_data = logic.process_image(img=img, save_with_date=False, config_name=config_name)  # [2.1]
        #print("ВОТ ОТСЮДА БЕРЕТСЯ",self.polygons,"\n")
        #print(logic.comparison(saved_data=self.polygons, detected_car_data=detected_car_data))
        self.update_display(logic.comparison(saved_data=self.polygons, detected_car_data=detected_car_data))
        #return logic.comparison(self.polygons, detected_car_data)

    # ----------------------------------------------------------------------
    # Точки (добавление, очистка)
    # ----------------------------------------------------------------------


    def add_polygon(self, color_index: int,points:list):
        # Строим QPolygonF из точек (каждая точка – [x, y])
        polygon = QPolygonF()
        for pt in points:
            polygon.append(QPointF(pt[0], pt[1]))

        # Выбираем цвет по индексу (циклически из self.colors)
        color_index = color_index % len(self.colors)
        color = QColor(self.colors[color_index])
        color.setAlpha(self.alpha)  # устанавливаем прозрачность заливки

        pen = QPen(QColor(self.colors[color_index]), self.line_size)
        brush = QBrush(color)

        # Создаём элемент полигона
        polygon_item = QGraphicsPolygonItem(polygon)
        polygon_item.setPen(pen)
        polygon_item.setBrush(brush)
        polygon_item.setZValue(1)  # выше видео (z=0), точки пока тоже z=1 – см. примечание

        self.scene.addItem(polygon_item)
        self.polygon_items.append(polygon_item)

    def clear_display(self):
        #self.polygons.clear()
        if hasattr(self, 'polygon_items'):
            for item in self.polygon_items:
                self.scene.removeItem(item)
        else:
            self.polygon_items = []
        print("Все точки удалены")

    # ----------------------------------------------------------------------
    # Управление RTSP через OpenCV поток
    # ----------------------------------------------------------------------
    def connect_rtsp(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Ошибка", "Введите RTSP URL")
            return

        # Останавливаем предыдущий поток, если есть
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.stop()

        # Создаём и запускаем новый поток
        self.camera_thread = CameraThread(url, (self.target_size.width(), self.target_size.height()))
        self.camera_thread.change_pixmap_signal.connect(self.update_frame)
        self.camera_thread.start()

        self.connect_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_rtsp(self):
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.stop()
            self.camera_thread = None

        self.connect_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        # Очищаем изображение
        self.pixmap_item.setPixmap(QPixmap())

    # ----------------------------------------------------------------------
    # Создание и управление статусбаром
    # ----------------------------------------------------------------------

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

    def status_bar_label_update(self,coords:int=-1,mask:str="-1"):
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

    def statusbar_show_temp_message(self, msg_type: str, success: bool, data=""):
        # Словарь с шаблонами сообщений
        templates = {
            "load_mask": {
                True: self.name["editor.statusbar.load.mask"],
                False: self.name["editor.statusbar.error"],
            },

        }

        if msg_type not in templates:
            return

        text = templates[msg_type][success]
        emoji = "🟢" if success else "🔴"
        full_text = f"   {emoji} - {text}"

        self.status_bar.showMessage(full_text + data, 3000)

    # ----------------------------------------------------------------------
    # Масштабирование (кнопки)
    # ----------------------------------------------------------------------

    def eventFilter(self, obj, event):
        """Перехват событий для dock-окон"""
        # 🔵 Проверяем, что это QDockWidget с нашей меткой
        if event.type() == QEvent.Resize:
            self.fit_view()
            return False  # Пропускаем событие дальше

        return super().eventFilter(obj, event)

    def zoom_in(self):
        self.view.scale(1.2, 1.2)

    def zoom_out(self):
        self.view.scale(1 / 1.2, 1 / 1.2)

    def fit_view(self):
        self.view.fit_to_view()

    # ----------------------------------------------------------------------
    # Закрытие окна
    # ----------------------------------------------------------------------
    def closeEvent(self, event):
        self.stop_rtsp()
        event.accept()