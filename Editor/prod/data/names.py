
NAMES = {
    "ru":{
        "title": "CamParking",

        "menu.file": "Файл",
        "menu.file.new": "Новое",
        "menu.file.open": "📂 Открыть",
        "menu.file.save": "💾 Сохранить",
        "menu.file.exit": "Выход",

        "menu.navigate": "CamParking",
        "menu.navigate.start": "Начало",
        "menu.navigate.editor": "Редактор",

        "menu.help": "Справка",
        "menu.help.about": "О программе"
    },
    "en":{
        "title": "CamParking",

        "menu.file": "File",
        "menu.file.new": "New",
        "menu.file.open": "📂 Open",
        "menu.file.save": "💾 Save",
        "menu.file.exit": "Exit",

        "menu.navigate": "CamParking",
        "menu.navigate.start": "Start",
        "menu.navigate.editor": "Editor",

        "menu.help": "Info",
        "menu.help.about": "About"
    }
}


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
    test(NAMES["ru"], NAMES["eu"])