import dearpygui.dearpygui as dpg
import Editor.core_backup.modules.constants as const

COLORS = {
    # Фоны с разными уровнями глубины
    'bg_deep': (22, 22, 24, 255),  # Глубокий тёмный фон
    'bg_dark': (32, 32, 34, 255),  # Тёмный фон
    'bg_medium': (42, 42, 44, 255),  # Средний фон
    'bg_light': (52, 52, 54, 255),  # Светлый фон
    'bg_highlight': (62, 62, 64, 255),  # Подсветка

    # Акценты
    'accent_steel': (100, 100, 110, 255),  # Стальной акцент
    'accent_silver': (140, 140, 150, 255),  # Серебряный акцент
    'accent_graphite': (80, 80, 90, 255),  # Графитовый акцент

    # Текст
    'text_white': (245, 245, 247, 255),  # Белый текст
    'text_gray': (180, 180, 185, 255),  # Серый текст
    'text_dim': (120, 120, 125, 255),  # Тусклый текст

    # Эффекты
    'border_dark': (60, 60, 65, 255),  # Тёмная граница
    'border_light': (90, 90, 95, 255),  # Светлая граница
    'shadow_soft': (0, 0, 0, 40),  # Мягкая тень
    'glow': (255, 255, 255, 20),  # Свечение
}

def theme_editor():
    """Создание стильного серого темы с современными эффектами"""

    # Профессиональная серая палитра


    with dpg.theme() as child_theme:

        # === ОСНОВНОЙ ДИЗАЙН ДЛЯ ОКНА ===
        with dpg.theme_component(dpg.mvChildWindow):
            # Градиентный фон с глубиной
            #dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (245, 45, 45, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, COLORS['bg_deep'])

            # Стильные скруглённые углы
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 5)

            # Утончённая граница
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_color(dpg.mvThemeCol_Border, COLORS['border_dark'])

            # Внутренние отступы для воздушности
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 20, 20)

            # Эффект приподнятости через тень (если поддерживается)

        # === ДОПОЛНИТЕЛЬНО: СТИЛЬ ДЛЯ ЗАГОЛОВКОВ ===
        with dpg.theme_component(dpg.mvText):
            dpg.add_theme_color(dpg.mvThemeCol_Text, COLORS['text_white'])

        # === ДОПОЛНИТЕЛЬНО: СТИЛЬ ДЛЯ ПОЛЕЙ ВВОДА ===
        with dpg.theme_component(dpg.mvInputText):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, COLORS['bg_medium'])
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, COLORS['bg_light'])
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, COLORS['bg_highlight'])
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_color(dpg.mvThemeCol_Border, COLORS['border_light'])

        # === ДОПОЛНИТЕЛЬНО: СТИЛЬ ДЛЯ СПИСКОВ ===


        # === ДОПОЛНИТЕЛЬНО: СТИЛЬ ДЛЯ ПОЛОС ПРОКРУТКИ ===


    return child_theme

def theme_detector():
    with dpg.theme() as child_theme:
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (45, 245, 45, 255))
    return child_theme

def status_bar():
    with dpg.theme() as theme:
        with dpg.theme_component(dpg.mvAll):
            # Градиентный фон с глубиной
            # dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (245, 45, 45, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, COLORS['bg_deep'])

            # Стильные скруглённые углы
            #dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 5)

            # Утончённая граница
            #dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            #dpg.add_theme_color(dpg.mvThemeCol_Border, COLORS['border_dark'])

            # Внутренние отступы для воздушности
            #dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 20, 20)

            # Эффект приподнятости через тень (если поддерживается)
    return theme
