import dearpygui.dearpygui as dpg
import os
import asyncio
import modules.constants as const
import modules.start_window as sw
import modules.editor_window as ew
import modules.detection_window as dw

class window():
    async def run(self):
        self.current_tags:dict = {}  # Теги текущих созданных меню

        dpg.create_context()
        dpg.create_viewport(
            resizable=True,
            title='CamParking',
            min_width=800,
            min_height=600,
            width=const.WINDOW_WIDTH,
            height=const.WINDOW_HEIGHT,)
        dpg.configure_app(docking=True, init_file="layout.ini")
        self.setup()
        self.show_window("start") #Выбираем окно

        #self.print_windows_stack() #Отладка

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()



    def setup(self):
        '''
        instance - это ссылка на объект (для обращения при вызове)
        menu_config - это ссылка на конфигурацию из constants
        '''

        self.create_font()
        self.create_bar() # Создаем единый бар


        #Модуль, который всегда видно
        self.create_menu_from_config(const.always_visible, self,None,"always_visible")

        # Создаем экземпляры модулей и регистрируем их меню
        self.start_instance = sw.program()# Стартовое окно
        self.create_menu_from_config(const.start, self.start_instance,sw.program.get_tags(),"start")

        self.editor_instance = ew.program()# Редактор
        self.create_menu_from_config(const.editor, self.editor_instance,ew.program.get_tags(),"editor")

        self.detector_instance = dw.program()# Детектор
        self.create_menu_from_config(const.detector, self.detector_instance,dw.program.get_tags(),"detector")


    def create_menu_from_config(self, menu_config: dict, instance: object, menu_content, name: str):
        """Создает меню из конфигурации"""
        language = const.LANGUAGE

        # Инициализируем список тегов для этого модуля
        if name not in self.current_tags:
            self.current_tags[name] = []

        for menu_name, menu_data in menu_config.items():
            # Создаем меню (например, "Файл")
            menu_tag = f"main_menu_{menu_name}"
            with dpg.menu(label=menu_data["label"][language], tag=menu_tag, parent="main_menu_bar"):
                # Добавляем все пункты этого меню
                for item in menu_data["items"]:
                    self.add_menu_item(item, instance, language)

            # Сохраняем тег созданного меню
            self.current_tags[name].append(menu_tag)

        # Добавляем окна модуля
        if menu_content is not None:
            for tag in menu_content:
                if tag not in self.current_tags[name]:  # Избегаем дубликатов
                    self.current_tags[name].append(tag)

        print(f"✓ Создано меню: {list(menu_config.keys())} для модуля '{name}'")

    def add_menu_item(self, item: dict, instance: object, language: str):
        """Добавляет один пункт меню"""
        label = item["label"][language]
        func_path = item.get("func", "none")

        print(f"Создание меню: {label}, функция: {func_path}")

        if func_path == "none":
            callback = None
        else:
            # Собираем все аргументы из item, кроме 'label' и 'func'
            args = {}
            for key, value in item.items():
                if key not in ['label', 'func']:
                    args[key] = value

            # Создаем callback
            callback = self.create_func_callback(instance, func_path, args, label)

        # Добавляем пункт меню
        if callback is not None:
            dpg.add_menu_item(label=label, callback=callback)
        else:
            dpg.add_menu_item(label=label)


    #####========================== Создание калбеков =====================================
    def create_func_callback(self, instance, func_path: str, args: dict,label:str):
        def callback():
            parts = func_path.split('.') # делим функцию на части
            if func_path.startswith("dpg."):
                obj, path_parts = dpg, parts[1:]  # Пропускаем "dpg"
            elif func_path.startswith("self."):
                obj, path_parts = instance, parts[1:]  # Пропускаем "self"

            else: # ================ Проверка ошибки ======================
                print(f"❌ Неизвестный формат: {func_path}")
                return

            # Ищем по цепочке атрибутов
            for part in path_parts:
                if hasattr(obj, part):
                    obj = getattr(obj, part)
                else: # ================ Проверка ошибки ======================
                    print(f"❌ Атрибут '{part}' не найден у {obj}")
                    return

            # Проверяем и вызываем
            if not callable(obj): # ================ Проверка ошибки ======================
                print(f"❌ Объект {obj} не является вызываемым")
                return

            print(f"Вызов {func_path} с аргументами: {args}")
            return obj(**args) if args else obj()
        return callback

    # ============= Скрывает все текущие меню =================
    def hide_menu_all(self):
        for value in self.current_tags.values():
            for tag in value:
                dpg.hide_item(tag)

    def show_menu_all(self):
        for value in self.current_tags.values():
            for tag in value:
                dpg.show_item(tag)

    def show_menu(self, menu_name: str):
        for tag in self.current_tags[menu_name]:
            dpg.show_item(tag)

    def hide_menu(self, menu_name: str):
        for tag in self.current_tags[menu_name]:
            dpg.hide_item(tag)

    def show_window(self, name: str):
        print(f"=== Переключаемся на окно {name} ===")
        #print(self.current_tags)
        self.hide_menu_all()
        self.show_menu("always_visible")
        dpg.hide_item('main_menu_start_zaglushka')
        self.show_menu(name)
        print("✓ Активно: name")



    def create_font(self):
        with dpg.font_registry():
            if os.path.exists(const.FONT_PATH):
                default_font = dpg.add_font(const.FONT_PATH, const.FONT_SIZE)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic, parent=default_font)
                dpg.bind_font(default_font)
                print("Шрифт с поддержкой кириллицы установлен")
            else:
                print("Шрифт не найден")

    def create_bar(self):
        """Создает единый меню-бар"""
        with dpg.viewport_menu_bar(tag="main_menu_bar"):
            pass  # Меню будем добавлять динамически

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



if __name__ == '__main__':
    editor = window()
    asyncio.run(editor.run())