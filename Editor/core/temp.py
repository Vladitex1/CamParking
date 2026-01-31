case
"camera":
# Дополнительные меню для редактора
with dpg.menu(label="Меню2"):
    dpg.add_menu_item(label="Открыть редактор",callback=lambda: [self.interface_main_window(),self.interface_tool_window()])
    dpg.add_menu_item(label="бяк", callback=lambda: print("бяк"))

with dpg.menu(label="Файл"):
    dpg.add_menu_item(label="Открыть изображение",callback=lambda: dpg.show_item("file_dialog"))
    dpg.add_menu_item(label="Открыть",callback=lambda: (dpg.show_item("mask_dialog"),setattr(self, 'editor_online', False)))
    dpg.add_menu_item(label="Сохранить", callback=lambda: self.fast_save())
    dpg.add_menu_item(label="Сохранить как",callback=lambda: (dpg.show_item("save_dialog"),setattr(self, 'editor_online', False)))
    dpg.add_menu_item(label="Очистить", callback=lambda: self.clear_file())
    dpg.add_menu_item(label="Настройки", callback=lambda: self.settings())
    dpg.add_menu_item(label="Выйти")

with dpg.menu(label="Подключение"):
    dpg.add_menu_item(label="Сделать фото",callback=lambda: self.get_screenshot_from_camera())
    dpg.add_menu_item(label="Подключение",callback=lambda: self.interface_main_window())
    dpg.add_menu_item(label="Открыть результаты",callback=lambda: self.interface_tool_window())
    dpg.add_menu_item(label="Настройки соединения")

with dpg.menu(label="ИИ"):
    dpg.add_menu_item(label=f"Найти занятые места на фото\nВыбранная маска: {None}",callback=lambda: self.make_detection())

with dpg.menu(label="О программе"):
    dpg.add_menu_item(label="Информация")

dpg.add_spacer(width=15)
dpg.add_text(label=self.active_menu[0])
dpg.add_spacer(width=int(const.MAIN_WIDTH / 2))
dpg.add_text("", tag="current_file")

if make_callback(i) == None:
    dpg.add_menu_item(label=item)
    print("None")
else:
    dpg.add_menu_item(label=item, callback=callback)
    print(str(callback))

    '''match id:
    case 1:#окно старта
        try:
            for i in self.ew_elements:
                dpg.hide_item(i)
        except:
            pass
        dpg.show_item("start_window")
    case 2:#открытие эдитора
        try:
            dpg.hide_item("start_window")
        except:
            pass
        for i in self.ew_elements:
            dpg.show_item(i)'''

    def create_all_windows(self):
        self.create_font()
        windows = []

        # Сначала создаем глобальный бар
        self.create_bar(const.LANGUAGE)
        dpg.hide_item("global_bar")
        # Потом создаем редактор ВНУТРИ глобального бара
        ew.program()
        dw.program()
        self.ew_elements = ew.program.get_tags()
        self.dw_elements = dw.program.get_tags()
        # Сделаем editor_bar дочерним окном global_bar
        #dpg.set_item_parent(ew.EDITOR_BAR_TAG, const.GLOBAL_BAR_TAG)  # !!! Важно !!!

        for i in self.ew_elements:
            dpg.hide_item(i)
        for i in self.dw_elements:
            dpg.hide_item(i)

        windows.append(sw.run())
        for i in range(len(windows)):
            dpg.hide_item(windows[i])