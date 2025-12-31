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
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="menu:get")]
    ])

def get_back_new_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="new:menu:get")]
    ])

# ========== КОМАНДЫ ==========
@router.message(Command("goadmin"))
async def goadmin_command(message: types.Message,bot: Bot):
    user_id = message.from_user.id
    await message.delete()
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id-1,  # Предыдущее сообщение
        request_timeout= 5
    )

    if not whitelist.check_user(user_id):
        await message.answer("⛔ У вас нет доступа к боту\n")
    else:
        if whitelist.check_permission(user_id) == 2:
            # Создаем клавиатуру с кнопкой-триггером
            await message.answer(
                "🤖 Переход в админ-панель\n",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="Перейти в меню",
                    callback_data="admin:menu:get")]]))
        else:
            text = f"Недостаточно прав"
            if whitelist.check_permission(user_id) == 0:
                await message.answer(
                    text,
                reply_markup=get_back_new_keyboard())
            else:
                await message.answer(
                    text,
                reply_markup=get_back_keyboard())

# ========== ОБРАБОТЧИКИ КНОПОК ==========
@router.callback_query(F.data == "menu:get")
async def user_menu(callback: types.CallbackQuery):
    if whitelist.valid_user_permissions(callback.from_user.id, 1):
        # Удаляем сообщение с кнопкой через 5 секунд
        # Отправляем новое сообщение
        await callback.message.edit_text(
            "Выберите действие в меню ниже:\n",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔍 Мой ID", callback_data="menu:id")],
                [InlineKeyboardButton(text="❓ Помощь", callback_data="menu:help")]
            ])
        )
    else:
        get_back_new_keyboard()


@router.callback_query(F.data == "menu:id")
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


@router.callback_query(F.data == "menu:help")
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
