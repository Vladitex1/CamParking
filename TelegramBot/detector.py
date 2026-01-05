import json
import os
from TelegramBot import logic

# self.check_auto(save="Отладка1.mask", processed_image = "test3.jpg")

def check_auto(save: str, processed_image: str, config_name:str = "conf_1"):
    # ======= Функция, которая вытаскивает данные из сохранения. СЮДА ПИХАТЬ ГОТОВОЕ СОХРАНЕНИЕ ===============
    # [1] - данные, из сохранения, path - это файл, по которому делался сейв
    # [2] - данные для быстрого доступ - Это то, что должно с камеры приходить
    # [3] - сведение данных через алгоритм

    saved_data, path = read_data(save)  # [1]
    detected_car_data = logic.process_image(processed_image,True,config_name)  # [2]
    return logic.comparison(saved_data, detected_car_data)  # [3]


def read_data(filename="saved_data.txt"):
    SAVEDIR = "../saves/"
    try:
        with open(SAVEDIR + filename, 'r', encoding='utf-8') as file:
            content = file.read().strip()
        # Пробуем загрузить как JSON
        data = json.loads(content)
        polygons = data.get("polygons", {})
        parent_file = data.get("parent_file", "")
        return polygons, parent_file
    except Exception as e:
        print(e)
