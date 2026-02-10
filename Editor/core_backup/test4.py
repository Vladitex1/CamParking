import dearpygui.dearpygui as dpg
import os
import threading
import time

dpg.create_context()

LAYOUT_FILE = "docking_layout.ini"
print(f"Layout file: {os.path.abspath(LAYOUT_FILE)}")

# Включаем докинг с автосохранением при выходе
dpg.configure_app(
    docking=True,
    docking_space=True,
    init_file=LAYOUT_FILE,  # Автосохранение при выходе
    load_init_file=True  # Автозагрузка при старте
)

# Главное окно
with dpg.window(tag="main", no_title_bar=True):
    dpg.add_text("Main Area")
    dpg.add_text("Auto-save: OFF", tag="auto_save_status")

# Окна для докинга
with dpg.window(label="Tools", tag="tools", width=200):
    dpg.add_text("Tools")
    dpg.add_button(label="Save Now", callback=lambda: save_layout())
    dpg.add_button(label="Toggle Auto-save", callback=lambda: toggle_auto_save)
    dpg.add_button(label="Exit", callback=lambda: exit_app)

with dpg.window(label="Workspace", tag="workspace"):
    dpg.add_text("Workspace")
    dpg.add_text("Status: Ready", tag="status")
    dpg.add_text("Last save: Never", tag="last_save")

with dpg.window(label="Properties", tag="properties", width=200):
    dpg.add_text("Properties")

# Флаги для автосохранения
auto_save_enabled = False
auto_save_thread = None
last_window_positions = {}


def get_window_positions():
    """Получает текущие позиции всех окон"""
    positions = {}
    windows = ["tools", "workspace", "properties"]
    for win in windows:
        if dpg.does_item_exist(win):
            try:
                pos = dpg.get_item_pos(win)
                size = dpg.get_item_rect_size(win)
                positions[win] = (pos, size)
            except:
                pass
    return positions


def has_layout_changed():
    """Проверяет, изменился ли layout"""
    global last_window_positions
    current = get_window_positions()

    if not last_window_positions:
        last_window_positions = current
        return True

    # Сравниваем позиции
    for win in current:
        if win not in last_window_positions:
            return True
        if current[win] != last_window_positions[win]:
            return True

    return False


def save_layout():
    """Сохраняет layout"""
    global last_window_positions
    try:
        dpg.save_init_file(LAYOUT_FILE)
        last_window_positions = get_window_positions()

        current_time = time.strftime("%H:%M:%S")
        print(f"✅ [{current_time}] Layout saved to {LAYOUT_FILE}")
        dpg.set_value("status", "Status: ✅ Layout saved")
        dpg.set_value("last_save", f"Last save: {current_time}")
        return True
    except Exception as e:
        print(f"❌ Error saving layout: {e}")
        dpg.set_value("status", f"Status: ❌ Save failed")
        return False


def auto_save_worker():
    """Рабочий поток для автосохранения"""
    global auto_save_enabled
    while auto_save_enabled:
        time.sleep(5)  # Проверяем каждые 5 секунд

        # Проверяем, изменился ли layout
        if has_layout_changed():
            try:
                # Выполняем сохранение в основном потоке
                dpg.split_frame(delay=0)
                save_layout()
            except:
                pass


def toggle_auto_save():
    """Включает/выключает автосохранение"""
    global auto_save_enabled, auto_save_thread

    if auto_save_enabled:
        # Выключаем автосохранение
        auto_save_enabled = False
        if auto_save_thread:
            auto_save_thread.join(timeout=2)
            auto_save_thread = None
        dpg.set_value("auto_save_status", "Auto-save: OFF")
        print("🛑 Auto-save disabled")
    else:
        # Включаем автосохранение
        auto_save_enabled = True
        auto_save_thread = threading.Thread(target=auto_save_worker, daemon=True)
        auto_save_thread.start()
        dpg.set_value("auto_save_status", "Auto-save: ON")
        print("✅ Auto-save enabled")


def exit_app():
    """Выход из приложения"""
    print("Exiting application...")
    save_layout()
    dpg.stop_dearpygui()


def setup_initial_layout():
    """Настраивает начальный layout"""
    # Инициализируем позиции окон
    global last_window_positions
    last_window_positions = get_window_positions()

    # Если файл существует, layout уже загружен через load_init_file=True
    if not os.path.exists(LAYOUT_FILE):
        # Устанавливаем начальные позиции
        dpg.set_item_pos("tools", [0, 0])
        dpg.set_item_width("tools", 200)
        dpg.set_item_height("tools", 500)

        dpg.set_item_pos("workspace", [210, 0])
        dpg.set_item_width("workspace", 400)
        dpg.set_item_height("workspace", 500)

        dpg.set_item_pos("properties", [620, 0])
        dpg.set_item_width("properties", 200)
        dpg.set_item_height("properties", 500)

        # Сохраняем начальный layout
        save_layout()
        print("✅ Created initial layout")
    else:
        print("✅ Layout loaded automatically")


# Создаем viewport
dpg.create_viewport(
    title='Docking with Auto-save',
    width=850,
    height=600
)

# Запускаем
dpg.setup_dearpygui()
dpg.show_viewport()

# Настраиваем layout через небольшой таймаут
dpg.set_frame_callback(5, setup_initial_layout)

print("Starting application...")

# Запускаем автосохранение по умолчанию
toggle_auto_save()

# Основной цикл
try:
    dpg.start_dearpygui()
except KeyboardInterrupt:
    print("Interrupted by user")
except Exception as e:
    print(f"Error: {e}")
finally:
    # Отключаем автосохранение перед выходом
    auto_save_enabled = False
    if auto_save_thread:
        auto_save_thread.join(timeout=1)

    # Сохраняем перед выходом
    save_layout()
    print("✅ Final save completed")

    dpg.destroy_context()