from itertools import count

import cv2
import dearpygui.dearpygui as dpg
import numpy as np
from dearpygui.dearpygui import file_dialog
import os


menu_height = 30
mask_editor_width = 1300
settings_width = 300
height = 700 ##Высота

width = settings_width+mask_editor_width ##ширина
window_width = width + 40
window_height = height + menu_height+ 55

class window():
    def __init__(self):
        self.current_tool = 1
        self.current_file = None
        self.image_data = None
        self.texture_id = None
        self.selected_image = None
        self.image_path = "nullimage.jpg"
        self.current_polygon = []
        self.polygons = []
        self.mask = None
        self.editor_online = False
        self.polygon_num = -1
        self.debug_bool = False

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
          # ← ДОБАВЬ ЭТУ СТРОКУ

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def setup_input_handlers(self):
        """Минимальная настройка обработчиков"""
        with dpg.handler_registry():
            dpg.add_mouse_click_handler(callback=self.simple_click,parent="image_display")

    def simple_click(self, sender, app_data):
        mouse_button = app_data
        self.mouse_pos = dpg.get_mouse_pos()
        x, y = self.mouse_pos

        # ПРОСТАЯ ПРОВЕРКА: обрабатываем клики только если редактор активен
        if not self.editor_online:
            return

        # Получаем область редактора
        editor_pos = dpg.get_item_pos("image_display")
        editor_size = dpg.get_item_rect_size("image_display")

        # Проверяем, что клик в пределах редактора
        if not (editor_pos[0] <= x <= editor_pos[0] + editor_size[0] and
                editor_pos[1] <= y <= editor_pos[1] + editor_size[1]):
            return

        # Остальной код без изменений
        draw_x = x - 8
        draw_y = y - 34

        if draw_x > 0 and draw_y > 0:
            print(f"🖱️ КЛИК: кнопка={mouse_button}, x={draw_x}, y={draw_y}")

        if self.current_tool == 1:
            if draw_x > 0 and draw_y > 0:
                if mouse_button == 0:  # Left click - add point
                    self.current_polygon.append((draw_x, draw_y))
                    print(f"Polygon point added: ({x}, {y}) - Total points: {len(self.current_polygon)}")
                elif mouse_button == 1:  # Right click - complete polygon
                    if len(self.current_polygon) >= 3:
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
                'name': 'noname'
            })

            print(f"Polygon completed with {len(self.current_polygon)} points")
            print(self.polygons)
            self.update_polygons_list()

            self.current_polygon.clear()



    def update_display(self):

        # Берем оригинальное изображение (0-255)
        overlay = self.get_current_image_info()[1]

        # Update texture
        self.load_image(self.w, self.h, overlay, self.texture_id)

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
            font_path = "C:/Windows/Fonts/arial.ttf"
            if os.path.exists(font_path):
                default_font = dpg.add_font(font_path, 16)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic, parent=default_font) ### подключение кириллицы
                dpg.bind_font(default_font)
                print("Шрифт с поддержкой кириллицы установлен")
            else:
                print("Шрифт не найден")

        with dpg.viewport_menu_bar(): ##выпадающее меню
            with dpg.menu(label="Файл"):
                dpg.add_menu_item(label="Открыть")
                dpg.add_menu_item(label="Сохранить")
                dpg.add_menu_item(label="Выйти")

        with dpg.viewport_menu_bar():
            with dpg.menu(label="About"):
                dpg.add_menu_item(label="info")



         # Высота меню

        with dpg.window(
                label="Main Window",
                tag="Main Window",
                no_title_bar=True,
                no_move=True,
                no_resize=True,
                no_scrollbar=True,
                no_collapse=True,
                no_close=True,
                width=window_width,
                height=window_height - menu_height,  # Учитываем высоту меню
                pos=(0, menu_height)  # Сдвигаем вниз
        ):


            with dpg.group(horizontal=True):
                ######################## окно с редактором
                with dpg.child_window(width=mask_editor_width, height=height, tag="editor_area"):
                    #with dpg.group(horizontal=True):
                       # dpg.add_spacer(width=int(mask_editor_width / 2 - 50))  # Отступ
                       # dpg.add_text("Редактор маски")


                    self.dir, self.i, self.w, self.h = self.prepare_image()  # Получаем информацию о файле для начальной текстуры

                    # Создаем начальную текстуру
                    if self.i is not None and self.w > 0 and self.h > 0:
                        with dpg.texture_registry():
                            self.texture_id = dpg.add_raw_texture(
                                width=self.w,
                                height=self.h,
                                default_value = self.i,
                                format=dpg.mvFormat_Float_rgb
                            )

                        # Отображение текстуры
                        with dpg.drawlist(width=self.w, height=self.h, tag="image_display", parent="editor_area"):
                            dpg.draw_image(
                                self.texture_id,
                                (0, 0),
                                (self.w, self.h),
                                uv_min=(0, 0),
                                uv_max=(1, 1)
                            )
                    else:
                        print("❌ Не удалось создать текстуру - нет данных изображения")


                with dpg.child_window(width=width-mask_editor_width, height=height,tag = "buttons_area"):
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=int(settings_width/2-50)) #Отступ
                        dpg.add_text("Инструменты")
                    #dpg.add_button(label="Editor", callback=lambda: self.brush())
                    dpg.add_radio_button(
                        items=["Полигон", "Кисть", "Ластик"],
                        callback=self.tool_changed,

                    )
                    dpg.add_spacer(height=2)
                    dpg.add_text(tag="current_tool")
                    dpg.add_spacer(height=2)

                    dpg.add_separator() ##separation <------

                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=int(settings_width/2-50))  # Отступ
                        dpg.add_text("Mask")

                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Load", callback=lambda: dpg.show_item("file_dialog"), width=80, height=25)
                        dpg.add_spacer(width=25)
                        dpg.add_button(label="Save", callback=lambda: print("Button clicked!"), width=80, height=25)
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
                        #dpg.add_file_extension("All files{.*}")


                    dpg.add_text("Selected file: None", tag="current_file")

                    dpg.add_spacer(height=2)
                    dpg.add_separator() ##separation <------

                    dpg.add_text("Соединение с камерой", tag="CameraIP")
                    dpg.add_spacer(height=2)
                    with dpg.group(horizontal=True):
                        dpg.add_input_text(tag = "input_ip")
                        dpg.add_button(label="->", width=80, height=25,callback=self.connect_button)

                    dpg.add_text("Статус:", tag="connect_text")

                    dpg.add_spacer(height=2)
                    dpg.add_separator()  ##separation <------

                    with dpg.group(tag="polygons_list"):
                        pass




    def update_polygons_list(self):
        # Очищаем старый список
        dpg.delete_item("polygons_list", children_only=True)

        # Добавляем полигоны
        for i, poly in enumerate(self.polygons):
            with dpg.group(horizontal=True, parent="polygons_list"):
                dpg.add_text(str(i) + poly['name'])#: {len(poly['points'])} точек"")
                dpg.add_button(label="X"),# callback= self.delete_polygon(idx))
                dpg.add_button(label="rename")#, callback = lambda

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

    def prepare_image(self,image_path = "dev/nullimage.jpg"): ##чисто подготавливает картинку, фильтрует данные и возращает филтрованное
        readed_image = cv2.imread(image_path) # чтение изображение библ Cv2
        image_rgb = cv2.cvtColor(readed_image, cv2.COLOR_BGR2RGB)       # Конвертируем BGR → RGB
        # Подготавливаем данные для текстуры
        self.image_height, self.image_width = image_rgb.shape[:2]
        self.image_data = (image_rgb.astype(np.float32) / 255.0).flatten()
        return self.image_path,self.image_data,self.image_width,self.image_height

    def load_image(self, width, height, image_data, texture_tag):
        try:
            dpg.delete_item(texture_tag)
            dpg.delete_item("image_display")

            # Создаем новую текстуру с новыми размерами
            with dpg.texture_registry():
                new_texture_id = dpg.add_raw_texture(
                    width=width,  # ← НОВЫЕ размеры
                    height=height,
                    default_value=image_data,
                    format=dpg.mvFormat_Float_rgb
                )


            self.texture_id = new_texture_id  # Сохраняем новый ID текстуры

            # Создаем новый drawlist
            with dpg.drawlist(width=width, height=height, tag="image_display", parent="editor_area"):
                dpg.draw_image(
                    new_texture_id,  # ← используем НОВЫЙ texture_id
                    (0, 0),
                    (width, height),
                    uv_min=(0, 0),
                    uv_max=(1, 1)
                )

            # Сохраняем новые размеры
            self.w = width
            self.h = height

            print(f"✅ Текстура обновлена: {width}x{height}")

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
            self.load_image(self.w,self.h,self.i,self.texture_id)
            self.editor_online = True

    def clear_file(self):
        self.dir, self.i, self.w, self.h = self.prepare_image()
        self.load_image(self.w, self.h, self.i, self.texture_id)
        self.editor_online = False

    def get_current_image_info(self):
        return self.image_path,self.image_data,self.image_width,self.image_height

###################################################################################################################################################

if __name__ == '__main__':
    window()
