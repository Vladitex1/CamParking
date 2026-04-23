import os
import cv2
import tomli
import tomli_w
import numpy as np
from ultralytics import YOLO
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QImage
import sys

# ========== МОДЕЛЬ И ДЕТЕКЦИЯ ==========
_MODEL_CACHE = {}


def get_model(model_path: str):
    """Возвращает модель YOLO, загружая её один раз."""
    if model_path not in _MODEL_CACHE:
        _MODEL_CACHE[model_path] = YOLO(model_path)
    return _MODEL_CACHE[model_path]


def detect_on_image(image, config: dict):
    """Детекция на изображении с использованием конфига"""
    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "model", config["model_name"]))
    model = get_model(model_path)

    results = model.predict(
        source=image,
        conf=config['conf'],
        iou=config['iou'],
        imgsz=config['imgsz'],
        classes=config['classes']
    )

    annotated_frame = results[0].plot(
        line_width=config.get("line_width", 2),
        font_size=config.get("font_size", 12),
        conf=config.get("show_conf", True),
        labels=config.get("labels", True)
    )

    vehicles_info = []
    for obj in results[0].boxes:
        class_id = int(obj.cls[0])
        confidence = float(obj.conf[0])
        class_name = results[0].names[class_id]

        if class_name in ["car", "truck", "bus"]:
            x1, y1, x2, y2 = map(int, obj.xyxy[0])
            vehicles_info.append({
                "type": class_name,
                "confidence": confidence * 100,
                "position": [x1, y1, x2, y2]
            })

    return annotated_frame, vehicles_info


# ========== ОСНОВНОЕ ОКНО ==========
class ConfigEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_dir = "../model/config"
        self.image_dir = "../img/camphoto"
        self.current_config_path = None

        self.setWindowTitle("YOLO Config Editor & Detector")
        self.setMinimumSize(1200, 800)

        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # ========== ЛЕВАЯ ПАНЕЛЬ - СПИСОК КОНФИГОВ ==========
        left_panel = QWidget()
        left_panel.setFixedWidth(250)
        left_layout = QVBoxLayout(left_panel)

        left_layout.addWidget(QLabel("📁 Конфигурации YOLO:"))

        self.config_list = QListWidget()
        self.config_list.itemClicked.connect(self.on_config_selected)
        left_layout.addWidget(self.config_list)

        btn_refresh = QPushButton("🔄 Обновить список")
        btn_refresh.clicked.connect(self.refresh_config_list)
        left_layout.addWidget(btn_refresh)

        btn_new = QPushButton("➕ Новый конфиг")
        btn_new.clicked.connect(self.new_config)
        left_layout.addWidget(btn_new)

        btn_delete = QPushButton("🗑️ Удалить конфиг")
        btn_delete.clicked.connect(self.delete_config)
        left_layout.addWidget(btn_delete)

        left_layout.addStretch()

        # ========== ЦЕНТРАЛЬНАЯ ПАНЕЛЬ - РЕДАКТИРОВАНИЕ ==========
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)

        # Группа основных параметров
        main_group = QGroupBox("🎯 Основные параметры YOLO")
        main_grid = QGridLayout(main_group)

        main_grid.addWidget(QLabel("Модель:"), 0, 0)
        self.model_name = QLineEdit()
        self.model_name.setPlaceholderText("yolo26s.pt")
        main_grid.addWidget(self.model_name, 0, 1)

        main_grid.addWidget(QLabel("Confidence (0.0-1.0):"), 1, 0)
        self.conf = QDoubleSpinBox()
        self.conf.setRange(0.0, 1.0)
        self.conf.setSingleStep(0.05)
        self.conf.setDecimals(3)
        main_grid.addWidget(self.conf, 1, 1)

        main_grid.addWidget(QLabel("IoU (0.0-1.0):"), 2, 0)
        self.iou = QDoubleSpinBox()
        self.iou.setRange(0.0, 1.0)
        self.iou.setSingleStep(0.05)
        self.iou.setDecimals(3)
        main_grid.addWidget(self.iou, 2, 1)

        main_grid.addWidget(QLabel("Image Size:"), 3, 0)
        self.imgsz = QSpinBox()
        self.imgsz.setRange(320, 2560)
        self.imgsz.setSingleStep(64)
        main_grid.addWidget(self.imgsz, 3, 1)

        main_grid.addWidget(QLabel("Классы (COCO IDs):"), 4, 0)
        self.classes = QLineEdit()
        self.classes.setPlaceholderText("2, 5, 7 (car, bus, truck)")
        main_grid.addWidget(self.classes, 4, 1)

        center_layout.addWidget(main_group)

        # Группа визуализации
        visual_group = QGroupBox("🎨 Визуализация")
        visual_grid = QGridLayout(visual_group)

        visual_grid.addWidget(QLabel("Толщина рамки:"), 0, 0)
        self.line_width = QSpinBox()
        self.line_width.setRange(1, 10)
        visual_grid.addWidget(self.line_width, 0, 1)

        visual_grid.addWidget(QLabel("Размер текста:"), 1, 0)
        self.font_size = QDoubleSpinBox()
        self.font_size.setRange(0.5, 5.0)
        self.font_size.setSingleStep(0.5)
        self.font_size.setDecimals(1)
        visual_grid.addWidget(self.font_size, 1, 1)

        self.show_conf = QCheckBox("Показывать уверенность")
        visual_grid.addWidget(self.show_conf, 2, 0, 1, 2)

        self.labels = QCheckBox("Показывать названия классов")
        visual_grid.addWidget(self.labels, 3, 0, 1, 2)

        center_layout.addWidget(visual_group)

        # Кнопки сохранения
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("💾 Сохранить конфиг")
        btn_save.clicked.connect(self.save_config)
        btn_save_as = QPushButton("📄 Сохранить как...")
        btn_save_as.clicked.connect(self.save_config_as)
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_save_as)
        center_layout.addLayout(btn_layout)

        center_layout.addStretch()

        # ========== ПРАВАЯ ПАНЕЛЬ - ДЕТЕКЦИЯ ==========
        right_panel = QWidget()
        right_panel.setMinimumWidth(500)
        right_layout = QVBoxLayout(right_panel)

        # Выбор изображения
        image_select_layout = QHBoxLayout()
        image_select_layout.addWidget(QLabel("📷 Изображение:"))

        self.image_combo = QComboBox()
        self.image_combo.setEditable(True)
        self.image_combo.currentTextChanged.connect(self.on_image_selected)
        image_select_layout.addWidget(self.image_combo)

        btn_browse = QPushButton("📁 Обзор...")
        btn_browse.clicked.connect(self.browse_image)
        image_select_layout.addWidget(btn_browse)

        btn_refresh_images = QPushButton("🔄 Обновить")
        btn_refresh_images.clicked.connect(self.refresh_image_list)
        image_select_layout.addWidget(btn_refresh_images)

        right_layout.addLayout(image_select_layout)

        # Кнопка детекции
        self.btn_detect = QPushButton("🔍 ЗАПУСТИТЬ ДЕТЕКЦИЮ")
        self.btn_detect.setStyleSheet("font-size: 14px; padding: 10px; background-color: #4CAF50; color: white;")
        self.btn_detect.clicked.connect(self.run_detection)
        right_layout.addWidget(self.btn_detect)

        # Предпросмотр изображения (РАСТЯГИВАЕТСЯ)
        preview_group = QGroupBox("📸 Предпросмотр")
        preview_layout = QVBoxLayout(preview_group)
        self.preview_label = QLabel("Выберите изображение")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setStyleSheet("border: 1px solid gray; background-color: #2d2d2d;")
        self.preview_label.setScaledContents(True)  # <-- РАСТЯГИВАЕТ
        preview_layout.addWidget(self.preview_label)
        right_layout.addWidget(preview_group)

        # Результат детекции
        result_group = QGroupBox("🎯 Результат детекции")
        result_layout = QVBoxLayout(result_group)

        # Результат - изображение (РАСТЯГИВАЕТСЯ)
        self.result_label = QLabel("Здесь появится результат")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setMinimumHeight(300)
        self.result_label.setStyleSheet("border: 1px solid gray; background-color: #2d2d2d;")
        self.result_label.setScaledContents(True)  # <-- РАСТЯГИВАЕТ
        result_layout.addWidget(self.result_label)

        # Результат - текст
        self.result_text = QTextEdit()
        self.result_text.setMaximumHeight(150)
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)

        right_layout.addWidget(result_group)

        # Статус
        self.status_label = QLabel("Готов")
        self.status_label.setStyleSheet("color: gray; padding: 5px;")
        right_layout.addWidget(self.status_label)

        # ========== СПЛИТТЕР ==========
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([250, 400, 550])

        main_layout.addWidget(splitter)

        # Загружаем данные
        self.refresh_config_list()
        self.refresh_image_list()

    # ========== КОНФИГИ ==========
    def refresh_config_list(self):
        """Обновляет список TOML файлов"""
        self.config_list.clear()
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        for file in sorted(os.listdir(self.config_dir)):
            if file.endswith('.toml'):
                self.config_list.addItem(file)

        if self.config_list.count() > 0:
            self.status_label.setText(f"📁 Найдено {self.config_list.count()} конфигов")
            # Автоматически загружаем первый
            self.config_list.setCurrentRow(0)
            self.on_config_selected(self.config_list.item(0))
        else:
            self.status_label.setText("📁 Нет конфигов. Создайте новый!")

    def on_config_selected(self, item):
        """Автоматически загружает выбранный конфиг"""
        config_name = item.text()
        self.current_config_path = os.path.join(self.config_dir, config_name)

        try:
            with open(self.current_config_path, 'rb') as f:
                config = tomli.load(f)

            # Заполняем поля
            self.model_name.setText(config.get("model_name", ""))
            self.conf.setValue(config.get("conf", 0.25))
            self.iou.setValue(config.get("iou", 0.45))
            self.imgsz.setValue(config.get("imgsz", 640))

            classes = config.get("classes", [2, 5, 7])
            self.classes.setText(", ".join(map(str, classes)))

            self.line_width.setValue(config.get("line_width", 2))
            self.font_size.setValue(config.get("font_size", 1.0))
            self.show_conf.setChecked(config.get("show_conf", True))
            self.labels.setChecked(config.get("labels", True))

            self.status_label.setText(f"✅ Загружен: {config_name}")

        except Exception as e:
            self.status_label.setText(f"❌ Ошибка загрузки: {e}")

    def get_current_config(self):
        """Собирает текущие значения в словарь"""
        classes_text = self.classes.text().strip()
        if classes_text:
            classes = [int(x.strip()) for x in classes_text.split(",")]
        else:
            classes = [2, 5, 7]

        return {
            "model_name": self.model_name.text(),
            "conf": self.conf.value(),
            "iou": self.iou.value(),
            "imgsz": self.imgsz.value(),
            "classes": classes,
            "line_width": self.line_width.value(),
            "font_size": self.font_size.value(),
            "show_conf": self.show_conf.isChecked(),
            "labels": self.labels.isChecked()
        }

    def save_config(self):
        """Сохраняет текущий конфиг"""
        if not self.current_config_path:
            self.save_config_as()
            return

        try:
            config = self.get_current_config()
            with open(self.current_config_path, 'wb') as f:
                tomli_w.dump(config, f)

            self.status_label.setText(f"💾 Сохранено: {os.path.basename(self.current_config_path)}")
            #QMessageBox.information(self, "Успех", "Конфигурация сохранена!")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить:\n{e}")

    def save_config_as(self):
        """Сохраняет конфиг в новый файл"""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Сохранить конфиг", self.config_dir, "TOML files (*.toml)"
        )

        if file_name:
            if not file_name.endswith('.toml'):
                file_name += '.toml'

            self.current_config_path = file_name
            self.save_config()
            self.refresh_config_list()

    def delete_config(self):
        """Удаляет текущий конфиг"""
        if not self.current_config_path:
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить {os.path.basename(self.current_config_path)}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                os.remove(self.current_config_path)
                self.current_config_path = None
                self.refresh_config_list()
                self.status_label.setText("🗑️ Конфиг удалён")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить:\n{e}")

    def new_config(self):
        """Создаёт новый конфиг со значениями по умолчанию"""
        self.current_config_path = None

        self.model_name.setText("yolo26s.pt")
        self.conf.setValue(0.25)
        self.iou.setValue(0.45)
        self.imgsz.setValue(640)
        self.classes.setText("2, 5, 7")
        self.line_width.setValue(2)
        self.font_size.setValue(1.0)
        self.show_conf.setChecked(True)
        self.labels.setChecked(True)

        self.status_label.setText("🆕 Новый конфиг (нажмите Сохранить)")

        # Сразу предлагаем сохранить
        reply = QMessageBox.question(
            self, "Новый конфиг",
            "Создать новый конфиг?",
            QMessageBox.Save | QMessageBox.Cancel
        )
        if reply == QMessageBox.Save:
            self.save_config_as()

    # ========== ИЗОБРАЖЕНИЯ ==========
    def refresh_image_list(self):
        """Обновляет список изображений"""
        self.image_combo.clear()
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)

        for file in sorted(os.listdir(self.image_dir)):
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                self.image_combo.addItem(file)

        if self.image_combo.count() > 0:
            self.status_label.setText(f"📸 Найдено {self.image_combo.count()} изображений")
            self.on_image_selected(self.image_combo.currentText())

    def on_image_selected(self, image_name):
        """Автоматически показывает выбранное изображение (растянуто)"""
        if not image_name:
            return

        image_path = os.path.join(self.image_dir, image_name)
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            # Не масштабируем, просто устанавливаем - setScaledContents сделает растяжение
            self.preview_label.setPixmap(pixmap)
            self.status_label.setText(f"📷 Выбрано: {image_name}")
        else:
            self.preview_label.setText("Изображение не найдено")

    def browse_image(self):
        """Открывает диалог выбора изображения"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", self.image_dir,
            "Image files (*.jpg *.jpeg *.png *.bmp)"
        )
        if file_path:
            # Копируем в папку если нужно
            import shutil
            file_name = os.path.basename(file_path)
            dest_path = os.path.join(self.image_dir, file_name)

            if file_path != dest_path:
                shutil.copy(file_path, dest_path)

            self.refresh_image_list()
            self.image_combo.setCurrentText(file_name)

    # ========== ДЕТЕКЦИЯ ==========
    def run_detection(self):
        """Запускает детекцию на выбранном изображении"""
        self.save_config()
        image_name = self.image_combo.currentText()
        if not image_name:
            QMessageBox.warning(self, "Ошибка", "Выберите изображение!")
            return

        if not self.current_config_path:
            QMessageBox.warning(self, "Ошибка", "Выберите конфиг!")
            return

        try:
            self.btn_detect.setEnabled(False)
            self.btn_detect.setText("⏳ Обработка...")
            self.status_label.setText("🔄 Запуск детекции...")
            QApplication.processEvents()

            # Загружаем конфиг
            with open(self.current_config_path, 'rb') as f:
                config = tomli.load(f)

            # Загружаем изображение
            image_path = os.path.join(self.image_dir, image_name)
            image = cv2.imread(image_path)
            if image is None:
                raise Exception(f"Не удалось загрузить изображение: {image_path}")

            # Детекция
            self.status_label.setText("🚀 Детекция YOLO...")
            QApplication.processEvents()

            annotated_frame, vehicles = detect_on_image(image, config)

            # Сохраняем результат во временный файл
            temp_result_path = "temp_result.jpg"
            cv2.imwrite(temp_result_path, annotated_frame)

            # Показываем результат (растянуто)
            pixmap = QPixmap(temp_result_path)
            self.result_label.setPixmap(pixmap)

            # Текстовый результат
            result_info = f"✅ Детекция завершена!\n"
            result_info += f"📷 Изображение: {image_name}\n"
            result_info += f"⚙️ Конфиг: {os.path.basename(self.current_config_path)}\n"
            result_info += f"🚗 Найдено машин: {len(vehicles)}\n\n"

            if vehicles:
                result_info += "📋 Список найденных машин:\n"
                for i, v in enumerate(vehicles, 1):
                    result_info += f"  {i}. {v['type']} (уверенность: {v['confidence']:.1f}%)\n"
            else:
                result_info += "⚠️ Машин не найдено\n"

            self.result_text.setText(result_info)
            self.status_label.setText(f"✅ Готово! Найдено {len(vehicles)} машин")

            # Очищаем временный файл через таймер
            QTimer.singleShot(100, lambda: self.cleanup_temp(temp_result_path))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка детекции:\n{e}")
            self.result_text.setText(f"❌ Ошибка: {e}")
            self.status_label.setText(f"❌ Ошибка: {e}")

        finally:
            self.btn_detect.setEnabled(True)
            self.btn_detect.setText("🔍 ЗАПУСТИТЬ ДЕТЕКЦИЮ")

    def cleanup_temp(self, path):
        """Удаляет временный файл"""
        try:
            if os.path.exists(path):
                os.remove(path)
        except:
            pass


def main():
    app = QApplication(sys.argv)
    window = ConfigEditor()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()