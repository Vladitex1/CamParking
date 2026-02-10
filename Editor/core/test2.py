import sys
import cv2
import numpy as np
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import queue
import threading
import time


class VideoThread(QThread):
    """Поток для чтения видео с буферизацией"""
    frame_signal = Signal(np.ndarray)
    error_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.cap = None
        self.running = False
        self.rtsp_url = ""
        self.buffer = queue.Queue(maxsize=2)  # Буфер на 2 кадра
        self.latest_frame = None
        self.lock = threading.Lock()

    def connect(self, url):
        """Подключение к камере"""
        self.rtsp_url = url
        if self.cap:
            self.cap.release()
            self.cap = None

        try:
            # Добавляем параметры для стабильности
            if 'rtsp_transport' not in url:
                if '?' in url:
                    url += '&rtsp_transport=tcp'
                else:
                    url += '?rtsp_transport=tcp'

            self.cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)

            # Настройки для снижения задержки
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.cap.set(cv2.CAP_PROP_FPS, 30)

            if not self.cap.isOpened():
                raise Exception("Не удалось открыть камеру")

            # Очищаем буфер
            while not self.buffer.empty():
                try:
                    self.buffer.get_nowait()
                except queue.Empty:
                    pass

        except Exception as e:
            self.error_signal.emit(f"Ошибка подключения: {str(e)}")
            return False

        return True

    def run(self):
        """Основной цикл чтения кадров"""
        self.running = True

        while self.running:
            if self.cap and self.cap.isOpened():
                try:
                    ret, frame = self.cap.read()

                    if ret:
                        # Обновляем последний кадр
                        with self.lock:
                            self.latest_frame = frame.copy()

                        # Добавляем в буфер если есть место
                        if self.buffer.qsize() < 2:
                            try:
                                self.buffer.put_nowait(frame)
                            except queue.Full:
                                pass

                        # Отправляем кадр в GUI
                        self.frame_signal.emit(frame)
                    else:
                        self.error_signal.emit("Потеря соединения с камерой")
                        time.sleep(1)  # Пауза перед повторной попыткой

                except Exception as e:
                    print(f"Ошибка чтения: {e}")
                    time.sleep(0.1)
            else:
                time.sleep(0.1)

    def stop(self):
        """Остановка потока"""
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.wait()

    def get_latest_frame(self):
        """Получение последнего кадра"""
        with self.lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None


class RTSPViewer(QMainWindow):
    """Быстрое приложение для RTSP трансляции с рисованием точек"""

    def __init__(self):
        super().__init__()
        self.video_thread = VideoThread()
        self.points = []  # Список точек
        self.current_frame = None

        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("RTSP Viewer - Fast")
        self.setGeometry(100, 100, 900, 600)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Верхняя панель
        top_panel = QWidget()
        top_layout = QHBoxLayout()

        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("rtsp://адрес")
        self.url_edit.setMinimumWidth(400)

        self.connect_btn = QPushButton("▶")
        self.connect_btn.setFixedSize(40, 30)

        self.clear_btn = QPushButton("🗑")
        self.clear_btn.setFixedSize(40, 30)
        self.clear_btn.setEnabled(False)

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Высокое", "Среднее", "Низкое"])
        self.quality_combo.currentTextChanged.connect(self.update_quality)

        top_layout.addWidget(QLabel("RTSP:"))
        top_layout.addWidget(self.url_edit)
        top_layout.addWidget(self.connect_btn)
        top_layout.addWidget(self.clear_btn)
        top_layout.addWidget(QLabel("Качество:"))
        top_layout.addWidget(self.quality_combo)
        top_layout.addStretch()

        top_panel.setLayout(top_layout)

        # Область видео
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: #000;
                border: 2px solid #444;
            }
        """)

        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Информация о точках
        self.points_label = QLabel("Точек: 0")
        self.status_bar.addPermanentWidget(self.points_label)

        # FPS счетчик
        self.fps_label = QLabel("FPS: 0")
        self.status_bar.addPermanentWidget(self.fps_label)

        layout.addWidget(top_panel)
        layout.addWidget(self.video_label, 1)

        central_widget.setLayout(layout)

        # Подключаем сигналы
        self.connect_btn.clicked.connect(self.toggle_connection)
        self.clear_btn.clicked.connect(self.clear_points)
        self.video_thread.frame_signal.connect(self.update_frame)
        self.video_thread.error_signal.connect(self.handle_error)

        # Обработчик кликов
        self.video_label.mousePressEvent = self.video_clicked

        # Таймер для FPS расчета
        self.fps_timer = QElapsedTimer()
        self.fps_timer.start()
        self.frame_counter = 0

        # Таймер для обновления дисплея
        self.display_timer = QTimer()
        self.display_timer.setInterval(33)  # 30 FPS
        self.display_timer.timeout.connect(self.update_display)

        # Устанавливаем качество
        self.quality = 1.0

    def toggle_connection(self):
        """Подключение/отключение"""
        if not self.video_thread.isRunning():
            self.connect_camera()
        else:
            self.disconnect_camera()

    def connect_camera(self):
        """Подключение к камере"""
        url = self.url_edit.text().strip()
        if not url:
            self.status_bar.showMessage("Введите URL камеры")
            return

        if self.video_thread.connect(url):
            self.video_thread.start()
            self.connect_btn.setText("⏹")
            self.clear_btn.setEnabled(True)
            self.url_edit.setEnabled(False)
            self.display_timer.start()
            self.status_bar.showMessage("Подключение...")
        else:
            self.status_bar.showMessage("Ошибка подключения")

    def disconnect_camera(self):
        """Отключение камеры"""
        self.video_thread.stop()
        self.connect_btn.setText("▶")
        self.clear_btn.setEnabled(False)
        self.url_edit.setEnabled(True)
        self.display_timer.stop()
        self.video_label.clear()
        self.status_bar.showMessage("Отключено")

    def update_frame(self, frame):
        """Получение нового кадра из потока"""
        self.current_frame = frame.copy()
        self.frame_counter += 1

    def update_display(self):
        """Обновление отображения (вызывается таймером)"""
        if self.current_frame is not None:
            # Рассчитываем FPS
            elapsed = self.fps_timer.elapsed() / 1000.0
            if elapsed >= 1.0:  # Каждую секунду
                fps = self.frame_counter / elapsed
                self.fps_label.setText(f"FPS: {fps:.1f}")
                self.frame_counter = 0
                self.fps_timer.restart()

            frame = self.current_frame.copy()

            # Применяем масштабирование качества
            if self.quality != 1.0:
                h, w = frame.shape[:2]
                new_w = int(w * self.quality)
                new_h = int(h * self.quality)
                frame = cv2.resize(frame, (new_w, new_h))

            # Рисуем точки
            if self.points and frame is not None:
                h, w = frame.shape[:2]
                for point in self.points:
                    x, y = point
                    # Масштабируем координаты если нужно
                    if self.quality != 1.0:
                        x = int(x * self.quality)
                        y = int(y * self.quality)
                    cv2.circle(frame, (int(x), int(y)), 6, (0, 255, 0), -1)
                    cv2.circle(frame, (int(x), int(y)), 7, (255, 0, 0), 2)

            # Конвертируем в RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Создаем QImage
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # Создаем QPixmap и отображаем
            pixmap = QPixmap.fromImage(qt_image)
            self.video_label.setPixmap(pixmap.scaled(
                self.video_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))

    def update_quality(self, quality_text):
        """Обновление качества"""
        if quality_text == "Высокое":
            self.quality = 1.0
        elif quality_text == "Среднее":
            self.quality = 0.5
        elif quality_text == "Низкое":
            self.quality = 0.3

    def video_clicked(self, event):
        """Обработка клика по видео"""
        if not self.video_thread.isRunning() or self.current_frame is None:
            return

        pixmap = self.video_label.pixmap()
        if not pixmap:
            return

        # Получаем клик
        pos = event.position()

        # Получаем размеры
        label_size = self.video_label.size()
        pixmap_size = pixmap.size()

        # Вычисляем смещение (центрирование)
        x_offset = (label_size.width() - pixmap_size.width()) / 2
        y_offset = (label_size.height() - pixmap_size.height()) / 2

        # Координаты на pixmap
        pixmap_x = pos.x() - x_offset
        pixmap_y = pos.y() - y_offset

        # Пропорции
        scale_x = self.current_frame.shape[1] / pixmap_size.width()
        scale_y = self.current_frame.shape[0] / pixmap_size.height()

        # Координаты на оригинальном кадре
        x = pixmap_x * scale_x / self.quality
        y = pixmap_y * scale_y / self.quality

        # Добавляем точку
        self.points.append((x, y))
        self.points_label.setText(f"Точек: {len(self.points)}")

    def clear_points(self):
        """Очистка точек"""
        self.points = []
        self.points_label.setText("Точек: 0")

    def handle_error(self, error_msg):
        """Обработка ошибок"""
        self.status_bar.showMessage(f"Ошибка: {error_msg}")
        if "Потеря соединения" in error_msg:
            QTimer.singleShot(2000, lambda: self.video_thread.connect(self.url_edit.text()))

    def resizeEvent(self, event):
        """Изменение размера окна"""
        super().resizeEvent(event)

    def closeEvent(self, event):
        """Закрытие приложения"""
        self.video_thread.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Проверяем OpenCV
    try:
        import cv2
    except ImportError:
        QMessageBox.critical(None, "Ошибка",
                             "OpenCV не установлен!\n"
                             "pip install opencv-python")
        sys.exit(1)

    # Минималистичный стиль
    app.setStyle("Fusion")

    # Темная тема для лучшего отображения видео
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(20, 20, 20))
    palette.setColor(QPalette.Button, QColor(45, 45, 45))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(palette)

    window = RTSPViewer()
    window.show()

    sys.exit(app.exec())