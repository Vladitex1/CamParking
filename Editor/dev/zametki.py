


# [{'num': 0, 'points': [(805.0, 247.0), (813.0, 262.0), (802.0, 476.0), (560.0, 439.0)], 'type': 'polygon'}]
with dpg.window(label="Main Window", tag="Main Window",
                no_title_bar=True, no_move=True, no_resize=True,
                width=window_width, height=window_height - menu_height,
                pos=(0, menu_height)):
    pass  # Пустое окно-контейнер

# Левое окно - абсолютное позиционирование
with dpg.window(label="Tools", tag="buttons_area",
                no_title_bar=True, no_move=True, no_resize=True,
                width=settings_width, height=height,
                pos=(0, menu_height), no_scrollbar=True):

#https://fonts.google.com/icons?lang=ru_Cyrl&preview.size=63&categoryFilters=Feeling:%2FExpressive%2FPlayful&selected=Material+Symbols+Outlined:autorenew:FILL@0;wght@400;GRAD@0;opsz@24&icon.size=24&icon.color=%23e3e3e3

# слайдер

dpg.add_slider_float(
    label="Прозрачность группы",
    default_value=1.0,
    min_value=0.0,
    max_value=1.0,
    callback=lambda s, a: dpg.configure_item("my_group", alpha=a)
)


import ast
pos = []
text_data = []
real_data = []

def save_data(data,filename = "save/saved_data.txt",parentfile = None):
    open(filename, 'w').close()
    with open(filename, "a") as file:
        file.write(str(data))

# чтение файла файл
def read_data(filename = "save/saved_data.txt"):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read().strip()
        result = ast.literal_eval(content)
    return result


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
    dpg.add_button(label="button", callback=lambda: print("click"), width=80, height=25)
    dpg.add_spacer(width=25)

dpg.add_spacer(height=2)

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

###фильтр данных, сопоставление
for name, position in saved_data.items():
    found_car = False
    for current_center in range(len(detect_center_list)):
        if is_inside_polygon(detect_center_list[current_center], position):
            occupied.append(name)
            found_car = True
            break
    if not found_car:
        free.append(name)