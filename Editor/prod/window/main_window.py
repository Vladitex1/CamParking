from PySide6.QtWidgets import *
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QProcess
from Editor.prod.window import start_window , editor_window, connect_window
from Editor.prod.data import names as names
from Editor.prod.data.style import change_theme
from Editor.prod.data.names import change_language
import sys
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.name = names.NAMES[names.get_language()]
        self.setWindowTitle(self.name["title"])
        self.setGeometry(100, 100, 900, 700)

        # Создаем центральный виджет для переключения страниц
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # Добавляем страницы в StackedWidget
        self.create_windows()

        # Создаем меню
        self.create_menu()

        # Создаем панель инструментов
        self.create_nav_toolbar()


    def create_windows(self):
        self.menus = [[f"📝{self.name["menu.navigate.start"]}", start_window.StartWindow()],
                 [f"🖼️{self.name["menu.navigate.editor"]}", editor_window.EditorWindow()],
                 [f"📹{self.name["menu.navigate.connect"]}", connect_window.ConnectWindow()],
                 ]

        for name, window in self.menus:
            self.central_widget.addWidget(window)

    def create_menu(self):
        """Создание меню"""
        menubar = self.menuBar()

        # Меню "Страницы" для переключения
        navigation_menu = menubar.addMenu(self.name["menu.navigate"])

        for num,(name,menu) in enumerate(self.menus):
            page = QAction(str(name), self)
            page.setShortcut(f"F{num+1}")
            page.triggered.connect(lambda checked, page=num: self.switch_page(page))
            navigation_menu.addAction(page)


        settings_menu = menubar.addMenu(self.name["menu.parameters"])

        settings_action = QAction(self.name["menu.parameters.settings"], self)
        settings_action.setShortcut("Ctrl+F3")
        #settings_action.triggered.connect(lambda: pass)
        settings_menu.addAction(settings_action)
        #self.name["menu.parameters.switch_theme"]
        turn_on_navigation = QAction("включить меню навигации", self)
        turn_on_navigation.triggered.connect(lambda: self.navigation_toolbar.show())
        turn_on_navigation.setShortcut("Ctrl+F4")
        settings_menu.addAction(turn_on_navigation)

        change_theme_action = QAction(self.name["menu.parameters.switch_theme"], self)
        change_theme_action.triggered.connect(lambda: change_theme())
        change_theme_action.setShortcut("Ctrl+F5")
        settings_menu.addAction(change_theme_action)

        change_language_action = QAction(self.name["menu.parameters.switch_language"], self)
        change_language_action.triggered.connect(lambda: (change_language(),self.switch_language_warning()))
        change_language_action.setShortcut("Ctrl+F6")
        settings_menu.addAction(change_language_action)


        # Меню "Справка"
        help_menu = menubar.addMenu(self.name["menu.help"])

        about_action = QAction(self.name["menu.help.about"], self)
        about_action.triggered.connect(self.show_about)
        about_action.setShortcut("Alt+F9")
        help_menu.addAction(about_action)
##
    def create_nav_toolbar(self,):
        toolbar = QToolBar(self.name["menu.menu_switcher.title"])
        self.addToolBar(toolbar)

        for num,(name,menu) in enumerate(self.menus):
            page = QAction(str(name), self)
            page.triggered.connect(lambda checked, page=num: self.switch_page(page))
            toolbar.addAction(page)

        self.navigation_toolbar = toolbar

    def switch_page(self, index):
        """Переключение между страницами"""
        self.central_widget.setCurrentIndex(index)

    def switch_language_warning(self):
        """Показать предупреждение о перезапуске"""


        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Требуется перезапуск / Restart Required")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setText(
            "Для применения языка необходим перезапуск приложения<br><br><i>Restart required to apply language changes</i>")
        msg_box.setTextFormat(Qt.RichText)

        # Создаем кнопки и сохраняем ссылки
        btn_continue = msg_box.addButton("Продолжить / Continue", QMessageBox.ButtonRole.AcceptRole)
        btn_restart = msg_box.addButton("🔄 Перезапустить / Restart", QMessageBox.ButtonRole.ApplyRole)
        btn_exit = msg_box.addButton("Выйти / Exit", QMessageBox.ButtonRole.RejectRole)

        msg_box.exec()
        clicked_button = msg_box.clickedButton()

        if clicked_button == btn_restart:
            python_exe = sys.executable# Путь к Python интерпретатору
            script_path = os.path.abspath(sys.argv[0])# Путь к скрипту (первый аргумент)
            args = sys.argv[1:]# Остальные аргументы (если есть)
            QProcess.startDetached(python_exe, [script_path] + args)# Запускаем новый процесс: python.exe + script.py + аргументы
            QApplication.quit()# Закрываем текущее приложение

        elif clicked_button == btn_exit:
            QApplication.quit()
        # Если btn_continue — просто закрываем окно

    def show_about(self):
        """Показать окно 'О программе'"""
        info_label = """
            <h2>🎨 CamParking</h2>
            <p><b>Версия:</b> 2.2.4 </p>
            <p><b>Описание:</b> Админское приложение для работы с изображением</p>

            <h3>Возможности:</h3>
            <ul>
                <li>Рисование различными кистями</li>
                <li>Работа со слоями</li>
                <li>Фильтры и эффекты</li>
                <li>Инструменты для работы с фигурами</li>
                <li>Добавление текста</li>
                <li>История действий (Undo/Redo)</li>
            </ul>

            <p><i>Создано с использованием PySide6</i></p>
            """

        QMessageBox.about(
            self,
            "О программе",
            info_label
        )

