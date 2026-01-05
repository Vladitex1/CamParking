from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import asyncio
from TelegramBot.handlers.config import whitelist
from TelegramBot.handlers import keyboards
import TelegramBot.detector as detector


router = Router()
logger = logging.getLogger(__name__)


# ========== ОБРАБОТЧИКИ КНОПОК ==========
@router.callback_query(F.data == "user:menu:get")
async def user_menu(callback: types.CallbackQuery):
    """Меню пользователя с логированием"""

    user_id = callback.from_user.id
    logger.debug(f"Обработка user:menu:get для user_id={user_id}")

    try:
        if whitelist.valid_user_permissions(user_id, 1):
            logger.info(f"Показано меню пользователя для user_id={user_id}")
            await callback.message.edit_text(
                "Выберите действие в меню ниже:\n",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🅿️ Свободные места", callback_data="user:parking:get")],
                    [InlineKeyboardButton(text="🔍 Мой ID", callback_data="user:menu:id")],
                    [InlineKeyboardButton(text="❓ Помощь", callback_data="user:menu:help")]
                ])
            )
        else:
            logger.warning(f"Нет прав для меню пользователя: user_id={user_id}")
            await callback.message.edit_text(
                "⛔ У вас нет доступа к этому меню",
                reply_markup=keyboards.keyboard(callback_1="new:menu:get")
            )
        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка в user_menu для user_id={user_id}: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)

 # ================= Работа с машинами функционал ================

@router.callback_query(F.data == "user:parking:get")##запрос свободных мест
async def get_parking(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logger.info(f"запрос парковочных мест user_id={user_id}")
    try:

        #🅿️🟢🔴
        occupied,free, = detector.check_auto(save="Отладка1.mask", processed_image ="test3.jpg",config_name="conf2")
        await callback.answer()
        freetext = f"\n{"=" * 8} Свободные места: {"=" * 8}\n"
        occupiedtext = f"\n{"=" * 10} Занятые места: {"=" * 10}\n"
        freemax = 0
        occupiedmax = 0
        for slot in free:
            freetext += f"🟢 {slot}\n"
            freemax += 1
        for slot in occupied:
            occupiedtext += f"🔴 {slot}\n"
            occupiedmax += 1
        endtext = f"\nВсего занято {occupiedmax} из {len(free) + len(occupied)}"
        newtext = "ℹ️ **Информация по парковочным местам:**\n\n" + occupiedtext + freetext + endtext
        for attempt in range(1, 4):  # 3 попытки
            try:
                await asyncio.wait_for(callback.message.edit_text(text=newtext,
                    reply_markup=keyboards.keyboard(callback_1="user:menu:get"),
                    parse_mode="Markdown"),
                    timeout=5.0)
                logger.info(f"✅ Успешно с {attempt} попытки")
                return  # выходим из функции

            except asyncio.TimeoutError:
                if attempt == 4:  # последняя попытка
                    await callback.message.answer(text=newtext,
                                                    reply_markup=keyboards.keyboard(callback_1="user:menu:get"),
                                                    parse_mode="Markdown")
                else:
                    await asyncio.sleep(1)  # пауза перед следующей попыткой




        await callback.message.edit_text(

        )

    except Exception as e:
        logger.error(f"Ошибка в get_parking: {e}")

 # ================= Остальное  ================

@router.callback_query(F.data == "user:menu:help")##настройки
async def show_help3(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logger.info(f"Показ справки для user_id={user_id}")

    try:
        await callback.message.edit_text(
            "ℹ️ **Помощь:**\n\n"
            "• Бот работает по вайтлисту\n"
            "• Только одобренные пользователи имеют доступ к боту.\n\n"
            "Связь с разработчиком: @gsoalnfeea",
            reply_markup=keyboards.keyboard(callback_1="user:menu:get"),
            parse_mode="Markdown"
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в show_help: {e}")


# ================= Стандартный функционал ================

@router.callback_query(F.data == "user:menu:id")
async def show_my_id(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logger.info(f"Показ ID для user_id={user_id}")

    try:
        level = whitelist.check_permission(user_id)
        text = (f"📋 Ваш профиль:\n"
                f"{whitelist.get_user_data(user_id)[2]} | {whitelist.get_user_data(user_id)[3]} | {whitelist.get_user_data(user_id)[4]}\n"
                f"ID: `{user_id}`\n"
                f"Доступ к боту: {'разрешен ✅' if whitelist.check_user(user_id) else 'запрещен ❌'}\n"
                f"Уровень учетной записи: {whitelist.user_lvl[level]} | {whitelist.user_lvl_icon[level]}\n")

        match level:
            case 2:
                await callback.message.edit_text(
                    text,
                    reply_markup=keyboards.keyboard(callback_1 = "user:menu:get",callback_2 = "admin:menu:get",text_2="Администрирование"),
                    parse_mode="Markdown",
                )
            case 1:
                await callback.message.edit_text(
                    text,
                    reply_markup=keyboards.keyboard(callback_1="new:menu:get"),
                    parse_mode="Markdown",
                )
            case _:
                await callback.message.edit_text(
                    text,
                    reply_markup=keyboards.keyboard(callback_1="new:menu:get"),
                    parse_mode="Markdown"
                )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в show_my_id: {e}")

@router.callback_query(F.data == "user:menu:help")
async def show_help(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    logger.info(f"Показ справки для user_id={user_id}")

    try:
        await callback.message.edit_text(
            "ℹ️ **Помощь:**\n\n"
            "• Бот работает по вайтлисту\n"
            "• Только одобренные пользователи имеют доступ к боту.\n\n"
            "Связь с разработчиком: @gsoalnfeea",
            reply_markup=keyboards.keyboard(callback_1="user:menu:get"),
            parse_mode="Markdown"
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в show_help: {e}")