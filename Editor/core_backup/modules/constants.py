from pathlib import Path

PROJECT_ROOT = str(Path(__file__).parent.parent.parent.parent)

MENU_BAR_HEIGHT = 24
STATUS_BAR_HEIGHT = 50
ASPECT_RATIO = 16 / 9

WINDOW_FULL_SIZE = [1800, 900]
WINDOW_WIDTH, WINDOW_HEIGHT = WINDOW_FULL_SIZE

# Меню бар (верхняя панель)
MENU_BAR_POS = (0, 0)
MENU_BAR_WIDTH = WINDOW_WIDTH

# Панель инструментов (слева)
TOOLS_WIDTH = int(WINDOW_WIDTH * 0.21)  # 21% от ширины = 378
TOOLS_HEIGHT = WINDOW_HEIGHT - MENU_BAR_HEIGHT  # 876 (не 900!)
TOOLS_POS_X = 0
TOOLS_POS_Y = MENU_BAR_HEIGHT  # 24

# Основное окно (справа)
MAIN_WIDTH = WINDOW_WIDTH - TOOLS_WIDTH  # 1800 - 378 = 1422
MAIN_HEIGHT = WINDOW_HEIGHT - MENU_BAR_HEIGHT - STATUS_BAR_HEIGHT   # 746
MAIN_POS_X = TOOLS_WIDTH  # 378
MAIN_POS_Y = MENU_BAR_HEIGHT  # 24

# Статус бар (внизу основного окна)
STATUS_BAR_WIDTH = MAIN_WIDTH  # 1422
# Позиция относительно ВСЕГО окна:
STATUS_BAR_POS_X = MAIN_POS_X  # 378
STATUS_BAR_POS_Y = MAIN_POS_Y + MAIN_HEIGHT-200  # 24 + 746 = 770


SETTINGS_WIDTH = 1000
SETTINGS_HEIGHT = 600
FONT_SIZE = 18

POLYGONS_COLORS = [(255, 0, 0, 100), (255, 140, 0, 100), (255, 255, 0, 100), (0, 255, 0, 100), (0, 255, 255, 100),
                   (0, 0, 255, 100), (255, 0, 255, 100)]



LANGUAGE: str = "ru"
# ======================= Paths ==========================
NULL_IMAGE = f"{PROJECT_ROOT}/Editor/dev/nullimage2.png"
CURRENT_FONT = "default_font.ttf"
FONT_PATH = f"{PROJECT_ROOT}/Editor/Fonts/{CURRENT_FONT}"

# ======================= Bar config ==========================





always_visible: dict = {
    "always_visible_navigation": {
        "label": {"ru": "Навигация", "en": "Navigation"},
        "items": [
            {
                "label": {"ru": "Начало", "en": "Start"},
                "func": "self.show_window",
                "name": "start"
            },
            {
                "label": {"ru": "Редактор", "en": "Editor"},
                "func": "self.show_window",
                "name": "editor"
            },
            {
                "label": {"ru": "Детекция", "en": "Detection"},
                "func": "self.show_window",
                "name": "detector"
            },
            {
                "label": {"ru": "Сохранить layout", "en": "deb"},
                "func": "self.save_layout",
            }
,
            {
                "label": {"ru":"Загрузить layout", "en": "deb"},
                "func": "self.load_layout",
            }
        ]
    }
}

start: dict = {
    "start_zaglushka": {
        "label": {"ru": "заглушка", "en": "zaglushka"},
        "items": [
            {
                "label": {"ru": "БУП!", "en": "BoooP!"},
                "func": "self.bup",
            },
        ]
    }
}

editor: dict = {
        "editor_file": {
        "label": {"ru": "Файл", "en": "File"},
        "items": [
            {
                "label": {"ru": "Открыть изображение", "en": "Open image"},
                "func": "dpg.show_item",
                "item": "editor_file_dialog"
            },
            {
                "label": {"ru": "Открыть маску", "en": "Open mask"},
                "func": "dpg.show_item",
                "item": "editor_mask_dialog"
            },
            {
                "label": {"ru": "Сохранить маску", "en": "Save mask"},
                "func": "dpg.show_item",
                "item": "editor_save_dialog"
            },
            {
                "label": {"ru": "Быстрое сохранение", "en": "Fast save"},
                "func": "self.file.bar_fast_save",
            },
            {
                "label": {"ru": "Очистить рабочую область", "en": "Clear workspace"},
                "func": "self.file.bar_clear_workspace"
                #"self": "None"
                # Нет аргументов - значит вызываем без них
            },


        ]}}

editor2: dict = {
    "editor_file": {
        "label": {"ru": "Файл2", "en": "File"},
        "items": [
            {
                "label": {"ru": "Сохранить", "en": "Save"},
                "action": {"type": "self", "method": "fast_save"}
            },
            {
                "label": {"ru": "Сохранить как...", "en": "Save as..."},
                "action": {"type": "dpg", "method": "show_item", "arg": "editor_save_dialog"}
            },

            {
                "label": {"ru": "Настройки", "en": "Settings"},
                "action": {"type": "self", "method": "settings"}
            }
        ]
    },
    "editor_connect": {
        "label": {"ru": "Подключение", "en": "Connection"},
        "items": [
            {
                "label": {"ru": "Сделать фото", "en": "Make Photo"},
                "action": {"type": "self",  "method": "get_screenshot_from_camera"}
            },
            {
                "label": {"ru": "Подключение", "en": "Connect"},
                "action": {"type": "self",  "method": "interface_main_window"}
            },
            {
                "label": {"ru": "Открыть результаты", "en": "Open results"},
                "action": {"type": "self",  "method": "interface_tool_window"}
            },
            {
                "label": {"ru": "Настройки соединения", "en": "Configure connect"},
                "action": {"type": "none","method":"none","arg":"none"}  # Пустое действие
            }
        ]
    },
    "editor_ai": {
        "label": {"ru": "ИИ", "en": "AI"},
        "items": [
            {
                "label": {"ru": "Обработка", "en": "Handler"},
                "action": {"type": "self", "method": "make_detection"}
            }
        ]
    },
    "editor_about": {
        "label": {"ru": "О программе", "en": "About"},
        "items": [
            {
                "label": {"ru": "Информация", "en": "Info"},
                "action": {"type": "none","method":"none","arg":"none"}
            }
        ]
    },
    "editor_debug": {
        "label": {"ru": "Дебаг", "en": "Debug"},
        "items": [
            {
                "label": {"ru": "Отобразить информацию", "en": "Take info"},
                "action": {"type": "none","method":"none","arg":"none"}
            }
        ]
    }
}

detector: dict = {
    "detection_file": {
        "label": {"ru": "Файл", "en": "File"},
        "items": [
            {
                "label": {"ru": "Открыть файл", "en": "Open file"},
                "action": {"type": "dpg", "method": "show_item", "arg": "detector_file_dialog"}
            }
        ]
    },
    "detection_connect": {
        "label": {"ru": "Подключение", "en": "Connection"},
        "items": [
            {
                "label": {"ru": "Сделать фото", "en": "Make Photo"},
                "action": {"type": "self",  "method": "get_screenshot_from_camera"}
            },
            {
                "label": {"ru": "Подключение", "en": "Connect"},
                "action": {"type": "self",  "method": "interface_main_window"}
            },
            {
                "label": {"ru": "Открыть результаты", "en": "Open results"},
                "action": {"type": "self",  "method": "interface_tool_window"}
            },
            {
                "label": {"ru": "Настройки соединения", "en": "Configure connect"},
                "action": {"type": "none","method":"none","arg":"none"}  # Пустое действие
            }
        ]
    }
}