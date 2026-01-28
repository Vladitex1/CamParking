from logging import exception

import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import logic.file as file

font_path = "../Editor/Fonts/default_font.ttf"
font_size = 50  # Увеличьте размер шрифта (5 слишком маленький!)
SAVES_PATH = "../save/"

colors_detect = [(0, 0, 255), (0, 255, 0), (100, 100, 100)]
colors_font = [(255,0, 0), (0, 255, 0), (100, 100, 100)]

def detect(image_path: str = None, occupied_data: list = None, mask: str = None,draw_name = False):
    """Простой и рабочий вариант через OpenCV"""
    # 1. Загрузи изображение
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Не удалось загрузить: {image_path}")

        height, width = image.shape[:2]
        print(f"Размер: {width}x{height}")

        # 2. Загрузи маску
        MASKPATH = "../save/"
        MASK_ENDING = ".mask"
        saved_data, _ = file.read_data(MASKPATH + mask+MASK_ENDING)

        print(f"Окупид: {occupied_data[0]}")
        print(f"Фри: {occupied_data[1]}")


        # 3. Рисуй полигоны
        for num, (name, points) in enumerate(saved_data.items()):
            # Преобразуй точки в numpy
            pts = np.array(points, np.int32).reshape((-1, 1, 2))

            # Выбери цвет
            if name in occupied_data[0]:
                color = colors_detect[0]  # красный - занято
            elif name in occupied_data[1]:
                color = colors_detect[1]  # зеленый - свободно
            else:
                color = colors_detect[2]  # серый - неизвестно

            # Нарисуй контур
            cv2.polylines(image, [pts], True, color, 2)

            # Заливка с прозрачностью
            overlay = image.copy()
            cv2.fillPoly(overlay, [pts], color)
            cv2.addWeighted(overlay, 0.3, image, 0.7, 0, image)

            # Текст
            center_x = int(np.mean([p[0] for p in points]))
            center_y = int(np.mean([p[1] for p in points]))

            # Загружаем шрифт


            # Конвертируем BGR -> RGB


            # Цвет текста - противоположный цвету фона для контраста
            # Конвертируем цвет BGR в RGB для PIL
            if name in occupied_data[0]:  # Красный фон (занято)
                text_color = colors_font[1]  # Белый текст
            elif name in occupied_data[1]:  # Зеленый фон (свободно)
                text_color = colors_font[0]  # Черный текст
            else:  # Серый фон (неизвестно)
                text_color = colors_detect[2]  # Белый текст

            font = ImageFont.truetype(font_path, font_size)
            img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img_pil)
            # Рисуем текст
            if not draw_name:
                draw.text((center_x, center_y-35), f"{num + 1}", font=font, fill=text_color)
            else:
                draw.text((center_x, center_y), f"{num + 1}", font=font, fill=text_color)
                draw.text((center_x-120, center_y + 55), f"{name}", font=font, fill=text_color)
            # Конвертируем обратно в BGR
            image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

        # 4. Сохрани
        filename = "../img/results/output_open.jpg"
        cv2.imwrite(filename, image)
        print(f"✅ Сохранено: output_open.jpg")

        return image,filename
    except Exception as e:
        print(f"Ошибка: {e}")

# Использование:
if __name__ == '__main__':
    occupied_data = [['У площадки (справа)', 'У площадки (слева)', 'Загон (слева)', 'Загон (справа)', 'Клумба (слева)', 'Клумба (справа)','Мусорка 1', 'Мусорка 2'],['Перед загоном']]
    detect(
        image_path="../img/input/camera_photo_2026-01-11_5.jpg",
        mask="../save/test4.mask",
        occupied_data=occupied_data,draw_name = False)