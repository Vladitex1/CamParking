from PySide6.QtGui import QFontDatabase
import os

#### иконки: qta-browser в shell

FONT_FAMILY = ""

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

HOVER = 10
PRESSED = 15
CHECKED = 15

STYLE = {
    "global": {
        "style_margin": "5px",
        "style_border_radius": "10px",
        "toolbar_icon_size_toolbar": "32px",
        "button_icon_size_dock": "25px",
        "button_font_size_st1": "17px",
        "button_padding_x_st1": "5px",
        "button_padding_y_st1": "10px",
        "button_text_align_st1": "left",
        "button_layout_st1": "RightToLeft",
        "button_icon_size_st1": "25px",
    },
    "dark": {
        "hover": HOVER,
        "pressed": PRESSED,
        "checked": CHECKED,
        "main_window_color": "#06141B",
        "dock_color": "#11212D",
        "text_color": "#CCD0CF",
        "button_background_color_st1": "#253745",
    },
    "light": {
        "hover": HOVER*-1,
        "pressed": PRESSED*-1,
        "checked": CHECKED*-1,
        "main_window_color": "#C9B59C",
        "dock_color": "#D9CFC7",
        "text_color": "#06141B",
        "button_background_color_st1": "#EFE9E3",
    }
}

#current_color = "light"  # или "dark"
current_color = "dark"  # или "dark"
# Глобальная таблица стилей
STYLESHEET = f"""
* {{
    font-family: "{FONT_FAMILY}";
    color: {STYLE[current_color]["text_color"]};
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
    background-color: {calc_color(STYLE[current_color]["button_background_color_st1"], STYLE[current_color]["hover"])};
}}
QPushButton:pressed[button="st1"] {{
    background-color: {calc_color(STYLE[current_color]["button_background_color_st1"], STYLE[current_color]["pressed"])};
}}
QPushButton:checked[button="st1"] {{
    background-color: {calc_color(STYLE[current_color]["button_background_color_st1"], STYLE[current_color]["checked"])};
}}

QPushButton[button="dock"] {{
    background-color: transparent;
    border: none;
    border-radius: {STYLE["global"]["style_border_radius"]};
    qproperty-iconSize: {STYLE["global"]["button_icon_size_dock"]} {STYLE["global"]["button_icon_size_dock"]};
}}
QPushButton:hover[button="dock"] {{
    background-color: {calc_color(STYLE[current_color]["dock_color"], STYLE[current_color]["hover"])};
}}
QPushButton:pressed[button="dock"] {{
    background-color: {calc_color(STYLE[current_color]["dock_color"], STYLE[current_color]["pressed"])};
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

QDockWidget[dock="help"]{{
    min-width: 300px;
    max-width: 350px;
}}

QDockWidget[dock="editor"]{{
    min-width: 270px;
}}

/* Заголовок дока (виджет со свойством dock="title") */
QWidget[dock="title"] {{
    border-top-left-radius: {STYLE["global"]["style_border_radius"]};
    border-top-right-radius: {STYLE["global"]["style_border_radius"]};
    background-color: {STYLE[current_color]["dock_color"]};
    margin-right: 5px;
    margin-left: 5px;
}}

/* Содержимое дока (виджет со свойством dock="main") */
QWidget[dock="main"] {{
    background-color: {STYLE[current_color]["dock_color"]};
    border-bottom-left-radius: {STYLE["global"]["style_border_radius"]};
    border-bottom-right-radius: {STYLE["global"]["style_border_radius"]};
    margin-right: 5px;
    margin-left: 5px;
}}
QWidget[dock="main"] QGroupBox QWidget {{
    border: none;
    background-color: {calc_color(STYLE[current_color]["dock_color"], STYLE[current_color]["hover"]) } ;
    border-radius: 2px;
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
    qproperty-iconSize: {STYLE["global"]["toolbar_icon_size_toolbar"]} {STYLE["global"]["toolbar_icon_size_toolbar"]};
    margin: {STYLE["global"]["style_margin"]};
    min-height: 50px;
}}
QToolBar[toolbar="toolbar"] QToolButton {{
    background-color: transparent;
    border: none;
    border-radius: 4px;
    padding: 4px;
}}
QToolBar[toolbar="toolbar"] QToolButton:hover {{
    background-color: {calc_color(STYLE[current_color]["dock_color"], int(STYLE[current_color]["hover"]))};
}}
QToolBar[toolbar="toolbar"] QToolButton:pressed {{
    background-color: {calc_color(STYLE[current_color]["dock_color"], int(STYLE[current_color]["pressed"]))};
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