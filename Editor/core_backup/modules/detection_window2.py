import cv2
import dearpygui.dearpygui as dpg
import numpy as np
import os
import logic.file as file
import logic.camera_control as camera
import logic.visualizer as visualizer
import logic.detector as detector
import Editor.core.app.constants as const
import Editor.core.app.themes as themes

FILE_TAG:str = "detector"
FILE_TAG=FILE_TAG+"_"

WINDOW_LABEL = f"{FILE_TAG}main_window"
WINDOW_TAG = f"{FILE_TAG}main_window"
TOOLS_LABEL = f"{FILE_TAG}tools_window"
TOOLS_TAG = f"{FILE_TAG}tools_window"


class program:
    def __init__(self):
        global FILE_TAG
        if not dpg.does_item_exist(WINDOW_TAG):
            self.texture_id = None
            self.img_info = None
            self.editor_online = False
            self.display_w:int = 100
            self.display_h:int = 100
            self.current_tool:int = 1
            self.current_polygon:list = []
            self.polygons:list = []
            self.parent_file_path:str = ""
            self.relative_path:str = ""
            self.image_width:int = 0
            self.image_height:int = 0
            self.image_data = None
            self.file_tag = FILE_TAG
            self.project_root = const.PROJECT_ROOT

            self.program_presets()
            self.interface_main_window()
            self.interface_tool_window()
            #setup_input_handlers()

    def get_tags(self=None):
        data: list = []
        data.append(WINDOW_TAG)
        data.append(TOOLS_TAG)
        return data

    def interface_main_window(self):
        with dpg.window(label=WINDOW_LABEL, tag=WINDOW_TAG,
                        no_title_bar=True, no_move=True, no_resize=True, no_collapse=True, no_close=True,
                        width=const.MAIN_WIDTH, height=const.MAIN_HEIGHT,
                        pos=(const.MAIN_POS_X, const.MAIN_POS_Y)):
            self.dir, self.img_info, self.width, self.height = self.prepare_image()

            if self.img_info is not None and self.width > 0 and self.height > 0:
                with dpg.texture_registry():
                    self.texture_id = dpg.add_raw_texture(
                        width=self.width,
                        height=self.height,
                        default_value=self.img_info,
                        format=dpg.mvFormat_Float_rgba
                    )

                with dpg.drawlist(width=self.width, height=self.height, tag=f"{self.file_tag}image_display", parent=f"{self.file_tag}main_window"):
                    dpg.draw_image(
                        self.texture_id,
                        (0, 0),
                        (self.width, self.height),
                        uv_min=(0, 0),
                        uv_max=(1, 1)
                    )
            else:
                print("❌ Не удалось создать текстуру - нет данных изображения")

    def interface_tool_window(self):
        with dpg.window(label=TOOLS_LABEL, tag=TOOLS_TAG,
                        no_title_bar=True, no_move=True, no_resize=True, no_collapse=True, no_close=True,
                        width=const.TOOLS_WIDTH, height=const.TOOLS_HEIGHT,
                        pos=(const.TOOLS_POS_X, const.TOOLS_POS_Y), no_scrollbar=True):
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=int(const.TOOLS_WIDTH / 2 - 50))
                dpg.add_text("Полигоны")

            with dpg.child_window(
                    tag=f"{self.file_tag}polygons_list",
                    height=400,
                    width=const.TOOLS_WIDTH - 15,
                    horizontal_scrollbar=False,
                    autosize_y=False
            ):
                dpg.bind_item_theme(f"{self.file_tag}polygons_list", themes.theme_detector())
            dpg.add_separator()

            dpg.add_text("ЗАЛАУПА")
            dpg.add_text("", wrap=0)

    def settings(self):
        if dpg.does_item_exist(f"{self.file_tag}modal_window"):
            dpg.delete_item(f"{self.file_tag}modal_window")
        x = const.TOOLS_POS_X + (const.WINDOW_WIDTH - const.SETTINGS_WIDTH) // 2
        y = const.TOOLS_POS_Y + (const.WINDOW_HEIGHT - const.SETTINGS_HEIGHT) // 2

        with dpg.window(
                label="Настройки",
                modal=True,
                show=True,
                id=f"{self.file_tag}modal_window",
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
            dpg.add_input_text(tag=f"{self.file_tag}dialog_input", width=300)


    def setup_input_handlers(self):
        with dpg.handler_registry():
            dpg.add_mouse_click_handler(callback=self.simple_click, parent=f"{self.file_tag}main_window")

    def simple_click(self, sender, app_data):
        mouse_button = app_data
        self.mouse_pos = dpg.get_mouse_pos(local=False)
        x, y = self.mouse_pos

        if not self.editor_online:
            return

        draw_x = x - 8 - const.TOOLS_WIDTH
        draw_y = y - const.MENU_BAR_HEIGHT - 5

        if draw_x > 0 and draw_y > 0:
            if draw_x < self.display_w and draw_y < self.display_h:
                print(f"🖱️ КЛИК: кнопка={mouse_button}, x={draw_x}, y={draw_y}")

                if self.current_tool == 1:
                    original_x = int(draw_x / (self.display_w / self.width))
                    original_y = int(draw_y / (self.display_h / self.height))

                    self.current_polygon.append((original_x, original_y))
                    print(f"Polygon point added: оригинал({original_x}, {original_y})")

                    if len(self.current_polygon) > 3:
                        self.current_polygon.append(self.current_polygon[0])
                        self.complete_polygon(new=True)

                self.update_display()

    def complete_polygon(self, name='noname', new=False):
        if name == 'noname':
            name = 'noname' + " " + str(len(self.polygons))

        self.polygons.append({
            'num': len(self.polygons),
            'points': self.current_polygon.copy(),
            'type': 'polygon',
            'name': name,
            'text_pos': None
        })

        if new:
            self.update_polygons_list()

        self.current_polygon.clear()

    def scale_points_for_display(self, points):
        if not hasattr(self, 'display_w') or not hasattr(self, 'w') or self.width == 0:
            return points

        scale_x = self.display_w / self.width
        scale_y = self.display_h / self.height
        return [(int(x * scale_x), int(y * scale_y)) for x, y in points]


    def update_display(self):
        overlay = self.get_current_image_info()[1]
        self.load_image(self.width, self.height, overlay,self.get_current_image_info()[0])

        if len(self.polygons) > 0:
            for i in range(len(self.polygons)):
                tag = f"{self.file_tag}polygon" + str(i)
                scaled_points = self.scale_points_for_display(self.polygons[i]['points'])
                dpg.draw_polyline(scaled_points, color=(255, 0, 255, 255),
                                  thickness=2, tag=tag, parent=f"{self.file_tag}image_display")

            for i in range(len(self.polygons)):
                tag = f"{self.file_tag}polypoint" + str(i)
                j = i % len(const.POLYGONS_COLORS)

                scaled_fill_points = self.scale_points_for_display(self.polygons[i]['points'])
                dpg.draw_polygon(scaled_fill_points, color=(255, 0, 0, 100), fill=const.POLYGONS_COLORS[j],
                                 tag=tag, parent=f"{self.file_tag}image_display")

                points = self.polygons[i]['points']
                center_x = sum(p[0] for p in points) / len(points)
                center_y = sum(p[1] for p in points) / len(points)

                scaled_center = self.scale_points_for_display([(center_x - 30, center_y)])[0]
                self.polygons[i]['text_pos'] = scaled_center

                dpg.draw_text(
                    pos=scaled_center,
                    text=self.polygons[i]['name'],
                    color=(255, 255, 0, 255),
                    size=18,
                    tag=f"{self.file_tag}polytext_{i}",
                    parent=f"{self.file_tag}image_display"
                )

        if self.current_polygon:
            if len(self.current_polygon) > 1:
                scaled_current = self.scale_points_for_display(self.current_polygon)
                dpg.draw_polyline(scaled_current, color=(0, 255, 255, 255),
                                  thickness=2, tag=f"{self.file_tag}current_polyline", parent=f"{self.file_tag}image_display")

            for i, point in enumerate(self.current_polygon):
                scaled_point = self.scale_points_for_display([point])[0]
                dpg.draw_circle(center=scaled_point, radius=3, color=(255, 0, 255, 255),
                                fill=(255, 0, 0, 255), tag=f"{self.file_tag}point_{i}", parent=f"{self.file_tag}image_display")

            scaled_current_fill = self.scale_points_for_display(self.current_polygon)
            dpg.draw_polygon(scaled_current_fill, color=(0, 255, 0, 100),
                             fill=(255, 255, 0, 100), tag=f"{self.file_tag}current_polygon", parent=f"{self.file_tag}image_display")

    def update_polygons_list(self):
        dpg.delete_item("polygons_list", children_only=True)
        for i, poly in enumerate(self.polygons):
            with dpg.group(horizontal=True, parent=f"{self.file_tag}polygons_list"):
                with dpg.group(horizontal=True, tag=f"{self.file_tag}const_visible" + str(i)):
                    self.add_alfa_button("icons/visabilityon.png",
                                         (lambda fixed: lambda s, a: self.hide_polygon(fixed))(poly['points']),
                                         "hide_button" + str(i), True)
                    self.add_alfa_button("icons/visabilityoff.png",
                                         (lambda fixed: lambda s, a: self.show_polygon(fixed))(poly['points']),
                                         "show_button" + str(i), False)

                    dpg.add_input_text(
                        tag=f"{self.file_tag}poly_namespace_" + str(i),
                        default_value=poly['name'],
                        width=195,
                        enabled=False,
                        show=True
                    )
                    dpg.bind_item_theme("poly_namespace_" + str(i), themes.theme2())

                with dpg.group(horizontal=True, tag=f"{self.file_tag}non_const_visible" + str(i), show=True):
                    self.add_alfa_button("icons/edit.png",
                                         (lambda fixed: lambda s, a: self.rename_activate(fixed))(i),
                                         "edit_button_" + str(i), True)
                    self.add_alfa_button("icons/editoff.png",
                                         (lambda fixed: lambda s, a: self.rename_polygon(fixed))(i),
                                         "edit_off_button" + str(i), False)
                    self.add_alfa_button("icons/delete.png",
                                         (lambda fixed: lambda s, a: self.delete_polygon(fixed))(poly['points']),
                                         "delete_button" + str(i), True)

    def rename_activate(self, i):
        dpg.configure_item("poly_namespace_" + str(i), enabled=True)
        dpg.focus_item("poly_namespace_" + str(i))
        dpg.hide_item("edit_button_" + str(i))
        dpg.show_item("edit_off_button" + str(i))

    def rename_polygon(self, i):
        newname = dpg.get_value('poly_namespace_' + str(i))
        self.polygons[i]['name'] = newname
        dpg.configure_item("poly_namespace_" + str(i), enabled=False)
        dpg.hide_item("edit_off_button" + str(i))
        dpg.show_item("edit_button_" + str(i))
        self.update_display()

    def delete_polygon(self, points):
        for i, poly in enumerate(self.polygons):
            if self.polygons[i]['points'] == points:
                del self.polygons[i]
                break
        self.update_polygons_list()
        self.update_display()

    def hide_polygon(self, points):
        for i, poly in enumerate(self.polygons):
            if self.polygons[i]['points'] == points:
                dpg.hide_item("polygon" + str(i))
                dpg.hide_item("polytext_" + str(i))
                dpg.hide_item("polypoint" + str(i))
                dpg.hide_item("hide_button" + str(i))
                dpg.show_item("show_button" + str(i))

    def show_polygon(self, points):
        for i, poly in enumerate(self.polygons):
            if self.polygons[i]['points'] == points:
                dpg.show_item("polygon" + str(i))
                dpg.show_item("polytext_" + str(i))
                dpg.show_item("polypoint" + str(i))
                dpg.hide_item("show_button" + str(i))
                dpg.show_item("hide_button" + str(i))

    def clear_poly_list(self):
        self.polygons = []
        self.update_polygons_list()

    def add_alfa_button(self, icon_path, callbacks, tag, show):
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

            dpg.add_image_button(texture_id, callback=callbacks, tag=tag, show=show)

        except Exception as e:
            print(f"❌ Ошибка создания кнопки: {e}")

    def connect_button(self, sender, app_data):
        input_text = dpg.get_value("input_ip")
        print(input_text)

    def tool_changed(self, sender, app_data):
        print(f"Selected: {app_data}")
        tool_mapping = {
            "Полигон": ["polygon", 1],
            "Кисть": ["brush", 2],
            "Ластик": ["", 0],
        }
        selected_tool = tool_mapping.get(app_data, "polygon")
        dpg.set_value("current_tool", f"Выбранный инструмент: {app_data}")
        self.current_tool = selected_tool[1]
        print(f"Selected tool: {selected_tool[1]}")

    def prepare_image(self, image_input:str = const.NULL_IMAGE):
        read_image = cv2.imread(image_input, cv2.IMREAD_UNCHANGED)
        filepath = os.path.relpath(image_input, const.PROJECT_ROOT)

        if read_image is None:
            print(f"❌ Не удалось загрузить изображение")
            read_image = np.zeros((100, 100, 4), dtype=np.uint8)

        if read_image.shape[2] == 3:
            image_rgba = cv2.cvtColor(read_image, cv2.COLOR_BGR2RGBA)
        elif read_image.shape[2] == 4:
            image_rgba = cv2.cvtColor(read_image, cv2.COLOR_BGRA2RGBA)
        else:
            image_rgba = cv2.cvtColor(read_image, cv2.COLOR_BGR2RGBA)

        self.parent_file_path = image_input
        self.image_height, self.image_width = image_rgba.shape[:2]
        data = (image_rgba.astype(np.float32) / 255.0)
        self.image_data = data.flatten()

        return filepath, self.image_data, self.image_width, self.image_height


    def load_image(self, width, height, image_data,image_dir):
        try:
            if hasattr(self, 'texture_id') and dpg.does_item_exist(self.texture_id):
                dpg.delete_item(self.texture_id)

            with dpg.texture_registry():
                self.texture_id = dpg.add_raw_texture(
                    width=width,
                    height=height,
                    default_value=image_data,
                    format=dpg.mvFormat_Float_rgba
                )

            if dpg.does_item_exist("image_display"):
                dpg.delete_item("image_display")

            image_ratio = width / height
            available_ratio = const.MAIN_WIDTH / const.MAIN_HEIGHT

            if image_ratio > available_ratio:
                self.display_w = const.MAIN_WIDTH - 50
                self.display_h = int(self.display_w / image_ratio)
            else:
                self.display_h = const.MAIN_HEIGHT - 20
                self.display_w = int(self.display_h * image_ratio)

            with dpg.drawlist(width=self.display_w, height=self.display_h, tag=f"{self.file_tag}image_display", parent=WINDOW_TAG):
                dpg.draw_image(
                    self.texture_id,
                    (0, 0),
                    (self.display_w, self.display_h),
                    uv_min=(0, 0),
                    uv_max=(1, 1)
                )

            self.width = width
            self.height = height
            dpg.set_value("current_file", os.path.basename(image_dir))
            self.image_path = image_dir
            print(f"✅ Текстура обновлена: оригинал {width}x{height} -> отображение {self.display_w}x{self.display_h}")

        except Exception as e:
            print(f"❌ Ошибка обновления текстуры: {e}")

    def file_selected(self, sender, app_data):
        if app_data["file_path_name"]:
            self.selected_filepath = app_data["file_path_name"]
            filepath = os.path.relpath(self.selected_filepath, self.project_root)
            print("Загружаем файл:", filepath)
            self.selected_image = filepath
            self.dir, self.img_info, self.width, self.height = self.prepare_image(filepath)
            print(f"Размеры: {self.width}x{self.height}")
            self.clear_poly_list()
            self.load_image(self.width, self.height, self.img_info,self.dir)
            self.editor_online = True

    def clear_file(self):
        self.dir, self.img_info, self.width, self.height = self.prepare_image()
        self.load_image(self.width, self.height, self.img_info,self.dir)
        self.editor_online = False
        self.polygons.clear()
        self.update_polygons_list()

    def save_button(self, sender, app_data):
        if len(self.polygons) != 0:
            self.savedata = {}
            self.selected_filepath = app_data["file_path_name"]
            filepath = os.path.relpath(self.selected_filepath, const.PROJECT_ROOT)
            print("Сохраняемый файл:", filepath)
            for i, poly in enumerate(self.polygons):
                if len(poly['points']) > 0 and poly['points'][0] == poly['points'][-1]:
                    del poly['points'][-1]
                self.savedata.setdefault(poly['name'], poly['points'])

            file.save_data(self.savedata, filepath, self.parent_file_path)
            self.editor_online = True
        else:
            print("Сохранение не удалось.")

    def fast_save(self):
        if not self.editor_online:
            return
        self.savedata = {}
        print("быстрое сохранение")
        for i, poly in enumerate(self.polygons):
            if len(poly['points']) > 0 and poly['points'][0] == poly['points'][-1]:
                del poly['points'][-1]
            self.savedata.setdefault(poly['name'], poly['points'])
        print(f"{self.savedata, self.relative_path, self.parent_file_path}")
        if hasattr(self, 'relative_path'):
            file.save_data(self.savedata, self.relative_path, self.parent_file_path)
        self.editor_online = True

    def get_current_image_info(self):
        return self.image_path, self.image_data, self.image_width, self.image_height

    def load_mask(self, sender, app_data):
        self.savedata = {}
        self.selected_filepath = app_data["file_path_name"]
        self.relative_path = os.path.relpath(self.selected_filepath, const.PROJECT_ROOT)


        saved_data, prepared_file = file.read_data(self.relative_path)
        print(f"Parent file: {self.parent_file_path}")
        self.image_path = prepared_file
        if not dpg.get_value("onlymask"):
            self.dir, self.img_info, self.width, self.height = self.prepare_image(prepared_file)
            self.load_image(self.width, self.height, self.img_info,self.dir)
        else:
            dpg.set_value("current_file", f"Загружена маска от файла:{os.path.basename(self.relative_path)}")

        self.current_polygon.clear()
        self.polygons.clear()
        for sd_value in saved_data:
            self.current_polygon = saved_data[sd_value]
            if len(self.current_polygon) > 0 and self.current_polygon[0] != self.current_polygon[-1]:
                self.current_polygon.append(self.current_polygon[0])
            self.complete_polygon(sd_value)
        self.update_polygons_list()
        self.update_display()
        self.editor_online = True

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

    def program_presets(self):



            with dpg.file_dialog(
                    directory_selector=False,
                    show=False,
                    callback=self.file_selected,
                    default_path=f"{const.PROJECT_ROOT}/img",
                    id=f"{self.file_tag}file_dialog",
                    width=700,
                    height=400
            ):
                dpg.add_file_extension("Images{.jpg,.jpeg,.png,.bmp,.gif}")

            with dpg.file_dialog(
                    directory_selector=False,
                    default_filename="",
                    default_path=f"{const.PROJECT_ROOT}/save",
                    show=False,
                    callback=self.load_mask,
                    id=f"{self.file_tag}mask_dialog",
                    width=700,
                    height=400,
                    modal=True,
            ):
                dpg.add_file_extension(".mask", color=(0, 255, 0, 255))
                dpg.add_checkbox(
                    label="Загрузить только маску",
                    default_value=False,
                    tag=f"{self.file_tag}onlymask"
                )

            with dpg.file_dialog(
                    directory_selector=False,
                    default_filename="newmask.mask",
                    default_path=f"{const.PROJECT_ROOT}/save",
                    show=False,
                    callback=self.save_button,
                    id=f"{self.file_tag}save_dialog",
                    width=700,
                    height=400,
                    modal=True
            ):
                dpg.add_file_extension(".mask", color=(0, 255, 0, 255))
