from PySide6.QtGui import QFontDatabase, QFont

STYLESHEET_DARK2 = """
    /* === Базовые настройки для главного окна === */
    QMainWindow {
        background-color: #1e1e1e;   /* Цвет фона всего главного окна (тёмно-серый) */
    }

    /* === Статус-бар (полоса внизу окна) === */
    QStatusBar {
        font: 22px "Segoe UI", sans-serif;  /* Шрифт: размер 22px, семейство Segoe UI, запасной sans-serif */
        border: 1px solid white;           /* Рамка: толщина 1px, сплошная, цвет тёмно-сине-серый */
        border-radius: 3px;                  /* Скругление углов рамки */
        padding: 2px 5px;                    /* Внутренние отступы: 2px сверху/снизу, 5px слева/справа */
        max-height: 28px;                     /* Максимальная высота статус-бара — 28 пикселей */
    }
    /* Стиль для всех QLabel, которые находятся внутри QStatusBar (например, для постоянных сообщений) */
    QStatusBar QLabel {
        color: white;                         /* Цвет текста — белый */
        padding: 3px 10px;                    /* Отступы внутри метки: 3px сверху/снизу, 10px слева/справа */
        border-radius: 3px;                    /* Скругление углов фона метки */
        background-color: rgba(0,0,0,0.2);    /* Полупрозрачный чёрный фон (20% непрозрачности) */
        margin: 2px;                           /* Внешние отступы вокруг метки */
    }

    /* === Обычные кнопки (QPushButton) === */
    QPushButton {
        font-size: 17px;                       /* Размер шрифта 17px */
        border-radius: 10px;                    /* Сильное скругление углов (овальные кнопки) */
        background-color: #2d2d2d;              /* Тёмно-серый фон */
        color: white;                            /* Белый текст */
        padding: 5px 10px;                       /* Внутренние отступы: 5px сверху/снизу, 10px слева/справа */
        border: none;                             /* Убираем стандартную рамку */
    }
    /* Состояние при наведении курсора */
    QPushButton:hover {
        background-color: #3d3d3d;               /* Чуть более светлый серый при наведении */
    }
    /* Состояние, когда кнопка зажата (checked) — например, для toggle-кнопок */
    QPushButton:checked {
        background-color: #007acc;               /* Синий фон, когда кнопка активна/выбрана */
    }
    /* Состояние при нажатии (pressed) */
    QPushButton:pressed {
        background-color: #005a9e;               /* Ещё более тёмный синий при нажатии */
    }

    /* === Чекбоксы (используются как кнопки выбора полигона) === */
    QCheckBox {
        font-size: 23px;                          /* Крупный шрифт */
        border-radius: 10px;                       /* Сильное скругление */
        background-color: #2d2d2d;                 /* Тёмно-серый фон */
        color: white;                               /* Белый текст */
        spacing: 8px;                               /* Расстояние между индикатором и текстом/иконкой */
        padding: 5px;                               /* Внутренние отступы со всех сторон */
    }
    /* Псевдоэлемент indicator — квадратик-галочка, который мы скрываем */
    QCheckBox::indicator {
        left: -5px;          /* Сдвигаем индикатор влево за пределы видимой области */
        width: 0px;          /* Делаем ширину нулевой (скрываем) */
        height: 0px;         /* Делаем высоту нулевой (скрываем) */
    }
    /* Состояние индикатора, когда чекбокс отмечен */
    QCheckBox::indicator:checked {
        background-color: #007acc;   /* Задаём цвет фона для скрытого индикатора (не влияет на внешний вид, но можно оставить) */
    }
    /* Наведение на чекбокс */
    QCheckBox:hover {
        background-color: #3d3d3d;
    }
    /* Чекбокс в отмеченном состоянии (сам виджет) */
    QCheckBox:checked {
        background-color: #007acc;    /* Синий фон для всего чекбокса, когда он отмечен */
    }

    /* === Поля ввода (однострочные) === */
    QLineEdit {
        font-size: 17px;               /* Размер шрифта 17px */
        border-radius: 10px;            /* Скругление углов */
        background-color: #2d2d2d;      /* Тёмно-серый фон */
        color: white;                   /* Белый текст */
        padding-left: 5px;              /* Отступ текста от левого края */
        border: 1px solid #34495e;      /* Тонкая рамка такого же цвета, как у статус-бара */
        selection-background-color: #007acc;  /* Цвет фона выделенного текста (синий) */
    }

    /* === Обычные метки (QLabel) === */
    QLabel {
        font-size: 17px;               /* Размер шрифта 17px */
        border-radius: 10px;            /* Скругление углов фона */
        background-color: #2d2d2d;      /* Тёмно-серый фон */
        color: white;                   /* Белый текст */
        padding: 5px;                   /* Отступы со всех сторон */
    }

    /* === Группа с рамкой (QGroupBox), например, для области со списком полигонов === */
    QGroupBox {
        border: 1px solid #34495e;      /* Тонкая рамка вокруг группы */
        border-radius: 5px;              /* Небольшое скругление углов рамки */
        margin-top: 10px;                 /* Внешний отступ сверху, чтобы освободить место для заголовка */
        padding-top: 10px;                /* Внутренний отступ сверху, чтобы содержимое не прилипало к заголовку */
    }
    /* Псевдоэлемент title — заголовок группы */
    QGroupBox::title {
        subcontrol-origin: margin;        /* Заголовок позиционируется относительно внешнего отступа (margin) */
        left: 10px;                        /* Сдвигаем заголовок вправо на 10px от левого края */
        padding: 0 5px 0 5px;              /* Внутренние отступы заголовка: сверху/снизу 0, слева/справа 5px */
    }
"""
FONT_FAMILY=""
def load_font():
    global FONT_FAMILY
    # Загружаем шрифт (возвращает ID или -1 при ошибке)
    #font_id = QFontDatabase.addApplicationFont("../fonts/default_font.ttf")
    font_id = QFontDatabase.addApplicationFont("../fonts/Lorenzo Sans Medium.ttf")
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
        "clicked": 20,
        "pressed": 15,
        "style_margin": "5px",
        "style_border_radius": "10px",
        ## тулбары
        "toolbar_icon_size_toolbar": "32px",
        ## кнопка
        "button_font_size_st1": "17px",
        "button_padding_x_st1": "5px",
        "button_padding_y_st1": "10px",
        "button_text_align_st1": "left",
        "button_layout_st1": "RightToLeft",
        "button_icon_size_st1": "20px",
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

#current_color = "light"
current_color = "dark"
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
    background-color: {calc_color(STYLE[current_color]["button_background_color_st1"], 7)};
}}
QPushButton:pressed[button="st1"] {{
    background-color: {calc_color(STYLE[current_color]["button_background_color_st1"], 15)}; 
}}
QPushButton:checked[button="st1"] {{
    background-color: {calc_color(STYLE[current_color]["button_background_color_st1"], 5)}; 
}}


/* === Стилизация Окна (QMainWindow) === */

QMainWindow {{
    background-color: {STYLE[current_color]["main_window_color"]};
}}
/* === Стилизация док-окон (QDockWidget) === */

QDockWidget[dock="main"] {{
    background-color: {STYLE[current_color]["dock_color"]};
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
    color: {STYLE[current_color]["text_color"]};
    min-width: 230;
    max-width: 500;
}}

QDockWidget[dock="help"] {{
    background-color: {STYLE[current_color]["dock_color"]};
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
    color: {STYLE[current_color]["text_color"]};
    min-width: 300;
    max-width: 350;
}}

QDockWidget QWidget {{
    background-color: {calc_color(STYLE[current_color]["dock_color"], 1)};
    border-bottom-left-radius: {STYLE["global"]["style_border_radius"]};
    border-bottom-right-radius: {STYLE["global"]["style_border_radius"]};
    margin-right: 5px;
    margin-left: 5px;
    min-width: 10px;

}}

QDockWidget::title {{
    background-color: {STYLE[current_color]["dock_color"]};
    color: {STYLE[current_color]["text_color"]};
    padding-left: 5px;
    padding-top: 10px;   /* примерные значения для центрирования */
    padding-bottom: 10px;
    border-top-left-radius: {STYLE["global"]["style_border_radius"]};
    border-top-right-radius: {STYLE["global"]["style_border_radius"]};
    margin-left: 5px;
    margin-right: 5px;
}}

QDockWidget::float-button{{
    background-color: {STYLE[current_color]["dock_color"]};
    background-image: url("../icons/close_fullscreen.png");
    background-repeat: no-repeat;
    background-position: center;
    border-radius: {STYLE["global"]["style_border_radius"]};
    position: right;
    right: 45px;
    min-width: 20px;
    min-height: 20px;
    subcontrol-position: center right;
}}

QDockWidget::close-button {{
    background-color: {STYLE[current_color]["dock_color"]};
    background-image: url("../icons/remove.svg");

    background-repeat: no-repeat;
    background-position: center;
    border-radius: {STYLE["global"]["style_border_radius"]};
    position: right;
    right: 15px;
    min-width: 20px;
    min-height: 20px;
    subcontrol-position: center right;
}}

QDockWidget::close-button:hover, QDockWidget::float-button:hover {{
    background-color: {calc_color(STYLE[current_color]["dock_color"], STYLE["global"]["hover"])};
}}

QDockWidget::close-button:pressed, QDockWidget::float-button:pressed {{
    background-color: {calc_color(STYLE[current_color]["dock_color"], STYLE["global"]["pressed"])};
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
