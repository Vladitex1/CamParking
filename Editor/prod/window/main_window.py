from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from Editor.prod.window import start_window as text_page_w, editor_window as img_dock_w
from Editor.prod.data import config as config
from Editor.prod.data import names as names


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.name= names.NAMES[config.language]
        self.setWindowTitle(self.name["title"])
        self.setGeometry(100, 100, 900, 700)

        # Создаем центральный виджет для переключения страниц
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # Создаем страницы
        self.text_page = text_page_w.TextPageWidget()
        self.image_page = img_dock_w.ImageDockWidget()

        # Добавляем страницы в StackedWidget
        self.central_widget.addWidget(self.text_page)
        self.central_widget.addWidget(self.image_page)

        # Создаем меню
        self.create_menu()

        # Создаем панель инструментов
        self.create_nav_toolbar()
#       self.create_toolbar()

        # Создаем статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово. Текущая страница: Текстовая")


    def create_menu(self):
        """Создание меню"""
        menubar = self.menuBar()

        # Меню "Страницы" для переключения
        pages_menu = menubar.addMenu(self.name["menu.navigate"])

        text_page_action = QAction(self.name["menu.navigate.start"], self)
        text_page_action.setShortcut("F1")
        text_page_action.triggered.connect(lambda: self.switch_page(0))
        pages_menu.addAction(text_page_action)

        image_page_action = QAction(self.name["menu.navigate.editor"], self)
        image_page_action.setShortcut("F2")
        image_page_action.triggered.connect(lambda: self.switch_page(1))
        pages_menu.addAction(image_page_action)


        # Меню "Файл"
        file_menu = menubar.addMenu(self.name["menu.file"])

        new_action = QAction(self.name["menu.file.new"], self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)

        open_action = QAction(self.name["menu.file.open"], self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)

        save_action = QAction(self.name["menu.file.save"], self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction(self.name["menu.file.exit"], self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню "Справка"
        help_menu = menubar.addMenu(self.name["menu.help"])

        about_action = QAction(self.name["menu.help.about"], self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
##
    def create_nav_toolbar(self):
        toolbar = QToolBar("Панель инструментов")
        self.addToolBar(toolbar)

        text_page_btn = QAction("📝 Текст", self)
        text_page_btn.triggered.connect(lambda: self.switch_page(0))
        toolbar.addAction(text_page_btn)

        image_page_btn = QAction("🖼️ Изображение", self)
        image_page_btn.triggered.connect(lambda: self.switch_page(1))
        toolbar.addAction(image_page_btn)




    def switch_page(self, index):
        """Переключение между страницами"""
        self.central_widget.setCurrentIndex(index)

        # Обновляем статус бар
        if index == 0:
            self.status_bar.showMessage("Текущая страница: Текстовая")
            #Editor
            #self.EditorDock.setVisible(False)
            #self.editor_load_image_action.setVisible(False)

        else:
            self.status_bar.showMessage("Текущая страница: Работа с изображением")
            #Editor
            #self.EditorDock.setVisible(True)
            #self.editor_load_image_action.setVisible(True)

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

