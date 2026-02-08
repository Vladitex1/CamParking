import dearpygui.dearpygui as dpg

dpg.create_context()
dpg.configure_app(docking=True)

with dpg.window(tag="main", no_title_bar=True): pass
with dpg.window(label="Left", width=150): dpg.add_text("Left panel")
with dpg.window(label="Center"): dpg.add_text("Center")
with dpg.window(label="Right", width=150): dpg.add_text("Right panel")

dpg.create_viewport()
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()