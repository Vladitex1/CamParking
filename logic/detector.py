import json
from sys import exception

from . import  file
from . import logic

MASKPATH = "../save/"
MASK_ENDING = ".mask"



def check_auto(mask: str = None, image = None, config_name:str = "conf_1"):
    # ======= Функция, которая вытаскивает данные из сохранения. СЮДА ПИХАТЬ ГОТОВОЕ СОХРАНЕНИЕ ===============
    # [1] - данные, из сохранения, path - это файл, по которому делался сейв
    # [2] - обработка изображения
    # [3] - сведение данных через алгоритм
    try:
        if mask is None:
            print("Ошибка: не выбрана маска")
            return 1
        elif config_name is None:
            print("Ошибка: не выбран конфиг Yolo")
            return 2

        suspect,saved_data, path = file.load_data(f"{MASKPATH}{mask}")# [1]

        print(f"sd:{saved_data}")
        print(f"path:{path}")
        print(f"image:{image}")

        if image is not None:
            detected_car_data = logic.process_image(image=image,save_img=False, timestamp=True, config_name=config_name) #[2]
            if detected_car_data == 0:
                print("Ошибка в работе обработки изображения")
                return 3
        else:
            print("Ошибка: не передано ни изображение, ни имя файла")
            return 4

        return logic.comparison(saved_data, detected_car_data)
    except Exception:
        print("Ошибка: в работе функции распознавания")
        return 5
