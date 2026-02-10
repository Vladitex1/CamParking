import dearpygui.dearpygui as dpg
import os

dpg.create_context()

LAYOUT_FILE = "docking_layout.ini"
print(f"Layout file: {os.path.abspath(LAYOUT_FILE)}")

# Включаем докинг и автосохранение
dpg.configure_app(
    docking=True,
    docking_space=True,
    init_file=LAYOUT_FILE,  # Автосохранение при выходе
    load_init_file=True  # Автозагрузка при старте
)

# Главное окно (должно быть первым!)
with dpg.window(tag="main", no_title_bar=True):
    dpg.add_text("Главное окно")

# Окно 1
with dpg.window(label="Окно 1", tag="window1", width=300):
    dpg.add_text("Содержимое окна 1")
    dpg.add_button(label="Сохранить", callback=lambda: dpg.save_init_file(LAYOUT_FILE))

# Окно 2
with dpg.window(label="Окно 2", tag="window2"):
    dpg.add_text("Содержимое окна 2")
    dpg.add_text(f"Файл layout: {LAYOUT_FILE}")

# Настраиваем viewport
dpg.create_viewport(title='Simple 2-Window Docking', width=900, height=600)


# Функция для начального позиционирования
def setup_initial_positions():
    if not os.path.exists(LAYOUT_FILE):
        # Устанавливаем начальные позиции только если файла нет
        dpg.set_item_pos("window1", [0, 0])
        dpg.set_item_width("window1", 300)
        dpg.set_item_height("window1", 500)

        dpg.set_item_pos("window2", [310, 0])
        dpg.set_item_width("window2", 500)
        dpg.set_item_height("window2", 500)

        # Сохраняем начальный layout
        dpg.save_init_file(LAYOUT_FILE)
        print("✅ Created initial layout")


dpg.setup_dearpygui()
dpg.show_viewport()

# Настраиваем начальные позиции через кадр
dpg.set_frame_callback(5, setup_initial_positions)

# Запускаем
dpg.start_dearpygui()

# При выходе layout автоматически сохранится благодаря init_file
dpg.destroy_context()