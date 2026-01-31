import dearpygui.dearpygui as dpg
import Editor.core.modules.constants as const


def theme_editor():
    with dpg.theme() as child_theme:
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (245, 45, 45, 255))
    return child_theme

def theme_detector():
    with dpg.theme() as child_theme:
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (45, 245, 45, 255))
    return child_theme

def theme2():
    with dpg.theme() as textbox_theme:
        with dpg.theme_component(dpg.mvInputText):
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 6)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 0, 0, 0))
    return textbox_theme
