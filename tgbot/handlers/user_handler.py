from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.config import whitelist, newusermanager
import handlers.admin_handler as ah
from aiogram import Bot

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
async def goadmin_command(message: types.Message, bot: Bot):
    # Удаляем команду /goadmin
    await message.delete()

    # Пытаемся удалить предыдущее сообщение бота
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id - 1  # Предыдущее сообщение
    )
    # Отправляем новое меню
    await message.answer(
        "Админ панель",
        reply_markup=ah.get_admin_main_menu(message.from_user.id)
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
    first_name = callback.from_user.first_name
    if not whitelist.check_user(user_id):
        await callback.message.edit_text("⛔ У вас нет доступа к боту")
        return

    await callback.message.edit_text(
    f"🤖 Добро пожаловать, {first_name}!\n"
        "Выберите действие в меню ниже:",
        reply_markup=get_main_menu()
    )
    await callback.answer()

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