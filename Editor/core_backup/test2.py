import dearpygui.dearpygui as dpg

dpg.create_context()

# == 1. Включаем экспериментальный докинг ==
dpg.configure_app(docking=True, docking_space=True, docking_shift_only=False)
dpg.configure_app(init_file="docking_layout.ini")

# == 2. Расширенная стилизация ==
# Цветовая палитра (современная темная тема с акцентами)
COLORS = {
    "bg_dark": (18, 18, 24, 255),
    "bg_panel": (30, 32, 40, 255),
    "bg_panel_light": (40, 42, 54, 255),
    "accent_primary": (100, 149, 237, 255),
    "accent_secondary": (147, 112, 219, 255),
    "accent_success": (46, 204, 113, 255),
    "accent_warning": (241, 196, 15, 255),
    "accent_danger": (231, 76, 60, 255),
    "text_primary": (220, 220, 220, 255),
    "text_secondary": (150, 152, 160, 255),
    "border": (60, 63, 80, 255),
    "border_light": (80, 85, 105, 255),
}

# Создаем главную тему
with dpg.theme(tag="__global_theme"):
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, COLORS["bg_dark"])
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, COLORS["bg_panel"])
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, COLORS["bg_panel_light"])
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (50, 52, 68, 255))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (60, 62, 78, 255))
        dpg.add_theme_color(dpg.mvThemeCol_TitleBg, COLORS["bg_panel"])
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, COLORS["accent_primary"])
        dpg.add_theme_color(dpg.mvThemeCol_CheckMark, COLORS["accent_primary"])
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, COLORS["accent_primary"])
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, COLORS["accent_secondary"])
        dpg.add_theme_color(dpg.mvThemeCol_Button, (60, 63, 80, 255))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (80, 85, 105, 255))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (100, 105, 125, 255))
        dpg.add_theme_color(dpg.mvThemeCol_Header, COLORS["accent_primary"])
        dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (120, 169, 255, 255))
        dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (140, 189, 255, 255))
        dpg.add_theme_color(dpg.mvThemeCol_Separator, COLORS["border"])
        dpg.add_theme_color(dpg.mvThemeCol_SeparatorHovered, COLORS["accent_primary"])
        dpg.add_theme_color(dpg.mvThemeCol_SeparatorActive, COLORS["accent_secondary"])
        dpg.add_theme_color(dpg.mvThemeCol_ResizeGrip, (100, 100, 100, 100))
        dpg.add_theme_color(dpg.mvThemeCol_ResizeGripHovered, COLORS["accent_primary"])
        dpg.add_theme_color(dpg.mvThemeCol_ResizeGripActive, COLORS["accent_secondary"])
        dpg.add_theme_color(dpg.mvThemeCol_Text, COLORS["text_primary"])
        dpg.add_theme_color(dpg.mvThemeCol_TextSelectedBg, COLORS["accent_primary"])
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
        dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 6)
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 10)
        dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8)
        dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 8)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 6)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 10, 8)
        dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 6, 6)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 15, 15)
        dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 1)
        dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
        dpg.add_theme_style(dpg.mvStyleVar_PopupBorderSize, 1)
        dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)

# Специальная тема для кнопок с акцентом
with dpg.theme(tag="accent_button_theme"):
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button, COLORS["accent_primary"])
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (120, 169, 255, 255))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (140, 189, 255, 255))
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 12, 8)

# Тема для панелей с заголовком
with dpg.theme(tag="panel_theme"):
    with dpg.theme_component(dpg.mvChildWindow):
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, COLORS["bg_panel"])
        dpg.add_theme_color(dpg.mvThemeCol_Border, COLORS["border_light"])
        dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 12, 12)

# Тема для разделителей
with dpg.theme(tag="separator_theme"):
    with dpg.theme_component(dpg.mvSeparator):
        dpg.add_theme_color(dpg.mvThemeCol_Separator, COLORS["accent_secondary"])
        dpg.add_theme_style(dpg.mvStyleVar_SeparatorTextAlign, 0.5)
        dpg.add_theme_style(dpg.mvStyleVar_SeparatorTextPadding, 0, 5)

# == 3. Создаем viewport с улучшенным заголовком ==
dpg.create_viewport(
    title='✨ Advanced Docking Editor | Dark Theme v1.0',
    width=1400,
    height=850,
    small_icon="",
    large_icon=""
)
dpg.set_viewport_resizable(True)

# == 4. Стилизация разделителей докинга (если доступно) ==
try:
    with dpg.theme() as docking_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_DockingSeparatorSize, 4.0)
            dpg.add_theme_color(dpg.mvThemeCol_DockingPreview, COLORS["accent_primary"])
            dpg.add_theme_color(dpg.mvThemeCol_DockingEmptyBg, COLORS["bg_panel_light"])
except:
    pass

# == 5. Создаем окна с богатой стилизацией ==
# Панель инструментов (слева)
with dpg.window(
        label="🛠️ Tools",
        tag="tools_window",
        no_title_bar=True,
        no_move=False,
        width=250,
        height=400
):
    # Заголовок панели
    with dpg.group(horizontal=True):
        dpg.add_spacer(width=5)
        dpg.add_text("🔧 TOOLSET", color=COLORS["accent_primary"])

    dpg.add_separator()
    dpg.add_spacer(height=5)

    # Группа основных инструментов
    dpg.add_text("Main Tools", color=COLORS["text_secondary"])
    dpg.add_button(label="  ✏️  Select Tool", width=220, height=40)
    dpg.add_button(label="  🖌️  Brush Tool", width=220, height=40)
    dpg.add_button(label="  🅰️  Text Tool", width=220, height=40)
    dpg.add_button(label="  ⬡  Shape Tool", width=220, height=40)

    dpg.add_spacer(height=15)
    dpg.add_separator()
    dpg.add_spacer(height=10)

    # Группа настроек
    dpg.add_text("Tool Properties", color=COLORS["text_secondary"])
    dpg.add_slider_float(label="Size", default_value=15.0, min_value=1.0, max_value=100.0, width=220)
    dpg.add_slider_float(label="Opacity", default_value=1.0, min_value=0.0, max_value=1.0, width=220)
    dpg.add_slider_float(label="Hardness", default_value=0.5, min_value=0.0, max_value=1.0, width=220)

    dpg.add_spacer(height=10)
    dpg.add_color_edit((255, 255, 255), label="Color", width=220)

    dpg.add_spacer(height=15)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Save Preset", width=105)
        dpg.add_button(label="Load Preset", width=105)

# Центральная рабочая область
with dpg.window(
        label="🎨 Workspace",
        tag="workspace_window",
        no_title_bar=True,
        no_move=False
):
    # Декоративный верхний бар
    with dpg.group(horizontal=True):
        dpg.add_button(label="🞂", width=30, height=30)
        dpg.add_button(label="⬤", width=30, height=30)
        dpg.add_button(label="✕", width=30, height=30)
        dpg.add_spacer(width=10)
        dpg.add_text("ACTIVE DOCUMENT: Untitled.psd", color=COLORS["text_secondary"])
        dpg.add_spacer()
        dpg.add_button(label="💾 Save", width=80)
        dpg.add_button(label="📤 Export", width=80)

    dpg.add_separator()
    dpg.add_spacer(height=20)

    # Основное содержимое
    with dpg.group(horizontal=True, width=-1):
        dpg.add_spacer(width=50)
        with dpg.child_window(width=600, height=400, border=True):
            dpg.add_text("🖼️  Canvas Preview", color=COLORS["accent_primary"])
            dpg.add_separator()
            dpg.add_spacer(height=150)
            with dpg.group(horizontal=True):
                dpg.add_spacer()
                dpg.add_text("Your Creative Workspace", color=COLORS["text_secondary"])
                dpg.add_spacer()
            dpg.add_spacer(height=150)
            with dpg.group(horizontal=True):
                dpg.add_spacer()
                dpg.add_button(label="Create New Canvas", width=180, height=40)
                dpg.add_spacer()

        dpg.add_spacer(width=50)

    dpg.add_spacer(height=20)
    dpg.add_separator()

    # Статус бар
    with dpg.group(horizontal=True):
        dpg.add_text("Status:", color=COLORS["text_secondary"])
        dpg.add_text("  Ready", color=COLORS["accent_success"])
        dpg.add_spacer()
        dpg.add_text("Zoom: 100%", color=COLORS["text_secondary"])
        dpg.add_spacer(width=20)
        dpg.add_text("Position: X:0 Y:0", color=COLORS["text_secondary"])

# Панель слоев (справа)
with dpg.window(
        label="📑 Layers",
        tag="layers_window",
        no_title_bar=True,
        no_move=False,
        width=280,
        height=500
):
    # Заголовок с элементами управления
    with dpg.group(horizontal=True):
        dpg.add_text("LAYER STACK", color=COLORS["accent_primary"])
        dpg.add_spacer()
        dpg.add_button(label="+", width=30)
        dpg.add_button(label="−", width=30)

    dpg.add_separator()
    dpg.add_spacer(height=10)

    # Список слоев с улучшенным видом
    layers_data = [
        {"name": "Background", "visible": True, "locked": False, "color": (66, 135, 245)},
        {"name": "Foreground", "visible": True, "locked": True, "color": (245, 66, 135)},
        {"name": "Text Layer", "visible": True, "locked": False, "color": (135, 245, 66)},
        {"name": "Effects", "visible": False, "locked": False, "color": (245, 135, 66)},
        {"name": "Adjustments", "visible": True, "locked": False, "color": (135, 66, 245)},
    ]

    for i, layer in enumerate(layers_data):
        with dpg.child_window(height=60, border=True):
            with dpg.group(horizontal=True):
                # Цветной индикатор
                with dpg.drawlist(width=20, height=45):
                    dpg.draw_rectangle((0, 0), (15, 45), fill=layer["color"], color=layer["color"])

                dpg.add_spacer(width=5)

                # Информация о слое
                with dpg.group():
                    dpg.add_text(layer["name"], color=COLORS["text_primary"])
                    dpg.add_text(f"Layer {i + 1}", color=COLORS["text_secondary"])

                dpg.add_spacer()

                # Элементы управления
                visibility_icon = "👁️" if layer["visible"] else "👁️‍🗨️"
                lock_icon = "🔓" if not layer["locked"] else "🔒"

                dpg.add_button(label=visibility_icon, width=40)
                dpg.add_button(label=lock_icon, width=40)
                dpg.add_button(label="⋮", width=30)

        dpg.add_spacer(height=5)

    dpg.add_spacer(height=15)
    dpg.add_separator()
    dpg.add_spacer(height=10)

    # Группа действий со слоями
    dpg.add_text("Layer Actions", color=COLORS["text_secondary"])
    with dpg.group(horizontal=True):
        dpg.add_button(label="Merge Down", width=130)
        dpg.add_button(label="Flatten", width=130)

    with dpg.group(horizontal=True):
        dpg.add_button(label="Add Mask", width=130)
        dpg.add_button(label="Apply Filter", width=130)

    dpg.add_spacer(height=10)
    dpg.add_slider_float(label = "Opacity", default_value=100.0, min_value=0.0, max_value=100.0, format="%.0f%%")

# == 6. Применяем темы ==
dpg.bind_theme("__global_theme")
dpg.bind_item_theme("tools_window", "panel_theme")
dpg.bind_item_theme("layers_window", "panel_theme")

# Применяем акцентную тему к некоторым кнопкам
accent_buttons = ["Create New Canvas", "Save", "Export"]
for item in dpg.get_all_items():
    try:
        label = dpg.get_item_label(item)
        if label in accent_buttons:
            dpg.bind_item_theme(item, "accent_button_theme")
    except:
        pass


# == 7. Заглушка для кнопок с улучшенным выводом ==
def button_callback(sender, app_data):
    label = dpg.get_item_label(sender)
    print(f"🖱️  Button clicked: {label}")
    # Визуальная обратная связь
    original_color = dpg.get_item_configuration(sender)["colors"][0] if "colors" in dpg.get_item_configuration(
        sender) else None
    if original_color:
        dpg.configure_item(sender, color=(200, 200, 255, 255))
        dpg.split_frame(delay=5)
        dpg.configure_item(sender, color=original_color)


for item in dpg.get_all_items():
    if "Button" in str(dpg.get_item_type(item)):
        dpg.set_item_callback(item, button_callback)


# == 8. Функция для попытки настроить layout после запуска ==
def setup_layout():
    try:
        viewport_width = dpg.get_viewport_width()
        viewport_height = dpg.get_viewport_height()

        # Устанавливаем начальные позиции окон
        dpg.set_item_pos("tools_window", [10, 30])
        dpg.set_item_width("tools_window", 250)
        dpg.set_item_height("tools_window", viewport_height - 60)

        dpg.set_item_pos("layers_window", [viewport_width - 290, 30])
        dpg.set_item_width("layers_window", 280)
        dpg.set_item_height("layers_window", viewport_height - 60)

        dpg.set_item_pos("workspace_window", [270, 30])
        dpg.set_item_width("workspace_window", viewport_width - 570)
        dpg.set_item_height("workspace_window", viewport_height - 60)

        print("🎨 Layout configured successfully")
    except Exception as e:
        print(f"⚠️  Layout setup failed: {e}")


# == 4. Полная стилизация системы докинга ==
try:
    with dpg.theme(tag="docking_theme"):
        with dpg.theme_component(dpg.mvAll):
            # === ОСНОВНЫЕ ЦВЕТА ДОКИНГА ===

            # Цвет квадратика предпросмотра (синего) при закреплении
            # Варианты: accent_primary(синий), accent_secondary(фиолетовый),
            # accent_success(зеленый), accent_warning(желтый), accent_danger(красный)
            dpg.add_theme_color(dpg.mvThemeCol_DockingPreview,
                                COLORS["accent_primary"])  # Основной цвет превью

            # Цвет фона пустой области для докинга
            dpg.add_theme_color(dpg.mvThemeCol_DockingEmptyBg,
                                (40, 45, 60, 180))  # Темный полупрозрачный фон

            # === РАЗМЕРЫ И СТИЛИ ===

            # Толщина разделителя между закрепленными окнами (в пикселях)
            dpg.add_theme_style(dpg.mvStyleVar_DockingSeparatorSize, 6.0)

            # === ЭКСПЕРИМЕНТАЛЬНЫЕ НАСТРОЙКИ (могут не поддерживаться) ===
            try:
                # Попытка установить закругление углов разделителя
                dpg.add_theme_style(dpg.mvStyleVar_DockingSeparatorRounding, 3.0)
            except:
                pass  # Игнорируем если не поддерживается

            try:
                # Попытка установить отступ разделителя
                dpg.add_theme_style(dpg.mvStyleVar_DockingSeparatorPadding, 2.0, 2.0)
            except:
                pass

    # Применяем созданную тему докинга
    dpg.bind_theme("docking_theme")
    print("✅ Docking styling applied successfully")

except Exception as e:
    print(f"⚠️  Partial or no docking styling available: {e}")
    # Резервный минимальный стиль, если основные настройки не работают
    try:
        with dpg.theme(tag="docking_theme_fallback"):
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_DockingSeparatorSize, 4.0)
        dpg.bind_theme("docking_theme_fallback")
        print("✅ Applied fallback docking style")
    except:
        print("❌ Docking styling completely unavailable in this version")

# == 9. Запускаем приложение ==
dpg.setup_dearpygui()
dpg.show_viewport()

# Пытаемся настроить layout через небольшую задержку
dpg.set_frame_callback(5, setup_layout)

dpg.start_dearpygui()
dpg.destroy_context()