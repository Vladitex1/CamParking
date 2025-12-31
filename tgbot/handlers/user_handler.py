from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.config import whitelist, newusermanager,handlermanager

from aiogram import Bot

###Добавить проверку на уровень пользователя
###у нового пользователя иногда меню не убирается

import handlers.new_user_handler as nuh
import handlers.admin_handler as ah

router = Router()


# ========== КЛАВИАТУРЫ ==========

def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]
    ])

def get_back_new_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="get_new_menu")]
    ])

# ========== КОМАНДЫ ==========
@router.message(Command("goadmin")) #############ЕСЛИ СКАКАТЬ МЕЖДУ СООБЩЕНИЯМИ, ТО УДАЛЯТЬ НЕ НАДО!!!!!!!!!
async def goadmin_command(message: types.Message, bot: Bot):
    await handlermanager.del_messages(0, bot=bot, message=message)
    user_id = message.from_user.id
    if whitelist.valid_user_permissions(message.from_user.id,2):
        await message.edit_text(
            f"🤖 Добро пожаловать, {message.from_user.first_name}!\n"
            "Режим администрирования:",
            reply_markup=ah.get_admin_main_menu(user_id)
        )
    else:
        num = whitelist.check_permission(user_id)
        if num == 0:
            await message.answer(
            f"Недостаточно прав",
            reply_markup=get_back_new_keyboard())
        else:
            await message.answer(
            f"Недостаточно прав",
            reply_markup=get_back_keyboard())

# ========== ОБРАБОТЧИКИ КНОПОК ==========
@router.callback_query(F.data == "menu_myid")
async def show_my_id(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    level = whitelist.check_permission(user_id)

    await callback.message.edit_text(
        f"📋 Ваш профиль:\n\n"
        f"ID: `{user_id}`\n"
        f"Доступ к боту: {'разрешен ✅' if whitelist.check_user(user_id) else 'запрещен ❌'}\n"
        f"Уровень учетной записи: `{whitelist.user_lvl[level]}`\n",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_callback(callback: types.CallbackQuery, bot: Bot):
    if whitelist.valid_user_permissions(callback.from_user.id, 1):
        # Удаляем сообщение с кнопкой через 5 секунд
        #await callback.message.delete() #########################################################не нравится что исчезает.
        # Отправляем новое сообщение
        await callback.message.edit_text(
            "Выберите действие в меню ниже:\n",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔍 Мой ID", callback_data="menu_myid")],
                [InlineKeyboardButton(text="❓ Помощь", callback_data="menu_help")]
            ])
        )
    else:
        get_back_new_keyboard()
    #await callback.answer()  # Не забудьте это!



@router.callback_query(F.data == "menu_help")
async def show_help(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ **Помощь:**\n\n"
        "• Бот работает по вайтлисту\n"
        "• Только одобренные пользователи имеют доступ к боту.\n\n"
        "Связь с разработчиком: @gsoalnfeea",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()
