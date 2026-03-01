from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QFontDatabase
import os
from Editor.prod.data.prefers_manager import save_config
import qtawesome as qta

#### иконки: qta-browser в shell
app = None
FONT_FAMILY = ""
current_color = "dark"  # или "dark"
#======================= сигнал, который будет передавать новое имя темы ================================

class ThemeSignals(QObject):
    changed = Signal(str)

theme_signals = ThemeSignals()  # глобальный объект для доступа к сигналу

def load_theme(color:str="light"):
    global current_color
    if app != None:
        current_color = color
        app.setStyleSheet(get_stylesheet())

def change_theme():
    global current_color
    if current_color == "dark":
        current_color = "light"
    else:
        current_color = "dark"
    load_theme(current_color)
    save_config(theme = current_color)
    theme_signals.changed.emit(current_color)   # <-- добавить


def load_font():
    global FONT_FAMILY
    # Загружаем шрифт (возвращает ID или -1 при ошибке)
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "fonts", "Lorenzo Sans Medium.ttf"))
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id != -1:
        families = QFontDatabase.applicationFontFamilies(font_id)
        if families:
            FONT_FAMILY = families[0]
            print(f"Шрифт '{FONT_FAMILY}' успешно загружен")
    else:
        FONT_FAMILY = "Arial"                      # ← строка, а не объект QFont!
        print("Ошибка загрузки шрифта, используем Arial")

def calc_color(color: str, percent: int):
    color = color.lstrip('#')
    rgb = [int(color[i:i+2], 16) for i in (0, 2, 4)]
    amount = round(255 * (percent / 100))
    new_rgb = [min(255, max(0, ch + amount)) for ch in rgb]
    return "#{:02x}{:02x}{:02x}".format(*new_rgb)




STYLE = {
    "global": {
        "hovered": 10,
        "pressed": 15,
        "checked": 15,


        "style_margin": "5px",
        "style_border_radius": "10px",
        "toolbar_icon_size_toolbar": 27,
        "button_icon_size_dock": "25px",
        "button_font_size_st1": "17px",
        "button_padding_x_st1": "5px",
        "button_padding_y_st1": "10px",
        "button_text_align_st1": "left",
        "button_layout_st1": "RightToLeft",
        "button_icon_size_st1": "25px",

        "accent_color": "red",
        "secondary_text_color": "#5a5a5a",

    },
    "dark": {
        "main_window_color": "#1e1e1e",
        "dock_color": "#2c2c2c",
        "text_color": "#d8d8d8",
        "button_background_color_st1": "#39393c",
    },
    "light": {
        "main_window_color": "#c2c2c2",
        "dock_color": "#d9d9d9",
        "text_color": "#353535",
        "button_background_color_st1": "#efefef",
    }
}


# Глобальная таблица стилей

def get_stylesheet():
    return f"""* 
{{
    font-family: "{FONT_FAMILY}";
    background-color: {STYLE[current_color]["main_window_color"]};
    color: {STYLE[current_color]["text_color"]};
}}

QLabel[window="main"] {{
    border: 6px double {STYLE["global"]["secondary_text_color"]};
    background-color: {STYLE[current_color]["dock_color"]};
}}


QPushButton[button="st1"] {{
    background-color: {STYLE[current_color]["button_background_color_st1"]};
    font-size: {STYLE["global"]["button_font_size_st1"]};
    border-radius: {STYLE["global"]["style_border_radius"]};
    padding: {STYLE["global"]["button_padding_x_st1"]} {STYLE["global"]["button_padding_y_st1"]};
    text-align: {STYLE["global"]["button_text_align_st1"]};
    qproperty-layoutDirection: {STYLE["global"]["button_layout_st1"]};
    qproperty-iconSize: {STYLE["global"]["button_icon_size_st1"]} {STYLE["global"]["button_icon_size_st1"]};
}}
QPushButton:hover[button="st1"] {{
    background-color: {calc_color(STYLE[current_color]["button_background_color_st1"], STYLE["global"]["hovered"])};
    border-bottom: 2px solid {STYLE["global"]["accent_color"]};
}}
QPushButton:pressed[button="st1"] {{
    background-color: {calc_color(STYLE[current_color]["button_background_color_st1"], STYLE["global"]["checked"])};
}}
QPushButton:checked[button="st1"] {{
    background-color: {calc_color(STYLE[current_color]["button_background_color_st1"], STYLE["global"]["checked"])};
}}

QPushButton[button="dock"] {{
    background-color: transparent;
    border: none;
    border-radius: {STYLE["global"]["style_border_radius"]};
    qproperty-iconSize: {STYLE["global"]["button_icon_size_dock"]} {STYLE["global"]["button_icon_size_dock"]};
}}
QPushButton:hover[button="dock"] {{
    background-color: {calc_color(STYLE[current_color]["dock_color"], STYLE["global"]["hovered"])};
}}
QPushButton:pressed[button="dock"] {{
    background-color: {calc_color(STYLE[current_color]["dock_color"], STYLE["global"]["pressed"])};
}}

/* === Стилизация Окна (QMainWindow) === */
QMainWindow {{
    background-color: {STYLE[current_color]["main_window_color"]};
    color: {STYLE[current_color]["text_color"]};
}}

/* === Стилизация док-окон (QDockWidget) === */
QDockWidget{{
    background-color: transparent;   /* убираем фон самого дока, чтобы margin работали */
    
}}

/* Заголовок дока (виджет со свойством dock="title") */
QWidget[dock="title"]{{
    border-top-left-radius: {STYLE["global"]["style_border_radius"]};
    border-top-right-radius: {STYLE["global"]["style_border_radius"]};
    background-color: {calc_color(STYLE[current_color]["dock_color"],3) };
    margin-right: {STYLE["global"]["style_margin"]};
    margin-left: {STYLE["global"]["style_margin"]};
}}

/* Содержимое дока (виджет со свойством dock="main") */
QWidget[dock="main"] {{
    background-color: {STYLE[current_color]["dock_color"]};
    border-bottom-left-radius: {STYLE["global"]["style_border_radius"]};
    border-bottom-right-radius: {STYLE["global"]["style_border_radius"]};
    margin-right: {STYLE["global"]["style_margin"]};
    margin-left: {STYLE["global"]["style_margin"]};
    margin-bottom: {STYLE["global"]["style_margin"]};
}}
QLabel[dock="title"] {{
    background-color: {calc_color(STYLE[current_color]["dock_color"],3) };
}}

QLabel[dock="main"] {{
    background-color: {STYLE[current_color]["dock_color"]};
}}

/*{calc_color(STYLE[current_color]["dock_color"],STYLE["global"]["hovered"]) };*/

/*====================== Настройка скрол бара ======================*/
QWidget[dock="scroll"] {{
    background-color: {STYLE[current_color]["dock_color"]};
    border: 2px solid {STYLE[current_color]["main_window_color"]}; ###################################################
}}

QScrollBar:vertical {{
    background-color: {STYLE[current_color]["dock_color"]};
    width: 20px;

}}
QScrollBar::handle:vertical {{
    background-color: {calc_color(STYLE[current_color]["dock_color"],STYLE["global"]["hovered"]) } ;
    min-height: 25px;
    border-radius: 3px;
    margin: 5px;
}}
QScrollBar::sub-line:vertical,
QScrollBar::add-line:vertical {{
    height: 0px;
    background: none;
}}
/*======================= Настройка мелких элементов ===================================*/
QCheckBox {{
    padding-left: 4px;
    border-radius: 9px;
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
}}



QTextEdit{{
background-color: {calc_color(STYLE[current_color]["dock_color"],STYLE["global"]["hovered"]) };
}}

QLineEdit {{
margin-left:10px;
padding-left: 10px;
margin-right: 20px;
border-radius: {STYLE["global"]["style_border_radius"]};
background-color: {calc_color(STYLE[current_color]["dock_color"],STYLE["global"]["hovered"]) };
}}


QGroupBox::title {{
    margin-top: 0;   
    subcontrol-position: top center;
    background-color: transparent;
    color: transparent;
    height: 0;
}}


/* Toolbar */
QToolBar[toolbar="toolbar"] {{
    background-color: {STYLE[current_color]["dock_color"]};
    border-radius: {STYLE["global"]["style_border_radius"]};
    margin: {STYLE["global"]["style_margin"]};
    min-height: 45px;

}}
QToolBar[toolbar="toolbar"] QToolButton {{
    min-height: 40px;
    min-width: 40px;
    background-color: transparent;
    border: none;
    border-radius: {STYLE["global"]["style_border_radius"]};
    
}}
QToolBar[toolbar="toolbar"] QToolButton:hover {{
    background-color: {calc_color(STYLE[current_color]["dock_color"], int(STYLE["global"]["hovered"]))};
}}
QToolBar[toolbar="toolbar"] QToolButton:pressed {{
    background-color: {calc_color(STYLE[current_color]["dock_color"], int(STYLE["global"]["pressed"]))};
}}

/* StatusBar */
QStatusBar[statusbar="statusbar"] {{
    background-color: {STYLE[current_color]["dock_color"]};
    border-radius: {STYLE["global"]["style_border_radius"]};
    margin: {STYLE["global"]["style_margin"]};
    min-height: 25px;
}}

QAction[button="st1"] {{
    color: {STYLE[current_color]["text_color"]};
}}

"""
