import dearpygui.dearpygui as dpg


class AsciiIcons:
    def __init__(self):
        dpg.create_context()
        dpg.create_viewport(title='ASCII Icons', width=400, height=350)

        with dpg.window(label="ASCII Иконки"):
            dpg.add_text("Геометрические фигуры:")

            dpg.add_text("Треугольник:")
            dpg.add_text("   /\\")
            dpg.add_text("  /  \\")
            dpg.add_text(" /____\\")

            dpg.add_text("Квадрат:")
            dpg.add_text("  _▶__")
            dpg.add_text(" |    |")
            dpg.add_text(" |____|")

            dpg.add_text("Инструменты:")
            dpg.add_text("✐ Карандаш | 📐 Треугольник | 📏 Линейка")
            dpg.add_text("(используйте текстовые обозначения)")

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()


AsciiIcons()