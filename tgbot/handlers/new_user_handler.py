from aiogram import Router, types, F,Bot
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.config import whitelist, newusermanager,handlermanager

router = Router()


def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="new:menu:get")]
    ])

@router.callback_query(F.data == "new:menu:get")
async def new_menu_get(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🤖 Добро пожаловать!\n"
        "Выберите действие в меню ниже:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔍 Мой ID", callback_data="new:menu:id")],
                [InlineKeyboardButton(text="Запросить/Проверить доступ", callback_data="new:menu:getinvite")],
                [InlineKeyboardButton(text="❓ Помощь", callback_data="new:menu:help")]
            ]
        )
    )
    await callback.answer()  # Не забудь!

# ========== КОМАНДА /start ==========
@router.message(Command("start"))
async def start_command(message: types.Message):  # Исправлено: message, а не callback

    user_id = message.from_user.id
    if whitelist.check_user(user_id):
        await message.answer(  # Исправлено: message.answer
            "✅ У вас уже есть доступ!\n",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Войти", callback_data="menu:get")]
                ]
            )
        )
        await message.delete()
    else:
        await message.answer("Добро пожаловать в CamParking!\n"
                             "для начала работы вам необходимо запросить доступ"
                             ,callback_data="new:menu:get")


# ========== ОБРАБОТЧИКИ КНОПОК ==========
@router.callback_query(F.data == "new:menu:getinvite")
async def new_menu_getinvite(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not whitelist.check_user(user_id):
        user_username = callback.from_user.username or ""
        user_firstname = callback.from_user.first_name or ""
        user_lastname = callback.from_user.last_name or ""

        if newusermanager.approve_user(user_id, user_username, user_firstname, user_lastname):
            await callback.message.edit_text(
                f"ID: `{user_id}`\n"
                f"Вы запросили доступ. Ожидайте подтверждения.\n",
                callback_data="new:menu:get",
                parse_mode="Markdown"
            )
        else:
            await callback.message.edit_text(
                "⛔ Вы уже запрашивали доступ ранее.\n",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="◀️ Назад", callback_data="new:menu:get")]]))

    else:
        await callback.message.edit_text(
            "✅ У вас уже есть доступ!\n",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Войти", callback_data="menu:get")]
            ])
        )
    await callback.answer()

@router.callback_query(F.data == "new:menu:id")
async def show_my_id(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    has_access = whitelist.check_user(user_id)

    await callback.message.edit_text(
        f"📋 Ваш профиль:\n\n"
        f"ID: {user_id}\n"
        f"Доступ: {'✅ разрешен' if has_access else '❌ запрещен'}\n",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="new:menu:get")]
        ])
    )
    await callback.answer()


@router.callback_query(F.data == "new:menu:help")
async def show_help(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ **Помощь:**\n\n"
        "• Бот работает по вайтлисту\n"
        "• Только добавленные пользователи имеют доступ\n"
        "• Админ может добавлять новых пользователей\n"
        "• У вас пока нет прав.\n\n"
        "Команды:\n"
        "/start - главное меню\n",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="new:menu:get")]
        ]),
        parse_mode="Markdown"
    )
    await callback.answer()


#####Технический