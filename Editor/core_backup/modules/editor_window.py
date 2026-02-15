import cv2
import dearpygui.dearpygui as dpg
import numpy as np
import os
import logic.file as file
import logic.camera_control as camera
import logic.visualizer as visualizer
import logic.detector as detector
import Editor.core_backup.modules.constants as const
import Editor.core_backup.modules.themes as themes
import Editor.core_backup.modules.global_func as glbl_func
#import time

from pathlib import Path

FILE_TAG:str = "editor"
FILE_TAG=FILE_TAG+"_"

WINDOW_TAG = f"{FILE_TAG}back_window"
WINDOW_CHILD_TAG = WINDOW_TAG+"_child"

MAIN_TAG = f"{FILE_TAG}main_window"
MAIN_CHILD_TAG = WINDOW_TAG+"_child"

TOOLS_TAG = f"{FILE_TAG}tools_window"
TOOLS_CHILD_TAG = TOOLS_TAG+"_child"

STATUS_BAR_TAG = f"{FILE_TAG}status_bar_window"
STATUS_BAR_CHILD_TAG = STATUS_BAR_TAG+"_child"
## Название тега для поля где располагается картинка (Холст) !!! НЕ САМА КАРТИНКА !!!!
HOLST_NAME = "holst"
TAG_LIST: list = []


class program:
    def __init__(self):
        global FILE_TAG
        if not dpg.does_item_exist(WINDOW_TAG):
            self.var:dict = {
                'texture_id':None,
                'editor_online':False,
                'project_root': str(Path(__file__).parent.parent.parent.parent.resolve()),
                'display_w':100,
                'display_h':100,
                'current_tool':1,
                'current_polygon':[],
                'save_data':{},
                'polygons': [],
                'current_file_path': None,
                'image_width':0,
                'image_height':0,
                'file_tag':FILE_TAG,
                'current_texture_tag':"",
                'image_path':"",
                'last_window_positions':{},
            }

            self.func = self.functional(self)
            self.polygons = self.polygons(self)
            self.file = self.file(self)
            self.front = self.front(self)

            self.setup_input_handlers()
            self.program_presets()

    def get_tags(self=None):
        return TAG_LIST

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
            self.var['editor_online'] = False


            dpg.add_file_extension(".mask", color=(0, 255, 0, 255))
            dpg.add_file_extension(".json", color=(255, 165, 0, 255))
            dpg.add_spacer(height=10)

            with dpg.group(horizontal=False):
                dpg.add_checkbox(
                    label="Загрузить только маску",
                    default_value=False,
                    tag=f"{self.var['file_tag']}onlymask",
                )
                dpg.add_separator()
                text = "Добавлят только полигоны из сохраненного файла"
                dpg.add_text(text,color=(200, 200, 200, 255), wrap=0)

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
            self.last_window_positions = {}
            #self.back_window()
            #self.setup_layout() #начальная предустановка
            #self.setup_dynamic_layout()
            #self.test()
            self.interface_main_window()
            self.interface_tool_window()
            self.interface_status_bar()
            dpg.set_frame_callback(5, self.setup_initial_layout)

        def back_window(self):
            with dpg.window(tag=WINDOW_TAG,no_title_bar=True,
                            width = 1920, height=1080,
                            pos=(5,50),
                            no_move=True,
                            no_bring_to_front_on_focus=True,
                            #autosize=True
                            ):#,resizable=True):
                TAG_LIST.append(WINDOW_TAG)

        def interface_main_window(self):
            with dpg.window(label=MAIN_TAG, tag=MAIN_TAG,
                            #no_title_bar=True,# no_move=True,# no_resize=True,
                            no_collapse=True,
                            no_close=True,#no_bring_to_front_on_focus=True,
                            #width=const.MAIN_WIDTH, height=const.MAIN_HEIGHT, ##начальные показатели
                            #pos=(const.MAIN_POS_X, const.MAIN_POS_Y)
                            ): ##начальные показатели
                self.func.set_img_data(glbl_func.upload_image(parent=WINDOW_CHILD_TAG,
                                                              file_tag=self.var['file_tag'],
                                                              current_texture_tag=self.var['current_texture_tag']))
            TAG_LIST.append(MAIN_TAG)

        def interface_tool_window(self):

            with dpg.window(label=TOOLS_TAG, tag=TOOLS_TAG,
                            #parent = MAIN_TAG,
                            #no_title_bar=True, #no_move=True,
                            #no_resize=True,
                            no_collapse=True,
                            no_close=True,
                            #width=const.TOOLS_WIDTH, height=const.TOOLS_HEIGHT,
                            #pos=(const.TOOLS_POS_X, const.TOOLS_POS_Y),
                            no_scrollbar=True):

                with dpg.group(horizontal=True):
                    #dpg.add_spacer(width=int(const.TOOLS_WIDTH / 2 - 50))
                    dpg.add_text("Полигоны")

                with dpg.child_window(
                        tag=f"{self.var['file_tag']}polygons_list",
                        #height=400,
                        #width=const.TOOLS_WIDTH - 15,
                        horizontal_scrollbar=False,
                        #autosize_y=True,
                        #autosize_x=True,
                ):
                    dpg.bind_item_theme(f"{self.var['file_tag']}polygons_list", themes.theme_editor())
                        #dpg.bind_item_theme(f"{self.var['file_tag']}polygons_list", themes.theme_editor())
                    dpg.add_separator()

                dpg.add_text("Текущие параметры:")
                dpg.add_text("", wrap=0)
                glbl_func.add_alfa_button(
                    icon_path=os.path.join(self.var['project_root'], "Editor/icons/settings.png"),
                    callback=lambda s, a, u: self.settings(),
                    tag=f"{self.var['file_tag']}test_{1}", show=True)
                dpg.add_separator()
                dpg.add_spacer(height=200)
                TAG_LIST.append(TOOLS_TAG)

        def interface_status_bar(self):
            with dpg.window(label=STATUS_BAR_TAG, tag=STATUS_BAR_TAG,
                            #no_title_bar=True, #no_move=True,
                            #parent=MAIN_TAG,
                            #no_resize=True,
                            no_collapse=True,
                            no_close=True,
                            #autosize=True,
                            #min_size= (0,0),
                            #width=const.STATUS_BAR_WIDTH-16, height=const.STATUS_BAR_HEIGHT,
                            #pos=(const.STATUS_BAR_POS_X,const.STATUS_BAR_POS_Y),
                            #no_bring_to_front_on_focus=True,

                            ):
                with dpg.child_window(
                        #frame_style=True,
                        #pos = (5,5),
                        parent = STATUS_BAR_TAG,
                        tag=STATUS_BAR_CHILD_TAG,
                        height=50,#const.STATUS_BAR_HEIGHT,
                        #width=const.STATUS_BAR_WIDTH,
                        horizontal_scrollbar=False,
                        no_scrollbar=True,
                        #autosize_y=True,
                        autosize_x=True,
                        no_scroll_with_mouse=True,
                ):


                    dpg.add_text("widgets")
                    #dpg.add_text(default_value="Статус: готов", tag=f"{self.var['file_tag']}status_text")
                    dpg.bind_item_theme(STATUS_BAR_TAG, themes.theme_editor())
            TAG_LIST.append(STATUS_BAR_TAG)

        def setup_initial_layout(self):
            """Настраивает начальный layout"""
            # Инициализируем позиции окон
            from Editor.core.main import LAYOUT_FILE
            # Если файл существует, layout уже загружен через load_init_file=True
            if not os.path.exists(LAYOUT_FILE):
                # Устанавливаем начальные позиции
                dpg.set_item_pos(TOOLS_TAG, [const.TOOLS_POS_X,const.TOOLS_POS_Y])
                #dpg.set_item_width(TOOLS_TAG, const.TOOLS_WIDTH)
                #dpg.set_item_height(TOOLS_TAG, const.TOOLS_HEIGHT)

                dpg.set_item_pos(MAIN_TAG, [const.MAIN_POS_X,const.MAIN_POS_Y])
                #dpg.set_item_width(MAIN_TAG, const.MAIN_WIDTH)
                #dpg.set_item_height(MAIN_TAG, const.MAIN_HEIGHT)

                dpg.set_item_pos(STATUS_BAR_TAG, [const.STATUS_BAR_POS_X,const.STATUS_BAR_POS_Y])
                #dpg.set_item_width(STATUS_BAR_TAG, const.STATUS_BAR_WIDTH)
                #dpg.set_item_height(STATUS_BAR_TAG, const.STATUS_BAR_HEIGHT)

                # Сохраняем начальный layout
                print("✅ Created initial layout")
            else:
                print("✅ Layout loaded automatically")

        def setup_layout(self):
            try:
                viewport_width = dpg.get_viewport_width()
                viewport_height = dpg.get_viewport_height()

                # Устанавливаем начальные позиции окон
                if dpg.does_item_exist(WINDOW_TAG):
                    dpg.configure_item(WINDOW_TAG, pos=(0, const.MENU_BAR_HEIGHT), width=viewport_width,
                                       height=viewport_height)

                if dpg.does_item_exist(MAIN_TAG):
                    dpg.configure_item(MAIN_TAG, pos=(const.MAIN_POS_X,
                                                      const.MAIN_POS_Y))  # ,width=viewport_width,height=viewport_height)

                if dpg.does_item_exist(TOOLS_TAG):
                    dpg.configure_item(TOOLS_TAG, pos=(0, const.MENU_BAR_HEIGHT), width=viewport_width,
                                       height=viewport_height)

                if dpg.does_item_exist(STATUS_BAR_TAG):
                    dpg.configure_item(STATUS_BAR_TAG, pos=(0, const.MENU_BAR_HEIGHT), width=viewport_width,
                                       height=viewport_height)

                # dpg.set_item_pos("layers_window", [viewport_width - 290, 30])
                # dpg.set_item_width("layers_window", 280)
                # dpg.set_item_height("layers_window", viewport_height - 60)

                # dpg.set_item_pos("workspace_window", [270, 30])
                # dpg.set_item_width("workspace_window", viewport_width - 570)
                # dpg.set_item_height("workspace_window", viewport_height - 60)

                print("🎨 Layout configured successfully")
            except Exception as e:
                print(f"⚠️  Layout setup failed: {e}")

        def setup_dynamic_layout(self):
            """Настраивает динамический layout"""
            # Привязываем обновление layout к изменению viewport
            if not hasattr(self.parent, 'layout_configured'):
                dpg.set_viewport_resize_callback(self.setup_layout)
                #self.parent.layout_configured = True

        def settings(self):
            if dpg.does_item_exist(f"{self.var['file_tag']}modal_window"):
                dpg.delete_item(f"{self.var['file_tag']}modal_window")
            x = const.TOOLS_POS_X + (const.WINDOW_WIDTH - const.SETTINGS_WIDTH) // 2
            y = const.TOOLS_POS_Y + (const.WINDOW_HEIGHT - const.SETTINGS_HEIGHT) // 2

            with dpg.window(
                    label="Настройки",
                    modal=True,
                    show=True,
                    id=f"{self.var['file_tag']}modal_window",
                    no_title_bar=False,
                    no_move=False,
                    collapsed=True,
                    width=const.SETTINGS_WIDTH,
                    height=const.SETTINGS_HEIGHT,
                    horizontal_scrollbar=True,
                    max_size=(const.WINDOW_WIDTH,const.WINDOW_HEIGHT),
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
                dpg.add_input_text(tag=f"{self.var['file_tag']}dialog_input", width=300)

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
                self.func.set_img_data(glbl_func.upload_image(image_path = app_data["file_path_name"],
                 parent = WINDOW_CHILD_TAG,
                 file_tag = self.var['file_tag'],
                 current_texture_tag = self.var['current_texture_tag']))
                self.var['editor_online'] = True

        def bar_open_mask(self,sender,app_data):
            self.savedata = {}
            file_path = app_data["file_path_name"]
            self.var['editor_online'] = True
            #self.relative_path = os.path.relpath(self.selected_filepath, self.project_root)
            #print(f"1: {self.selected_filepath}")
            #print(f"2: {self.project_root}")
            #print(f"3: {self.relative_path}")

            print(f"{file_path}")
            saved_data, parent_file = file.load_data(file_path)#self.selected_filepath)
            self.var['image_data'] = [parent_file,None,None,None]
            self.var['current_file_path'] = file_path
            #print(f"INFO:bar_open_mask:Parent file: {parent_file}")
            if not dpg.get_value("onlymask"):
                self.func.set_img_data(glbl_func.upload_image(image_path = glbl_func.absolute_path(parent_file),
                 parent = WINDOW_CHILD_TAG,
                 file_tag = self.var['file_tag'],
                 current_texture_tag = self.var['current_texture_tag']))

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
                file.save_data(self.var['savedata'], filepath, self.var['image_path'])

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
                    file.save_data(self.var['savedata'], self.var['current_file_path'], self.var['image_path'])
            else:
                print("быстрое сохранение не удалось")

        def bar_clear_workspace(self):
            print("область очищена")
            #self.var['image_data'] = [] #Очищение текущих метаданных
            #self.func.set_img_data([])
            self.func.set_img_data(glbl_func.upload_image(image_path=None,
                                                          parent=WINDOW_CHILD_TAG,
                                                          file_tag=self.var['file_tag'],
                                                          current_texture_tag=self.var['current_texture_tag']))
            self.func.delete_active_tags()
            self.poly.clear_polygon_list()
            self.var['current_file_path'] = None
            #self.polygons.clear()
            #self.update_polygons_list()

    class functional:
        def __init__(self,parent):
            self.parent = parent
            self.var = parent.var
            self.poly = parent.polygons  # ЭКЗЕМПЛЯР!

        def set_img_data(self,data):
            if data == 0:
                print("ошибка присвоения данных")
                return 0
            self.var['image_path'] = data[0]
            self.var['image_data'] = data[1]
            self.var['image_width'] = data[2]
            self.var['image_height'] = data[3]
            self.var['current_texture_tag'] = data[4]
            self.var['display_w'] = data[5]
            self.var['display_h'] = data[6]
            if data[7] == True:
                self.var['editor_online'] = False
            else:
                self.var['editor_online'] = True

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

        def complete_polygon(self, name:str='noname', new:bool=False):
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
                        dpg.add_text(f"#{i}: ")
                        glbl_func.add_alfa_button(icon_path = os.path.join(self.var['project_root'], "Editor/icons/visabilityon.png"),
                                             callback = (lambda fixed: lambda s, a: self.hide_polygon(fixed))(poly['points']),
                                             tag = f"{self.var['file_tag']}hide_button_{i}",show =  True)


                        glbl_func.add_alfa_button(icon_path = os.path.join(self.var['project_root'], "Editor/icons/visabilityoff.png"),
                                             callback = (lambda fixed: lambda s, a: self.show_polygon(fixed))(poly['points']),
                                             tag = f"{self.var['file_tag']}show_button_{i}", show =False)
                        dpg.add_input_text(
                            tag=f"{self.var['file_tag']}poly_namespace_{i}",
                            default_value=f"{poly['name']}",
                            width=155,
                            enabled=False,
                            show=True
                        )
                        dpg.bind_item_theme(f"{self.var['file_tag']}poly_namespace_{i}", themes.theme_editor())

                    with dpg.group(horizontal=True, tag=f"{self.var['file_tag']}non_const_visible_{i}", show=True):
                        glbl_func.add_alfa_button(icon_path = os.path.join(self.var['project_root'], "Editor/icons/edit.png"),
                                             callback = (lambda fixed: lambda s, a: self.rename_activate(fixed))(i),
                                             tag = f"{self.var['file_tag']}edit_button_{i}", show = True)
                        glbl_func.add_alfa_button(icon_path = os.path.join(self.var['project_root'], "Editor/icons/editoff.png"),
                                             callback = (lambda fixed: lambda s, a: self.rename_polygon(fixed))(i),
                                             tag = f"{self.var['file_tag']}edit_off_button_{i}", show = False)
                        glbl_func.add_alfa_button(icon_path = os.path.join(self.var['project_root'], "Editor/icons/delete.png"),
                                             callback = (lambda fixed: lambda s, a: self.delete_polygon(fixed))(poly['points']),
                                             tag = f"{self.var['file_tag']}delete_button_{i}", show = True)

        def rename_activate(self, i:int):
            dpg.configure_item(f"{self.var['file_tag']}poly_namespace_{i}", enabled=True)
            dpg.focus_item(f"{self.var['file_tag']}poly_namespace_{i}")
            dpg.hide_item(f"{self.var['file_tag']}edit_button_{i}")
            dpg.show_item(f"{self.var['file_tag']}edit_off_button_{i}")

        def rename_polygon(self, i:int):
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
            print(self.var['polygons'])
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

        def connect_button(self, sender, app_data):
            input_text = dpg.get_value("input_ip")
            print(input_text)