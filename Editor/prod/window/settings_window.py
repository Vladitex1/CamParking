import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QPoint, QRect, Signal
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QAction, QImage
import numpy as np
from dearpygui.dearpygui import theme
from Editor.prod.data.prefers_manager import *
from Editor.prod.data.style import STYLE,change_theme, current_color
import Editor.prod.data.style as style
from Editor.prod.data.names import NAMES,get_language,change_language
from Editor.prod.data.signal_bus import signal
import Editor.prod.data.global_var as global_var
import qtawesome as qta
'''
ВСТАВИТЬ ИКОНКИ QTA В настройки в текст (нужно сделать менеджер для переключения иконок)
'''

class SettingsWindow(QWidget):
    """Первая страница с текстом и кнопкой"""

    def __init__(self):
        self.name = NAMES[get_language()]
        self.data = load_config()
        super().__init__()
        self.settings_layouts = []
        self.options = []
        self.icons = []

        self.theme_element()
        self.language_element()
        self.client_options()

        self.load_settings()
        self.display_elements()

        signal.theme_changed.connect(self.update_theme_buttons)
        self.update_theme_buttons()

    def update_theme_buttons(self):
        for button,icon_path,scale in self.icons:
            icon = qta.icon(icon_path, color=style.STYLE[style.current_color]["text_color"],
                            options=[{'scale_factor': scale, 'color_disabled': style.STYLE[style.current_color]["text_color"]}])
            button.setIcon(icon)


    def theme_element(self):
        theme_group = QGroupBox("theme")
        theme_layout = QVBoxLayout()

        theme_label = QPushButton(f"  {self.name["settings.theme.title"]}")
        theme_label.setStyleSheet(f"font-size: {STYLE["global"]["font_size_h2"]};"
                                  f" font-weight: bold;"
                                  f" text-align: left;"
                                  f"qproperty-iconSize: 35px 35px;"
                                  f"padding: 5px;")
        theme_label.setDisabled(True)
        theme_label.setFlat(True)
        self.icons.append([theme_label,"mdi6.theme-light-dark",1.2])

        theme_layout.addWidget(theme_label)

        self.theme_buttons:dict = {}
        for i in STYLE.keys():
            if i != "global":
                button = QRadioButton(i)
                #button.setStyleSheet(f"color: {STYLE[style.current_color]["text_color"]};")
                button.toggled.connect(lambda checked, theme=i: change_theme(theme))
                self.theme_buttons[i] = button
                theme_layout.addWidget(button)

        theme_group.setLayout(theme_layout)
        self.settings_layouts.append(theme_group)


    def theme_element_change(self,setter_getter:bool = None,name:str = None):
        match setter_getter:
            case True:
                print(self.theme_buttons)
                if name in self.theme_buttons:
                    self.theme_buttons[name].setChecked(True)
            case False:
                #return [(name,self.theme_buttons[name].isChecked()) for name in self.theme_buttons]
                for name in self.theme_buttons:
                    if self.theme_buttons[name].isChecked() == True:
                        return name

    def language_element(self):
        language_group = QGroupBox("theme")
        language_layout = QVBoxLayout()

        language_label = QPushButton(f"  {self.name["settings.language.title"]}")
        language_label.setStyleSheet(f"font-size: {STYLE["global"]["font_size_h2"]};"
                                  f" font-weight: bold;"
                                  f" text-align: left;"
                                  f"qproperty-iconSize: 35px 35px;"
                                  f"padding: 5px;")
        language_label.setDisabled(True)
        language_label.setFlat(True)
        self.icons.append([language_label,"mdi6.translate-variant",1.2])

        language_label_about = QLabel(self.name["settings.language.about"])
        language_label_about.setStyleSheet(f"font-size: {STYLE["global"]["font_size_h4"]}; color: {STYLE["global"]["warning_color"]};")

        language_layout.addWidget(language_label)
        language_layout.addWidget(language_label_about)

        self.language_buttons:dict = {}
        for i in NAMES.keys():
            button = QRadioButton(f"{NAMES[i]["language.emoji"]} | {NAMES[i]["language.fullname"]}")
            button.toggled.connect(lambda checked, language=i: change_language(language))
            self.language_buttons[i] = button
            language_layout.addWidget(button)

        language_group.setLayout(language_layout)
        self.settings_layouts.append(language_group)

    def language_element_change(self,setter_getter:bool = None,name:str = None):
        match setter_getter:
            case True:
                print(self.language_buttons)
                if name in self.language_buttons:
                    self.language_buttons[name].setChecked(True)
            case False:
                #return [(name,self.theme_buttons[name].isChecked()) for name in self.theme_buttons]
                for name in self.language_buttons:
                    if self.language_buttons[name].isChecked() == True:
                        return name

    def client_options(self):
        options_group = QGroupBox("options")
        options_layout = QVBoxLayout()

        options_label = QPushButton(f"  {self.name["settings.options.title"]}")#self.name["settings.language.title"])
        options_label.setStyleSheet(f"font-size: {STYLE["global"]["font_size_h2"]};"
                                  f" font-weight: bold;"
                                  f" text-align: left;"
                                  f"qproperty-iconSize: 35px 35px;"
                                  f"padding: 5px;")
        options_label.setDisabled(True)
        options_label.setFlat(True)
        self.icons.append([options_label,"mdi6.tune-variant",1.2])




        options_fast_nav_label = QLabel(f"{self.name["settings.options.fast.nav.title"]}")#self.name["settings.language.title"])
        options_fast_nav_label.setStyleSheet(f"font-size: {STYLE["global"]["font_size_h3"]}; font-weight: bold;")
        options_fast_nav_about_label = QLabel(f"{self.name["settings.options.fast.nav.about"]}")#self.name["settings.language.about"])
        options_fast_nav_about_label.setStyleSheet(f"font-size: {STYLE["global"]["font_size_h4"]}; color: {STYLE["global"]["secondary_text_color"]};")


        self.options_button_fast_navigation = QCheckBox(f"{self.name["settings.options.fast.nav.button"]}")
        self.options.append(self.options_button_fast_navigation)
        self.options_button_fast_navigation.toggled.connect(signal.fast_nav_changed)

        options_debug_label = QLabel(f"{self.name["settings.options.debug.title"]}")  # self.name["settings.language.title"])
        options_debug_label.setStyleSheet(f"font-size: {STYLE["global"]["font_size_h3"]}; font-weight: bold;")
        options_debug_about_label = QLabel(f"{self.name["settings.options.debug.about"]}")  # self.name["settings.language.about"])
        options_debug_about_label.setStyleSheet(f"font-size: {STYLE["global"]["font_size_h4"]}; color: {STYLE["global"]["warning_color"]};")
        self.options_button_debug = QCheckBox(f"{self.name["settings.options.debug.button"]}")
        self.options.append(self.options_button_debug)


        options_layout.addWidget(options_label)

        options_layout.addWidget(options_fast_nav_label)
        options_layout.addWidget(options_fast_nav_about_label)
        options_layout.addWidget(self.options_button_fast_navigation)

        options_layout.addWidget(options_debug_label)
        options_layout.addWidget(options_debug_about_label)
        options_layout.addWidget(self.options_button_debug)

        options_group.setLayout(options_layout)
        self.settings_layouts.append(options_group)

    def option_changed(self,setter_getter:bool = None,num:int = None):
        match setter_getter:
            case True:
                self.options[num].setChecked(True)
            case False:
                temp = []
                #return [(name,self.theme_buttons[name].isChecked()) for name in self.theme_buttons]
                for num,i in enumerate(self.options):
                    if i.isChecked() == True:
                        temp.append(1)
                    else:
                        temp.append(0)
                return temp

    def load_settings(self):
        self.theme_element_change(True, self.data["client_theme"])
        self.language_element_change(True, self.data["client_language"])
        self.options_button_fast_navigation.setChecked(self.data["client_fast_navigation"])
        self.options_button_debug.setChecked(self.data["client_debug"])
        signal.fast_nav_changed.emit(self.data["client_fast_navigation"])


    def display_elements(self):
        # 1. Верхняя панель с заголовком и кнопкой назад (не прокручивается)
        title_box = QHBoxLayout()
        title_label = QPushButton(f" {self.name['settings.title']}")
        title_label.setStyleSheet(f"font-size: {STYLE['global']['font_size_h1']};"
                                  f" font-weight: bold;"
                                  f" text-align: left;"
                                  f"qproperty-iconSize: 55px 55px;"
                                  f"padding-left: 5px;")
        title_label.setDisabled(True)
        title_label.setFlat(True)
        self.icons.append([title_label, "mdi6.cogs", 1.1])

        title_back_button = QPushButton()
        title_back_button.clicked.connect(lambda: signal.menu_switch_request.emit(global_var.page[0]))
        title_back_button.setProperty("button", "st2")
        self.icons.append([title_back_button, "mdi6.arrow-u-left-top-bold", 1.1])



        title_box.addWidget(title_label)
        title_box.addStretch()
        title_box.addWidget(self.save_button())
        if self.data["client_debug"]:
            title_box.addWidget(self.debug_button())
        title_box.addWidget(title_back_button)

        # 2. Контейнер для прокручиваемого содержимого
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 20, 20)  # убираем лишние отступы

        # Добавляем элементы из self.settings_layouts
        for item in self.settings_layouts:
            if isinstance(item, QLayout):
                scroll_layout.addLayout(item)
            else:
                scroll_layout.addWidget(item)

        scroll_layout.addStretch()  # чтобы содержимое прижималось к верху, если места больше

        # 3. Создаём QScrollArea и помещаем туда контейнер
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # важно: позволяет контенту подстраиваться по ширине
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # горизонтальная не нужна
        scroll_area.setWidget(scroll_content)

        # 4. Главный layout окна
        main_layout = QVBoxLayout(self)
        main_layout.addSpacing(20)
        main_layout.addLayout(title_box)
        main_layout.addWidget(scroll_area)  # вместо прямого добавления элементов
        # main_layout.addStretch() уже не нужно, т.к. scroll_area сам растягивается

        self.setLayout(main_layout)

    def show_message(self):
        """Показать сообщение из текстового поля"""

        correct,error = save_config(
            client_theme=self.theme_element_change(False),
            client_language=self.language_element_change(False),
            client_fast_navigation=self.options_button_fast_navigation.isChecked(),
            client_debug=self.options_button_debug.isChecked(),
                    )
        if correct:
            QMessageBox.information(self, self.name["settings.save.title"], self.name["settings.save.true"])
        else:
            QMessageBox.warning(self, self.name["settings.save.title"], f"{self.name["settings.save.false"]}\n {error}")

    def elements(self):
        pass

    def debug_button(self):
        debug_btn = QPushButton(f"{self.name["debug"]}")
        debug_btn.clicked.connect(lambda:print(self.option_changed(False),self.print_all_qthreads()))
        debug_btn.setProperty("button", "st2")
        self.icons.append([debug_btn, "mdi6.information-slab-box", 1.2])
        return debug_btn

    def save_button(self):
        save_button = QPushButton(self.name["settings.save.title"])
        save_button.clicked.connect(self.show_message)
        save_button.setProperty("button", "st2")
        self.icons.append([save_button, "mdi6.floppy", 1.2])
        return save_button


    def print_all_qthreads(self):
        """Выводит в консоль информацию о всех активных потоках (Python + QThread)."""
        import threading
        import sys
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QThread
        lines = []
        lines.append("\n" + "=" * 60)
        lines.append("🔍 ОТЛАДКА ПОТОКОВ")
        lines.append("=" * 60)

        # 1. Потоки Python (threading)
        lines.append(f"\n📌 Потоки Python (active_count: {threading.active_count()}):")
        for t in threading.enumerate():
            lines.append(f"   • {t.name} | daemon={t.daemon} | alive={t.is_alive()}")
            if hasattr(t, '_target') and t._target:
                lines.append(f"     target: {t._target}")

        # 2. QThread с родителями (через findChildren)
        lines.append("\n📌 QThread объекты (имеющие родителя):")
        app = QApplication.instance()
        found = 0
        if app:
            all_qthreads = set()
            for widget in app.allWidgets():
                for qth in widget.findChildren(QThread):
                    all_qthreads.add(qth)
            if all_qthreads:
                for qth in all_qthreads:
                    lines.append(f"   • {qth} | isRunning={qth.isRunning()} | isFinished={qth.isFinished()}")
                    if qth.parent():
                        lines.append(f"     parent: {qth.parent()}")
                    found += 1
        if found == 0:
            lines.append("   (не найдено)")

        # 3. Диагностика «потерянного» потока (без объекта)
        lines.append("\n💡 Если вы видите сообщение 'QThread: Destroyed while thread is still running',")
        lines.append("   значит существует поток ОС, у которого уже нет Python-объекта QThread.")
        lines.append("   Такие потоки невозможно отобразить через Python API.")
        lines.append("=" * 60)

        print("\n".join(lines))