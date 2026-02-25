from PySide6.QtGui import QFontDatabase, QFont
import os
import qtawesome as qta
import base64

####иконки: qta-browser в shell

FONT_FAMILY=""
def load_font():
    global FONT_FAMILY
    # Загружаем шрифт (возвращает ID или -1 при ошибке)
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "fonts", "Lorenzo Sans Medium.ttf"))
    #font_id = QFontDatabase.addApplicationFont("../fonts/default_font.ttf")
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id != -1:
        families = QFontDatabase.applicationFontFamilies(font_id) # Получаем список семейств, которые добавились (обычно одно)
        if families:
            FONT_FAMILY = families[0]
            print(f"Шрифт '{FONT_FAMILY}' успешно загружен")
    else:
        FONT_FAMILY = QFont("Arial", 14)
        print("Ошибка загрузки шрифта")
        print(f"Стандартный шрифт загружен")

def calc_color(color:str,percent:int):
    print(color)
    color = color.lstrip('#')
    rgb = [int(color[i:i + 2], 16) for i in (0, 2, 4)]

    # Рассчитываем шаг (10% от 255 — это примерно 25.5 единиц)
    amount = round(255 * (percent / 100))

    # Прибавляем и ограничиваем диапазон от 0 до 255
    new_rgb = []
    for channel in rgb:
        new_channel = min(255, max(0, channel + amount))
        new_rgb.append(new_channel)

    # Форматируем обратно в HEX
    return "#{:02x}{:02x}{:02x}".format(*new_rgb)

STYLE = {
    "global":{
        "hover": 10,
        "pressed": 15,
        "checked": 15,

        "style_margin": "5px",
        "style_border_radius": "10px",
        ## тулбары
        "toolbar_icon_size_toolbar": "32px",
        ## кнопка  верхнее меню дока
        "button_icon_size_dock": "25px",
        ## кнопка стиль 1
        "button_font_size_st1": "17px",
        "button_padding_x_st1": "5px",
        "button_padding_y_st1": "10px",
        "button_text_align_st1": "left",
        "button_layout_st1": "RightToLeft",
        "button_icon_size_st1": "25px",
    },
    "dark":{
        ## оформление окна
        "main_window_color": "#06141B",
        "dock_color": "#11212D",
        "text_color": "#CCD0CF",
        ##Кнопка темная
        "button_background_color_st1": "#253745",
    },
    "light": {

        ## оформление окна
        "main_window_color": "#C9B59C",
        "dock_color": "#D9CFC7",
        "text_color": "#06141B",

        ##Кнопка темная
        "button_background_color_st1": "#EFE9E3",

    }
    #Кнопка при наведении
}

current_color = "light"
#current_color = "dark"
# Глобальные параметры стиля
STYLESHEET = f"""
*{{
    font-family: "{FONT_FAMILY}";
}}


QPushButton[button="st1"] {{ /* Кнопки для редактора  */
    background-color: {STYLE[current_color]["button_background_color_st1"]};
    color: {STYLE[current_color]["text_color"]};
    
    font-size: {STYLE["global"]["button_font_size_st1"]};               
    border-radius: {STYLE["global"]["style_border_radius"]};  
    padding: {STYLE["global"]["button_padding_x_st1"]} {STYLE["global"]["button_padding_y_st1"]};  
    text-align: {STYLE["global"]["button_text_align_st1"]};
    qproperty-layoutDirection: {STYLE["global"]["button_layout_st1"]};
    qproperty-iconSize: {STYLE["global"]["button_icon_size_st1"]} {STYLE["global"]["button_icon_size_st1"]};

}}
QPushButton:hover[button="st1"] {{
    background-color: {calc_color(STYLE[current_color]["button_background_color_st1"], STYLE["global"]["hover"])};
}}
QPushButton:pressed[button="st1"] {{
    background-color: {calc_color(STYLE[current_color]["button_background_color_st1"], STYLE["global"]["pressed"])}; 
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
    background-color: {calc_color(STYLE[current_color]["dock_color"], STYLE["global"]["hover"])};
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
QDockWidget {{
    background-color: {STYLE[current_color]["dock_color"]};
}}

QDockWidget[dock="main"] {{
    min-width: 250;
    max-width: 500;
 
}}

QDockWidget[dock="help"] {{
    min-width: 300;
    max-width: 350;

}}


QLabel,QVBoxLayout ,QScrollArea, QGroupBox, QWidget#dockMainContent {{
    background-color: red;
}}



#dockTitleBar {{
    background-color: {STYLE[current_color]["dock_color"]};
    margin-right: 5px;
    margin-left: 5px;
    border-top-left-radius: {STYLE["global"]["style_border_radius"]};
    border-top-right-radius: {STYLE["global"]["style_border_radius"]};
    qproperty-iconSize: {STYLE["global"]["toolbar_icon_size_toolbar"]} {STYLE["global"]["toolbar_icon_size_toolbar"]};
}}

#dock_main_scroll_widget {{/*####################################################################*/
    background-color: {STYLE[current_color]["dock_color"]};

}}

/* Toolbar */

QToolBar[toolbar="toolbar"] {{
    background-color: {STYLE[current_color]["dock_color"]};
    border-radius: {STYLE["global"]["style_border_radius"]};
    qproperty-iconSize: {STYLE["global"]["toolbar_icon_size_toolbar"]} {STYLE["global"]["toolbar_icon_size_toolbar"]};
    margin: {STYLE["global"]["style_margin"]};
}}

QToolBar[toolbar="toolbar"] QToolButton {{
    background-color: transparent;
    color: {STYLE[current_color]["text_color"]};  /* для иконок с currentColor */
    border: none;
    border-radius: 4px;
    padding: 4px;
}}

QToolBar[toolbar="toolbar"] QToolButton:hover {{
    background-color: {calc_color(STYLE[current_color]["dock_color"], STYLE["global"]["hover"])};
}}

QToolBar[toolbar="toolbar"] QToolButton:pressed {{
    background-color: {calc_color(STYLE[current_color]["dock_color"], STYLE["global"]["pressed"])};
}}



QStatusBar[statusbar="statusbar"]{{
    background-color: {STYLE[current_color]["dock_color"]};
    border-radius: {STYLE["global"]["style_border_radius"]};
    margin: {STYLE["global"]["style_margin"]};
    min-height: 25px;
}}

QAction[button="st1"]{{
    color: {STYLE[current_color]["text_color"]};
}}

"""
