from ultralytics import YOLO
import os
import cv2

model_path = "../backup/yolov8x.pt"
image = "img/input/test4.jpg"


def setup():
    """Инициализация детектора YOLOv8"""

    #проверка на наличие дирикторий в корне программы
    os.makedirs("models", exist_ok=True)
    os.makedirs("img/result", exist_ok=True)

    #проверка на наличие модели
    if not os.path.exists(model_path):
        print("❌ Модель не найдена")
        return None
    model = YOLO(model_path)
    return model


def detect_on_image(input_image, output_image="output.jpg"):
    """Детекция на одном изображении"""
    model = setup()
    if model is None:
        return 0, [], []

    try:
        # ДОБАВЬТЕ ЭТО НЕПОСРЕДСТВЕННО ПЕРЕД cvtColor:


        print("✅ Обработка изображения успешна")

        #ret, threshold_image = cv2.threshold(input_image, 127, 255, 0)
        #gray_image#, "Пёсик в градациях серого")
        #threshold_image#, "Чёрно-белый пёсик")

        # Детекция с настройками
        results = model.predict(
            source=input_image,  # Путь к изображению
            conf=0.1,  # Порог уверенности (0.3-0.7)
            iou=0.4,  # Порог для подавления дубликатов
            imgsz=2560,  # Размер обработки (320, 640, 1280)
            classes=[2, 5, 7]  # Только машины, автобусы, грузовики (COCO IDs)
        )

        # Отрисовка результатов
        annotated_frame = results[0].plot(
            line_width=2,  # Толщина рамки
            font_size=1.0,  # Размер текста
            conf=True,  # Показывать уверенность
            labels=True  # Показывать названия классов
        )

        # Сохраняем результат

        cv2.imwrite(output_image, annotated_frame)

        # Обработка детекций
        cars_found = 0
        vehicles_info = []

        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = result.names[cls]

                if class_name in ["car", "truck", "bus"]:
                    cars_found += 1
                    bbox = [int(coord) for coord in box.xyxy[0].tolist()]


                    vehicles_info.append({
                        "type": class_name,
                        "confidence": conf * 100,
                        "position": bbox
                    })

                    print(vehicles_info)
                    #print(bbox)
                    #print(f"🚗 {class_name}{cars_found}: {conf * 100:.1f}%")


        print(f"📊 Найдено транспортных средств: {cars_found}")
        return cars_found, vehicles_info, []

    #обработчик ошибок
    except Exception as e:
        print(f"❌ Ошибка детекции: {e}")
        return 0, [], []

#def create_parking_boxes(input_image):
    #input_image

def handler():
    print("🔄 Запуск системы детекции...")

    result_image = "img/result/result.jpg"
    cars_count, vehicles, _ = detect_on_image(image, result_image)

    if cars_count > 0:

        image_display = cv2.imread(result_image)
        #cv2.imshow("result", image_display)
        print(f"✅ Результат сохранен в: {result_image}")
        #cv2.waitKey(0)  # 3 секунд
       # cv2.destroyAllWindows()

    vehicles_data = []
    #print(vehicles)
    for i in range(len(vehicles)):
        newpos = []
        pos = vehicles[i]['position']
        newpos.append((pos[0], pos[1]))
        newpos.append((pos[2], pos[1]))
        newpos.append((pos[0], pos[3]))
        newpos.append((pos[2], pos[3]))
        vehicles_data.append(newpos)

    return vehicles_data


def comparison(saved_data = None,detected_car_data = None):
    #print(saved_data)
    ###  поиск позиции по точке внутри полигона из приложения
    ###  1 - делаем центральную точку внутри позиции найденного авто
    ###  2 - ищем точку внутри

    temp = []

    ### нахождение центральной точки в найденных машинах
    for i in range(len(detected_car_data)):
        tempdata_x1 = detected_car_data[i][0][0]
        tempdata_x2 = detected_car_data[i][1][0]
        center_x = ((tempdata_x2 - tempdata_x1) / 2) + tempdata_x1
        tempdata_y1 = detected_car_data[i][0][1]
        tempdata_y2 = detected_car_data[i][2][1]
        center_y = ((tempdata_y2 - tempdata_y1) / 2) + tempdata_y1
        temp.append((center_x,center_y))
    print(temp)
    print(saved_data)
    for k, sd_value in saved_data.items():
        for j in range(len(temp)):
            if is_inside_polygon(temp[j],sd_value):
                print("обнаружен автомобиль на позиции: ", k)



def is_inside_polygon(point, polygon):
    # Функция для проверки нахождения точки внутри полигона
    x, y = point
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside
