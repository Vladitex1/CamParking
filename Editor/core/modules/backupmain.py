import dearpygui.dearpygui as dpg
import os
import asyncio
import modules.constants as const
import modules.start_window as sw
import modules.editor_window as ew
import modules.detection_window as dw

class window():
    async def run(self):
        self.debug_bool = False
        self.menu_bar_id = 0
        self.editor_bar_data=[]
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

        self.create_all_windows()
        # Показываем стартовое окно
        self.show_window(1)
        self.print_windows_stack()
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()


    def print_windows_stack(self):
        """Выводит список всех окон в консоль"""
        all_items = dpg.get_all_items()
        windows = []

        for item in all_items:
            item_type = dpg.get_item_type(item)
            if "mvWindowAppItem" in str(item_type):
                tag = dpg.get_item_alias(item) or f"ID: {item}"
                label = dpg.get_item_label(item) or "Без названия"
                pos = dpg.get_item_pos(item)
                show_state = dpg.is_item_visible(item)

                if tag == "menu_bar":
                    self.menu_bar_id = item

                windows.append({
                    'id': item,
                    'tag': tag,
                    'label': label,
                    'pos': pos,
                    'visible': show_state
                })

        print(f"\n=== Стек окон ({len(windows)}) ===")
        for i, window in enumerate(windows, 1):
            print(f"{i}. '{window['label']}' (тег: {window['tag']})")
            print(f"   ID: {window['id']}, Позиция: {window['pos']}, Видимо: {window['visible']}")

        return windows

    def create_font(self):
        with dpg.font_registry():
            if os.path.exists(const.FONT_PATH):
                default_font = dpg.add_font(const.FONT_PATH, const.FONT_SIZE)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic, parent=default_font)
                dpg.bind_font(default_font)
                print("Шрифт с поддержкой кириллицы установлен")
            else:
                print("Шрифт не найден")

    def create_bar(self, language):
        # Создаем ОДИН viewport_menu_bar в самом верху
        with dpg.window(label=const.GLOBAL_BAR_TAG, tag=const.GLOBAL_BAR_TAG,
                        no_title_bar=True, no_move=True, no_resize=True,
                        no_collapse=True, no_close=True,
                        width=const.WINDOW_FULL_SIZE[0],
                        height=const.MENU_BAR_HEIGHT,
                        pos=(0, 0)):

            with dpg.viewport_menu_bar():
                # ================ Всегда доступно ======================
                for menu_name, menu_data in const.always_visible.items():  # FIX: используем .items()
                    with dpg.menu(label=menu_data["label"][language], tag=menu_name):
                        for item in menu_data["items"]:
                            # Фабрика для создания callback'ов с ПРАВИЛЬНЫМ захватом
                            def create_callback(item_data=item, lang=language):
                                action_data = item_data["action"]
                                label_text = item_data["label"][lang]

                                def callback():
                                    self.menu_callback_handler(
                                        action_type=action_data["type"],
                                        method_name=action_data.get("method"),
                                        arg=action_data.get("arg"),
                                        item_label=label_text
                                    )

                                return callback

                            # Создаем и привязываем callback
                            callback_func = create_callback()

                            dpg.add_menu_item(
                                label=item["label"][language],
                                callback=callback_func
                            )

                        # Добавляем debug пункт в конец меню
                        dpg.add_menu_item(
                            label="debug",
                            callback=self.print_windows_stack
                        )

        return const.GLOBAL_BAR_TAG

    def menu_callback_handler(self, action_type, method_name, arg, item_label):
        """Обработчик callback для пункта меню"""
        print(f"Menu clicked: {item_label}")
        print(f"Debug: action_type={action_type}, type={type(action_type)}")
        print(f"Debug: method_name={method_name}, type={type(method_name)}")

        try:
            match str(action_type):  # Приводим к строке для надежности
                case "none":
                    print(f"No action for: {item_label}")
                    return None
                case "self":
                    if method_name is None:
                        print(f"Error: No method specified for '{item_label}'")
                        return None
                    method = getattr(self, method_name)
                    return method(arg) if arg is not None else method()
                case "dpg":
                    if method_name is None:
                        print(f"Error: No method specified for '{item_label}'")
                        return None
                    method = getattr(dpg, method_name)
                    return method(arg) if arg is not None else method()
                case _:
                    if method_name is None:
                        print(f"Error: No method specified for '{item_label}'")
                        return None
                    # Если action_type - это объект, а не строка
                    method = getattr(action_type, method_name)
                    return method(arg) if arg is not None else method()
        except AttributeError as e:
            print(f"AttributeError in menu callback '{item_label}': {e}")
            print(f"action_type: {action_type}, method: {method_name}")
        except Exception as e:
            print(f"Error in menu callback '{item_label}': {e}")
            import traceback
            traceback.print_exc()

    def create_all_windows(self):
        self.create_font()
        windows = []
        sw.program()
        ew.program()
        dw.program()
        self.ew_elements = ew.program.get_tags()  # список тегов окон редактора (включая editor_bar)
        self.sw_elements = sw.program.get_tags()
        self.dw_elements = dw.program.get_tags()  # список тегов окон детектора (включая detector_bar)

        # Скрываем все окна
        for i in self.sw_elements+self.ew_elements+self.dw_elements:
            dpg.hide_item(i)
        for i in range(len(windows)):
            dpg.hide_item(windows[i])

        # Создаем глобальный бар
        self.create_bar(const.LANGUAGE)

        # Сначала показываем стартовое окно и глобальный бар
        self.show_window(1)

    def set_active_menu(self,data):
        self.active_menu = data

    def show_window(self, id: int):
        match id:
            case 1:  # Стартовое окно
                # Скрываем все окна редактора и детектора
                try:
                    for i in self.ew_elements:  # окна редактора
                        dpg.hide_item(i)
                except:
                    pass
                try:
                    for i in self.dw_elements:  # окна детектора
                        dpg.hide_item(i)
                except:
                    pass
                # Скрываем бары редактора и детектора, показываем глобальный бар
                dpg.hide_item("editor_bar")  # или как там называется тег бара редактора
                dpg.hide_item("detector_bar")
                dpg.show_item(const.GLOBAL_BAR_TAG)  # показываем глобальный бар
                dpg.show_item("start_window")

            case 2:  # Редактор
                # Скрываем стартовое окно и окна детектора
                try:
                    dpg.hide_item("start_window")
                except:
                    pass
                try:
                    for i in self.dw_elements:
                        dpg.hide_item(i)
                except:
                    pass
                # Скрываем глобальный бар и бар детектора, показываем бар редактора
                dpg.hide_item(const.GLOBAL_BAR_TAG)
                dpg.hide_item("detector_bar")
                dpg.show_item("editor_bar")
                # Показываем окна редактора
                for i in self.ew_elements:
                    dpg.show_item(i)

            case 3:  # Детекция
                # Скрываем стартовое окно и окна редактора
                try:
                    dpg.hide_item("start_window")
                except:
                    pass
                try:
                    for i in self.ew_elements:
                        dpg.hide_item(i)
                except:
                    pass
                # Скрываем глобальный бар и бар редактора, показываем бар детектора
                dpg.hide_item(const.GLOBAL_BAR_TAG)
                dpg.hide_item("editor_bar")
                dpg.show_item("detector_bar")
                # Показываем окна детектора
                for i in self.dw_elements:
                    dpg.show_item(i)






if __name__ == '__main__':
    editor = window()
    asyncio.run(editor.run())