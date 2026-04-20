from Editor.prod.data.prefers_manager import save_config
NAMES = {
    "RU":{

        # =============== Global ====================

        "language.emoji": "🇷🇺",
        "language.fullname": "Русский",

        # =============== Program ====================

        "title": "CamParking",
        "debug": "Дебаг",

        # =============== Menu ====================
        "menu.file": "Файл",
        "menu.file.new": "Новое",
        "menu.file.open": "Открыть",
        "menu.file.save": "Сохранить",
        "menu.file.exit": "Выход",

        "menu.navigate": "CamParking",
        "menu.navigate.start": "Начало",
        "menu.navigate.editor": "Редактор",
        "menu.navigate.connect": "Подключение",

        "menu.parameters": "Параметры",
        "menu.parameters.settings": "Настройки",
        "menu.parameters.switch_theme": "Сменить тему",
        "menu.parameters.switch_language": "Switch to English",

        "menu.help": "Справка",
        "menu.help.about": "О программе",

        # =============== Menu.menu_switcher ====================

        "menu.menu_switcher.title": "Меню быстрой навигации",

        #================= Start =================

        "start.title": "Добро пожаловать на начальную страницу!",
        "start.about": "Выберите действие, с которого хотите начать:",

        # =============== Dock ====================

        "dock.unpin": "Открепить/Закрепить окно",
        "dock.close": "Закрыть окно",

        #================= Editor.toolbar =================

        "editor.toolbar.title":"Панель инструментов",

        "editor.toolbar.load.file":"Загрузить файл маски",
        "editor.toolbar.load.mask":"Загрузить только маску",
        "editor.toolbar.load.image":"Загрузить только изображение",
        "editor.toolbar.save.as":"Сохранить как",
        "editor.toolbar.save.fast":"Быстрое сохранение",
        "editor.toolbar.clear":"Очистить рабочую область",
        "editor.toolbar.test.image":"Загрузить тестовое изображение",
        "editor.toolbar.capture.image":"Сделать скриншот с камеры",
        "editor.toolbar.back":"Вернуться в начало",

        #================= Editor.toolbar.dialog =================

        "editor.toolbar.load.file.title": "Загрузить маску",
        "editor.toolbar.load.mask.title": "Загрузить только маску",
        "editor.toolbar.load.image.title": "Загрузить только изображение",
        "editor.toolbar.save.as.title": "Сохранить как",


        #================= Editor.editor.dock =================
        #self.name["editor.help.dock.name"]
        "editor.editor.dock.title": "Редактор",
        "editor.editor.dock.name": "Полигоны",
        "editor.editor.dock.button.delete.all": "Удалить выбранные",
        "editor.editor.dock.button.select.all": "Выделить всё",
        "editor.editor.dock.button.unselect.all": "Снять выделение",

        #================= Editor.help.dock =================

        "editor.help.dock.title": "Помощь",
        "editor.help.dock.name": """
        <h2>🤿 Редактор масок</h2>
        <p>Создание полигональных масок для разметки изображений.</p>
        
        <h3>🖱️ Управление мышью</h3>
        <ul>
            <li><b>ЛКМ</b> — добавить точку/перетащить точку/перетащить полигон</li>
            <li><b>СКМ</b> — добавить точку на ребро полигона</li>
            <li><b>ПКМ</b> — удалить точку/завершить полигон (от 3 точек)</li>
        </ul>
        
        <h3>⌨️ Горячие клавиши</h3>
        <ul>
            <li><b>Alt+1</b> (⌥1) — загрузить проект (маска + изображение)</li>
            <li><b>Alt+2</b> (⌥2) — загрузить только полигоны</li>
            <li><b>Alt+3</b> (⌥3) — загрузить изображение</li>
            <li><b>Shift+Alt+3</b> (⇧⌥3) — захват с RTSP-камеры</li>
            <li><b>Alt+S</b> (⌥S) — сохранить как новый файл</li>
            <li><b>Shift+Alt+S</b> (⇧⌥S) — быстрое сохранение</li>
            <li><b>Alt+D</b> (⌥D) — очистить всё</li>
            <li><b>Alt+E</b> (⌥E) — вернуться в главное меню</li>
        </ul>
        <p><i>Макс. 9 точек на полигон</i></p>
        """,

        #================= Editor.statusbar =================
        "editor.statusbar.load.mask": f"Маска загружена: ",
        "editor.statusbar.load.image": f"Изображение создано успешно: ",
        "editor.statusbar.save.as": f"Новое сохранение создано успешно: ",
        "editor.statusbar.save.fast": f"Быстрое сохранение выполнено успешно: ",
        "editor.statusbar.test.image": f"Тестовое изображение загружено: ",
        "editor.statusbar.error": f"Ошибка: ",

        # ================= Editor.statusbar.dots =================

        "editor.statusbar.point.true": f"Точки: ",
        "editor.statusbar.point.false": f"Нет точек",

        # ================= Editor.statusbar.masks =================

        "editor.statusbar.mask.true": f"Текущая маска: ",
        "editor.statusbar.mask.false": f"Нет маски",


        # ================= Settings =================

        "settings.title": f"Настройки:",

        # ================= Settings.theme =================

        "settings.theme.title": f"Тема:",

        # ================= Settings.language =================

        "settings.language.title": f"Язык:",
        "settings.language.about": f"Необходим перезапуск",

        # ================= Settings.options =================

        "settings.options.title": f"Опции:",
        "settings.options.fast.nav.title": f"Панель быстрой навигации",
        "settings.options.fast.nav.about": f"Панель в верхней части экрана позволяющая быстро переключаться между страницами программы.",
        "settings.options.fast.nav.button": f"Панель быстрой навигации",

        "settings.options.debug.title": f"Дебаг функции:",
        "settings.options.debug.about": f"Необходим перезапуск",
        "settings.options.debug.button": f"Дебаг",



        # ================= Settings.save =================

        "settings.save.title": f"Сохранить",
        "settings.save.true": f"Сохранение успешно",
        "settings.save.false": f"Сохранение не выполнено.",

        # ================= Connect.toolbar =================
        "connect.toolbar.title": "Панель инструментов",

        # ================= Connect.dock =================
        "connect.dock.title": "Подключение",
        "connect.dock.name": "ЗАГОЛОВОК",
        "connect.dock.button.camera": "Камера",
        "connect.dock.button.connect.config": "Конфигурация камеры",
        "connect.dock.button.detection.toggle": "Распознавание Live",

        # ================= Connect.form =================

        "connect.form.window.name": "Окно генерации RTSP",
        "connect.form.title": "Форма для подключения",
        "connect.form.login": "Логин:",
        "connect.form.pass": "Пароль:",
        "connect.form.ip": "IP Адрес:",
        "connect.form.port": "Порт:",
        "connect.form.stream.path": "Путь к потоку:",


    },
    "EN":{

        # =============== Global ====================
        "language.emoji": "🇬🇧",
        "language.fullname": "English",

        # =============== Program ====================

        "title": "CamParking",
        "debug": "Debug",

        # =============== Menu ====================
        "menu.file": "File",
        "menu.file.new": "New",
        "menu.file.open": "Save",
        "menu.file.save": "Save",
        "menu.file.exit": "Exit",

        "menu.navigate": "CamParking",
        "menu.navigate.start": "Start page",
        "menu.navigate.editor": "Editor page",
        "menu.navigate.connect": "Connect page",

        "menu.parameters": "Parameters",
        "menu.parameters.settings": "Settings",
        "menu.parameters.switch_theme": "Switch theme",
        "menu.parameters.switch_language": "Переключить на Русский",

        "menu.help": "Help",
        "menu.help.about": "About program",

        # =============== Menu.menu_switcher ====================

        "menu.menu_switcher.title": "Fast navigation menu",

        # ================= Start =================

        "start.title": "Welcome to start page!",
        "start.about": "Select the action you want to start with:",

        # =============== Dock ====================

        "dock.unpin": "Pin/Unpin window",
        "dock.close": "Close window",

        #================= Editor.toolbar =================
        "editor.toolbar.title": "Editor toolbar",

        "editor.toolbar.load.file": "Load save",
        "editor.toolbar.load.mask": "Load only mask",
        "editor.toolbar.load.image": "Load only image",
        "editor.toolbar.save.as": "Save as",
        "editor.toolbar.save.fast": "Fast save",
        "editor.toolbar.clear": "Clear workspace",
        "editor.toolbar.test.image": "Load test image",
        "editor.toolbar.capture.image":"Take screenshot from camera",
        "editor.toolbar.back":"Back to start page",

        #================= Editor.toolbar.dialog =================

        "editor.toolbar.load.file.title": "Load mask",
        "editor.toolbar.load.mask.title": "Load only mask",
        "editor.toolbar.load.image.title": "Load only image",
        "editor.toolbar.save.as.title": "Save as",


        #================= Editor.editor.dock =================

        "editor.editor.dock.title": "Editor",
        "editor.editor.dock.name": "Parking slots:",
        "editor.editor.dock.button.delete.all": "Delete selected",
        "editor.editor.dock.button.select.all": "Select all",
        "editor.editor.dock.button.unselect.all": "Unselect all",

        #================= Editor.help.dock =================

        "editor.help.dock.title": "Help",
        "editor.help.dock.name": """
        <h2>🤿 Mask Editor</h2>
        <p>Create polygonal masks for image annotation.</p>

        <h3>🖱️ Mouse Controls</h3>
        <ul>
            <li><b>LMB</b> — add point / drag point / drag whole polygon</li>
            <li><b>MMB</b> — add point on polygon edge</li>
            <li><b>RMB</b> — delete point / finish polygon (min 3 points)</li>
        </ul>

        <h3>⌨️ Keyboard Shortcuts</h3>
        <ul>
            <li><b>Alt+1</b> (⌥1) — load project (mask + image)</li>
            <li><b>Alt+2</b> (⌥2) — load polygons only</li>
            <li><b>Alt+3</b> (⌥3) — load image</li>
            <li><b>Shift+Alt+3</b> (⇧⌥3) — capture from RTSP camera</li>
            <li><b>Alt+S</b> (⌥S) — save as new file</li>
            <li><b>Shift+Alt+S</b> (⇧⌥S) — quick save (overwrite)</li>
            <li><b>Alt+D</b> (⌥D) — clear all</li>
            <li><b>Alt+E</b> (⌥E) — back to main menu</li>
        </ul>

        <p><i>Max 9 points per polygon</i></p>
        """,

        #================= Editor.statusbar =================
        "editor.statusbar.load.mask": f"Mask loaded successful: ",
        "editor.statusbar.load.image": f"Image created successfully: ",
        "editor.statusbar.save.as": f"New save created successfully: ",
        "editor.statusbar.save.fast": f"Fast save successful: ",
        "editor.statusbar.test.image": f"Test image loaded successful: ",
        "editor.statusbar.error": f"Error: ",

        #================= Editor.statusbar.dots =================
        "editor.statusbar.point.true": f"Points: ",
        "editor.statusbar.point.false": f"No points",
        #================= Editor.statusbar.masks =================
        "editor.statusbar.mask.true": f"Current mask: ",
        "editor.statusbar.mask.false": f"No mask",

        # ================= Settings =================

        "settings.title": f"Settings:",

        # ================= Settings.theme =================

        "settings.theme.title": f"Theme:",

        # ================= Settings.language =================

        "settings.language.title": f"Language:",
        "settings.language.about": f"Restart required",

        # ================= Settings.options =================

        "settings.options.title": f"Options:",
        "settings.options.fast.nav.title": f"Fast navigation bar:",
        "settings.options.fast.nav.about": f"The bar at the top of the screen allows you to quickly switch program pages",
        "settings.options.fast.nav.button": f"Fast navigation bar:",

        "settings.options.debug.title": f"Enable debug functional:",
        "settings.options.debug.about": f"Restart required",
        "settings.options.debug.button": f"Debug",

        # ================= Settings.save =================

        "settings.save.title": f"Save",
        "settings.save.true": f"Saving complete",
        "settings.save.false": f"Save not done",


        # ================= Connect.toolbar =================
        "connect.toolbar.title": "Connect toolbar",


        # ================= Connect.dock =================

        "connect.dock.title": "Connect",
        "connect.dock.name": "ZAGOLOVOK",
        "connect.dock.button.camera": "Camera",
        "connect.dock.button.connect.config": "Connection config",
        "connect.dock.button.detection.toggle": "Toggle detection",

        # ================= Connect.form =================

        "connect.form.window.name": "Connection settings",
        "connect.form.title": "Connection form",
        "connect.form.login": "Login:",
        "connect.form.pass": "Password:",
        "connect.form.ip": "IP address:",
        "connect.form.port": "Port:",
        "connect.form.stream.path": "Stream path:"

    },

}

current_language: str = "RU"
def set_language(language: str):
    global current_language
    current_language = language

def get_language():
    global current_language
    return current_language

def change_language(lang_name:str=None):
    global current_language
    if lang_name != None:
        if lang_name in NAMES.keys():
            current_language = lang_name
    else:
        if current_language == "RU":
            current_language = "EN"
        else:
            current_language = "RU"


def test(dict1, dict2):
    """Простое сравнение двух словарей с переводами."""

    keys1 = set(dict1.keys())
    keys2 = set(dict2.keys())

    print("=== СРАВНЕНИЕ СЛОВАРЕЙ ===")
    print(f"Всего ключей в 1-м: {len(keys1)}")
    print(f"Всего ключей во 2-м: {len(keys2)}")

    # Ключи только в первом
    only_in_first = keys1 - keys2
    if only_in_first:
        print(f"\n❌ Только в первом словаре: {sorted(only_in_first)}")

    # Ключи только во втором
    only_in_second = keys2 - keys1
    if only_in_second:
        print(f"\n❌ Только во втором словаре: {sorted(only_in_second)}")

    # Общие ключи
    common = keys1 & keys2
    print(f"\n✅ Общие ключи: {len(common)}")

    # Проверка совпадения значений
    different = []
    for key in common:
        if dict1[key] != dict2[key]:
            different.append((key, dict1[key], dict2[key]))

# Пример использования:
if __name__ == "__main__":
    test(NAMES["RU"], NAMES["EN"])