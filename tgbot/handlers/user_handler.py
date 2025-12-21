from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.config import whitelist, newusermanager
import handlers.admin_handler as ah

router = Router()


# ========== КЛАВИАТУРЫ ==========
def get_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Мой ID", callback_data="menu_myid")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="menu_help")]
    ])

def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]
    ])


# ========== КОМАНДЫ ==========
@router.message(Command("goadmin"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    await message.answer(  # обычный пользователь
        "Админ панель",
        reply_markup=ah.get_back_admin_keyboard()
    )

@router.message(Command("logined_user"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    whitelist.load()

    if not whitelist.check_user(user_id):
        await message.answer("⛔ У вас нет доступа к боту\n")
    else:
        await message.answer( #обычный пользователь
            "🤖 Добро пожаловать!\n"
            "Выберите действие в меню ниже:",
            reply_markup=get_main_menu()
        )


# ========== ОБРАБОТЧИКИ КНОПОК ==========
@router.callback_query(F.data == "menu_myid")
async def show_my_id(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    level = whitelist.check_permission(user_id)

    await callback.message.edit_text(
        f"📋 Ваш профиль:\n\n"
        f"ID: `{user_id}`\n"
        f"Доступ: {'✅ разрешен' if whitelist.check_user(user_id) else '❌ запрещен'}\n"
        f"Уровень учетной записи: `{whitelist.user_lvl[level]}`\n",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if not whitelist.check_user(user_id):
        await callback.message.edit_text("⛔ У вас нет доступа к боту")
        return

    await callback.message.edit_text(
        "🤖 Добро пожаловать!\n"
        "Выберите действие в меню ниже:",
        reply_markup=get_main_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "menu_help")
async def show_help(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ **Помощь:**\n\n"
        "• Бот работает по вайтлисту\n"
        "• Только добавленные пользователи имеют доступ\n"
        "• Админ может добавлять новых пользователей\n\n"
        "Команды:\n"
        "/start - главное меню\n"
        "/adduser - добавить пользователя",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()