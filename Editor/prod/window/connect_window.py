import sys
import os
from pathlib import Path
import cv2
import numpy as np
import logic.detector as detector
import Editor.prod.data.prefers_manager as pm
import av
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QPoint, QSize, QTimer, QEvent, QUrl, QRectF, QPointF, QThread, Signal, QMutex, \
    QWaitCondition, QTimer
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
        import concurrent.futures
        from urllib.parse import urlparse
        import socket
        container = None
        options = {
            'rtsp_transport': 'udp',
            'fflags': 'nobuffer',
            'flags': 'low_delay',
            'probesize': '32',
            'analyzeduration': '0',
            'max_delay': '0'
        }
        print("старт подключения.")
        while self._run_flag:

            try:
                # -------- ПРЕДВАРИТЕЛЬНАЯ ПРОВЕРКА ПОРТА ----------
                try:
                    parsed = urlparse(self.url)
                    host = parsed.hostname
                    port = parsed.port
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)  # ждём ответа 2 секунды
                except Exception as e:
                    print(f"ошибка парса строки {e}")
                try:
                    sock.connect((host, port))
                    sock.close()
                except:
                    print("ошибка введенный данных")
                    break
                # ------------------------------------------------


                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(lambda: av.open(self.url, options=options))
                    container = future.result(timeout=5)  # ждём открытия до 5 секунд

                stream = container.streams.video[0]
                stream.thread_type = 'AUTO'

                for packet in container.demux(stream):
                    for frame in packet.decode():
                        if not self._run_flag:
                            print("камера не найдена.")
                            break
                        img = frame.to_ndarray(format='rgb24')
                        if (img.shape[1], img.shape[0]) != self.target_size:
                            img = cv2.resize(img, self.target_size, interpolation=cv2.INTER_LINEAR)
                        h, w, ch = img.shape
                        bytes_per_line = ch * w
                        qt_image = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
                        self.change_pixmap_signal.emit(qt_image)
                    if not self._run_flag:
                        print("камера не найдена.")
                        break
            except TimeoutError:
                print("время вышло")
                break
            except av.error.InvalidDataError:
                print("неверно указаны данные")
                break
            except av.error.HTTPUnauthorizedError:
                print("неверно указан логин или пароль")
                break
            else:
                print("ошибка ввода")
                break
            finally:
                if container is not None:
                    print("Поток заверешен корректно")
                    container.close()

        print("✅ Поток PyAV завершён")

    def stop(self):
        self._run_flag = False
        self.wait()

class ProcessingThread(QThread):
    # Сигнал для передачи результата обратно в главный поток
    result_ready = Signal(object)   # объект с результатами (можно dict)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.frame = None          # текущий кадр для обработки
        self.polygons = []         # текущая маска (список полигонов)
        self.config_name = ""      # имя конфига
        self.mutex = QMutex()      # для безопасного обмена данными
        self.cond = QWaitCondition()
        self._processing = False
        self.busy = False  # флаг занятости

    def set_frame(self, frame, polygons, config_name):
        """Вызывается из главного потока, чтобы задать кадр для обработки"""
        self.mutex.lock()
        self.frame = frame.copy() if frame is not None else None
        self.polygons = polygons.copy()
        self.config_name = config_name
        self.mutex.unlock()
        self.cond.wakeOne()   # разбудить поток, если он ждёт

    def run(self):
        while self._run_flag:
            self.mutex.lock()
            if self.frame is None:
                self.cond.wait(self.mutex)
                self.mutex.unlock()
                continue

            # забираем данные
            frame = self.frame
            polygons = self.polygons
            config_name = self.config_name
            self.frame = None
            self.mutex.unlock()

            # ← теперь поток занят
            self.busy = True

            try:
                detected_car_data = logic.process_image(
                    img=frame,
                    save_with_date=False,
                    config_name=config_name
                )
                comparison_result = logic.comparison(
                    saved_data=polygons,
                    detected_car_data=detected_car_data
                )
                self.result_ready.emit(comparison_result)
            except Exception as e:
                print(f"Ошибка в ProcessingThread: {e}")
                self.result_ready.emit(None)
            finally:
                # ← освобождаем флаг (даже если была ошибка)
                self.busy = False

    def stop(self):
        self._run_flag = False
        self.cond.wakeAll()
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
        self.widget_buttons = []
        self.img = None
        self.checked = True
        self.project_root = str(Path(__file__).parent.parent.parent.parent.resolve())
        # Центральный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        # Панель управления RTSP
        self.dock_main()
        self.create_viewport()
        self.create_toolbar()
        #self.create_resolution_controls()
        self.create_statusbar()
        # Статус бар
        self.update_theme_buttons()
        signal.changed.connect(self.update_theme_buttons)
        # Поток камеры (будет создан при подключении)
        self.camera_thread = None
        self.processing_thread = ProcessingThread()
        self.processing_thread.result_ready.connect(self.on_processing_result)
        self.processing_thread.start()
        # Целевой размер для масштабирования кадров
        self.target_size = QSize(1920,1080)

    # ----------------------------------------------------------------------
    # Панель URL и кнопки подключения
    # ----------------------------------------------------------------------

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
            ("дебаг", "mdi.flask", lambda: self.debug(self.img,"confwd"), "Alt+V"),
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

    def debug(self, img, config_name):
        # Передаём копию текущего кадра (self.img) и текущую маску
        self.processing_thread.set_frame(
            frame=self.img,
            polygons=self.polygons.copy(),
            config_name=config_name
        )
        # Можно добавить индикацию, что обработка запущена

    def toggle_auto_detect(self,breaking=None):
        if breaking:
            self.checked = True
            self.auto_timer.stop()
        else:
            if self.checked:
                self.checked = False
                self.auto_timer.start(2000)  # 1000 мс = 1 сек
            else:
                self.checked = True
                self.auto_timer.stop()

    def auto_debug(self):
        # Если есть кадр и поток обработки ещё не перегружен
        if (self.img is not None and
                self.processing_thread.isRunning() and
                not self.processing_thread.busy):  # добавить проверку
            # Передаём текущий кадр и текущую маску в поток
            self.processing_thread.set_frame(
                frame=self.img,
                polygons=self.polygons.copy(),
                config_name="confwn"  # или какой конфиг нужен
            )

    def on_processing_result(self, comparison_result):
        # comparison_result — это то, что возвращает logic.comparison (например, список [0,1] или имена полигонов)
        if comparison_result is not None:
            self.update_display(comparison_result)
        else:
            # ошибка обработки
            pass

    def debug23(self,img,config_name):
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

        #self.connect_btn.setEnabled(False)
        #self.stop_btn.setEnabled(True)

    def stop_rtsp(self):
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.stop()
            self.camera_thread = None

        #self.connect_btn.setEnabled(True)
        #self.stop_btn.setEnabled(False)

        # Очищаем изображение
        self.pixmap_item.setPixmap(QPixmap())

    # ----------------------------------------------------------------------
    # Создание и управление докинг окном
    # ----------------------------------------------------------------------

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

    def dock_main(self):

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


        #####
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.auto_debug)
        # Например, добавим чекбокс для включения авторежима

        #####
        control_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Введите RTSP URL (например, rtsp://admin:pass@192.168.1.100:554/stream)")
        userdata = pm.load_config()

        self.url_input.setText(f"rtsp://{userdata["camera_login"]}:{userdata["camera_pass"]}@{userdata["camera_ip"]}:{userdata["camera_port"]}/{userdata["camera_stream_path"]}")
        #self.stop_btn.setEnabled(False)

        control_layout.addWidget(QLabel("RTSP URL:"))
        control_layout.addWidget(self.url_input)


        layout.addLayout(control_layout)
        ####


        # Кнопки действий
        actions_data = [
            ("Подключиться", "mdi6.connection", self.connect_rtsp),
            ("Форма настройки", "mdi6.camera-plus", lambda: self.connect_modal_window(self,"Окно подключения","Форма для подключения")),
            ("Переключить авто-детекцию", "mdi6.car-connected", lambda: (self.toggle_auto_detect(),self.update_display())),
            ("Отключиться", "mdi6.camera-off", lambda: (self.stop_rtsp(),self.clear_display(),self.toggle_auto_detect(True))),
            #(self.name["editor.editor.dock.button.select.all"], "mdi6.check-all", self.stop_rtsp),
        ]
        for name, icon_path, slot in actions_data:
            button = QPushButton(name)
            self.button_icon.append([button, icon_path, 1.1])
            self.widget_buttons.append(button)
            if slot:
                button.clicked.connect(slot)
            button.setProperty("button", "st1")
            #button.setVisible(False)
            layout.addWidget(button)

        # layout.addStretch()

        self.create_dock(
            name=self.name["editor.editor.dock.title"],
            position="left",
            content=dock_content,
            min_width=300,
            max_width=650,
            max_height=1000,
        )

    def connect_modal_window(self,parent, title, message):
        """
        Показывает модальное диалоговое окно с заголовком и сообщением.
        Возвращает True, если нажата кнопка OK, иначе False.
        """
        dialog = QDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(message))


        userdata = pm.load_config()
        login_label = QLabel("Логин: ")
        login_textbox = QLineEdit(userdata["camera_login"])

        pass_label = QLabel("Пароль: ")
        pass_textbox = QLineEdit(userdata["camera_pass"])

        ip_label = QLabel("Ip Адрес: ")
        ip_textbox = QLineEdit(userdata["camera_ip"])

        port_label = QLabel("Порт")
        port_textbox = QLineEdit(userdata["camera_port"])

        stream_path = QComboBox()
        stream_path_label = QLabel("Путь подключения:")
        stream_path.addItems(["stream1", "stream2", "live1", "live2"])
        #self.combo.currentTextChanged.connect(self.on_changed)

        login = QHBoxLayout()
        login.addWidget(login_label)
        login.addWidget(login_textbox)

        passwd = QHBoxLayout()
        passwd.addWidget(pass_label)
        passwd.addWidget(pass_textbox)

        ip = QHBoxLayout()
        ip.addWidget(ip_label)
        ip.addWidget(ip_textbox)

        port = QHBoxLayout()
        port.addWidget(port_label)
        port.addWidget(port_textbox)

        stream = QHBoxLayout()
        stream.addWidget(stream_path_label)
        stream.addWidget(stream_path)

        layout.addLayout(login)
        layout.addLayout(passwd)
        layout.addLayout(ip)
        layout.addLayout(port)
        layout.addLayout(stream)

        def button_ok():
            save_config = { "camera_ip": ip_textbox.text(),
                            "camera_port": port_textbox.text(),
                            "camera_login": login_textbox.text(),
                            "camera_pass": pass_textbox.text(),
                            "camera_stream_path": stream_path.currentText()}


            pm.save_config(filename=0, **save_config)
            dialog.accept()
            print("Конфиг камеры сохранен")
            self.url_input.setText(f"rtsp://{login_textbox.text()}:{pass_textbox.text()}@{ip_textbox.text()}:{port_textbox.text()}/{stream_path.currentText()}")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(lambda:button_ok())


        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        return dialog.exec() == QDialog.Accepted

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
        self.processing_thread.stop()
        self.auto_timer.stop()
        event.accept()