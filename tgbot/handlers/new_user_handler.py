from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.config import whitelist, newusermanager

router = Router()


def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="get_new_menu")]
    ])

@router.callback_query(F.data == "get_new_menu")
async def get_new_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🤖 Добро пожаловать!\n"
        "Выберите действие в меню ниже:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔍 Мой ID", callback_data="menu_new_user_myid")],
                [InlineKeyboardButton(text="Запросить доступ", callback_data="get_invite")],
                [InlineKeyboardButton(text="❓ Помощь", callback_data="menu_new_user_help")]
            ]
        )
    )
    await callback.answer()  # Не забудь!


# ========== КОМАНДА /start ==========
@router.message(Command("start"))
async def start_command(message: types.Message):  # Исправлено: message, а не callback
    user_id = message.from_user.id
    await message.delete()
    if whitelist.check_user(user_id):
        await message.answer(  # Исправлено: message.answer
            "✅ У вас уже есть доступ!\n",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Войти", callback_data="back_to_menu")]
                ]
            )
        )
    else:
        await message.answer("У вас недостаточно прав.\n",reply_markup=get_back_keyboard())


# ========== ОБРАБОТЧИКИ КНОПОК ==========
@router.callback_query(F.data == "get_invite")
async def get_invite_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if whitelist.check_user(user_id):
        # Если пользователь уже в вайтлисте
        await callback.message.answer(
            "✅ У вас уже есть доступ!\n",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Войти", callback_data="back_to_menu")]
            ])
        )
    else:
        user_id = callback.from_user.id
        user_username = callback.from_user.username or ""
        user_firstname = callback.from_user.first_name or ""
        user_lastname = callback.from_user.last_name or ""

        if newusermanager.approve_user(user_id, user_username, user_firstname, user_lastname):
            await callback.message.edit_text(
                f"ID: `{user_id}`\n"
                f"Вы запросили доступ. Ожидайте подтверждения.\n",
                reply_markup=get_new_user_menu(),
                parse_mode="Markdown"
            )
        else:
            await callback.answer("⛔ Вы уже запрашивали доступ ранее.")
    await callback.answer()


@router.callback_query(F.data == "menu_new_user_myid")
async def show_my_id(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    has_access = whitelist.check_user(user_id)

    await callback.message.edit_text(
        f"📋 Ваш профиль:\n\n"
        f"ID: {user_id}\n"
        f"Доступ: {'✅ разрешен' if has_access else '❌ запрещен'}\n",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="get_new_menu")]
        ])
    )
    await callback.answer()


@router.callback_query(F.data == "menu_new_user_help")
async def show_help(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ **Помощь:**\n\n"
        "• Бот работает по вайтлисту\n"
        "• Только добавленные пользователи имеют доступ\n"
        "• Админ может добавлять новых пользователей\n"
        "• У вас пока нет прав.\n\n"
        "Команды:\n"
        "/start - главное меню\n",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


#####Технический