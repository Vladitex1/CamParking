from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from Editor.prod.window import start_window , editor_window
from Editor.prod.data import config as config
from Editor.prod.data import names as names
from Editor.prod.data.style import change_theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.name = names.NAMES[config.language]
        self.setWindowTitle(self.name["title"])
        self.setGeometry(100, 100, 900, 700)

        # Создаем центральный виджет для переключения страниц
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # Создаем страницы
        self.start_window = start_window.StartWindow()
        self.editor_window = editor_window.EditorWindow()

        # Добавляем страницы в StackedWidget
        self.central_widget.addWidget(self.start_window )
        self.central_widget.addWidget(self.editor_window)

        # Создаем меню
        self.create_menu()

        # Создаем панель инструментов
        self.create_nav_toolbar()

        # Создаем статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово. Текущая страница: Текстовая")


    def create_menu(self):
        """Создание меню"""
        menubar = self.menuBar()

        # Меню "Страницы" для переключения
        navigation_menu = menubar.addMenu(self.name["menu.navigate"])

        nav_start = QAction(self.name["menu.navigate.start"], self)
        nav_start.setShortcut("F1")
        nav_start.triggered.connect(lambda: self.switch_page(0))
        navigation_menu.addAction(nav_start)

        nav_editor = QAction(self.name["menu.navigate.editor"], self)
        nav_editor.setShortcut("F2")
        nav_editor.triggered.connect(lambda: self.switch_page(1))
        navigation_menu.addAction(nav_editor)


        settings_menu = menubar.addMenu("Параметры")

        settings_action = QAction("Настройки", self)
        settings_action.setShortcut("F3")
        #settings_action.triggered.connect(lambda: pass)
        settings_menu.addAction(settings_action)


        change_theme_action = QAction("Переключить тему", self)
        change_theme_action.triggered.connect(lambda: change_theme())
        change_theme_action.setShortcut("F4")

        settings_menu.addAction(change_theme_action)


        # Меню "Справка"
        help_menu = menubar.addMenu(self.name["menu.help"])

        about_action = QAction(self.name["menu.help.about"], self)
        about_action.triggered.connect(self.show_about)
        about_action.setShortcut("F5")
        help_menu.addAction(about_action)
##
    def create_nav_toolbar(self):
        toolbar = QToolBar("Панель инструментов")
        self.addToolBar(toolbar)

        text_page_btn = QAction("📝 Начало", self)
        text_page_btn.triggered.connect(lambda: self.switch_page(0))
        toolbar.addAction(text_page_btn)

        image_page_btn = QAction("🖼️ Редактор", self)
        image_page_btn.triggered.connect(lambda: self.switch_page(1))
        toolbar.addAction(image_page_btn)




    def switch_page(self, index):
        """Переключение между страницами"""
        self.central_widget.setCurrentIndex(index)

        # Обновляем статус бар
        if index == 0:
            self.status_bar.showMessage("Текущая страница: Текстовая")

        else:
            self.status_bar.showMessage("Текущая страница: Работа с изображением")


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

