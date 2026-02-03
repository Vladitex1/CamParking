from pathlib import Path

PROJECT_ROOT = str(Path(__file__).parent.parent.parent.parent)

MENU_BAR_HEIGHT = 24
ASPECT_RATIO = 16 / 9
WINDOW_FULL_SIZE = [1800, 900]#[1200,900]#
WINDOW_HEIGHT = WINDOW_FULL_SIZE[1]
TOOLS_POS_X = 0
TOOLS_POS_Y = MENU_BAR_HEIGHT
TOOLS_WIDTH = int(WINDOW_FULL_SIZE[0] / 100 * 21)
TOOLS_HEIGHT = WINDOW_HEIGHT

MAIN_POS_X = TOOLS_WIDTH
MAIN_POS_Y = MENU_BAR_HEIGHT
MAIN_WIDTH = int(WINDOW_FULL_SIZE[0] - TOOLS_WIDTH)
MAIN_HEIGHT = WINDOW_HEIGHT
WINDOW_WIDTH = TOOLS_WIDTH + MAIN_WIDTH

SETTINGS_WIDTH = 1000
SETTINGS_HEIGHT = 600
FONT_SIZE = 18

POLYGONS_COLORS = [(255, 0, 0, 100), (255, 140, 0, 100), (255, 255, 0, 100), (0, 255, 0, 100), (0, 255, 255, 100),
                   (0, 0, 255, 100), (255, 0, 255, 100)]

GLOBAL_BAR_TAG: str = "global_bar"

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
                "id": 1
            },
            {
                "label": {"ru": "Редактор", "en": "Editor"},
                "func": "self.show_window",
                "id": 2
            },
            {
                "label": {"ru": "Детекция", "en": "Detection"},
                "func": "self.show_window",
                "id": 3
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
        "label": {"ru": "Файл", "en": "File"},
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