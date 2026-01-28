import cv2
import dearpygui.dearpygui as dpg
import numpy as np
import os
import logic.file as file
import logic.camera_control as camera
import logic.visualizer as visualizer
import logic.detector as detector
import asyncio
import modules.constants as const
from datetime import date
import modules.start_window as start_window



class window():
    async def run(self):
        self.project_root = os.getcwd()
        self.current_tool = 1
        self.selected_filepath = None
        self.image_data = None
        self.texture_id = None
        self.selected_image = None
        self.image_path = "../dev/nullimage.jpg"
        self.current_polygon = []
        self.polygons = []
        self.mask = None
        self.editor_online = False
        self.polygon_num = -1
        self.debug_bool = False
        self.w = 100
        self.h = 100
        self.image_data = None
        self.parentfile = None
        self.relative_path = None
        self.display_w = 100
        self.display_h = 100
        self.active_menu = None
        dpg.create_context()
        dpg.create_viewport(
            title='CamParking',
            width=const.WINDOW_WIDTH,
            height=const.WINDOW_HEIGHT,
            min_width=const.WINDOW_WIDTH,
            min_height=const.WINDOW_HEIGHT,
            max_width=const.WINDOW_WIDTH,
            max_height=const.WINDOW_HEIGHT
        )
        self.setup_input_handlers()
        self.program_presets()
        await self.interface()

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def setup_input_handlers(self):
        with dpg.handler_registry():
            dpg.add_mouse_click_handler(callback=self.simple_click, parent="main_window")

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
                    original_x = int(draw_x / (self.display_w / self.w))
                    original_y = int(draw_y / (self.display_h / self.h))

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
        if not hasattr(self, 'display_w') or not hasattr(self, 'w') or self.w == 0:
            return points

        scale_x = self.display_w / self.w
        scale_y = self.display_h / self.h
        return [(int(x * scale_x), int(y * scale_y)) for x, y in points]

    def update_display(self):
        overlay = self.get_current_image_info()[1]
        self.load_image(self.w, self.h, overlay,self.get_current_image_info()[0])

        if len(self.polygons) > 0:
            for i in range(len(self.polygons)):
                tag = "polygon" + str(i)
                scaled_points = self.scale_points_for_display(self.polygons[i]['points'])
                dpg.draw_polyline(scaled_points, color=(255, 0, 255, 255),
                                  thickness=2, tag=tag, parent="image_display")

            for i in range(len(self.polygons)):
                tag = "polypoint" + str(i)
                j = i % len(const.POLYGONS_COLORS)

                scaled_fill_points = self.scale_points_for_display(self.polygons[i]['points'])
                dpg.draw_polygon(scaled_fill_points, color=(255, 0, 0, 100), fill=const.POLYGONS_COLORS[j],
                                 tag=tag, parent="image_display")

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
                    tag=f"polytext_{i}",
                    parent="image_display"
                )

        if self.current_polygon:
            if len(self.current_polygon) > 1:
                scaled_current = self.scale_points_for_display(self.current_polygon)
                dpg.draw_polyline(scaled_current, color=(0, 255, 255, 255),
                                  thickness=2, tag="current_polyline", parent="image_display")

            for i, point in enumerate(self.current_polygon):
                scaled_point = self.scale_points_for_display([point])[0]
                dpg.draw_circle(center=scaled_point, radius=3, color=(255, 0, 255, 255),
                                fill=(255, 0, 0, 255), tag=f"point_{i}", parent="image_display")

            scaled_current_fill = self.scale_points_for_display(self.current_polygon)
            dpg.draw_polygon(scaled_current_fill, color=(0, 255, 0, 100),
                             fill=(255, 255, 0, 100), tag="current_polygon", parent="image_display")

    async def interface(self):
        with dpg.font_registry():
            if os.path.exists(const.FONT_PATH):
                default_font = dpg.add_font(const.FONT_PATH, const.FONT_SIZE)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic, parent=default_font)
                dpg.bind_font(default_font)
                print("Шрифт с поддержкой кириллицы установлен")
            else:
                print("Шрифт не найден")

        with dpg.viewport_menu_bar():
            with dpg.menu(label="Меню"):
                dpg.add_menu_item(label=f"Открыть редактор", callback=lambda: [self.interface_main_window(), self.interface_tool_window()])
                dpg.add_menu_item(label="бяк", callback=lambda: print("бяк"))
            with dpg.menu(label="Файл"):
                dpg.add_menu_item(label="Открыть изображение", callback=lambda: dpg.show_item("file_dialog"))
                dpg.add_menu_item(label="Открыть", callback=lambda: (dpg.show_item("mask_dialog"),
                                                                     setattr(self, 'editor_online', False)))
                dpg.add_menu_item(label="Сохранить", callback=lambda: self.fast_save())
                dpg.add_menu_item(label="Сохранить как", callback=lambda: (dpg.show_item("save_dialog"),
                                                                           setattr(self, 'editor_online', False)))
                dpg.add_menu_item(label="Очистить", callback=lambda: self.clear_file())
                dpg.add_menu_item(label="Настройки", callback=lambda: self.settings())
                dpg.add_menu_item(label="Выйти")
            with dpg.menu(label="Подключение"):
                dpg.add_menu_item(label="Сделать фото", callback=lambda: self.get_screenshot_from_camera())
                dpg.add_menu_item(label="Подключение", callback=lambda: self.interface_main_window())
                dpg.add_menu_item(label="Открыть результаты", callback=lambda: self.interface_tool_window())
                dpg.add_menu_item(label="Настройки соединения")
            with dpg.menu(label="ИИ"):
                dpg.add_menu_item(label=f"Найти занятые места на фото\nВыбранная маска: {None}", callback=lambda: self.make_detection())
            with dpg.menu(label="О программе"):
                dpg.add_menu_item(label="Информация")
            dpg.add_spacer(width = 15)
            dpg.add_text(label=self.active_menu)
            dpg.add_spacer(width = int(const.MAIN_WIDTH / 2))
            dpg.add_text("", tag="current_file")



        self.active_menu = start_window.run()


    def interface_main_window(self):
        with dpg.window(label="Main Window", tag="main_window",
                        no_title_bar=True, no_move=True, no_resize=True, no_collapse=True, no_close=True,
                        width=const.MAIN_WIDTH, height=const.MAIN_HEIGHT,
                        pos=(const.MAIN_POS_X, const.MAIN_POS_Y)):

            self.dir, self.i, self.w, self.h = self.prepare_image()

            if self.i is not None and self.w > 0 and self.h > 0:
                with dpg.texture_registry():
                    self.texture_id = dpg.add_raw_texture(
                        width=self.w,
                        height=self.h,
                        default_value=self.i,
                        format=dpg.mvFormat_Float_rgba
                    )

                with dpg.drawlist(width=self.w, height=self.h, tag="image_display", parent="main_window"):
                    dpg.draw_image(
                        self.texture_id,
                        (0, 0),
                        (self.w, self.h),
                        uv_min=(0, 0),
                        uv_max=(1, 1)
                    )
            else:
                print("❌ Не удалось создать текстуру - нет данных изображения")

    def interface_tool_window(self):
        with dpg.window(label="Tools", tag="tools_area",
                        no_title_bar=True, no_move=True, no_resize=True, no_collapse=True, no_close=True,
                        width=const.TOOLS_WIDTH, height=const.TOOLS_HEIGHT,
                        pos=(const.TOOLS_POS_X, const.TOOLS_POS_Y), no_scrollbar=True):
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=int(const.TOOLS_WIDTH / 2 - 50))
                dpg.add_text("Полигоны")

            with dpg.child_window(
                    tag="polygons_list",
                    height=400,
                    width=const.WINDOW_WIDTH - 15,
                    horizontal_scrollbar=False,
                    autosize_y=False
            ):
                dpg.bind_item_theme("polygons_list", self.child_theme)
            dpg.add_separator()

            dpg.add_text("Управление")
            dpg.add_text("", wrap=0)

    def settings(self):
        if dpg.does_item_exist("modal_window"):
            dpg.delete_item("modal_window")
        x = const.TOOLS_POS_X + (const.WINDOW_WIDTH - const.SETTINGS_WIDTH) // 2
        y = const.TOOLS_POS_Y + (const.WINDOW_HEIGHT - const.SETTINGS_HEIGHT) // 2

        with dpg.window(
                label="Настройки",
                modal=True,
                show=True,
                id="modal_window",
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
            dpg.add_input_text(tag="dialog_input", width=300)

    def program_presets(self):
        with dpg.theme() as self.child_theme:
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (45, 45, 45, 255))
        with dpg.theme() as self.textbox_theme:
            with dpg.theme_component(dpg.mvInputText):
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 6)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 0, 0, 0))

        with dpg.file_dialog(
                directory_selector=False,
                show=False,
                callback=self.file_selected,
                id="file_dialog",
                width=700,
                height=400
        ):
            dpg.add_file_extension("Images{.jpg,.jpeg,.png,.bmp,.gif}")

        with dpg.file_dialog(
                directory_selector=False,
                default_filename="",
                default_path="../../save",
                show=False,
                callback=self.load_mask,
                id="mask_dialog",
                width=700,
                height=400,
                modal=True,
        ):
            dpg.add_file_extension(".mask", color=(0, 255, 0, 255))
            dpg.add_checkbox(
                label="Загрузить только маску",
                default_value=False,
                tag="onlymask"
            )

        with dpg.file_dialog(
                directory_selector=False,
                default_filename="newmask.mask",
                default_path="../../save",
                show=False,
                callback=self.save_button,
                id="save_dialog",
                width=700,
                height=400,
                modal=True
        ):
            dpg.add_file_extension(".mask", color=(0, 255, 0, 255))

    def update_polygons_list(self):
        dpg.delete_item("polygons_list", children_only=True)
        for i, poly in enumerate(self.polygons):
            with dpg.group(horizontal=True, parent="polygons_list"):
                with dpg.group(horizontal=True, tag="const_visible" + str(i)):
                    self.add_alfa_button("../icons/visabilityon.png",
                                         (lambda fixed: lambda s, a: self.hide_polygon(fixed))(poly['points']),
                                         "hide_button" + str(i), True)
                    self.add_alfa_button("../icons/visabilityoff.png",
                                         (lambda fixed: lambda s, a: self.show_polygon(fixed))(poly['points']),
                                         "show_button" + str(i), False)

                    dpg.add_input_text(
                        tag="poly_namespace_" + str(i),
                        default_value=poly['name'],
                        width=195,
                        enabled=False,
                        show=True
                    )
                    dpg.bind_item_theme("poly_namespace_" + str(i), self.textbox_theme)

                with dpg.group(horizontal=True, tag="non_const_visible" + str(i), show=True):
                    self.add_alfa_button("../icons/edit.png",
                                         (lambda fixed: lambda s, a: self.rename_activate(fixed))(i),
                                         "edit_button_" + str(i), True)
                    self.add_alfa_button("../icons/editoff.png",
                                         (lambda fixed: lambda s, a: self.rename_polygon(fixed))(i),
                                         "edit_off_button" + str(i), False)
                    self.add_alfa_button("../icons/delete.png",
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

    def prepare_image(self, image_input = None):
        if image_input == None:
            image_input = "dev/nullimage.png"

        readed_image = cv2.imread(image_input, cv2.IMREAD_UNCHANGED)
        filepath = os.path.relpath(image_input, self.project_root)

        if readed_image is None:
            print(f"❌ Не удалось загрузить изображение")
            readed_image = np.zeros((100, 100, 4), dtype=np.uint8)

        if readed_image.shape[2] == 3:
            image_rgba = cv2.cvtColor(readed_image, cv2.COLOR_BGR2RGBA)
        elif readed_image.shape[2] == 4:
            image_rgba = cv2.cvtColor(readed_image, cv2.COLOR_BGRA2RGBA)
        else:
            image_rgba = cv2.cvtColor(readed_image, cv2.COLOR_BGR2RGBA)

        self.parentfile = image_input
        self.image_height, self.image_width = image_rgba.shape[:2]
        image_data = (image_rgba.astype(np.float32) / 255.0)
        self.image_data = image_data.flatten()

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
                self.display_h = const.WINDOW_HEIGHT - 20
                self.display_w = int(self.display_h * image_ratio)

            with dpg.drawlist(width=self.display_w, height=self.display_h, tag="image_display", parent="main_window"):
                dpg.draw_image(
                    self.texture_id,
                    (0, 0),
                    (self.display_w, self.display_h),
                    uv_min=(0, 0),
                    uv_max=(1, 1)
                )

            self.w = width
            self.h = height
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
            self.dir, self.i, self.w, self.h = self.prepare_image(filepath)
            print(f"Размеры: {self.w}x{self.h}")
            self.clear_poly_list()
            self.load_image(self.w, self.h, self.i,self.dir)
            self.editor_online = True

    def clear_file(self):
        self.dir, self.i, self.w, self.h = self.prepare_image()
        self.load_image(self.w, self.h, self.i,self.dir)
        self.editor_online = False
        self.polygons.clear()
        self.update_polygons_list()

    def save_button(self, sender, app_data):
        if len(self.polygons) != 0:
            self.savedata = {}
            self.selected_filepath = app_data["file_path_name"]
            filepath = os.path.relpath(self.selected_filepath, self.project_root)
            print("Сохраняемый файл:", filepath)
            for i, poly in enumerate(self.polygons):
                if len(poly['points']) > 0 and poly['points'][0] == poly['points'][-1]:
                    del poly['points'][-1]
                self.savedata.setdefault(poly['name'], poly['points'])

            file.save_data(self.savedata, filepath, self.parentfile)
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
        print(f"{self.savedata, self.relative_path, self.parentfile}")
        if hasattr(self, 'relative_path'):
            file.save_data(self.savedata, self.relative_path, self.parentfile)
        self.editor_online = True

    def get_current_image_info(self):
        return self.image_path, self.image_data, self.image_width, self.image_height

    def load_mask(self, sender, app_data):
        self.savedata = {}
        self.selected_filepath = app_data["file_path_name"]
        self.relative_path = os.path.relpath(self.selected_filepath, self.project_root)


        saved_data, prepared_file = file.read_data(self.relative_path)
        print(f"Parent file: {self.parentfile}")
        self.image_path = prepared_file
        if not dpg.get_value("onlymask"):
            self.dir, self.i, self.w, self.h = self.prepare_image(prepared_file)
            self.load_image(self.w, self.h, self.i,self.dir)
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
            INPUT_DIR = "../../img/results/"
            another_img = "output_open.jpg"
            mask = "../save/test4.mask"
            image = camera.get_img_sync()
            print(f"фото получено")

            # Получаем данные о парковке ============== Обработка фото

            occupied, free = detector.check_auto(mask=mask, processed_image=image, config_name="confwn")
            print(f"фото обработано ИИ")

            image, filename = visualizer.detect(image_path=image, mask=mask, occupied_data=[occupied, free],
                                                draw_name=False)
            print(f"фото обработано для вывода")

            self.dir, self.i, self.w, self.h = self.prepare_image(filename)
            self.image_path = image
            self.load_image(self.w, self.h, self.i,self.dir)
            self.editor_online = True
            self.polygons.clear()
            self.update_polygons_list()

        except Exception as e:
            print(e)


    def make_detection(self):

        data1, data2 = detector.check_auto(mask="../save/test4.mask",processed_image=self.get_current_image_info()[0],config_name="confwn")
        data = [data1,data2]
        image, filename = visualizer.detect(image_path=self.get_current_image_info()[0], mask="../save/test4.mask", occupied_data=data,
                                            draw_name=False)
        filepath, image_data, image_width, image_height = self.prepare_image(filename)
        self.load_image(width=image_width, height=image_height, image_data=image_data,image_dir = filepath)
        self.editor_online = False
        print(f"{self.parentfile}{self.i, self.w, self.h}")


if __name__ == '__main__':
    editor = window()
    asyncio.run(editor.run())