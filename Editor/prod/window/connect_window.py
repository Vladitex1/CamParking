import sys
from PySide6.QtCore import Qt, QPointF, QUrl, QRectF
from PySide6.QtGui import QPen, QColor, QBrush, QWheelEvent
from PySide6.QtWidgets import (QApplication, QMainWindow, QGraphicsView,
                               QGraphicsScene, QVBoxLayout, QWidget,
                               QPushButton, QHBoxLayout, QLineEdit, QLabel,
                               QMessageBox, QStatusBar)
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem


class GraphicsView(QGraphicsView):
    """Класс представления с поддержкой масштабирования колесиком мыши"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(self.renderHints())
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def wheelEvent(self, event: QWheelEvent):
        # Масштабирование колесиком мыши
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        # Сохраняем позицию под курсором
        old_pos = self.mapToScene(event.position().toPoint())

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.scale(zoom_factor, zoom_factor)

        # Восстанавливаем позицию под курсором
        new_pos = self.mapToScene(event.position().toPoint())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

    def fit_to_view(self):
        """Масштабирует сцену под размер окна"""
        self.fitInView(self.scene().itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)


class ConnectWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RTSP камера с точками (масштабирование)")
        self.resize(800, 600)

        # Центральный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Панель управления RTSP
        control_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Введите RTSP URL (например, rtsp://admin:pass@192.168.1.100:554/stream)")
        self.url_input.setText("rtsp://admin:@192.168.0.27:554/stream1")  # Пример
        self.connect_btn = QPushButton("Подключиться")
        self.stop_btn = QPushButton("Остановить")
        self.stop_btn.setEnabled(False)

        control_layout.addWidget(QLabel("RTSP URL:"))
        control_layout.addWidget(self.url_input)
        control_layout.addWidget(self.connect_btn)
        control_layout.addWidget(self.stop_btn)

        main_layout.addLayout(control_layout)

        # Панель управления масштабом
        zoom_layout = QHBoxLayout()
        self.zoom_in_btn = QPushButton("+")
        self.zoom_out_btn = QPushButton("-")
        self.fit_btn = QPushButton("По размеру окна")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.fit_btn.clicked.connect(self.fit_view)

        zoom_layout.addWidget(self.zoom_in_btn)
        zoom_layout.addWidget(self.zoom_out_btn)
        zoom_layout.addWidget(self.fit_btn)
        zoom_layout.addStretch()  # Растяжка справа

        main_layout.addLayout(zoom_layout)

        # Graphics View и Scene (используем наш кастомный GraphicsView)
        self.view = GraphicsView()
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        main_layout.addWidget(self.view)

        # Кнопка очистки точек
        button_layout = QHBoxLayout()
        self.clear_button = QPushButton("Очистить точки")
        self.clear_button.clicked.connect(self.clear_points)
        button_layout.addWidget(self.clear_button)
        main_layout.addLayout(button_layout)

        # Видео элемент
        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)

        # Медиа плеер для RTSP
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.video_item)

        # Подключение сигналов
        self.connect_btn.clicked.connect(self.connect_rtsp)
        self.stop_btn.clicked.connect(self.stop_rtsp)
        #self.player.error.connect(self.handle_error)
        self.player.mediaStatusChanged.connect(self.handle_status_changed)
        # При изменении размера видео подгоняем размер сцены
        self.video_item.nativeSizeChanged.connect(self.on_video_size_changed)

        # Включаем отслеживание мыши
        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

        # Список точек
        self.points = []

        # Статус бар
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Готов к подключению")

    def eventFilter(self, obj, event):
        if obj == self.view.viewport() and event.type() == event.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self.add_point(event.position())
                return True
        return super().eventFilter(obj, event)

    def add_point(self, pos: QPointF):
        # Преобразуем координаты viewport в координаты сцены
        scene_pos = self.view.mapToScene(pos.toPoint())
        # Рисуем точку (красный кружок)
        pen = QPen(Qt.GlobalColor.red, 2)
        brush = QBrush(QColor(255, 0, 0, 100))
        ellipse = self.scene.addEllipse(scene_pos.x() - 5, scene_pos.y() - 5, 10, 10, pen, brush)
        ellipse.setZValue(1)
        self.points.append(ellipse)
        print(f"Точка добавлена: ({scene_pos.x():.1f}, {scene_pos.y():.1f})")

    def clear_points(self):
        for point in self.points:
            self.scene.removeItem(point)
        self.points.clear()
        print("Все точки удалены")

    def connect_rtsp(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Ошибка", "Введите RTSP URL")
            return

        self.player.setSource(QUrl(url))
        self.player.play()

        self.connect_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.statusBar.showMessage("Подключение...")

    def stop_rtsp(self):
        self.player.stop()
        self.player.setSource(QUrl())  # сброс источника
        self.connect_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.statusBar.showMessage("Остановлено")

    def handle_error(self, error, error_string):
        QMessageBox.critical(self, "Ошибка медиа", f"Ошибка: {error_string}")
        self.stop_rtsp()

    def handle_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            self.statusBar.showMessage("Поток загружен, воспроизведение...")
        elif status == QMediaPlayer.MediaStatus.BufferingMedia:
            self.statusBar.showMessage("Буферизация...")
        elif status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.statusBar.showMessage("Конец потока")
        elif status == QMediaPlayer.MediaStatus.InvalidMedia:
            self.statusBar.showMessage("Некорректный медиа-источник")

    def on_video_size_changed(self):
        """При изменении размера видео подгоняем сцену под размер view"""
        self.view.fit_to_view()

    def zoom_in(self):
        self.view.scale(1.2, 1.2)

    def zoom_out(self):
        self.view.scale(1 / 1.2, 1 / 1.2)

    def fit_view(self):
        self.view.fit_to_view()

    def closeEvent(self, event):
        self.player.stop()
        event.accept()

