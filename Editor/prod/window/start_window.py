import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QAction, QImage
import numpy as np

class TextPageWidget(QWidget):
    """Первая страница с текстом и кнопкой"""

    def __init__(self):
        super().__init__()

        # Создаем элементы
        title_label = QLabel("Добро пожаловать на первую страницу!")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        info_label = QLabel(
            "Это демонстрационное приложение с двумя страницами.\n\n"
            "На второй странице вы можете загрузить изображение и расставлять на нем точки.\n"
            "Точки можно перемещать, перетаскивая их мышью.\n\n"
            "Используйте меню вверху для переключения между страницами."
        )
        info_label.setWordWrap(True)

        # Создаем кнопку
        self.message_btn = QPushButton("Показать сообщение")
        self.message_btn.clicked.connect(self.show_message)

        # Создаем текстовое поле
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Введите текст здесь...")
        self.text_edit.setMaximumHeight(100)

        # Создаем список
        self.list_widget = QListWidget()
        self.list_widget.addItems(["Элемент 1", "Элемент 2", "Элемент 3"])

        # Создаем переключатели
        self.checkbox1 = QCheckBox("Опция 1")
        self.checkbox2 = QCheckBox("Опция 2")
        self.radio1 = QRadioButton("Вариант A")
        self.radio2 = QRadioButton("Вариант B")

        # Группируем переключатели
        options_group = QGroupBox("Настройки")
        options_layout = QVBoxLayout()
        options_layout.addWidget(self.checkbox1)
        options_layout.addWidget(self.checkbox2)
        options_layout.addWidget(self.radio1)
        options_layout.addWidget(self.radio2)
        options_group.setLayout(options_layout)

        # Создаем прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(50)

        # Создаем слайдер
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self.slider_changed)

        # Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(title_label)
        main_layout.addWidget(info_label)
        main_layout.addSpacing(20)

        # Верхняя часть с кнопкой и текстом
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.message_btn, 1)
        top_layout.addWidget(self.text_edit, 2)
        main_layout.addLayout(top_layout)

        # Средняя часть со списком и настройками
        middle_layout = QHBoxLayout()
        middle_layout.addWidget(self.list_widget, 1)
        middle_layout.addWidget(options_group, 1)
        main_layout.addLayout(middle_layout)

        # Нижняя часть с прогрессом
        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(QLabel("Прогресс:"))
        bottom_layout.addWidget(self.progress_bar)
        bottom_layout.addWidget(QLabel("Слайдер:"))
        bottom_layout.addWidget(self.slider)
        main_layout.addLayout(bottom_layout)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def show_message(self):
        """Показать сообщение из текстового поля"""
        text = self.text_edit.toPlainText()
        if text:
            QMessageBox.information(self, "Сообщение", text)
        else:
            QMessageBox.warning(self, "Внимание", "Введите текст в поле!")

    def slider_changed(self, value):
        """Обработчик изменения слайдера"""
        self.progress_bar.setValue(value)