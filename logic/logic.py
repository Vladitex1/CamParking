import os
from datetime import date
import cv2
import numpy as np
from ultralytics import YOLO
import tomli
import cv2
import time


#MODELPATH = "../../backup/yolov8x.pt"
#MODELPATH = "models/yolo11m.pt"
MODELPATH = "../models/"
CONFIG_DIR = "../models/config/"
# ============ ДОБАВЬ ЭТО ============
# Глобальная переменная для кэширования модели


def process_image(image= None,img=None,debug:bool = False,config_name:str = "conf_1"):
    # ================ Блок подготовки имени файла для результата ================
    try:
        INPUT_DIR = "../img/results/"
        OUTPUT_DIR = "../img/results/"
        os.makedirs(INPUT_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        if debug == False:
            filecount = 0
            for file in os.listdir(OUTPUT_DIR):
                if f"result_{date.today()}" in file:
                    filecount += 1
            if filecount == 0:
                result_image_name = f"{OUTPUT_DIR}result_{date.today()}.jpg"
            else:
                result_image_name = f"{OUTPUT_DIR}result_{date.today()}_{filecount}.jpg"
        else:
            result_image_name = f"{OUTPUT_DIR}last_result.jpg"


        # ================ Начало обработки фото ================
        #сюда передается название файла на ввод и название файла, которое будет при сохранении

        with open(CONFIG_DIR+config_name+".toml", 'rb') as f:
            config = tomli.load(f)
            print(f"залупа{config}")
            if img is None:
                cars_count, vehicles, detection_results = detect_on_raw_image(image, config)
            else:
                cars_count, vehicles, detection_results = detect_on_raw_image(img, config)
            print(f"вехиклес1231231231231{vehicles}{cars_count}{detection_results}")
            annotated_frame = detection_results[0].plot(    # Отрисовка квадратов (результатов)
                line_width=config["line_width"],  # Толщина рамки
                font_size=config["font_size"],  # Размер текста
                conf=config["show_conf"],  # Показывать уверенность
                labels=config["labels"]  # Показывать названия классов

            )
        # ================ Сохранение результата ================
        print("✅ Обработка изображения успешна")
        if cars_count > 0:  # Если автомобилей не найдено, то сохранения не будет.
            try:
                cv2.imwrite(result_image_name, annotated_frame)  # сохранение данных в картинку results
                print(f"✅ Результат сохранен в: {result_image_name}")
            except Exception as e:
                print("Ошибка детекции - ", str(e))

        # ================ Запись результатов детекции в нужном нам формате ================
        vehicles_data = []
        print(f"вехиклес{vehicles}")
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

def detect_on_raw_image(input_image,config):
    """Детекция на одном изображении"""
    print(os.listdir(MODELPATH))
    MODEL = YOLO(MODELPATH+config["model_name"])
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

        #print(f"📊 Найдено транспортных средств: {cars_found}")
        return cars_found, vehicles_info,detection_results

    #обработчик ошибок
    except Exception as e:
        print(f"❌ Ошибка детекции: {e}")
        return 0, [], []

def comparison(saved_data = None,detected_car_data = None):
    ###поиск позиции по точке внутри полигона из приложения
    ###1 - делаем центральную точку внутри позиции найденного авто
    ###2 - ищем точку внутри

    detect_center_list = []
    ### нахождение центральной точки в найденных машинах
    #print(len(detected_car_data))
    for i in range(len(detected_car_data)):
        tempdata_x1 = detected_car_data[i][0][0]
        tempdata_x2 = detected_car_data[i][1][0]
        center_x = ((tempdata_x2 - tempdata_x1) / 2) + tempdata_x1
        tempdata_y1 = detected_car_data[i][0][1]
        tempdata_y2 = detected_car_data[i][2][1]
        center_y = ((tempdata_y2 - tempdata_y1) / 2) + tempdata_y1
        detect_center_list.append((center_x,center_y))  #### ====== 1 ======

    occupied = []
    free = []
    print(f"хуисосработайблять{detect_center_list}")

    ###фильтр данных, сопоставление
    for name, position in saved_data.items():
        found_car = False
        for current_center in range(len(detect_center_list)):
            if is_inside_polygon(detect_center_list[current_center],position):
                occupied.append(name)
                found_car = True
                break
        if not found_car:
            free.append(name)

    #debug_print(occupied, free,saved_data) ##вывод информации в консоль
    return occupied, free

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

def is_inside_polygon(point, polygon):
    polygon_np = np.array(polygon).astype(np.int32)
    result = cv2.pointPolygonTest(polygon_np,point,False)
    return result >= 0