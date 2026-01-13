import json
from . import  file
from . import logic

def check_auto(mask: str = None, processed_image = None,img = None, config_name:str = "conf_1"):
    # ======= Функция, которая вытаскивает данные из сохранения. СЮДА ПИХАТЬ ГОТОВОЕ СОХРАНЕНИЕ ===============
    # [1] - данные, из сохранения, path - это файл, по которому делался сейв
    # [2.1] - обработка изображения из path
    # [2.2] - обработка изображения напрямую переданного
    # [3] - сведение данных через алгоритм
    if mask is None:
        print("Ошибка: не выбрана маска")
        return [], []
    saved_data, path = file.read_data(mask)# [1]
    print(f"sd{saved_data}")
    print(f"path{path}")
    if img is not None: # Если передано изображение (img), используем его
        detected_car_data = logic.process_image(img=img, debug=True, config_name=config_name) #[2.1]
    elif processed_image is not None: # Иначе используем имя файла
        detected_car_data = logic.process_image(image=processed_image, debug=True, config_name=config_name) #[2.2]
    else:
        print("Ошибка: не передано ни изображение, ни имя файла")
        return [], []

    return logic.comparison(saved_data, detected_car_data)