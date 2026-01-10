import json
import os
from TelegramBot import logic
import cv2
import time

# self.check_auto(save="Отладка1.mask", processed_image = "test3.jpg")

def check_auto(save: str, processed_image,img, config_name:str = "conf_1"):
    # ======= Функция, которая вытаскивает данные из сохранения. СЮДА ПИХАТЬ ГОТОВОЕ СОХРАНЕНИЕ ===============
    # [1] - данные, из сохранения, path - это файл, по которому делался сейв
    # [2] - данные для быстрого доступ - Это то, что должно с камеры приходить
    # [3] - сведение данных через алгоритм
    saved_data, path = read_data(save)
    # Если передано изображение (img), используем его
    if img is not None:
        detected_car_data = logic.process_image(img=img, debug=True, config_name=config_name)
    # Иначе используем имя файла
    elif processed_image is not None:
        detected_car_data = logic.process_image(image=processed_image, debug=True, config_name=config_name)
    else:
        print("Ошибка: не передано ни изображение, ни имя файла")
        return [], []

    return logic.comparison(saved_data, detected_car_data)

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

async def get_img_from_cam():
    print("⏳ Жду пробуждение камеры...")
    url = "rtsp://admin:@192.168.0.25:554/h264?tcp"

    # Медленный "прогрев" для ночного режима
    for attempt in range(3):  # 3 попытки
        print(f"  Попытка {attempt + 1}...")
        cap = cv2.VideoCapture(url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Минимальный буфер
        cap.set(cv2.CAP_PROP_FPS, 5)  # Низкий FPS
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Низкое разрешение
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        start_time = time.time()
        timeout = 10  # 10 секунд максимум

        while time.time() - start_time < timeout:
            ret, frame = cap.read()
            if ret and frame is not None:
                cap.release()
                print(f"✅ Изображение получено за {time.time() - start_time:.1f} сек")
                return frame

        cap.release()
        raise TimeoutError("Не удалось получить изображение с камеры")