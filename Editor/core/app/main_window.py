from PySide6.QtWidgets import (
    QMainWindow, QDockWidget
)
from PySide6.QtCore import Qt

from Editor.core.widgets.image_view import ImageView
from Editor.core.widgets.tools_panel import ToolsPanel
from Editor.core.widgets.status_panel import StatusPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CamParking Editor")
        self.resize(1200, 800)

        # центральный виджет
        self.image_view = ImageView()
        self.setCentralWidget(self.image_view)

        # dock панели
        self._create_docks()
        self._create_menu()

    def _create_docks(self):
        self.tools_dock = QDockWidget("Инструменты", self)
        self.tools_dock.setWidget(ToolsPanel())
        self.addDockWidget(Qt.LeftDockWidgetArea, self.tools_dock)

        self.status_dock = QDockWidget("Статус", self)
        self.status_dock.setWidget(StatusPanel())
        self.addDockWidget(Qt.BottomDockWidgetArea, self.status_dock)

        # разрешаем табы и сплит
        self.setDockOptions(
            QMainWindow.AllowTabbedDocks |
            QMainWindow.AllowNestedDocks
        )

    def _create_menu(self):
        menu = self.menuBar()

        file_menu = menu.addMenu("Файл")
        file_menu.addAction("Открыть изображение", self.image_view.open_image)

        view_menu = menu.addMenu("Вид")
        view_menu.addAction("Сохранить layout", self.save_layout)
        view_menu.addAction("Загрузить layout", self.load_layout)

    def save_layout(self):
        self._layout_state = self.saveState()

    def load_layout(self):
        if hasattr(self, "_layout_state"):
            self.restoreState(self._layout_state)
