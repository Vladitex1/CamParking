import os
import tomli
import tomli_w
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
    QPushButton, QListWidget, QFileDialog, QMessageBox, QGroupBox,
    QGridLayout, QComboBox
)
from PySide6.QtCore import Qt, QTimer
import sys


class ConfigEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_dir = "../model/config"
        self.current_config_path = None
        self.current_config = {}

        self.setWindowTitle("YOLO Config Editor")
        self.setMinimumSize(600, 500)

        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # Левая панель - список конфигов
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("📁 Конфигурации:"))

        self.config_list = QListWidget()
        self.config_list.itemClicked.connect(self.load_config_from_list)
        left_layout.addWidget(self.config_list)

        btn_refresh = QPushButton("🔄 Обновить список")
        btn_refresh.clicked.connect(self.refresh_config_list)
        left_layout.addWidget(btn_refresh)

        btn_new = QPushButton("➕ Новый конфиг")
        btn_new.clicked.connect(self.new_config)
        left_layout.addWidget(btn_new)

        main_layout.addWidget(left_panel, 1)

        # Правая панель - редактирование
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Группа основных параметров
        main_group = QGroupBox("🎯 Основные параметры YOLO")
        main_grid = QGridLayout(main_group)

        # model_name
        main_grid.addWidget(QLabel("Модель:"), 0, 0)
        self.model_name = QLineEdit()
        self.model_name.setPlaceholderText("yolo26s.pt")
        main_grid.addWidget(self.model_name, 0, 1)

        # conf
        main_grid.addWidget(QLabel("Confidence (0.0-1.0):"), 1, 0)
        self.conf = QDoubleSpinBox()
        self.conf.setRange(0.0, 1.0)
        self.conf.setSingleStep(0.05)
        self.conf.setDecimals(3)
        main_grid.addWidget(self.conf, 1, 1)

        # iou
        main_grid.addWidget(QLabel("IoU (0.0-1.0):"), 2, 0)
        self.iou = QDoubleSpinBox()
        self.iou.setRange(0.0, 1.0)
        self.iou.setSingleStep(0.05)
        self.iou.setDecimals(3)
        main_grid.addWidget(self.iou, 2, 1)

        # imgsz
        main_grid.addWidget(QLabel("Image Size:"), 3, 0)
        self.imgsz = QSpinBox()
        self.imgsz.setRange(320, 2560)
        self.imgsz.setSingleStep(64)
        main_grid.addWidget(self.imgsz, 3, 1)

        # classes
        main_grid.addWidget(QLabel("Классы (COCO IDs):"), 4, 0)
        self.classes = QLineEdit()
        self.classes.setPlaceholderText("2, 5, 7 (car, bus, truck)")
        main_grid.addWidget(self.classes, 4, 1)

        right_layout.addWidget(main_group)

        # Группа отображения
        visual_group = QGroupBox("🎨 Визуализация")
        visual_grid = QGridLayout(visual_group)

        # line_width
        visual_grid.addWidget(QLabel("Толщина рамки:"), 0, 0)
        self.line_width = QSpinBox()
        self.line_width.setRange(1, 10)
        visual_grid.addWidget(self.line_width, 0, 1)

        # font_size
        visual_grid.addWidget(QLabel("Размер текста:"), 1, 0)
        self.font_size = QDoubleSpinBox()
        self.font_size.setRange(0.5, 5.0)
        self.font_size.setSingleStep(0.5)
        self.font_size.setDecimals(1)
        visual_grid.addWidget(self.font_size, 1, 1)

        # show_conf
        self.show_conf = QCheckBox("Показывать уверенность")
        visual_grid.addWidget(self.show_conf, 2, 0, 1, 2)

        # labels
        self.labels = QCheckBox("Показывать названия классов")
        visual_grid.addWidget(self.labels, 3, 0, 1, 2)

        right_layout.addWidget(visual_group)

        # Кнопки сохранения
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("💾 Сохранить")
        btn_save.clicked.connect(self.save_config)
        btn_save_as = QPushButton("📄 Сохранить как...")
        btn_save_as.clicked.connect(self.save_config_as)
        btn_delete = QPushButton("🗑️ Удалить")
        btn_delete.clicked.connect(self.delete_config)

        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_save_as)
        btn_layout.addWidget(btn_delete)

        right_layout.addLayout(btn_layout)

        # Статус
        self.status_label = QLabel("Готов")
        self.status_label.setStyleSheet("color: gray; padding: 5px;")
        right_layout.addWidget(self.status_label)

        main_layout.addWidget(right_panel, 2)

        # Загружаем список конфигов
        self.refresh_config_list()

    def refresh_config_list(self):
        """Обновляет список доступных TOML файлов"""
        self.config_list.clear()
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        for file in os.listdir(self.config_dir):
            if file.endswith('.toml'):
                self.config_list.addItem(file)

        if self.config_list.count() > 0:
            self.status_label.setText(f"📁 Найдено {self.config_list.count()} конфигов")
        else:
            self.status_label.setText("📁 Нет конфигов. Создайте новый!")

    def load_config_from_list(self, item):
        """Загружает выбранный конфиг"""
        config_name = item.text()
        self.current_config_path = os.path.join(self.config_dir, config_name)

        try:
            with open(self.current_config_path, 'rb') as f:
                self.current_config = tomli.load(f)

            # Заполняем поля
            self.model_name.setText(self.current_config.get("model_name", ""))
            self.conf.setValue(self.current_config.get("conf", 0.25))
            self.iou.setValue(self.current_config.get("iou", 0.45))
            self.imgsz.setValue(self.current_config.get("imgsz", 640))

            # classes
            classes = self.current_config.get("classes", [2, 5, 7])
            self.classes.setText(", ".join(map(str, classes)))

            # визуализация
            self.line_width.setValue(self.current_config.get("line_width", 2))
            self.font_size.setValue(self.current_config.get("font_size", 1.0))
            self.show_conf.setChecked(self.current_config.get("show_conf", True))
            self.labels.setChecked(self.current_config.get("labels", True))

            self.status_label.setText(f"✅ Загружен: {config_name}")
            self.setWindowTitle(f"YOLO Config Editor - {config_name}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить конфиг:\n{e}")

    def get_current_config(self):
        """Собирает текущие значения в словарь"""
        # Парсим classes
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
            QMessageBox.information(self, "Успех", "Конфигурация сохранена!")

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

            try:
                config = self.get_current_config()
                with open(self.current_config_path, 'wb') as f:
                    tomli_w.dump(config, f)

                self.refresh_config_list()
                self.status_label.setText(f"💾 Сохранено: {os.path.basename(file_name)}")
                QMessageBox.information(self, "Успех", "Конфигурация сохранена!")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить:\n{e}")

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
                self.current_config = {}
                self.refresh_config_list()
                self.status_label.setText("🗑️ Конфиг удалён")
                self.setWindowTitle("YOLO Config Editor")

                # Очищаем поля
                self.model_name.clear()
                self.conf.setValue(0.25)
                self.iou.setValue(0.45)
                self.imgsz.setValue(640)
                self.classes.clear()
                self.line_width.setValue(2)
                self.font_size.setValue(1.0)
                self.show_conf.setChecked(True)
                self.labels.setChecked(True)

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить:\n{e}")

    def new_config(self):
        """Создаёт новый конфиг с значениями по умолчанию"""
        self.current_config_path = None
        self.current_config = {}

        # Сбрасываем поля
        self.model_name.setText("yolo26s.pt")
        self.conf.setValue(0.25)
        self.iou.setValue(0.45)
        self.imgsz.setValue(640)
        self.classes.setText("2, 5, 7")
        self.line_width.setValue(2)
        self.font_size.setValue(1.0)
        self.show_conf.setChecked(True)
        self.labels.setChecked(True)

        self.status_label.setText("🆕 Новый конфиг (не сохранён)")
        self.setWindowTitle("YOLO Config Editor - Новый конфиг")

        # Предлагаем сразу сохранить
        reply = QMessageBox.question(
            self, "Новый конфиг",
            "Создать новый конфиг? Нажмите Сохранить, чтобы записать файл.",
            QMessageBox.Ok
        )


def main():
    app = QApplication(sys.argv)
    window = ConfigEditor()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()