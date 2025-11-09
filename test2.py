import cv2
import dearpygui.dearpygui as dpg
import numpy as np
import os
import file

menu_height = 24
window_height = 700+menu_height  #высота

tools_pos_x= 0
tools_pos_y= menu_height
tools_width= 250       #ширина
tools_height= window_height     #высота

main_pos_x= tools_width
main_pos_y= menu_height
main_width= 1300
main_height= window_height

window_width = tools_width+main_width #ширина



class window():
    def __init__(self):
        self.current_tool = 1
        self.current_file = None
        self.image_data = None
        self.texture_id = None
        self.selected_image = None
        self.image_path = "dev/nullimage.jpg"
        self.current_polygon = []
        self.polygons = []
        self.mask = None
        self.editor_online = False
        self.polygon_num = -1
        self.debug_bool = False
        self.w = 100
        self.h = 100
        self.image_data = None

        dpg.create_context()
        dpg.create_viewport(
            title='CamParking',
            width=window_width,
            height=window_height,
            min_width=window_width,  # Минимальная ширина
            min_height=window_height,  # Минимальная высота
            max_width=window_width,  # Максимальная ширина
            max_height=window_height  # Максимальная высота
        )
        self.setup_input_handlers() #Обработчик нажатий
        self.interface()

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def setup_input_handlers(self):
        """Минимальная настройка обработчиков"""
        with dpg.handler_registry():
            dpg.add_mouse_click_handler(callback=self.simple_click,parent="main_window")

    def simple_click(self, sender, app_data):
        mouse_button = app_data
        self.mouse_pos = dpg.get_mouse_pos(local=False)
        x, y = self.mouse_pos

        # ПРОСТАЯ ПРОВЕРКА: обрабатываем клики только если редактор активен
       # if not self.editor_online:
         #  return

        # Остальной код без изменений
        draw_x = x - 8 - tools_width
        draw_y = y - menu_height - 5
        if draw_x > 0 and draw_y > 0:
            if draw_x < self.w or draw_y < self.h:
                if draw_x < self.w and draw_y < self.h:
                    print(f"🖱️ КЛИК: кнопка={mouse_button}, x={draw_x}, y={draw_y}")

                    if self.current_tool == 1:
                        if draw_x > 0 and draw_y > 0:
                            if mouse_button == 0:  # Left click - add point
                                self.current_polygon.append((int(draw_x), int(draw_y)))
                                print(f"Polygon point added: ({x}, {y}) - Total points: {len(self.current_polygon)}")
                                if len(self.current_polygon) > 3:
                                    self.current_polygon.append(self.current_polygon[0])
                                    self.complete_polygon()


            self.update_display()

    def complete_polygon(self):

            # ОТЛАДКА: проверяем результат
            non_zero = np.count_nonzero(self.mask)
            print(f"✅ Mask after drawContours - non-zero pixels: {non_zero}")

            # Add to polygons list (store as separate object)
            self.polygon_num += 1
            self.polygons.append({
                'num': self.polygon_num,
                'points': self.current_polygon.copy(),
                'type': 'polygon',
                'name': 'noname',
                'text_pos': ()
            })

            print(f"Polygon completed with {len(self.current_polygon)} points")
            print(self.polygons)
            self.update_polygons_list()

            self.current_polygon.clear()



    def update_display(self):

        # Берем оригинальное изображение (0-255)
        overlay = self.get_current_image_info()[1]

        # Update texture
        self.load_image(self.w, self.h, overlay)

        # Очищаем старые элементы рисования


        # рисуем все полигоны созданные ранее
        if len(self.polygons) > 0:




            for i in range(len(self.polygons)):
                tag = "polygon" + str(i)
                dpg.draw_polyline(self.polygons[i]['points'], color=(255, 0, 255, 255),
                                  thickness=2, tag=tag, parent="image_display")




            for i in range(len(self.polygons)):
                tag = "polypoint" + str(i)
                dpg.draw_polygon(self.polygons[i]['points'], color=(255, 0, 0, 100), fill=(255, 0, 0, 100),
                                                        tag=tag, parent="image_display")


###проверка по наличию текста нужна сюда
                if 'text_pos' in self.polygons[i]:
                    points = self.polygons[i]['points']
                    center_x = sum(p[0] for p in points) / len(points)
                    center_y = sum(p[1] for p in points) / len(points)
                    self.polygons[i]['text_pos'] = (center_x, center_y)

                # Используем сохраненную позицию
                dpg.draw_text(
                    pos=self.polygons[i]['text_pos'],
                    text=self.polygons[i]['name'],
                    color=(255, 255, 255, 255),
                    size=16,
                    tag=f"polytext_{i}",
                    parent="image_display"
                )

        # Draw current polygon in progress
        if self.current_polygon:
            if len(self.current_polygon) > 1:
                dpg.draw_polyline(self.current_polygon, color=(255, 0, 255, 255),
                                  thickness=2, tag="current_polyline", parent="image_display")

            for i, point in enumerate(self.current_polygon):
                dpg.draw_circle(center=point, radius=3, color=(255, 255, 0, 255),
                                fill=(255, 255, 0, 255), tag=f"point_{i}", parent="image_display")

            dpg.draw_polygon(self.current_polygon, color=(255, 0, 0, 100), fill=(255, 0, 0, 100), tag="current_polygon", parent="image_display")





    def interface(self):

        with dpg.font_registry():
            # Указываем шрифт и добавляем поддержку кириллицы
            font_path = "fonts/defaultfont.ttf"
            if os.path.exists(font_path):
                default_font = dpg.add_font(font_path, 18)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic, parent=default_font) ### подключение кириллицы
                dpg.bind_font(default_font)
                print("Шрифт с поддержкой кириллицы установлен")
            else:
                print("Шрифт не найден")

        with dpg.viewport_menu_bar(): ##выпадающее меню
            with dpg.menu(label="Файл"):
                dpg.add_menu_item(label="Открыть", callback=lambda: dpg.show_item("file_dialog"))
                dpg.add_menu_item(label="Сохранить")
                dpg.add_menu_item(label="Выйти")
            with dpg.menu(label="About"):
                dpg.add_menu_item(label="info")

        self.interface_main_window()
        self.interface_tool_window()


    def interface_main_window(self):
        with dpg.window(label="Main Window", tag="main_window",
                        no_title_bar=True, no_move=True, no_resize=True, no_collapse=True, no_close=True,
                        width=main_width, height=main_height,
                        pos=(main_pos_x, main_pos_y)):

            ######################## окно с редактором

            self.dir, self.i, self.w, self.h = self.prepare_image()  # Получаем информацию о файле для начальной текстуры

            # Создаем начальную текстуру
            if self.i is not None and self.w > 0 and self.h > 0:
                with dpg.texture_registry():
                    self.texture_id = dpg.add_raw_texture(
                        width=self.w,
                        height=self.h,
                        default_value=self.i,
                        format=dpg.mvFormat_Float_rgba
                    )

                # Отображение текстуры
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
                        width=tools_width, height=tools_height,
                        pos=(tools_pos_x, tools_pos_y), no_scrollbar=True):
                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=int(tools_width / 2 - 50))  # Отступ
                    dpg.add_text("Инструменты")
                # dpg.add_button(label="Editor", callback=lambda: self.brush())
                dpg.add_radio_button(
                    items=["Полигон", "Кисть", "Ластик"],
                    callback=self.tool_changed,

                )
                dpg.add_spacer(height=2)
                dpg.add_text(tag="current_tool")
                dpg.add_spacer(height=2)

                dpg.add_separator()  ##separation <------

                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=int(tools_width / 2 - 50))  # Отступ
                    dpg.add_text("Mask")

                with dpg.group(horizontal=True):
                    dpg.add_button(label="Load", callback=lambda: dpg.show_item("file_dialog"), width=80, height=25)
                    dpg.add_spacer(width=25)
                    dpg.add_button(label="Save", callback=lambda: dpg.show_item("save_dialog"), width=80, height=25)

                with dpg.group(horizontal=True):
                    dpg.add_button(label="Clear", callback=lambda: self.clear_file(), width=80, height=25)
                    dpg.add_spacer(width=25)
                    dpg.add_button(label="Save As", callback=lambda: print("Button clicked!"), width=80, height=25)


                dpg.add_spacer(height=2)

                with dpg.file_dialog(
                        directory_selector=False,
                        show=False,
                        callback=self.file_selected,
                        id="file_dialog",
                        width=500,
                        height=400
                ):
                    dpg.add_file_extension("Images{.jpg,.jpeg,.png,.bmp,.gif}")
                    # dpg.add_file_extension("All files{.*}")

                with dpg.file_dialog(
                        directory_selector=False,
                        default_filename="newmask.data",
                        default_path="./saves",
                        show=False,
                        callback=self.save_button,  # Функция-заглушка
                        id="save_dialog",
                        width=500,
                        height=400
                ):
                    dpg.add_file_extension("All files{.*}")

                dpg.add_text("Selected file: None", tag="current_file")

                dpg.add_spacer(height=2)
                dpg.add_separator()  ##separation <------

                dpg.add_text("Соединение с камерой", tag="CameraIP")
                dpg.add_spacer(height=2)
                with dpg.group(horizontal=True):
                    dpg.add_input_text(tag="input_ip")
                    dpg.add_button(label="->", width=80, height=25, callback=self.connect_button)

                dpg.add_text("Статус:", tag="connect_text")

                dpg.add_spacer(height=2)
                dpg.add_separator()  ##separation <------

                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=int(tools_width / 2 - 50))  # Отступ
                    dpg.add_text("Управление")

                with dpg.child_window(
                        tag="polygons_list",
                        height=150,
                        width=tools_width - 15,
                        horizontal_scrollbar=False,
                        autosize_y=False  # Фиксируем высоту для скролла
                ):
                    pass



                dpg.add_separator()

    def load_preset(self):
        pass


    def update_polygons_list(self):
        # Очищаем старый список
        dpg.delete_item("polygons_list", children_only=True)

        # Добавляем полигоны
        for i, poly in enumerate(self.polygons):
            with dpg.group(horizontal=True, parent="polygons_list"):
                self.add_alfa_button("icons/delete.png",(lambda fixed: lambda s, a: self.delete_polygon(fixed))(poly['points']),"delete_button"+str(i))
                dpg.add_input_text(tag="poly_namespace_"+str(i),default_value=poly['name'],width = 140,enabled=True,show=False)
                dpg.add_text(poly['name'], tag="poly_namespace_label"+str(i))
                self.add_alfa_button("icons/rename.png",
                                    (lambda fixed: lambda s, a: self.rename_button(fixed))(i),"rename_button_"+str(i))

    #Кнопка нажимается и убирается
    #Появляется меню и новая кнопка применить
    #кнопка применить нажимается и появляется лейбл

    def rename_button(self,i):
        dpg.hide_item("poly_namespace_label"+str(i))
        dpg.show_item("poly_namespace_"+str(i))
        dpg.configure_item("rename_button_"+str(i),
                           callback=(lambda fixed: lambda s, a: self.rename_polygon(fixed))(i))

    def rename_polygon(self,i):
        newname = dpg.get_value('poly_namespace_' + str(i))
        self.polygons[i]['name'] = newname
        dpg.hide_item("poly_namespace_" + str(i))
        dpg.show_item("poly_namespace_label"+str(i))
        dpg.configure_item("poly_namespace_label"+str(i),default_value = newname)
        dpg.configure_item("rename_button_"+str(i),
                           callback=(lambda fixed: lambda s, a: self.rename_button(fixed))(i)),"rename_button_"+str(i)
        self.update_display()

    def delete_polygon(self,points):
        for i,poly in enumerate(self.polygons):
            if self.polygons[i]['points'] == points:
                del self.polygons[i]

        self.update_polygons_list()
        self.update_display()

    def clear_poly_list(self):
        self.polygons = []
        self.update_polygons_list()

    def add_alfa_button(self, icon_path, callbacks, tag):
        try:
            image = cv2.imread(icon_path, cv2.IMREAD_UNCHANGED)
            if image is None:
                print(f"❌ Не удалось загрузить иконку: {icon_path}")
                return

            # Всегда используем RGBA формат для согласованности
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
                    format=dpg.mvFormat_Float_rgba  # Всегда используем RGBA
                )

            dpg.add_image_button(texture_id, callback=callbacks, tag=tag)

        except Exception as e:
            print(f"❌ Ошибка создания кнопки: {e}")

    def connect_button(self,sender,app_data): ##############подключение к камере
        input_text = dpg.get_value("input_ip")
        print(input_text)

    def tool_changed(self, sender, app_data):
        print(f"Selected: {app_data}")  # "Rectangle", "Polygon" и т.д.

        tool_mapping = {
            "Полигон": ["polygon",1],
            "Кисть": ["brush",2],
            "Ластик": ["",0],
        }



        selected_tool = tool_mapping.get(app_data, "polygon") #получаем ответ от списка (поиск инструмента)

        dpg.set_value("current_tool", f"Выбранный инструмент: {app_data}") #назначаем инструмент
        self.current_tool = selected_tool[1]
        print(f"Selected tool: {selected_tool[1]}")

    def prepare_image(self, image_path="dev/nullimage.jpg"):
        readed_image = cv2.imread(image_path)
        if readed_image is None:
            print(f"❌ Не удалось загрузить изображение: {image_path}")
            # Создаем черное изображение как заглушку
            readed_image = np.zeros((100, 100, 3), dtype=np.uint8)

        image_rgb = cv2.cvtColor(readed_image, cv2.COLOR_BGR2RGB)
        self.image_height, self.image_width = image_rgb.shape[:2]

        # Убедимся, что данные правильно выровнены
        image_data = (image_rgb.astype(np.float32) / 255.0)

        # Преобразуем в RGBA для согласованности
        if image_data.shape[2] == 3:
            # Добавляем альфа-канал
            h, w = image_data.shape[:2]
            rgba_image = np.ones((h, w, 4), dtype=np.float32)
            rgba_image[:, :, :3] = image_data
            image_data = rgba_image

        self.image_data = image_data.flatten()
        return image_path, self.image_data, self.image_width, self.image_height

    def load_image(self, width, height, image_data):
        try:
            # Удаляем старую текстуру если существует
            if hasattr(self, 'texture_id') and dpg.does_item_exist(self.texture_id):
                dpg.delete_item(self.texture_id)

            # Создаем новую текстуру с правильным форматом
            with dpg.texture_registry():
                self.texture_id = dpg.add_raw_texture(
                    width=width,
                    height=height,
                    default_value=image_data,
                    format=dpg.mvFormat_Float_rgba  # Используем RGBA для согласованности
                )

            # Обновляем drawlist
            if dpg.does_item_exist("image_display"):
                dpg.delete_item("image_display")

            with dpg.drawlist(width=width, height=height, tag="image_display", parent="main_window"):
                dpg.draw_image(
                    self.texture_id,
                    (0, 0),
                    (width, height),
                    uv_min=(0, 0),
                    uv_max=(1, 1)
                )

            self.w = width
            self.h = height
            print(f"✅ Текстура обновлена: {width}x{height}")

        except Exception as e:
            print(f"❌ Ошибка обновления текстуры: {e}")
            import traceback
            traceback.print_exc()

        except Exception as e:
            print(f"❌ Ошибка обновления текстуры: {e}")

    def file_selected(self, sender, app_data): ##чисто обрабатывает файл, выдает путь по итогу
        if app_data["file_path_name"]:
            filepath = app_data["file_path_name"]
            print("Загружаем файл:", filepath)
            self.current_file = app_data["file_name"]
            dpg.set_value("current_file", "Selected file: " + self.current_file)
            self.selected_image = filepath  # ← ДОБАВЬ ЭТУ СТРОКУ
            self.dir, self.i, self.w, self.h =self.prepare_image(filepath)
            print(str(self.w)+str(self.h))
            self.clear_poly_list()
            self.load_image(self.w,self.h,self.i)
            self.editor_online = True


    def clear_file(self):
        self.dir, self.i, self.w, self.h = self.prepare_image()
        self.load_image(self.w, self.h, self.i)
        self.editor_online = False

    def save_button(self, sender, app_data):
        self.savedata = {}
        filepath = app_data["file_path_name"]
        print("Сохраняемый файл:", filepath)
        self.current_file = app_data["file_name"]
        for i, poly in enumerate(self.polygons):
            del poly['points'][(len(poly['points'])-1)]
            self.savedata.setdefault(poly['name'], poly['points'])

        file.save_data(self.savedata,filepath)


    def get_current_image_info(self):
        return self.image_path,self.image_data,self.image_width,self.image_height

###################################################################################################################################################

if __name__ == '__main__':
    window()
