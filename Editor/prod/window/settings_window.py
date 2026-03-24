import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QPoint, QRect, Signal
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QAction, QImage
import numpy as np
from dearpygui.dearpygui import theme
from Editor.prod.data.prefers_manager import *
from Editor.prod.data.style import STYLE,change_theme,current_color
import Editor.prod.data.names as names
from Editor.prod.data.signal_bus import signal

class SettingsWindow(QWidget):
    """Первая страница с текстом и кнопкой"""

    def __init__(self):
        self.name = names.NAMES[names.get_language()]
        super().__init__()
        self.settings_layouts = []
        self.options = []

        self.theme_element()
        self.language_element()
        self.client_options()
        self.save_button_element()
        self.debug_button()
        self.display_elements()

        self.load_settings()


    def theme_element(self):
        theme_group = QGroupBox("theme")
        theme_layout = QVBoxLayout()

        theme_label = QLabel(self.name["settings.theme.title"])
        theme_label.setStyleSheet(f"font-size: {STYLE["global"]["font_size_h2"]}; font-weight: bold;")
        theme_layout.addWidget(theme_label)

        self.theme_buttons:dict = {}
        for i in STYLE.keys():
            if i != "global":
                button = QRadioButton(i)
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

        language_label = QLabel(self.name["settings.language.title"])
        language_label.setStyleSheet(f"font-size: {STYLE["global"]["font_size_h2"]}; font-weight: bold;")
        language_label_about = QLabel(self.name["settings.language.about"])
        language_label_about.setStyleSheet(f"font-size: {STYLE["global"]["font_size_h3"]}; color: {STYLE["global"]["secondary_text_color"]};")

        language_layout.addWidget(language_label)
        language_layout.addWidget(language_label_about)

        self.language_buttons:dict = {}
        for i in names.NAMES:
            button = QRadioButton(f"{names.NAMES[i]["language.emoji"]} | {names.NAMES[i]["language.fullname"]}")
            button.toggled.connect(lambda checked, language=i: names.change_language(language))
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

        options_label = QLabel("Опции:")#self.name["settings.language.title"])
        options_label.setStyleSheet(f"font-size: {STYLE["global"]["font_size_h2"]}; font-weight: bold;")

        options_fast_nav_label = QLabel("Меню быстрой навигации:")#self.name["settings.language.title"])
        options_fast_nav_label.setStyleSheet(f"font-size: {STYLE["global"]["font_size_h3"]}; font-weight: bold;")
        options_fast_nav_about_label = QLabel("Панель в верхней части экрана с позволяющая получить быстрый доступ ко всем страницам программы")#self.name["settings.language.about"])
        options_fast_nav_about_label.setStyleSheet(f"font-size: {STYLE["global"]["font_size_h3"]}; color: {STYLE["global"]["secondary_text_color"]};")


        self.options_toggle_fast_navigation = QCheckBox("Быстрая навигация")
        self.options.append(self.options_toggle_fast_navigation)
        self.options_toggle_fast_navigation.toggled.connect(signal.fast_nav_changed.emit)

        options_layout.addWidget(options_label)
        options_layout.addWidget(options_fast_nav_label)
        options_layout.addWidget(options_fast_nav_about_label)
        options_layout.addWidget(self.options_toggle_fast_navigation)

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
        data = load_config()
        self.theme_element_change(True, data["client_theme"])
        self.language_element_change(True, data["client_language"])
        #signal.fast_nav_changed.emit(True if data["client_fast_navigation"] == "1" else False) ##########################################

    def save_button_element(self):
        save_btn = QPushButton(self.name["settings.save.title"])
        save_btn.clicked.connect(self.show_message)
        save_btn.setProperty("button", "st1")
        #save_btn.style().polish(self.save_btn)

        self.settings_layouts.append(save_btn)
        #save_config(theme=current_color)

    def display_elements(self):
        title_label = QLabel(self.name["settings.title"])
        title_label.setStyleSheet(f"font-size: {STYLE["global"]["font_size_h1"]}; font-weight: bold;")
        main_layout = QVBoxLayout()
        main_layout.addWidget(title_label)
        main_layout.addSpacing(20)

        for widget in self.settings_layouts:  # теперь это виджеты
            main_layout.addWidget(widget)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def show_message(self):
        """Показать сообщение из текстового поля"""

        correct,error = save_config(
            client_theme=self.theme_element_change(False),
            client_language=self.language_element_change(False),
            client_fast_nav_menu=self.language_element_change(False)
                    )
        if correct:
            QMessageBox.information(self, self.name["settings.save.title"], self.name["settings.save.true"])
        else:
            QMessageBox.warning(self, self.name["settings.save.title"], f"{self.name["settings.save.false"]}\n {error}")

    def elements(self):
        pass

    def debug_button(self):
        save_btn = QPushButton("дебаг")
        save_btn.clicked.connect(lambda:print(self.option_changed(False)))
        save_btn.setProperty("button", "st1")
        #save_btn.style().polish(self.save_btn)

        self.settings_layouts.append(save_btn)