from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QFontDatabase
import os
from Editor.prod.data.prefers_manager import save_config
from Editor.prod.data.signal_bus import signal

#### иконки: qta-browser в shell
app = None
FONT_FAMILY = ""
current_color = "dark"
#======================= сигнал, который будет передавать новое имя темы ================================

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
    signal.changed.emit(current_color)   # <-- добавить

# ============================ Служебные функции" ====================
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

        "button_icon_size": "30px",
        "button_font_size_st1": "14px",
        "font_size_h1": "36px",
        "font_size_h2": "18px",
        "font_size_h3": "12px",

        
        "button_padding_x_st1": "5px",
        "button_padding_y_st1": "10px",
        "button_text_align_st1": "left",
        "button_layout_st1": "RightToLeft",
        "button_icon_size_st1": "25px",

        "accent_color": "#c3c3c3",
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
    font-size: {STYLE["global"]["font_size_h3"]};
    font-family: "{FONT_FAMILY}";
    background-color: {STYLE[current_color]["main_window_color"]};
    color: {STYLE[current_color]["text_color"]};
}}

QLabel[window="main"] {{
    border-radius: {STYLE["global"]["style_border_radius"]};
    background-color: {STYLE[current_color]["main_window_color"]};
    max-width: 1400px;
    min-width: 100px;
    min-height: 100px;
    
}}


QPushButton[button="st1"] {{
    background-color: {STYLE[current_color]["button_background_color_st1"]};
    font-size: {STYLE["global"]["font_size_h2"]};
    border-radius: {STYLE["global"]["style_border_radius"]};
    padding: {STYLE["global"]["button_padding_x_st1"]} {STYLE["global"]["button_padding_y_st1"]};
    text-align: {STYLE["global"]["button_text_align_st1"]};
    qproperty-layoutDirection: {STYLE["global"]["button_layout_st1"]};
    qproperty-iconSize: {STYLE["global"]["button_icon_size"]} {STYLE["global"]["button_icon_size"]};
    border: 2px solid {STYLE[current_color]["button_background_color_st1"]};
}}
QPushButton:hover[button="st1"] {{
    background-color: {calc_color(STYLE[current_color]["button_background_color_st1"], STYLE["global"]["hovered"])};
    border: 2px solid transparent;

}}
QPushButton:pressed[button="st1"] {{
    background-color: {calc_color(STYLE[current_color]["button_background_color_st1"], STYLE["global"]["checked"])};
}}
QPushButton:checked[button="st1"] {{
    background-color: {calc_color(STYLE[current_color]["button_background_color_st1"], STYLE["global"]["checked"])};
}}

QPushButton[button="dock"] {{
    max-width: {STYLE["global"]["button_icon_size"]};
    max-height: {STYLE["global"]["button_icon_size"]};
    background-color: transparent;
    border: none;
    border-radius: {STYLE["global"]["style_border_radius"]};
    qproperty-iconSize: {STYLE["global"]["button_icon_size"]} {STYLE["global"]["button_icon_size"]};
    
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
    background-color: {calc_color(STYLE[current_color]["dock_color"],0) };
    margin-right: {STYLE["global"]["style_margin"]};
    margin-left: {STYLE["global"]["style_margin"]};

}}

/* Содержимое дока (виджет со свойством dock="main") */
QWidget[dock="main"] {{
    background-color: {STYLE[current_color]["dock_color"]};
    margin-right: {STYLE["global"]["style_margin"]};
    margin-left: {STYLE["global"]["style_margin"]};
    margin-bottom: {STYLE["global"]["style_margin"]};
    border-bottom-left-radius: {STYLE["global"]["style_border_radius"]};
    border-bottom-right-radius: {STYLE["global"]["style_border_radius"]};
    
}}
QWidget[dock="title"] QLabel{{
    background-color: {calc_color(STYLE[current_color]["dock_color"],3) };
}}

QWidget[dock="main"] QLabel{{
    background-color: {STYLE[current_color]["dock_color"]};
}}

/*{calc_color(STYLE[current_color]["dock_color"],STYLE["global"]["hovered"]) };*/

/*====================== Настройка скрол бара ======================*/
QWidget[dock="scroll"] {{
    background-color: transparent;
    border: none;
}}

QScrollBar:vertical {{
    background-color: {STYLE[current_color]["dock_color"]};
    width: 8px;
}}
QScrollBar::handle:vertical {{
    background-color: transparent;
    min-height: 15px;
    width: 10px;
    border-radius: 4px;
    padding: 3px;
    margin-top: 5px; 
    margin-bottom: 5px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {STYLE[current_color]["button_background_color_st1"]};
}}







QScrollBar::sub-line:vertical,
QScrollBar::add-line:vertical {{
    height: 0px;
    background: none;
}}

/*======================= Настройка мелких элементов ===================================*/
QScrollArea {{
    background-color: {STYLE[current_color]["dock_color"]};
    /*border: 2px solid {STYLE["global"]["secondary_text_color"]};*/
    border-radius: {STYLE["global"]["style_border_radius"]};
}}

QCheckBox {{
    padding-left: 4px;
    border-radius: 9px;
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
}}

QTextEdit{{
background-color: {calc_color(STYLE[current_color]["dock_color"],STYLE["global"]["pressed"]) };
}}

QLineEdit {{
margin-right: 20px;
border-radius: {STYLE["global"]["style_border_radius"]};
background-color: {STYLE[current_color]["button_background_color_st1"]};
}}

QLabel[element="circle"]{{
    border-radius: 11px;
    border:2px solid  {STYLE[current_color]["button_background_color_st1"]};
}}




/* === Стили для полигонов === */
QWidget[dock="polygon_slot"] {{
    width: 20px;
    height: 20px;
    background-color: {STYLE[current_color]["button_background_color_st1"]};
    border-radius: 15px;
}}

QWidget[dock="polygon_slot"] QCheckBox {{
    background-color: {STYLE[current_color]["button_background_color_st1"]};
}}
QWidget[dock="polygon_slot"] QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 11px;
    border: 2px solid {calc_color(STYLE[current_color]["button_background_color_st1"],10)};
    background-color: transparent;
}}
QWidget[dock="polygon_slot"] QCheckBox::indicator:hover {{
    background-color: {calc_color(STYLE[current_color]["button_background_color_st1"],5)};
}}
QWidget[dock="polygon_slot"] QCheckBox::indicator:checked {{
    background-color: {calc_color(STYLE[current_color]["button_background_color_st1"],10)};
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
    qproperty-iconSize: {STYLE["global"]["button_icon_size"]} {STYLE["global"]["button_icon_size"]};

}}


/*    min-height: 25px;
    min-width: 25px;*/
QToolBar[toolbar="toolbar"] QToolButton {{
    
    margin:5px;
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
    min-height: 35px;
    padding-left: 5px;
}}

/* Контейнер внутри статусбара - прозрачный, без фона */
QWidget[statusbar="container"] {{
    background-color: transparent;
}}

/* QLabel внутри статусбара - прозрачные, без фона */
QLabel[statusbar="label"] {{
    background-color: transparent;
    color: {STYLE[current_color]["text_color"]};
    font-size: {STYLE["global"]["font_size_h3"]};
}}

/* Разделитель */
QLabel[statusbar="separator"] {{
    background-color: transparent;
    color: {STYLE["global"]["secondary_text_color"]};
}}

/* Сообщение от showMessage() */
QStatusBar::item {{
    color: {STYLE[current_color]["text_color"]};
    background-color: transparent;
    font-size: {STYLE["global"]["font_size_h3"]};
}}

QAction[button="st1"] {{
    color: {STYLE[current_color]["text_color"]};
}}

"""
