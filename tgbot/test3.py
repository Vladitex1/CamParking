from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio

# ========== НАСТРОЙКИ ==========
TOKEN = "8034081320:AAE6KBHZPeCXvu6QpiT1jDnwfty5hqvmBMg"  # <-- ВСТАВЬ СВОЙ ТОКЕН
ADMIN_ID = 1413700636  # Замени на свой ID

router = Router()

# ========== ВАЙТЛИСТ (простой список) ==========
WHITELIST = [ADMIN_ID]  # Начинаем со списка, где только админ


class AddUserState(StatesGroup):
    waiting_for_id = State()


# ========== КЛАВИАТУРЫ ==========
def get_main_menu() -> InlineKeyboardMarkup:
    """Главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Мой ID", callback_data="menu_myid")],
        [InlineKeyboardButton(text="➕ Добавить пользователя", callback_data="menu_adduser")],
        [InlineKeyboardButton(text="📋 Список пользователей", callback_data="menu_list")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="menu_help")]
    ])


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Кнопка Назад"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]
    ])


# ========== КОМАНДА /start ==========
@router.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id



    await message.answer(
        "🤖 Добро пожаловать!\n"
        "Выберите действие в меню ниже:",
        reply_markup=get_main_menu()
    )


# ========== ОБРАБОТЧИКИ КНОПОК ==========
@router.callback_query(F.data == "menu_myid")
async def show_my_id(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_text(
        f"📋 Ваш профиль:\n\n"
        f"ID: `{user_id}`\n"
        f"Доступ: {'✅ разрешен' if user_id in WHITELIST else '❌ запрещен'}",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "menu_adduser")
async def add_user_menu(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.message.edit_text(
            "⛔ Только администратор может добавлять пользователей",
            reply_markup=get_back_keyboard()
        )
    else:
        await callback.message.edit_text(
            "Введите ID пользователя для добавления в вайтлист:",
            reply_markup=get_back_keyboard()
        )
    await callback.answer()


@router.callback_query(F.data == "menu_list")
async def show_user_list(callback: types.CallbackQuery):
    if not WHITELIST:
        user_list = "Список пуст"
    else:
        user_list = "\n".join([f"• {uid}" for uid in WHITELIST])

    await callback.message.edit_text(
        f"📋 Пользователи в вайтлисте:\n\n{user_list}\n\n"
        f"Всего: {len(WHITELIST)} пользователей",
        reply_markup=get_back_keyboard()
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


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if user_id not in WHITELIST:
        await callback.message.edit_text("⛔ У вас нет доступа к боту")
        return

    await callback.message.edit_text(
        "🤖 Добро пожаловать!\n"
        "Выберите действие в меню ниже:",
        reply_markup=get_main_menu()
    )
    await callback.answer()


# ========== ОБРАБОТКА ВВОДА ID ДЛЯ ДОБАВЛЕНИЯ ==========
@router.message(F.from_user.id == ADMIN_ID)
async def handle_admin_input(message: types.Message):
    """Админ вводит ID пользователя"""
    try:
        user_id = int(message.text.strip())
        if user_id not in WHITELIST:
            WHITELIST.append(user_id)
            await message.answer(f"✅ Пользователь {user_id} добавлен")
        else:
            await message.answer(f"⚠️ Пользователь {user_id} уже в списке")
    except ValueError:
        await message.answer("❌ Введите корректный ID (только цифры)")


# ========== ЗАПУСК БОТА ==========
async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    print("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Замени ADMIN_ID на свой ID (узнать через @userinfobot)
    ADMIN_ID = 413700636 # <-- ЗАМЕНИ ЭТО ЧИСЛО!
    TOKEN = "8034081320:AAE6KBHZPeCXvu6QpiT1jDnwfty5hqvmBMg"  # <-- ВСТАВЬ СВОЙ ТОКЕН

    print("=" * 50)
    print(f"ADMIN_ID установлен: {ADMIN_ID}")
    print(f"Начальный вайтлист: {WHITELIST}")
    print("=" * 50)

    asyncio.run(main())