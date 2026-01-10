from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ========== АДМИНСКИЕ КЛАВИАТУРЫ ==========

def user_edit_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="↩️ Назад", callback_data="admin:menu:get"),
        InlineKeyboardButton(text="Выдать Админа", callback_data=f"edit_{user_id}_adm"),
        InlineKeyboardButton(text="Удалить", callback_data=f"edit_{user_id}_del"),
    ]])


# ========== КЛАВИАТУРЫ КАСТОМНЫЕ ==========


def keyboardH(text_1: str = "↩️ Назад", callback_1: str = "user:menu:get",
              text_2: str = "", callback_2: str = "",
              text_3: str = "", callback_3: str = "",
              text_4: str = "", callback_4: str = "") -> InlineKeyboardMarkup:
    buttons = []
    buttons.append(InlineKeyboardButton(text=text_1, callback_data=callback_1))
    if text_2:
        buttons.append(InlineKeyboardButton(text=text_2, callback_data=callback_2))
    if text_3:
        buttons.append(InlineKeyboardButton(text=text_3, callback_data=callback_3))
    if text_4:
        buttons.append(InlineKeyboardButton(text=text_4, callback_data=callback_4))

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def keyboardV(text_1: str = "↩️ Назад", callback_1: str = "user:menu:get",
              text_2: str = "", callback_2: str = "",
              text_3: str = "", callback_3: str = "",
              text_4: str = "", callback_4: str = "") -> InlineKeyboardMarkup:
    keyboard = []

    # Каждая кнопка на отдельной строке
    if text_1:
        keyboard.append([InlineKeyboardButton(text=text_1, callback_data=callback_1)])
    if text_2:
        keyboard.append([InlineKeyboardButton(text=text_2, callback_data=callback_2)])
    if text_3:
        keyboard.append([InlineKeyboardButton(text=text_3, callback_data=callback_3)])
    if text_4:
        keyboard.append([InlineKeyboardButton(text=text_4, callback_data=callback_4)])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
