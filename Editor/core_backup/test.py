# Тестовый код, который нужно запустить отдельно
import dearpygui.dearpygui as dpg
import cv2
import numpy as np

dpg.create_context()

# Загружаем тестовое изображение
image = np.ones((400, 600, 3), dtype=np.uint8) * 255  # Белый фон
cv2.putText(image, 'TEST IMAGE', (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 3)
image_rgba = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
image_data = (image_rgba.astype(np.float32) / 255.0).flatten()

# Простое окно без ограничений
with dpg.window(label="Тестовое окно", width=800, height=600, pos=(100, 100)):
    with dpg.drawlist(width=600, height=400):
        with dpg.texture_registry():
            tex = dpg.add_raw_texture(600, 400, image_data, format=dpg.mvFormat_Float_rgba)
        dpg.draw_image(tex, pmin=(0,0), pmax=(600,400), uv_min=(0,0), uv_max=(1,1))
    dpg.add_text("Если вы это видите - DPG работает")

dpg.create_viewport(title='Test', width=1200, height=800)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()