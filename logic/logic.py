import os
from datetime import date
import cv2
import numpy as np
from ultralytics import YOLO
import tomli
import cv2
import time

_MODEL_CACHE = {}

def get_model(model_path: str):
    """Возвращает модель YOLO, загружая её один раз."""
    if model_path not in _MODEL_CACHE:
        _MODEL_CACHE[model_path] = YOLO(model_path)
    return _MODEL_CACHE[model_path]

def process_image(image = None,save_img:bool=False,timestamp:bool = False, config_name:str = None):
    # ================ Блок подготовки имени файла для результата ================
    if image is None:
        print("Нет изображения | process_image")
        return 0
    if config_name is None:
        print("Не выбрана конфигурация для модели | process_image")
        return 0

    try:
        # ================ Начало обработки фото ================
        #сюда передается название файла на ввод и название файла, которое будет при сохранении
        print("Запуск распознавания Yolo")
        CONFIG_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "model", "config",config_name))
        with open(CONFIG_DIR, 'rb') as f:
            config = tomli.load(f) #загрузка конфигурации Yolo
            cars_count, vehicles, detection_results = detect_on_raw_image(image, config)
            annotated_frame = detection_results[0].plot(# Отрисовка квадратов (результатов)
                line_width=config["line_width"],  # Толщина рамки
                font_size=config["font_size"],  # Размер текста
                conf=config["show_conf"],  # Показывать уверенность
                labels=config["labels"]  # Показывать названия классов

            )
        # ================ Сохранение результата ================
        if save_img:
            INPUT_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "img"))
            OUTPUT_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "img"))
            os.makedirs(INPUT_DIR, exist_ok=True)
            os.makedirs(OUTPUT_DIR, exist_ok=True)

            if timestamp == False:
                filecount = 0
                for file in os.listdir(OUTPUT_DIR):
                    if f"result_{date.today()}" in file:
                        filecount += 1
                if filecount == 0:
                    result_image_name = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "img",
                                                                     f"{OUTPUT_DIR}result_{date.today()}.jpg"))
                else:
                    result_image_name = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "img",
                                                                     f"result_{date.today()}_{filecount}.jpg"))
            else:
                result_image_name = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "..", "img", f"last_result.jpg"))


            print("✅ Обработка изображения успешна")
            if cars_count > 0:  # Если автомобилей не найдено, то сохранения не будет.
                try:
                    cv2.imwrite(result_image_name, annotated_frame)  # сохранение данных в картинку results
                    print(f"✅ Результат сохранен в: {result_image_name}")
                except Exception as e:
                    print("Ошибка детекции - ", str(e))

        # ================ Запись результатов детекции в нужном нам формате ================
        vehicles_data = []
        for vehicle in vehicles:
            x1, y1, x2, y2 = vehicle['position']
            vehicles_data.append([
                (x1, y1),  # левый верх
                (x2, y1),  # правый верх
                (x1, y2),  # левый низ
                (x2, y2)  # правый низ
            ])
        return vehicles_data
    except Exception as e:
        print("Ошибка работы функции - ",str(e))
        return 0  # вместо None

def detect_on_raw_image(input_image,config):
    """Детекция на одном изображении"""
    MODEL_PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "model", str(config["model_name"])))
    MODEL = get_model(MODEL_PATH)
    try:
        print("Запуск системы детекции...")
        # Детекция с настройками
        detection_results = MODEL.predict(
            source=input_image,  # Путь к изображению
            conf=config['conf'],  # Порог уверенности (0.3-0.7)
            iou=config['iou'],  # Порог для подавления дубликатов
            imgsz=config['imgsz'],  # Размер обработки (320, 640, 1280)
            classes=config['classes']  # Только машины, автобусы, грузовики (COCO IDs)
        )

        # Обработка детекций
        print("Старт обработки результатов сканирования")
        cars_found = 0
        vehicles_info = []
        all_objects = detection_results[0].boxes
        for obj in all_objects:
            # Получаем данные об объекте
            class_id = int(obj.cls[0])  # ID класса
            confidence = float(obj.conf[0])  # Уверенность
            class_name = detection_results[0].names[class_id]  # Название класса

            # Если это машина, грузовик или автобус
            if class_name in ["car", "truck", "bus"]:
                # Увеличиваем счетчик
                cars_found += 1

                # Получаем координаты рамки этого объекта
                # xyxy содержит [x1, y1, x2, y2]
                x1 = int(obj.xyxy[0][0])  # Левый край
                y1 = int(obj.xyxy[0][1])  # Верхний край
                x2 = int(obj.xyxy[0][2])  # Правый край
                y2 = int(obj.xyxy[0][3])  # Нижний край

                # Сохраняем координаты
                bbox_coords = [x1, y1, x2, y2]

                # Добавляем в список
                vehicles_info.append({
                    "type": class_name,
                    "confidence": confidence * 100,  # В процентах
                    "position": bbox_coords  # Координаты [x1, y1, x2, y2]
                })

        return cars_found, vehicles_info, detection_results

    #обработчик ошибок
    except Exception as e:
        print(f"❌ Ошибка детекции: {e}")
        return 0, [], []

def comparison(saved_data:list = None,detected_car_data:list = None, nums:bool=False):
    '''
    Поиск занятого места по точке из массива распознанных автомобилей
        saved_data - массив из файла сохранения (маски)
        detected_Car_data - массив из найденных автомобилей системой распознавания Yolo
        nums - переключатель нумерации в статистике
    Алгоритм:
    №1 - ищем центральную точку внутри позиции найденного авто
    №2 - проверяем есть ли точка найденного автомобиля в одном из полигонов заданных пользователем ищем точку внутри
    '''
    if not detected_car_data:
        return []
    detect_center_list = []
    # №1 ниже цикл по нахождению центральной точки
    for i in range(len(detected_car_data)):
        data = detected_car_data[i]
        tempdata_x1 = data[0][0]
        tempdata_x2 = data[1][0]
        center_x = ((tempdata_x2 - tempdata_x1) / 2) + tempdata_x1
        tempdata_y1 = data[0][1]
        tempdata_y2 = data[2][1]
        center_y = ((tempdata_y2 - tempdata_y1) / 2) + tempdata_y1
        detect_center_list.append((center_x,center_y))
    occupied = []
    free = []
    def is_inside_polygon(point, polygon): # Вложенная функция, чтобы избавиться от повторения
        polygon_np = np.array(polygon).astype(np.int32)
        result = cv2.pointPolygonTest(polygon_np, point, False)
        return result >= 0

    for num,i in enumerate(saved_data): # №2 Поиск найденных автомобилей в заданных парковочных местах
        found_car = False
        for current_center in range(len(detect_center_list)):
            if is_inside_polygon(detect_center_list[current_center],i["points"]):
                if nums == True:
                    occupied.append([num,i["name"]])
                else:
                    occupied.append(i["name"])
                found_car = True
                break
        if not found_car:
            if nums == True:
                free.append([num,i["name"]])
            else:
                free.append(i["name"])
    return [occupied, free]

def debug_print(occupied, free,saved_data):
    print("=" * 40)
    print("🏁 РЕЗУЛЬТАТЫ ПРОВЕРКИ ПАРКОВКИ")
    print("=" * 40)

    print("\n🚗 ЗАНЯТЫЕ МЕСТА:")
    for spot in occupied:
        print(f"   • {spot}")

    print("\n🟢 СВОБОДНЫЕ МЕСТА:")
    for spot in free:
        print(f"   • {spot}")
    print(f"\n📊 ИТОГО: {len(occupied)}/{len(saved_data)} мест занято")

