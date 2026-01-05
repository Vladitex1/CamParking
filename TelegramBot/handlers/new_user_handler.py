from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .config import whitelist, usermanager
import logging
from . import keyboards
logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "new:menu:get")
async def new_menu_get(callback: types.CallbackQuery):
    user_id = callback.message.from_user.id
    await callback.message.edit_text(
        "🤖 Добро пожаловать!\n"
        "Выберите действие в меню ниже:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔍 Мой ID", callback_data="new:menu:id")],
                [InlineKeyboardButton(text="📨 Запросить | Проверить доступ 🔄", callback_data="new:menu:getinvite")],
                [InlineKeyboardButton(text="❓ Помощь", callback_data="new:menu:help")]
            ]
        )
    )
    logger.info(f"Вызвано меню нового пользователя от {user_id}")
    await callback.answer()

# ========== ОБРАБОТЧИКИ КНОПОК ==========
@router.callback_query(F.data == "new:menu:getinvite")
async def new_menu_getinvite(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logger.info(f"Вызвано меню запроса доступа от пользователя {user_id}")
    try:
        if not whitelist.check_user(user_id):
            user_username = callback.from_user.username or ""
            user_firstname = callback.from_user.first_name or ""
            user_lastname = callback.from_user.last_name or ""

            if usermanager.approve_user(user_id, user_username, user_firstname, user_lastname):
                logger.info(f"✅ Новая заявка от {user_id}")
                await callback.message.edit_text(
                    f"ID: `{user_id}`\n"
                    f"Вы запросили доступ. Ожидайте подтверждения.\n",
                    callback_data="new:menu:get",
                    parse_mode="Markdown"
                )
            else:
                logger.info(f"⚠️ Повтор запроса от {user_id}")
                await callback.message.edit_text(
                    "⛔ Вы уже запрашивали доступ ранее.\n",
                    reply_markup=keyboards.keyboard(callback_1="new:menu:get"))

        else:
            logger.info(f"✅ Уже в вайтлисте {user_id}")
            await callback.message.edit_text(
                "✅ У вас уже есть доступ!\n",
                reply_markup=keyboards.keyboard(callback_1="user:menu:get")
            )
        await callback.answer()
    except Exception as e:
        logger.error(f"❌ Ошибка в getinvite у {user_id}: {e}")

@router.callback_query(F.data == "new:menu:id")
async def show_my_id(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    has_access = whitelist.check_user(user_id)

    await callback.message.edit_text(
        f"📋 Ваш профиль:\n\n"
        f"ID: {user_id}\n"
        f"Доступ: {'✅ разрешен' if has_access else '❌ запрещен'}\n",
        reply_markup=keyboards.keyboard(callback_1="new:menu:get")
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
        reply_markup=keyboards.keyboard(callback_1="new:menu:get"),
        parse_mode="Markdown"
    )
    await callback.answer()
