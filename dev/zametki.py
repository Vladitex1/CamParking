


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