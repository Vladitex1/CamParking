import ast
import json
import os
pos = []
text_data = []
real_data = []
SAVEDIR = "../save/"

def save_data(data, filename="saved_data.txt", parentfile=None):
    # Создаем структуру данных
    save_structure = {
        "polygons": data,
        "parent_file": parentfile  # Добавляем путь к родительскому файлу
    }
    with open(filename, "w", encoding='utf-8') as file:
        # Используем json для более надежного сохранения
        json.dump(save_structure, file, ensure_ascii=False, indent=2)


# чтение файла файл
def read_data(file_path:str=None):
    try:
        if file_path != None:
            if not os.path.exists(file_path):
                print(f"ОШИБКА read_data: {file_path} - НЕ СУЩЕСТВУЕТ!")
                return None
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                #print(content)

            # Пробуем загрузить как JSON
            data = json.loads(content)
            polygons = data.get("polygons", {})
            parent_file = data.get("parent_file", "")
            print(data)

            return polygons, parent_file
    except Exception as e:
        print(f"ОШИБКА read_data: {e}")

