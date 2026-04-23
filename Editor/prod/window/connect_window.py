import os
from pathlib import Path
import numpy as np
import logic.camera_control as camera_control
from Editor.prod.data.prefers_manager import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import (
    QPixmap, QPen, QBrush, QColor, QAction, QPolygonF, QClipboard, QImage
)

import qtawesome as qta
import logic.file as file
import logic.logic as logic
import Editor.prod.data.style as style
from Editor.prod.data import global_var
from Editor.prod.data.properties import DockTitleBar
from Editor.prod.data.names import NAMES, get_language
from Editor.prod.data.signal_bus import signal


# ----------------------------------------------------------------------
# Поток для обработки кадров
# ----------------------------------------------------------------------
class ProcessingThread(QThread):
    result_ready = Signal(object)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.frame = None
        self.polygons = []
        self.config_name = ""
        self.mutex = QMutex()
        self.cond = QWaitCondition()
        self.busy = False

    def set_frame(self, frame, polygons, config_name):
        self.mutex.lock()
        if not self.busy and self.frame is None:
            self.frame = frame.copy() if frame is not None else None
            self.polygons = polygons.copy()
            self.config_name = config_name
            self.cond.wakeOne()
        self.mutex.unlock()

    def run(self):
        while self._run_flag:
            self.mutex.lock()
            if self.frame is None:
                self.cond.wait(self.mutex)
                self.mutex.unlock()
                continue

            frame = self.frame
            polygons = self.polygons
            config_name = self.config_name
            self.frame = None
            self.mutex.unlock()

            self.busy = True
            try:
                detected_car_data = logic.process_image(
                    image=frame,
                    save_img=False,
                    timestamp=False,
                    config_name=config_name
                )
                comparison_result = logic.comparison(
                    saved_data=polygons,
                    detected_car_data=detected_car_data,
                    nums=False
                )
                self.result_ready.emit(comparison_result)
            except Exception as e:
                print(f"Ошибка в ProcessingThread: {e}")
                self.result_ready.emit(None)
            finally:
                self.busy = False

    def stop(self):
        self._run_flag = False
        self.cond.wakeAll()
        self.wait()


# ----------------------------------------------------------------------
# GraphicsView с масштабированием
# ----------------------------------------------------------------------
class GraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(self.renderHints())
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def fit_to_view(self):
        self.fitInView(self.scene().itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)


# ----------------------------------------------------------------------
# Главное окно
# ----------------------------------------------------------------------
class ConnectWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.name = NAMES[get_language()]
        self.userdata = load_config()
        self.line_size = 3
        self.point_size = 7
        self.text_size = 25
        self.new_color = 4
        self.alpha = 80
        self.max_points_in_polygon = 9
        self.button_icon = []
        self.polygons = []
        self.points = []
        self.img_mutex = QMutex()
        self.config = None
        self.config_name = self.userdata["detection_config"]
        self.detection_timeout = self.userdata["detection_timeout"]
        self.current_color = 0
        self.detection_button = None
        self.auto_timer = QTimer()              # один таймер на всё окно
        self.target_size = QSize(1920, 1080)
        self.colors = [
            "#FF0000", "#FFA500", "#FFFF00", "#00FF00",
            "#00BFFF", "#0000FF", "#EE82EE",
        ]
        self.connect_button = None
        self.widget_buttons = []
        self.img = None
        self.checked = True
        self.online = False
        self.clipboard = QApplication.clipboard()
        self.project_root = str(Path(__file__).parent.parent.parent.parent.resolve())

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        self.create_viewport()
        self.create_toolbar()
        self.create_statusbar()

        self.update_theme_buttons()
        signal.theme_changed.connect(self.update_theme_buttons)

        self.camera_thread = None
        self.processing_thread = ProcessingThread()
        self.processing_thread.result_ready.connect(self.on_processing_result)
        self.processing_thread.start()          # ВАЖНО: запускаем поток обработки



    # ------------------------------------------------------------------
    # Видео-область
    # ------------------------------------------------------------------
    def create_viewport(self):
        self.view = GraphicsView()
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.main_layout.addWidget(self.view)

        self.pixmap_item = QGraphicsPixmapItem()
        self.pixmap_item.setZValue(0)
        self.scene.addItem(self.pixmap_item)

        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

    def update_frame(self, qimage):
        """Слот для обновления кадра из потока камеры"""
        pixmap = QPixmap.fromImage(qimage)
        self.pixmap_item.setPixmap(pixmap)

        if not hasattr(self, '_first_frame_done'):
            self._first_frame_done = True
            self.view.fit_to_view()

        # Приводим к RGB888, если нужно
        if qimage.format() != QImage.Format_RGB888:
            qimage = qimage.convertToFormat(QImage.Format_RGB888)

        # Безопасное получение данных без .setsize()
        ptr = qimage.constBits()
        # ptr - это sip.voidptr, его можно передать в np.frombuffer с указанием count
        arr = np.frombuffer(ptr, dtype=np.uint8, count=qimage.sizeInBytes())
        arr = arr.reshape(qimage.height(), qimage.width(), 3).copy()

        self.img_mutex.lock()
        self.img = arr
        self.img_mutex.unlock()

    # ------------------------------------------------------------------
    # Тулбар
    # ------------------------------------------------------------------
    def create_toolbar(self):
        def create_button(parent, data, style_name, style_class):
            name, icon_path, action = data
            if name == "":
                button = QPushButton()
            else:
                button = QPushButton(name)
            self.button_icon.append([button, icon_path, 1.1])
            self.widget_buttons.append(button)
            if callable(action):
                button.clicked.connect(action)
            button.setProperty(style_name, style_class)
            parent.addWidget(button)

        toolbar = QToolBar(self.name["connect.toolbar.title"])
        self.addToolBar(toolbar)
        toolbar.setProperty("toolbar", "toolbar")

        actions_data = [
            (self.name["editor.toolbar.load.mask"], "mdi6.vector-polygon", lambda: self.load_mask(), "Alt+4"),
            (self.name["editor.toolbar.clear"], "mdi6.delete", lambda: self.clear_display(), "Alt+Del"),
            "stretch",
            "special",
            "stretch",
            (self.name["editor.toolbar.back"], "mdi6.home", lambda: signal.menu_switch_request.emit(0), "Ctrl+Del"),
        ]

        if self.userdata["client_debug"]:
            actions_data.insert(2, (self.name["debug"], "mdi.flask", lambda: self.debug(self.img, "orange.toml"), "Alt+V"))

        for data in actions_data:
            match data:
                case "separator":
                    toolbar.addSeparator()
                case "stretch":
                    spacer = QWidget()
                    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                    spacer.setProperty("toolbar", "spacer")
                    toolbar.addWidget(spacer)
                case "special":
                    self.url_input = QLineEdit()
                    self.url_input.setProperty("QLineEdit", "toolbar")
                    self.url_input.setPlaceholderText("RTSP URL")
                    userdata = load_config()
                    self.url_input.setText(
                        f"rtsp://{userdata['camera_login']}:{userdata['camera_pass']}@{userdata['camera_ip']}:{userdata['camera_port']}/{userdata['camera_stream_path']}"
                    )

                    button_data = [
                        ["", "mdi6.content-copy", lambda: self.clipboard.setText(self.url_input.text())],
                        ["", "mdi6.cog-transfer", lambda: self.connect_modal_window(self, self.name["connect.form.window.name"])]
                    ]

                    create_button(toolbar, button_data[0], "button", "st_toolbar")
                    toolbar.addWidget(self.url_input)
                    create_button(toolbar, button_data[1], "button", "st_toolbar")
                    self.create_camera_connect_toggle(toolbar, "st_toggle_toolbar")
                    self.create_detection_toggle(toolbar, "st_toggle_toolbar")
                case _:
                    action = QAction(self)
                    action.setToolTip(data[0] + " / " + data[3])
                    action.setShortcut(data[3])
                    action.triggered.connect(data[2])
                    toolbar.addAction(action)
                    self.button_icon.append([action, data[1], 1.1])

    def update_theme_buttons(self):
        for button, icon_path, scale in self.button_icon:
            icon = qta.icon(icon_path, color=style.STYLE[style.current_color]["text_color"],
                            options=[{'scale_factor': scale}])
            button.setIcon(icon)

    # ------------------------------------------------------------------
    # Загрузка маски
    # ------------------------------------------------------------------
    def load_mask(self):
        if self.detection_button and self.detection_button.isChecked():
            self.detection_button.setChecked(False)  # остановит таймер
        file_path, _ = QFileDialog.getOpenFileName(
            self, self.name["editor.toolbar.load.file.title"], "../../save", "(*.mask)"
        )
        if file_path:
            self.fit_view()
            self.polygons.clear()
            correct, saved_data, parent_file = file.load_data(file_path)
            if correct:
                for i in saved_data:
                    self.add_polygon_meta(name=i['name'], points=i['points'])
                self.update_display()
                self.status_bar_label_update(mask=self.relative_path(file_path))
                self.statusbar_show_temp_message("load_mask", True, self.relative_path(file_path))
                print(f"load_mask - parent_file: '{parent_file}'")

    def add_polygon_meta(self, name: str = 'noname', points=None):
        new_polygon = {
            'id': len(self.polygons),
            'name': name,
            'points': points.copy(),
        }
        self.polygons.append(new_polygon)
        print(f"Добавлен полигон: {new_polygon}")

    def relative_path(self, input_filepath: str) -> str:
        return str(os.path.relpath(input_filepath, self.project_root).replace("\\", "/"))

    def absolute_path(self, input_filepath: str) -> str:
        return str(os.path.join(self.project_root, input_filepath).replace("\\", "/"))

    def update_display(self, detect_data=None):
        self.clear_display()
        if detect_data is None:
            for num, poly_data in enumerate(self.polygons):
                self.add_polygon(num, poly_data["points"])
        else:
            occupied_names = detect_data[0] if detect_data[0] else []
            for poly_data in self.polygons:
                if poly_data["name"] in occupied_names:
                    self.add_polygon(0, poly_data["points"])
                else:
                    self.add_polygon(3, poly_data["points"])

    # ------------------------------------------------------------------
    # Детекция
    # ------------------------------------------------------------------
    def debug(self, img, config_name):
        self.img_mutex.lock()
        frame_copy = self.img.copy() if self.img is not None else None
        self.img_mutex.unlock()
        if frame_copy is not None:
            self.processing_thread.set_frame(frame_copy, self.polygons.copy(), self.config_name)

    def auto_detect(self):
        # Защита от повторного входа, если предыдущий вызов ещё не завершился
        if hasattr(self, '_detecting') and self._detecting:
            return
        self._detecting = True

        try:
            # Диагностический вывод (можно оставить или закомментировать)
            text = f'''
    ============================================= 
    Параметры сканирования:

    Время таймаута: {self.detection_timeout}
    Выбранный конфиг: {self.config_name}
    =============================================         
            '''
            print(text)

            # 1. Если детекция отключена (кнопка не нажата) – выходим
            if not hasattr(self,
                           'detection_button') or self.detection_button is None or not self.detection_button.isChecked():
                return

            # 2. Если нет камеры – выключаем детекцию и выходим
            if not (self.camera_thread and self.camera_thread.isRunning()):
                if self.detection_button.isChecked():
                    self.detection_button.setChecked(False)
                return

            # 3. Если нет кадра – просто выходим (камера есть, но кадр ещё не пришёл)
            if self.img is None:
                return

            # 4. Убеждаемся, что поток обработки жив, иначе перезапускаем
            if not self.processing_thread.isRunning():
                self.processing_thread.start()
                # Дадим время на запуск, в следующий раз сработает
                return

            # 5. Если поток занят – не трогаем
            if self.processing_thread.busy:
                return

            # 6. Берём копию кадра под мьютексом
            self.img_mutex.lock()
            frame_copy = self.img.copy() if self.img is not None else None
            self.img_mutex.unlock()

            if frame_copy is not None:
                # 7. Отправляем в поток обработки
                self.processing_thread.set_frame(frame_copy, self.polygons.copy(), self.config_name)

        except Exception as e:
            print(f"Ошибка в auto_detect: {e}")
            # При критической ошибке выключаем детекцию, чтобы не зациклиться
            if hasattr(self, 'detection_button') and self.detection_button and self.detection_button.isChecked():
                self.detection_button.setChecked(False)
        finally:
            self._detecting = False

    def on_processing_result(self, comparison_result):
        if comparison_result is not None:
            self.update_display(comparison_result)


    # ------------------------------------------------------------------
    # Рисование полигонов
    # ------------------------------------------------------------------
    def add_polygon(self, color_index: int, points: list):
        polygon = QPolygonF()
        for pt in points:
            polygon.append(QPointF(pt[0], pt[1]))

        color_index = color_index % len(self.colors)
        color = QColor(self.colors[color_index])
        color.setAlpha(self.alpha)

        pen = QPen(QColor(self.colors[color_index]), self.line_size)
        brush = QBrush(color)

        polygon_item = QGraphicsPolygonItem(polygon)
        polygon_item.setPen(pen)
        polygon_item.setBrush(brush)
        polygon_item.setZValue(1)

        self.scene.addItem(polygon_item)
        self.polygon_items.append(polygon_item)

    def clear_display(self):
        if hasattr(self, 'polygon_items'):
            for item in self.polygon_items:
                if item.scene() == self.scene:
                    self.scene.removeItem(item)
            self.polygon_items.clear()
        else:
            self.polygon_items = []

    # ------------------------------------------------------------------
    # Управление RTSP
    # ------------------------------------------------------------------
    def connect_rtsp(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Ошибка", "Введите RTSP URL")
            return

        if not self.processing_thread.isRunning():
            self.processing_thread.start()

        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.stop()
            self.camera_thread.wait(3000)

        self.camera_thread = camera_control.CameraThread(url, (self.target_size.width(), self.target_size.height()))
        self.camera_thread.change_pixmap_signal.connect(self.update_frame)
        self.camera_thread.start()

    def stop_rtsp(self):
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.stop()
            self.camera_thread.wait(3000)
            self.camera_thread = None

        if self.processing_thread.isRunning():
            self.processing_thread.stop()

        self.pixmap_item.setPixmap(QPixmap())

    # ------------------------------------------------------------------
    # Docks
    # ------------------------------------------------------------------
    def create_dock(self, name: str = "", position: str = "left", content=None,
                    min_width: int = 10, max_width: int = 3000,
                    min_height: int = 10, max_height: int = 3000):
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
        dock.installEventFilter(self)
        dock.setProperty("dock_widget", "trackable")
        if position == "left":
            self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        else:
            self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        if not hasattr(self, 'tracked_docks'):
            self.tracked_docks = []
        self.tracked_docks.append(dock)

    def dock_main(self):
        def create_button2(parent, data, style_name, style_class):
            for name, icon_path, action in data:
                button = QPushButton(name)
                self.button_icon.append([button, icon_path, 1.1])
                self.widget_buttons.append(button)
                if action:
                    button.clicked.connect(action)
                button.setProperty(style_name, style_class)
                parent.addWidget(button)

        dock_content = QWidget()
        dock_content.setProperty("dock", "main")
        dock_content.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(dock_content)
        mrg = 25
        layout.setContentsMargins(mrg, mrg, mrg, mrg)

        title_label = QLabel(self.name["connect.dock.name"])
        title_label.setProperty("dock", "main")
        title_label.setStyleSheet(f"font-size: {style.STYLE['global']['font_size_h2']}; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        control_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setProperty("connect", "rtsp")
        self.url_input.setPlaceholderText("RTSP URL")
        userdata = load_config()
        self.url_input.setText(
            f"rtsp://{userdata['camera_login']}:{userdata['camera_pass']}@{userdata['camera_ip']}:{userdata['camera_port']}/{userdata['camera_stream_path']}"
        )
        control_layout.addWidget(self.url_input)
        camera_config_button_data = [("", "mdi6.cog-transfer", lambda: self.connect_modal_window(self, self.name["connect.form.window.name"]))]
        create_button2(control_layout, camera_config_button_data, "button", "st2")
        layout.addLayout(control_layout)

        toggles = QHBoxLayout()
        self.create_detection_toggle(toggles, "st_toggle")
        self.create_camera_connect_toggle(toggles, "st_toggle")
        layout.addLayout(toggles)

        self.create_dock(
            name=self.name["connect.dock.title"],
            position="left",
            content=dock_content,
            min_width=335,
            max_width=650,
            max_height=1000,
        )

    def create_camera_connect_toggle(self, parent, style_class):
        def slot(toggle: bool, button: QObject):
            if toggle:
                button.setEnabled(False)
                self.connect_rtsp()
            else:
                self.stop_rtsp()

        name = self.name["connect.dock.button.camera"]
        icon_path = "mdi6.connection"
        button = QPushButton(name)
        button.setCheckable(True)
        self.button_icon.append([button, icon_path, 1.1])
        self.widget_buttons.append(button)
        button.clicked.connect(lambda: slot(button.isChecked(), button))
        button.setProperty("button", style_class)

        signal.camera_ready.connect(lambda: button.setEnabled(True))
        signal.camera_thread_end_request.connect(lambda: (button.setEnabled(True), button.setChecked(False)))
        parent.addWidget(button)

    def create_detection_toggle(self, parent, style_class):
        def slot(toggle: bool):
            if toggle:
                self.auto_timer.start(int(self.detection_timeout))
            else:
                self.auto_timer.stop()
                self.update_display()

        self.auto_timer.timeout.connect(self.auto_detect)
        name = self.name["connect.dock.button.detection.toggle"]
        icon_path = "mdi6.car-info"
        button = QPushButton(name)
        button.setCheckable(True)
        self.detection_button = button  # <-- сохраняем
        self.button_icon.append([button, icon_path, 1.1])
        self.widget_buttons.append(button)
        button.toggled.connect(lambda checked: slot(checked))
        button.setProperty("button", style_class)
        parent.addWidget(button)

    def connect_modal_window(self, parent, title):
        dialog = QDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(self.name["connect.form.title"]))

        userdata = load_config()

        login_label = QLabel(self.name["connect.form.login"])
        login_textbox = QLineEdit(userdata["camera_login"])

        pass_label = QLabel(self.name["connect.form.pass"])
        pass_textbox = QLineEdit(userdata["camera_pass"])

        ip_label = QLabel(self.name["connect.form.ip"])
        ip_textbox = QLineEdit(userdata["camera_ip"])

        port_label = QLabel(self.name["connect.form.port"])
        port_textbox = QLineEdit(userdata["camera_port"])

        stream_path = QComboBox()
        stream_path_label = QLabel(self.name["connect.form.stream.path"])
        stream_path.addItems(["stream1", "stream2", "live1", "live2"])
        stream_path.setCurrentIndex(stream_path.findText(userdata["camera_stream_path"]))

        self.config = QComboBox()
        config_label = QLabel(self.name["connect.form.config"])
        path = "../../model/config/"
        configs = []
        for i in os.listdir(path):
            configs.append(i)
        self.config.addItems(configs)
        #stream_path.findText(userdata["camera_stream_path"])
        try:
            self.config.setCurrentIndex(self.config.findText(userdata["detection_config"]))

        except:
            pass

        timer_label = QLabel(self.name["connect.form.config"])
        timer_textbox = QLineEdit(str(userdata["detection_timeout"]))

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

        config_box = QHBoxLayout()
        config_box.addWidget(config_label)
        config_box.addWidget(self.config)

        timer_box = QHBoxLayout()
        timer_box.addWidget(timer_label)
        timer_box.addWidget(timer_textbox)

        layout.addLayout(login)
        layout.addLayout(passwd)
        layout.addLayout(ip)
        layout.addLayout(port)
        layout.addLayout(stream)
        layout.addLayout(config_box)
        layout.addLayout(timer_box)

        def button_ok():
            self.config_name = self.config.currentText()
            try:
                time = int(timer_textbox.text())
                if time < 1000:
                    time = 1000
            except:
                time = 1000
                timer_textbox.setText(str(time))
            self.detection_timeout = time

            config = {
                "camera_ip": ip_textbox.text(),
                "camera_port": port_textbox.text(),
                "camera_login": login_textbox.text(),
                "camera_pass": pass_textbox.text(),
                "camera_stream_path": stream_path.currentText(),
                "detection_config": self.config_name,
                "detection_timeout": self.detection_timeout,
            }
            save_config(filename=0, **config)
            dialog.accept()
            print("Конфиг камеры сохранен")
            self.url_input.setText(
                f"rtsp://{login_textbox.text()}:{pass_textbox.text()}@{ip_textbox.text()}:{port_textbox.text()}/{stream_path.currentText()}"
            )

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(button_ok)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        return dialog.exec() == QDialog.Accepted

    # ------------------------------------------------------------------
    # Статусбар
    # ------------------------------------------------------------------
    def create_statusbar(self):
        self.status_bar = QStatusBar(self)
        self.status_bar.setProperty("statusbar", "statusbar")
        self.status_bar.setSizeGripEnabled(False)

        self.status_container = QWidget()
        self.status_container.setProperty("statusbar", "container")
        status_layout = QHBoxLayout(self.status_container)
        status_layout.setContentsMargins(10, 0, 10, 0)
        status_layout.setSpacing(20)
        status_layout.addStretch()

        self.coords_label = QLabel()
        self.coords_label.setProperty("statusbar", "label")
        status_layout.addWidget(self.coords_label)

        separator = QLabel("│")
        separator.setProperty("statusbar", "separator")
        status_layout.addWidget(separator)

        self.mask_name_label = QLabel()
        self.mask_name_label.setProperty("statusbar", "label")
        status_layout.addWidget(self.mask_name_label)

        separator2 = QLabel(" ")
        separator2.setProperty("statusbar", "separator")
        status_layout.addWidget(separator2)

        self.status_bar.addPermanentWidget(self.status_container, stretch=0)
        self.setStatusBar(self.status_bar)

    def status_bar_label_update(self, coords: int = -1, mask: str = "-1"):
        if coords != -1:
            if coords is None:
                self.coords_label.setText(f"📍 {self.name['editor.statusbar.point.false']}")
            else:
                self.coords_label.setText(f"📍 {self.name['editor.statusbar.point.true']}{coords}/{self.max_points_in_polygon + 1}")
        if mask != "-1":
            if mask is None:
                self.mask_name_label.setText(f"📁 {self.name['editor.statusbar.mask.false']}")
            else:
                self.mask_name_label.setText(f"📁 {self.name['editor.statusbar.mask.true']}{mask}")

    def statusbar_show_temp_message(self, msg_type: str, success: bool, data=""):
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

    # ------------------------------------------------------------------
    # События
    # ------------------------------------------------------------------
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self.fit_view()
            return False
        return super().eventFilter(obj, event)

    def fit_view(self):
        self.view.fit_to_view()

    def closeEvent(self, event):
        self.stop_rtsp()
        self.processing_thread.stop()
        self.auto_timer.stop()
        event.accept()