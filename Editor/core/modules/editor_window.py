import cv2
import dearpygui.dearpygui as dpg
import numpy as np
import os
import logic.file as file
import logic.camera_control as camera
import logic.visualizer as visualizer
import logic.detector as detector
import Editor.core.modules.constants as const
import Editor.core.modules.themes as themes

from pathlib import Path

FILE_TAG:str = "editor"
FILE_TAG=FILE_TAG+"_"

WINDOW_TAG = f"{FILE_TAG}main_window"
TOOLS_TAG = f"{FILE_TAG}tools_window"
## Название тега для поля где располагается картинка (Холст) !!! НЕ САМА КАРТИНКА !!!!
HOLST_NAME = "holst"


class program:
    def __init__(self):
        global FILE_TAG
        if not dpg.does_item_exist(WINDOW_TAG):
            self.var:dict = {
                'project_root' : str(Path(__file__).parent.parent.parent.parent.resolve()),
                'null_image'   : "../dev/nullimage2.png",
                'texture_id':None,
                'editor_online':False,
                'display_w':100,
                'display_h':100,
                'current_tool':1,
                'current_polygon':[],
                'save_data':{},
                'polygons': [],
                'parent_file_pathv':"",
                'current_file_path': None,
                'image_width':0,
                'image_height':0,
                'file_tag':FILE_TAG,
                'current_texture_tag':"",
                'image_data':[],
            }

            self.func = self.functional(self)
            self.polygons = self.polygons(self)
            self.file = self.file(self)
            self.front = self.front(self)

            self.setup_input_handlers()
            self.program_presets()

    def get_tags(self=None):
        data: list = []
        data.append(WINDOW_TAG)
        data.append(TOOLS_TAG)
        return data

    def setup_input_handlers(self):
        with dpg.handler_registry():
            dpg.add_mouse_click_handler(callback=self.polygons.simple_click)

    def tool_changed(self, sender, app_data):
        print(f"Selected: {app_data}")
        tool_mapping = {
            "Полигон": ["polygon", 1],
            "Кисть": ["brush", 2],
            "Ластик": ["", 0],
        }
        selected_tool = tool_mapping.get(app_data, "polygon")
        #dpg.set_value("current_tool", f"Выбранный инструмент: {app_data}")
        self.var['current_tool'] = selected_tool[1]
        print(f"Selected tool: {selected_tool[1]}")

    def program_presets(self):

        with dpg.file_dialog(
                directory_selector=False,
                show=False,
                callback=self.file.bar_open_img,
                default_path=f"{const.PROJECT_ROOT}/img",
                id=f"{self.var['file_tag']}file_dialog",
                width=700,
                height=400
        ):
            dpg.add_file_extension("Images{.jpg,.jpeg,.png,.bmp,.gif}")

        with dpg.file_dialog(
                directory_selector=False,
                default_filename="",
                default_path=f"{const.PROJECT_ROOT}/save",
                show=False,
                callback=self.file.bar_open_mask,
                id=f"{self.var['file_tag']}mask_dialog",
                width=700,
                height=400,
                modal=True,
        ):
            dpg.add_file_extension(".mask", color=(0, 255, 0, 255))
            dpg.add_checkbox(
                label="Загрузить только маску",
                default_value=False,
                tag=f"{self.var['file_tag']}onlymask"
            )

        with dpg.file_dialog(
                directory_selector=False,
                default_filename="newmask.mask",
                default_path=f"{const.PROJECT_ROOT}/save",
                show=False,
                callback=self.file.bar_save_mask,
                id=f"{self.var['file_tag']}save_dialog",
                width=700,
                height=400,
                modal=True
        ):
            dpg.add_file_extension(".mask", color=(0, 255, 0, 255))

    ##Все, что пользователь видит
    class front:
        def __init__(self,parent):
            self.parent = parent
            self.func = parent.func  # ЭКЗЕМПЛЯР!
            self.var = parent.var
            self.interface_main_window()
            self.interface_tool_window()

        def get_menu_config(self):
            """Возвращает конфигурацию меню редактора"""
            return const.editor

        def interface_main_window(self):
            with dpg.window(label=WINDOW_TAG, tag=WINDOW_TAG,
                            no_title_bar=True, no_move=True, no_resize=True,
                            no_collapse=True, no_close=True,
                            width=const.MAIN_WIDTH, height=const.MAIN_HEIGHT,
                            pos=(const.MAIN_POS_X, const.MAIN_POS_Y)):

                self.func.upload_image()

        def interface_tool_window(self):
            with dpg.window(label=TOOLS_TAG, tag=TOOLS_TAG,
                            no_title_bar=True, no_move=True, no_resize=True, no_collapse=True, no_close=True,
                            width=const.TOOLS_WIDTH, height=const.TOOLS_HEIGHT,
                            pos=(const.TOOLS_POS_X, const.TOOLS_POS_Y), no_scrollbar=True):
                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=int(const.TOOLS_WIDTH / 2 - 50))
                    dpg.add_text("Полигоны")

                with dpg.child_window(
                        tag=f"{self.var['file_tag']}polygons_list",
                        height=400,
                        width=const.TOOLS_WIDTH - 15,
                        horizontal_scrollbar=False,
                        autosize_y=False
                ):
                    dpg.bind_item_theme(f"{self.var['file_tag']}polygons_list", themes.theme_editor())
                dpg.add_separator()

                dpg.add_text("ЗАЛАУПА")
                dpg.add_text("", wrap=0)

        def settings(self):
            if dpg.does_item_exist(f"{self.parent.file_tag}modal_window"):
                dpg.delete_item(f"{self.parent.file_tag}modal_window")
            x = const.TOOLS_POS_X + (const.WINDOW_WIDTH - const.SETTINGS_WIDTH) // 2
            y = const.TOOLS_POS_Y + (const.WINDOW_HEIGHT - const.SETTINGS_HEIGHT) // 2

            with dpg.window(
                    label="Настройки",
                    modal=True,
                    show=True,
                    id=f"{self.parent.file_tag}modal_window",
                    no_title_bar=False,
                    no_move=True,
                    width=const.SETTINGS_WIDTH,
                    height=const.SETTINGS_HEIGHT,
                    pos=(x, y - 20),
            ):
                with dpg.group(horizontal=True):
                    dpg.add_text("Размер шрифта:")
                    dpg.add_spacer(width=70)
                    dpg.add_button(label="+", callback=lambda: print("клик"), width=25, height=25)
                    dpg.add_text(str(const.FONT_SIZE))
                    dpg.add_button(label="-", callback=lambda: print("клик"), width=25, height=25)

                dpg.add_separator()
                dpg.add_text("Введите текст:")
                dpg.add_input_text(tag=f"{self.parent.file_tag}dialog_input", width=300)


    #работа с данными из bar
    class file:
        def __init__(self,parent):
            self.parent = parent
            self.var = parent.var
            self.func = parent.func
            self.poly = parent.polygons# ЭКЗЕМПЛЯР!

        def bar_open_img(self, sender, app_data):
            if app_data["file_path_name"]:
                #filepath = self.repath_file(app_data["file_path_name"])
                data = self.func.upload_image(app_data["file_path_name"])
                self.var['image_data'] = data
                self.var['editor_online'] = True

        def bar_open_mask(self,sender,app_data):
            self.savedata = {}
            file_path = app_data["file_path_name"]
            #self.relative_path = os.path.relpath(self.selected_filepath, self.project_root)
            #print(f"1: {self.selected_filepath}")
            #print(f"2: {self.project_root}")
            #print(f"3: {self.relative_path}")

            print(f"{file_path}")
            saved_data, parent_file = file.read_data(file_path)#self.selected_filepath)
            self.var['image_data'] = [parent_file,None,None,None]
            self.var['current_file_path'] = file_path
            #print(f"INFO:bar_open_mask:Parent file: {parent_file}")
            if not dpg.get_value("onlymask"):
                self.func.upload_image(self.func.absolute_path(parent_file))
            else:
                pass
                #dpg.set_value(f"{self.parent.file_tag}current_file", f"Загружена маска от файла:{os.path.basename(self.relative_path)}")

            self.var['current_polygon'].clear()
            self.var['polygons'].clear()
            for sd_value in saved_data:
                self.var['current_polygon'] = saved_data[sd_value]
                if len(self.var['current_polygon']) > 0 and self.var['current_polygon'][0] != self.var['current_polygon'][-1]:
                    self.var['current_polygon'].append(self.var['current_polygon'][0])
                self.poly.complete_polygon(sd_value)
            self.poly.update_polygons_list()

            self.func.update_display()
            self.var['editor_online'] = True


        def bar_save_mask(self, sender, app_data):
            print(f"current_filepath: {self.var['image_data']}")

            if len(self.var['polygons']) != 0:
                self.var['savedata'] = {}
                filepath = app_data["file_path_name"]
                print("Сохраняемый файл:", filepath)
                for i, poly in enumerate(self.var['polygons']):
                    if len(poly['points']) > 0 and poly['points'][0] == poly['points'][-1]:
                        del poly['points'][-1]
                    self.var['savedata'].setdefault(poly['name'], poly['points'])
                print(self.var['image_data'][0])
                file.save_data(self.var['savedata'], filepath, self.var['image_data'][0])
                self.var['editor_online'] = True
            else:
                print("Сохранение не удалось.")

        def bar_fast_save(self):
            if not self.var['editor_online']:
                return
            if self.var['current_file_path'] != None:
                self.var['savedata'] = {}
                print("быстрое сохранение")
                for i, poly in enumerate(self.var['polygons']):
                    if len(poly['points']) > 0 and poly['points'][0] == poly['points'][-1]:
                        del poly['points'][-1]
                    self.var['savedata'].setdefault(poly['name'], poly['points'])
                    file.save_data(self.var['savedata'], self.var['current_file_path'], self.var['image_data'][0])
            else:
                print("быстрое сохранение не удалось")


        def bar_clear_workspace(self):
            print("область очищена")
            self.var['image_data'] = [] #Очищение текущих метаданных
            self.func.upload_image()
            self.func.delete_active_tags()
            self.poly.clear_polygon_list()
            self.var['current_file_path'] = None
            self.var['editor_online'] = False #Блокировка области рисования
            #self.polygons.clear()
            #self.update_polygons_list()


    class functional:
        def __init__(self,parent):
            self.parent = parent
            self.var = parent.var
            self.poly = parent.polygons  # ЭКЗЕМПЛЯР!

        def upload_image(self,
                         image_path: str = None):
            """
            Загружает и отображает изображение.

            Args:
                image_path: Путь к файлу изображения
                upload_with_data: Массив numpy с данными изображения

            Returns:
                List: [путь, данные, ширина, высота] при успехе
                int: 0 при ошибке
            """
            try:

                # Загружаем из файла
                if image_path is None or image_path == "null":
                    image_path = self.var['null_image']

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

                if image_ratio > available_ratio:
                    ratio_width = main_width - 50
                    ratio_height = int(ratio_width / image_ratio)
                else:
                    ratio_height = main_height - 20
                    ratio_width = int(ratio_height * image_ratio)

                # --- 4. СОЗДАНИЕ ТЕКСТУРЫ И ОТОБРАЖЕНИЕ ---
                # Подготовка тега для drawlist
                holst_tag = f"{self.var['file_tag']}{HOLST_NAME}"

                # Удаляем существующий drawlist если есть
                if dpg.does_item_exist(holst_tag):
                    dpg.delete_item(holst_tag)

                # Создаем новый drawlist
                with dpg.drawlist(tag=holst_tag, parent=WINDOW_TAG,
                                  width=ratio_width, height=ratio_height):

                    # Удаляем старую текстуру
                    texture_tag = self.var['current_texture_tag']
                    if dpg.does_item_exist(texture_tag):
                        dpg.delete_item(texture_tag)

                    # Создаем новую текстуру
                    with dpg.texture_registry():
                        # Нормализуем данные для DearPyGui
                        if image_rgba.dtype == np.uint8:
                            texture_data = image_rgba.astype(np.float32) / 255.0
                        else:
                            texture_data = image_rgba.astype(np.float32)

                        texture_data_flat = texture_data.flatten()

                        self.var['current_texture_tag'] = dpg.add_raw_texture(
                            width=image_width,
                            height=image_height,
                            default_value=texture_data_flat,
                            format=dpg.mvFormat_Float_rgba
                        )

                    # Рисуем изображение
                    dpg.draw_image(
                        texture_tag=self.var['current_texture_tag'],
                        pmin=(0, 0),
                        pmax=(ratio_width, ratio_height),
                        uv_min=(0, 0),
                        uv_max=(1, 1)
                    )

                # --- 5. СОХРАНЕНИЕ ДАННЫХ И ВОЗВРАТ ---
                # Обновляем данные в родительском объекте
                self.var['image_width'] = image_width
                self.var['image_height'] = image_height
                self.var['display_w'] = ratio_width
                self.var['display_h'] = ratio_height

                print(f"✅ Изображение загружено: {image_width}x{image_height} -> {ratio_width}x{ratio_height}")

                return [
                    image_path if image_path else "from_data",
                    image_rgba,  # Возвращаем RGBA массив
                    image_width,
                    image_height
                ]

            except Exception as e:
                print(f"Ошибка в upload_image: {e}")
                return 0

            # функция для воспросизведения патча входной КОРОТКИЙ -> Длинный с рутом -> загрузка

        def relative_path(self, input_filepath: str):
            result = os.path.relpath(input_filepath, self.var['project_root'])
            return result
            # функция для воспросизведения патча входной Длинный -> Короткий -> Сохранение

        def absolute_path(self, input_filepath: str):
            result = os.path.join(self.var['project_root'], input_filepath)
            return result
            # функция для переназначения текущих данных

        def scale_points_for_display(self, points):
            scale_x = self.var['display_w'] / self.var['image_width']
            scale_y = self.var['display_h'] / self.var['image_height']
            return [(int(x * scale_x), int(y * scale_y)) for x, y in points]

        def delete_active_tags(self):
            # УДАЛЯЕМ ВСЕ СУЩЕСТВУЮЩИЕ ПОЛИГОНЫ
            for i in range(len(self.var['polygons']) + 10):  # +10 для запаса
                tags_to_delete = [
                    f"{self.var['file_tag']}polygon_{i}",
                    f"{self.var['file_tag']}polypoint_{i}",
                    f"{self.var['file_tag']}polytext_{i}"
                ]
                for tag in tags_to_delete:
                    if dpg.does_item_exist(tag):
                        dpg.delete_item(tag)

            # УДАЛЯЕМ ВСЕ ТОЧКИ текущего полигона
            for i in range(len(self.var['current_polygon']) + 10):
                point_tag = f"{self.var['file_tag']}point_{i}"
                if dpg.does_item_exist(point_tag):
                    dpg.delete_item(point_tag)

            # Удаляем текущий полигон
            if dpg.does_item_exist(f"{self.var['file_tag']}current_polyline"):
                dpg.delete_item(f"{self.var['file_tag']}current_polyline")

            if dpg.does_item_exist(f"{self.var['file_tag']}current_polygon"):
                dpg.delete_item(f"{self.var['file_tag']}current_polygon")

        def update_display(self):
            holst_tag = f"{self.var['file_tag']}{HOLST_NAME}"

            self.delete_active_tags()
            # Рисуем существующие полигоны
            if len(self.var['polygons']) > 0:
                for i in range(len(self.var['polygons'])):
                    tag = f"{self.var['file_tag']}polygon_{i}"
                    scaled_points = self.scale_points_for_display(self.var['polygons'][i]['points'])

                    dpg.draw_polyline(scaled_points, color=(255, 0, 255, 255),
                                      thickness=2, tag=tag, parent=holst_tag)

                for i in range(len(self.var['polygons'])):
                    tag = f"{self.var['file_tag']}polypoint_{i}"
                    j = i % len(const.POLYGONS_COLORS)

                    scaled_fill_points = self.scale_points_for_display(self.var['polygons'][i]['points'])
                    dpg.draw_polygon(scaled_fill_points, color=(255, 0, 0, 100), fill=const.POLYGONS_COLORS[j],
                                     tag=tag, parent=holst_tag)

                    points = self.var['polygons'][i]['points']
                    center_x = sum(p[0] for p in points) / len(points)
                    center_y = sum(p[1] for p in points) / len(points)

                    scaled_center = self.scale_points_for_display([(center_x - 30, center_y)])[0]
                    self.var['polygons'][i]['text_pos'] = scaled_center

                    dpg.draw_text(
                        pos=scaled_center,
                        text=self.var['polygons'][i]['name'],
                        color=(255, 255, 0, 255),
                        size=18,
                        tag=f"{self.var['file_tag']}polytext_{i}",
                        parent=holst_tag
                    )

            # Рисуем текущий полигон
            if self.var['current_polygon']:
                if len(self.var['current_polygon']) > 1:
                    tag = f"{self.var['file_tag']}current_polyline"
                    scaled_current = self.scale_points_for_display(self.var['current_polygon'])
                    dpg.draw_polyline(scaled_current, color=(0, 255, 255, 255),
                                      thickness=2, tag=tag,
                                      parent=holst_tag)

                for i, point in enumerate(self.var['current_polygon']):
                    tag = f"{self.var['file_tag']}point_{i}"
                    scaled_point = self.scale_points_for_display([point])[0]
                    dpg.draw_circle(center=scaled_point, radius=3, color=(255, 0, 255, 255),
                                    fill=(255, 0, 0, 255), tag=tag,
                                    parent=holst_tag)

                if len(self.var['current_polygon']) > 2:
                    tag = f"{self.var['file_tag']}current_polygon"
                    scaled_current_fill = self.scale_points_for_display(self.var['current_polygon'])
                    dpg.draw_polygon(scaled_current_fill, color=(0, 255, 0, 100),
                                     fill=(255, 255, 0, 100), tag=tag,
                                     parent=holst_tag)




        #####  НЕ РАБОТАЕТ (покачто)

        def get_screenshot_from_camera(self):
            try:
                INPUT_DIR = "../img/results/"
                another_img = "output_open.jpg"
                mask = "../saves/test4.mask"
                image = camera.get_img_sync()
                print(f"фото получено")

                # Получаем данные о парковке ============== Обработка фото

                occupied, free = detector.check_auto(mask=mask, processed_image=image, config_name="confwn")
                print(f"фото обработано ИИ")

                image, filename = visualizer.detect(image_path=image, mask=mask, occupied_data=[occupied, free],
                                                    draw_name=False)
                print(f"фото обработано для вывода")

                self.dir, self.img_info, self.width, self.height = self.prepare_image(filename)
                self.image_path = image
                self.load_image(self.width, self.height, self.img_info,self.dir)
                self.editor_online = True
                self.polygons.clear()
                self.update_polygons_list()

            except Exception as e:
                print(e)

        def make_detection(self):

            data1, data2 = detector.check_auto(mask=f"{const.PROJECT_ROOT}/saves/test4.mask",processed_image=self.get_current_image_info()[0],config_name="confwn")
            data = [data1,data2]
            image, filename = visualizer.detect(image_path=self.get_current_image_info()[0], mask=f"{const.PROJECT_ROOT}/saves/test4.mask", occupied_data=data,
                                                draw_name=False)
            filepath, image_data, image_width, image_height = self.prepare_image(filename)
            self.load_image(width=image_width, height=image_height, image_data=image_data,image_dir = filepath)
            self.editor_online = False
            print(f"{self.parent_file_path}{self.img_info, self.width, self.height}")


    class polygons:
        def __init__(self, parent):
            self.parent = parent
            self.var = parent.var
            self.func = parent.func  # ЭКЗЕМПЛЯР!

        def simple_click(self, sender, app_data):
            mouse_button = app_data
            mouse_pos = dpg.get_mouse_pos(local=False)
            x, y = mouse_pos

            if self.var['editor_online'] == False:
                return
            #
            draw_x = x - 8 - const.TOOLS_WIDTH
            draw_y = y - const.MENU_BAR_HEIGHT - 5
            print("клик")
            if draw_x > 0 and draw_y > 0:
                if draw_x < self.var['display_w'] and draw_y < self.var['display_h']:
                    print(f"🖱️ КЛИК: кнопка={mouse_button}, x={draw_x}, y={draw_y}")

                    if self.var['current_tool'] == 1:
                        original_x = int(draw_x / (self.var['display_w'] / self.var['image_width']))
                        original_y = int(draw_y / (self.var['display_h'] / self.var['image_height']))

                        self.var['current_polygon'].append((original_x, original_y))
                        print(f"Polygon point added: оригинал({original_x}, {original_y})")

                        if len(self.var['current_polygon']) > 3:
                            self.var['current_polygon'].append(self.var['current_polygon'][0])
                            self.complete_polygon(new=True)

                    self.func.update_display()

        def complete_polygon(self, name='noname', new=False):
            if name == 'noname':
                name = 'noname' + " " + str(len(self.var['polygons']))

            self.var['polygons'].append({
                'num': len(self.var['polygons']),
                'points': self.var['current_polygon'].copy(),
                'type': 'polygon',
                'name': name,
                'text_pos': None
            })

            if new:
                self.update_polygons_list()

            self.var['current_polygon'].clear()

        def update_polygons_list(self):
            dpg.delete_item(f"{self.var['file_tag']}polygons_list", children_only=True)
            for i, poly in enumerate(self.var['polygons']):
                with dpg.group(horizontal=True, parent=f"{self.var['file_tag']}polygons_list"):
                    with dpg.group(horizontal=True, tag=f"{self.var['file_tag']}const_visible_{i}"):
                        self.add_alfa_button(icon_path = os.path.join(self.var['project_root'], "Editor/icons/visabilityon.png"),
                                             callback = (lambda fixed: lambda s, a: self.hide_polygon(fixed))(poly['points']),
                                             tag = f"{self.var['file_tag']}hide_button_{i}",show =  True)


                        self.add_alfa_button(icon_path = os.path.join(self.var['project_root'], "Editor/icons/visabilityoff.png"),
                                             callback = (lambda fixed: lambda s, a: self.show_polygon(fixed))(poly['points']),
                                             tag = f"{self.var['file_tag']}show_button_{i}", show =False)

                        dpg.add_input_text(
                            tag=f"{self.var['file_tag']}poly_namespace_{i}",
                            default_value=poly['name'],
                            width=195,
                            enabled=False,
                            show=True
                        )
                        dpg.bind_item_theme(f"{self.var['file_tag']}poly_namespace_{i}", themes.theme2())

                    with dpg.group(horizontal=True, tag=f"{self.var['file_tag']}non_const_visible_{i}", show=True):
                        self.add_alfa_button(icon_path = os.path.join(self.var['project_root'], "Editor/icons/edit.png"),
                                             callback = (lambda fixed: lambda s, a: self.rename_activate(fixed))(i),
                                             tag = f"{self.var['file_tag']}edit_button_{i}", show = True)
                        self.add_alfa_button(icon_path = os.path.join(self.var['project_root'], "Editor/icons/editoff.png"),
                                             callback = (lambda fixed: lambda s, a: self.rename_polygon(fixed))(i),
                                             tag = f"{self.var['file_tag']}edit_off_button_{i}", show = False)
                        self.add_alfa_button(icon_path = os.path.join(self.var['project_root'], "Editor/icons/delete.png"),
                                             callback = (lambda fixed: lambda s, a: self.delete_polygon(fixed))(poly['points']),
                                             tag = f"{self.var['file_tag']}delete_button_{i}", show = True)

        def rename_activate(self, i):
            dpg.configure_item(f"{self.var['file_tag']}poly_namespace_{i}", enabled=True)
            dpg.focus_item(f"{self.var['file_tag']}poly_namespace_{i}")
            dpg.hide_item(f"{self.var['file_tag']}edit_button_{i}")
            dpg.show_item(f"{self.var['file_tag']}edit_off_button_{i}")

        def rename_polygon(self, i):
            newname = dpg.get_value(f"{self.var['file_tag']}poly_namespace_{i}")
            self.var['polygons'][i]['name'] = newname
            dpg.configure_item(f"{self.var['file_tag']}poly_namespace_{i}", enabled=False)
            dpg.hide_item(f"{self.var['file_tag']}edit_off_button_{i}")
            dpg.show_item(f"{self.var['file_tag']}edit_button_{i}")
            self.func.update_display()

        def delete_polygon(self, points):
            for i, poly in enumerate(self.var['polygons']):
                if self.var['polygons'][i]['points'] == points:
                    del self.var['polygons'][i]
                    break
            self.update_polygons_list()
            self.func.update_display()

        def hide_polygon(self, points):
            for i, poly in enumerate(self.var['polygons']):
                if self.var['polygons'][i]['points'] == points:
                    dpg.hide_item(f"{self.var['file_tag']}polygon_{i}")
                    dpg.hide_item(f"{self.var['file_tag']}polytext_{i}")
                    dpg.hide_item(f"{self.var['file_tag']}polypoint_{i}")
                    dpg.hide_item(f"{self.var['file_tag']}hide_button_{i}")
                    dpg.show_item(f"{self.var['file_tag']}show_button_{i}")

        def show_polygon(self, points):
            for i, poly in enumerate(self.var['polygons']):
                if self.var['polygons'][i]['points'] == points:
                    dpg.show_item(f"{self.var['file_tag']}polygon_{i}")
                    dpg.show_item(f"{self.var['file_tag']}polytext_{i}")
                    dpg.show_item(f"{self.var['file_tag']}polypoint_{i}")
                    dpg.hide_item(f"{self.var['file_tag']}show_button_{i}")
                    dpg.show_item(f"{self.var['file_tag']}hide_button_{i}")

        def clear_polygon_list(self):
            self.var['polygons'] = []
            self.update_polygons_list()

        def add_alfa_button(self, icon_path, callback, tag, show):
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

        def connect_button(self, sender, app_data):
            input_text = dpg.get_value("input_ip")
            print(input_text)