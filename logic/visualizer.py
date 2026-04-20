from logging import exception

import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import logic.file as file

font_path = "../Editor/fonts/default_font.ttf"
font_size = 50  # Увеличьте размер шрифта (5 слишком маленький!)
SAVES_PATH = "../save/"

colors_detect = [(0, 0, 255), (0, 255, 0), (100, 100, 100)]
colors_font = [(255,0, 0), (0, 255, 0), (100, 100, 100)]

def detect(image = None, occupied_data: list = None, mask: str = None,draw_name = False):
    """Простой и рабочий вариант через OpenCV"""
    # 1. Загрузи изображение
    try:
        if image is None:
            raise ValueError(f"Не удалось загрузить: {image}")

        if isinstance(image,str):
            image = cv2.imread(image)

        height, width = image.shape[:2]
        print(f"Размер: {width}x{height}")

        # 2. Загрузи маску
        MASKPATH = "../save/"
        MASK_ENDING = ".mask"

        success,saved_data, _ = file.load_data(f"{MASKPATH}{mask}")

        print(f"Occupied slots: {occupied_data[0]}")
        print(f"Free slots: {occupied_data[1]}")
        free = occupied_data[1]
        occupied = occupied_data[0]
        # 3. Рисуй полигоны
        print(saved_data[0]['name'])

        # Определяем цвет заливки
        occupied_names = {name for (num, name) in occupied}
        free_names = {name for (num, name) in free}

        for idx, place in enumerate(saved_data):
            name = place['name']
            points = place['points']
            pts = np.array(points, np.int32).reshape((-1, 1, 2))

            if name in occupied_names:
                color = colors_detect[0]  # красный
                status = "ЗАНЯТО"
            elif name in free_names:
                color = colors_detect[1]  # зелёный
                status = "СВОБОДНО"
            else:
                color = colors_detect[2]  # серый
                status = "НЕИЗВЕСТНО"

            print(f"[{idx}] {name} -> {status}")

            # Рисуем контур и заливку
            cv2.polylines(image, [pts], True, color, 2)
            overlay = image.copy()
            cv2.fillPoly(overlay, [pts], color)
            cv2.addWeighted(overlay, 0.3, image, 0.7, 0, image)

            # Вычисляем центр для текста
            center_x = int(np.mean([p[0] for p in points]))
            center_y = int(np.mean([p[1] for p in points]))

            # Цвет текста
            if name in occupied_names:
                text_color = colors_font[1]  # белый на красном
            elif name in free_names:
                text_color = colors_font[0]  # чёрный на зелёном
            else:
                text_color = colors_font[1]  # белый на сером

            # Рисуем текст через PIL (поддержка кириллицы)
            font = ImageFont.truetype(font_path, font_size)
            img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img_pil)

            if not draw_name:
                draw.text((center_x, center_y - 35), f"{idx + 1}", font=font, fill=text_color)
            else:
                draw.text((center_x, center_y), f"{idx + 1}", font=font, fill=text_color)
                draw.text((center_x - 120, center_y + 55), name, font=font, fill=text_color)

            image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

            # 4. Сохраняем результат
        saved_image_path = "../img/results/output_open.jpg"
        cv2.imwrite(saved_image_path, image)
        print(f"✅ Сохранено: {saved_image_path}")
        return [image, saved_image_path]
    except Exception as e:
        print(f"Ошибка: {e}")
        return 0

# Использование:
if __name__ == '__main__':
    occupied_data = [['У площадки (справа)', 'У площадки (слева)', 'Загон (слева)', 'Загон (справа)', 'Клумба (слева)', 'Клумба (справа)','Мусорка 1', 'Мусорка 2'],['Перед загоном']]
    detect(
        image_path="../img/input/camera_photo_2026-01-11_5.jpg",
        mask="../save/test4.mask",
        occupied_data=occupied_data,draw_name = False)