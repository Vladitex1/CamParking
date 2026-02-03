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

        self.menu_registry = {}  # Хранит конфиги меню от модулей
        self.active_instance = None  # Текущий активный экземпляр (редактор/детектор)
        self.current_menus = []  # Теги текущих созданных меню

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
        #self.print_windows_stack()
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def create_all_windows(self):
        self.create_font()
        self.create_bar(const.LANGUAGE) # Создаем единый бар


        #Модуль, который всегда видно
        self.register_module_bar(module_name="always_visible", menu_config=const.always_visible, instance=self)

        # Создаем экземпляры модулей и регистрируем их меню
        self.start_instance = sw.program()# Стартовое окно
        self.register_module_bar(module_name=sw.FILE_TAG, menu_config=const.start, instance=self.start_instance)

        self.editor_instance = ew.program()# Редактор
        self.register_module_bar(module_name=ew.FILE_TAG, menu_config=const.editor, instance=self.editor_instance)

        self.detector_instance = dw.program()# Детектор
        self.register_module_bar(module_name=dw.FILE_TAG, menu_config=const.detector, instance=self.detector_instance)

        # Получаем теги окон
        self.start_elements = sw.program.get_tags()
        self.editor_elements = ew.program.get_tags()
        self.detector_elements = dw.program.get_tags()

        for i in self.editor_elements + self.detector_elements: # Скрываем все, кроме стартового окна
            dpg.hide_item(i)
        for i in self.start_elements: # Показываем стартовое окно и его меню
            dpg.show_item(i)

        self.show_module_menu("start", const.LANGUAGE)

        #print("✓ Все окна созданы")
        #print(f"  Старт: {self.start_elements}")
        #print(f"  Редактор: {self.editor_elements}")
        #print(f"  Детектор: {self.detector_elements}")

    def register_module_bar(self, module_name: str, menu_config: dict, instance: object):
        #============== Регистрирация бара от модуля ===============
        self.menu_registry[module_name] = {
            'config': menu_config,
            'instance': instance
        }
        #print(f"✓ Зарегистрировано меню для: {module_name}")

    def show_module_menu(self, module_name: str, language: str = "ru"):
        """Показывает меню указанного модуля"""
        # Получаем конфиг и экземпляр модуля
        if module_name in self.menu_registry:
            module_data = self.menu_registry[module_name]
            menu_config = module_data['config']
            instance = module_data['instance']

            # Сохраняем активный экземпляр
            self.active_instance = instance

            # Создаем меню из конфига
            self.create_menus_from_config(menu_config, instance, language)
        else:
            print(f"✗ Модуль {module_name} не зарегистрирован")

    def create_menus_from_config(self, menu_config: dict, instance: object, language: str):
        """Создает меню из конфигурации"""
        for menu_name, menu_data in menu_config.items():
            # Создаем меню (например, "Файл")
            menu_tag = f"menu_{menu_name}"

            with dpg.menu(label=menu_data["label"][language], tag=menu_tag, parent="main_menu_bar"):
                # Добавляем все пункты этого меню
                for item in menu_data["items"]:
                    self.add_menu_item(item, instance, language)

            # Сохраняем тег созданного меню
            self.current_menus.append(menu_tag)

        print(f"✓ Создано меню: {list(menu_config.keys())}")

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

    def create_func_callback(self, instance, func_path: str, args: dict, label: str):
        """Создает callback для вызова функции с аргументами"""

        def callback():
            print(f"Меню: {label}")
            print(f"Путь к функции: {func_path}")
            try:
                # Разбираем путь к функции
                if func_path.startswith("dpg."):
                    # Вызов функции dpg
                    parts = func_path.split('.')
                    func_name = parts[1] if len(parts) > 1 else None

                    print(f"Вызов dpg.{func_name} с аргументами: {args}")

                    if func_name and hasattr(dpg, func_name):
                        func = getattr(dpg, func_name)
                        if args:
                            return func(**args)
                        else:
                            return func()
                    else:
                        print(f"❌ Функция {func_name} не найдена в dpg")

                elif func_path.startswith("self."):
                    # Цепочка атрибутов: self.file.bar_clear_workspace
                    parts = func_path.split('.')
                    current_obj = instance

                    # Пропускаем 'self' (первый элемент)
                    for i, part in enumerate(parts[1:], 1):
                        print(f"DEBUG: Шаг {i}: ищем '{part}' в {current_obj}")

                        # Проверяем, является ли текущий объект классом (вложенным классом)
                        # или экземпляром с доступными атрибутами
                        if hasattr(current_obj, part):
                            current_obj = getattr(current_obj, part)
                            print(f"DEBUG: Найден. Новый объект: {current_obj}, тип: {type(current_obj)}")
                        else:
                            # Возможно, part - это имя вложенного класса, доступного через __dict__
                            # или это имя метода внутри вложенного класса
                            print(f"❌ Атрибут '{part}' не найден у {current_obj}")
                            print(f"   Полный путь: {parts[:i + 1]}")
                            return
                    # После прохода по цепочке current_obj должен быть вызываемым объектом
                    if callable(current_obj):
                        if args:
                            print(f"Вызов функции с аргументами: {args}")
                            return current_obj(**args)
                        else:
                            print(f"Вызов функции без аргументов")
                            return current_obj()
                    else:
                        print(f"❌ Объект {current_obj} не является вызываемым")

                else:
                    print(f"❌ Неизвестный формат функции: {func_path}")

            except Exception as e:
                print(f"❌ Ошибка в меню '{label}': {e}")
                import traceback
                traceback.print_exc()

        return callback



    #####========================== Создание калбеков =====================================
    def create_callback(self, instance, method_name, arg, label):
        """Создает callback для вызова метода у instance"""

        def callback():
            print(f"Меню: {label}")
            try:
                if method_name:
                    method = getattr(instance, method_name)
                    if arg is not None:
                        return method(arg)
                    else:
                        return method()
            except Exception as e:
                print(f"Ошибка в меню '{label}': {e}")

        return callback

    def create_dpg_callback(self, method_name, arg, label):
        """Создает callback для вызова метода dpg"""

        def callback():
            print(f"Меню: {label}")
            try:
                if method_name:
                    method = getattr(dpg, method_name)
                    if arg is not None:
                        return method(arg)
                    else:
                        return method()
            except Exception as e:
                print(f"Ошибка в меню '{label}': {e}")

        return callback

    def clear_current_menus(self):
        #============= Удаляет все текущие меню =================
        for menu_tag in self.current_menus:
            if dpg.does_item_exist(menu_tag):
                dpg.delete_item(menu_tag)
        self.current_menus = []
        #print("✓ Очищены текущие меню")

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

    def create_bar(self, language: str = "en"):
        """Создает единый меню-бар"""
        GLOBAL_BAR_TAG: str = "global_bar"
        with dpg.window(label=GLOBAL_BAR_TAG, tag=GLOBAL_BAR_TAG,
                        no_title_bar=True, no_move=True, no_resize=True,
                        no_collapse=True, no_close=True,
                        width=const.WINDOW_FULL_SIZE[0],
                        height=const.MENU_BAR_HEIGHT,
                        pos=(0, 0)):
            # Контейнер для меню, который будем изменять
            with dpg.viewport_menu_bar(tag="main_menu_bar"):
                pass  # Меню будем добавлять динамически

        return GLOBAL_BAR_TAG

    def show_window(self, id: int):
        print(f"=== Переключаемся на окно {id} ===")

        self.clear_current_menus()
        self.show_module_menu("always_visible", const.LANGUAGE)
        match id:
            case 1:  # Стартовое окно
                for i in self.editor_elements + self.detector_elements:
                    dpg.hide_item(i)
                for i in self.start_elements:
                    dpg.show_item(i)
                self.show_module_menu(sw.FILE_TAG, const.LANGUAGE)
                print("✓ Активно: Стартовое окно")

            case 2:  # Редактор
                # Скрываем другие окна
                for i in self.detector_elements+self.start_elements:
                    dpg.hide_item(i)
                for i in self.editor_elements:
                    dpg.show_item(i)
                self.show_module_menu(ew.FILE_TAG, const.LANGUAGE)
                print("✓ Активно: Редактор")

            case 3:  # Детекция
                # Скрываем другие окна
                for i in self.editor_elements+self.start_elements:
                    dpg.hide_item(i)
                for i in self.detector_elements:
                    dpg.show_item(i)
                self.show_module_menu(dw.FILE_TAG, const.LANGUAGE)
                print("✓ Активно: Детектор")






if __name__ == '__main__':
    editor = window()
    asyncio.run(editor.run())