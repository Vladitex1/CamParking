from Editor.prod.data.prefers_manager import save_config
NAMES = {
    "RU":{
        # =============== Program ====================

        "title": "CamParking",

        # =============== Menu ====================
        "menu.file": "Файл",
        "menu.file.new": "Новое",
        "menu.file.open": "Открыть",
        "menu.file.save": "Сохранить",
        "menu.file.exit": "Выход",

        "menu.navigate": "CamParking",
        "menu.navigate.start": "Начало",
        "menu.navigate.editor": "Редактор",

        "menu.parameters": "Параметры",
        "menu.parameters.settings": "Настройки",
        "menu.parameters.switch_theme": "Сменить тему",
        "menu.parameters.switch_language": "Switch to English",

        "menu.help": "Справка",
        "menu.help.about": "О программе",

        # =============== Menu.menu_switcher ====================

        "menu.menu_switcher.title": "Меню быстрой навигации",
        "menu.menu_switcher.start": "Начало",
        "menu.menu_switcher.editor": "Редактор",


        #================= Editor.toolbar =================

        "editor.toolbar.title":"Панель инструментов",

        "editor.toolbar.load.file":"Загрузить файл маски",
        "editor.toolbar.load.mask":"Загрузить только маску",
        "editor.toolbar.load.image":"Загрузить только изображение",
        "editor.toolbar.save.as":"Сохранить как",
        "editor.toolbar.save.fast":"Быстрое сохранение",
        "editor.toolbar.clear":"Очистить рабочую область",
        "editor.toolbar.test.image":"Загрузить тестовое изображение",

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
        "editor.editor.dock.button.select.all": "Выбрать всё",

        #================= Editor.help.dock =================

        "editor.help.dock.title": "Помощь",
        "editor.help.dock.name": """
            <h2>🤿 Редактор масок</h2>

            <h3>Управление:</h3>
            <ul>
                <li>ЛКМ - Создание новой точки</li>
                <li>СКМ - Добавление точки в маску</li>
                <li>ПКМ - Завершить полигон</li>
            </ul>
            <p><i>Создано с использованием PySide6</i></p>
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


    },
    "EN":{
        # =============== Program ====================

        "title": "CamParking",

        # =============== Menu ====================
        "menu.file": "File",
        "menu.file.new": "New",
        "menu.file.open": "Save",
        "menu.file.save": "Save",
        "menu.file.exit": "Exit",

        "menu.navigate": "CamParking",
        "menu.navigate.start": "Start page",
        "menu.navigate.editor": "Editor page",

        "menu.parameters": "Parameters",
        "menu.parameters.settings": "Settings",
        "menu.parameters.switch_theme": "Switch theme",
        "menu.parameters.switch_language": "Переключить на Русский",

        "menu.help": "Help",
        "menu.help.about": "About program",

        # =============== Menu.menu_switcher ====================

        "menu.menu_switcher.title": "Fast navigation menu",
        "menu.menu_switcher.start": "Start page",
        "menu.menu_switcher.editor": "Editor page",


        #================= Editor.toolbar =================
        "editor.toolbar.title": "Toolbar",

        "editor.toolbar.load.file": "Load save",
        "editor.toolbar.load.mask": "Load only mask",
        "editor.toolbar.load.image": "Load only image",
        "editor.toolbar.save.as": "Save as",
        "editor.toolbar.save.fast": "Fast save",
        "editor.toolbar.clear": "Clear workspace",
        "editor.toolbar.test.image": "Load test image",

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

        #================= Editor.help.dock =================

        "editor.help.dock.title": "Help",
        "editor.help.dock.name": """
            <h2>🤿 Mask Editor</h2>

            <h3>Controls:</h3>
            <ul>
                <li>LMB - Create new point</li>
                <li>MMB - Add new point in mask</li>
                <li>RMB - End polygon</li>
            </ul>
            <p><i>Create with PySide6 library</i></p>
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

    },

}

current_language: str = ""
def set_language(language: str):
    global current_language
    current_language = language

def get_language():
    global current_language
    return current_language

def change_language():
    global current_language
    if current_language == "RU":
        current_language = "EN"
    else:
        current_language = "RU"
    save_config(language = current_language)


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
    test(NAMES["ru"], NAMES["en"])