import os
import dearpygui.dearpygui as dpg
import cv2
import numpy as np
import Editor.core_backup.modules.constants as const
from pathlib import Path
import Editor.core_backup.modules.themes as themes
from Editor.core_backup.modules.themes import theme_editor

var: dict = {
    'project_root': str(Path(__file__).parent.parent.parent.parent.resolve()),
    'null_image':  str("../dev/nullimage4.png"),
}

def upload_image(image_path: str = None,
                 parent:str=None,
                 file_tag:str=None,
                 current_texture_tag:str=None):
    try:
        HOLST_NAME = "holst"
        # Загружаем из файла
        if file_tag == None or parent == None or current_texture_tag == None:
            print("не указан один из параметров")
            return 0
        if image_path is None or image_path == "null":
            image_path = var['null_image']
            null = True
        else:
            null = False
        if not os.path.exists(image_path):
            print(f"Изображение не найдено: '{image_path}'")
            return 0

        # Чтение изображения
        image_data = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if image_data is None:
            print(f"Не удалось загрузить изображение: '{image_path}'")
            return 0

        # --- 2. КОНВЕРТАЦИЯ В RGBA ---
        # Приведение к 4 каналам (RGBA)
        if len(image_data.shape) == 2:  # Grayscale
            image_data = cv2.cvtColor(image_data, cv2.COLOR_GRAY2RGBA)
        elif image_data.shape[2] == 3:  # RGB/BGR
            if image_data.dtype == np.uint8:
                # Конвертация BGR → RGBA
                image_rgba = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGBA)
            else:
                # Для float и других типов
                image_rgba = np.ones((*image_data.shape[:2], 4), dtype=image_data.dtype)
                image_rgba[:, :, :3] = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
                image_rgba[:, :, 3] = 255 if image_data.dtype == np.uint8 else 1.0
        elif image_data.shape[2] == 4:  # Уже RGBA/BGRA
            image_rgba = cv2.cvtColor(image_data, cv2.COLOR_BGRA2RGBA)
        else:
            print(f"Неподдерживаемый формат: {image_data.shape} каналов")
            return 0

        # --- 3. РАСЧЕТ МАСШТАБИРОВАНИЯ ---
        image_height, image_width = image_rgba.shape[:2]
        image_ratio = image_width / image_height

        # Константы (должны быть определены в модуле const)
        try:
            main_width = const.MAIN_WIDTH
            main_height = const.MAIN_HEIGHT
        except AttributeError:
            # Значения по умолчанию если константы не определены
            main_width, main_height = 800, 600

        available_ratio = main_width / main_height

        PADDING = 55  # или 50, или другое значение

        # Можно даже разделить на горизонтальные и вертикальные отступы
        HORIZONTAL_PADDING = 30
        VERTICAL_PADDING = 30

        if image_ratio > available_ratio:
            ratio_width = main_width - HORIZONTAL_PADDING * 2  # Отступы слева и справа
            ratio_height = int(ratio_width / image_ratio)
        else:
            ratio_height = main_height - VERTICAL_PADDING * 2  # Отступы сверху и снизу
            ratio_width = int(ratio_height * image_ratio)

        # --- 4. СОЗДАНИЕ ТЕКСТУРЫ И ОТОБРАЖЕНИЕ ---
        # Подготовка тега для drawlist
        holst_tag = f"{file_tag}{HOLST_NAME}"

        # Удаляем существующий drawlist если есть
        if dpg.does_item_exist(holst_tag):
            dpg.delete_item(holst_tag)

        # Создаем новый drawlist
        with dpg.drawlist(tag=holst_tag, parent=parent,
                          width=ratio_width, height=ratio_height):
            # Удаляем старую текстуру
            if dpg.does_item_exist(current_texture_tag):
                dpg.delete_item(current_texture_tag)

            # Создаем новую текстуру
            with dpg.texture_registry():
                # Нормализуем данные для DearPyGui
                if image_rgba.dtype == np.uint8:
                    texture_data = image_rgba.astype(np.float32) / 255.0
                else:
                    texture_data = image_rgba.astype(np.float32)

                texture_data_flat = texture_data.flatten()

                current_texture_tag = dpg.add_raw_texture(
                    width=image_width,
                    height=image_height,
                    default_value=texture_data_flat,
                    format=dpg.mvFormat_Float_rgba
                )

            # Рисуем изображение
            dpg.draw_image(
                texture_tag=current_texture_tag,
                pmin=(0, 0),
                pmax=(ratio_width, ratio_height),
                uv_min=(0, 0),
                uv_max=(1, 1),
                #rounding=20
            )

        # --- 5. СОХРАНЕНИЕ ДАННЫХ И ВОЗВРАТ ---

        print(f"✅ Изображение загружено: {image_width}x{image_height} -> {ratio_width}x{ratio_height}")

        return [
            image_path,# if image_path else "from_data",
            image_rgba,
            image_width,
            image_height,
            current_texture_tag,
            ratio_width,
            ratio_height,
            null
        ]

    except Exception as e:
        print(f"Ошибка в upload_image: {e}")
        return 0

    # функция для воспросизведения патча входной КОРОТКИЙ -> Длинный с рутом -> загрузка


def relative_path(input_filepath: str):
    result = os.path.relpath(input_filepath, var['project_root'])
    return result
    # функция для воспросизведения патча входной Длинный -> Короткий -> Сохранение


def absolute_path(input_filepath: str):
    result = os.path.join(var['project_root'], input_filepath)
    return result
    # функция для переназначения текущих данных


def add_alfa_button(icon_path: str, callback, tag, show):
    try:
        image = cv2.imread(icon_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            print(f"❌ Не удалось загрузить иконку: {icon_path}")
            return

        if image.shape[2] == 4:
            image_rgba = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
        else:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w = image_rgb.shape[:2]
            image_rgba = np.ones((h, w, 4), dtype=np.uint8) * 255
            image_rgba[:, :, :3] = image_rgb

        image_data = (image_rgba.astype(np.float32) / 255.0).flatten()

        with dpg.texture_registry():
            texture_id = dpg.add_raw_texture(
                image.shape[1],
                image.shape[0],
                image_data,
                format=dpg.mvFormat_Float_rgba,
            )

        dpg.add_image_button(texture_id, callback=callback, tag=tag, show=show)

    except Exception as e:
        print(f"❌ Ошибка создания кнопки: {e}")
