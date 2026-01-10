from datetime import datetime
from aiogram import Router, types, F,Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton,FSInputFile,InputMediaPhoto
from aiogram.filters import Command
import logging
import asyncio
from TelegramBot.handlers.config import whitelist
from TelegramBot.handlers import keyboards
import TelegramBot.detector as detector
from PIL import Image
import os

user_keyboard_letter:str = "Выберите действие в меню ниже:\n"
def user_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🅿️ Свободные места", callback_data="parking:get")],
        [InlineKeyboardButton(text="🔍 Мой ID", callback_data="user:menu:id")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="user:menu:help")]
    ])

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
                text = user_keyboard_letter,
                reply_markup=user_keyboard(),
            )
        else:
            logger.warning(f"Нет прав для меню пользователя: user_id={user_id}")
            await callback.message.edit_text(
                "⛔ У вас нет доступа к этому меню",
                reply_markup=keyboards.keyboardH(callback_1="new:menu:get")
            )
        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка в user_menu для user_id={user_id}: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)

 # ================= Работа с машинами функционал ================

@router.callback_query(F.data == "parking:get")
async def get_parking(callback: types.CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    logger.info(f"запрос парковочных мест user_id={user_id}")
    try:
        # Удаляем меню
        await bot.delete_message(
            chat_id=chat_id,
            message_id=callback.message.message_id
        )

        INPUT_DIR = "../img/results/"
        image = "last_result.jpg"

        waiting = await callback.message.answer("⏳ Загрузка...")
        # Получение данных с камеры
        img = await detector.get_img_from_cam()
        # Получаем данные о парковке ============== Обработка фото
        occupied, free = detector.check_auto(save="Отладка1.mask",img=img, config_name="confwn",processed_image=None)
        await callback.answer()

        # Формируем текст
        freetext = f"\n{'=' * 5} Свободные места: {'=' * 5}\n"
        occupiedtext = f"\n{'=' * 6} Занятые места: {'=' * 6}\n"
        freemax = 0
        occupiedmax = 0

        for slot in free:
            freetext += f"🟢 {slot}\n"
            freemax += 1
        for slot in occupied:
            occupiedtext += f"🔴 {slot}\n"
            occupiedmax += 1

        endtext = f"\nВсего занято {occupiedmax} из {len(free) + len(occupied)}"
        newtext = "ℹ️ **Информация по парковочным местам:**\n\n" + freetext + occupiedtext + endtext

        # Сжимаем фото
        try:
            img = Image.open(INPUT_DIR + image)
            img.save(INPUT_DIR + "temp_compressed.jpg", 'JPEG', quality=60, optimize=True)
        except Exception as e:
            logger.warning(f"Ошибка при сжатии фото: {e}")
            # Если не удалось сжать, используем оригинальный файл
        # Параметры повторных попыток
        max_retries = 10  # 0 = бесконечные попытки ################################переделать цикл
        retry_delay = 2  # Задержка между попытками в секундах
        # ЦИКЛ ПОВТОРНЫХ ПОПЫТОК ОТПРАВКИ ФОТО
        photo_sent = False
        attempt = 0
        while max_retries == 0 or attempt < max_retries:
            try:
                attempt += 1
                logger.info(f"Попытка отправки фото #{attempt}")
                # Используем оригинальный файл, если сжатый не создался
                photo_path = INPUT_DIR + image
                if os.path.exists(INPUT_DIR + "temp_compressed.jpg"):
                    photo_path = INPUT_DIR + "temp_compressed.jpg"
                # Пытаемся отправить фото с таймаутом
                await asyncio.wait_for(
                    callback.message.answer_photo(
                        photo=FSInputFile(photo_path),
                        caption=f"📅{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}\n{newtext}",
                        parse_mode="Markdown",
                        reply_markup=keyboards.keyboardH(callback_1="parking:back",text_2="Повторить попытку",callback_2="parking:get")##
                    ),
                    timeout=5
                )
                # Если дошли сюда - фото успешно отправлено
                logger.info(f"✅ Фото отправлено успешно с попытки #{attempt}")
                photo_sent = True
                break  # ВЫХОДИМ ИЗ ЦИКЛА ПОСЛЕ УСПЕШНОЙ ОТПРАВКИ
            except asyncio.TimeoutError:
                logger.warning(f"⏱️ Таймаут при отправке фото (попытка {attempt})")
                if max_retries > 0 and attempt >= max_retries:
                    logger.error("❌ Превышено максимальное количество попыток")
                    raise asyncio.TimeoutError("Не удалось отправить фото из-за таймаутов")

                await asyncio.sleep(retry_delay)
                continue  # Продолжаем цикл

            except Exception as e:
                logger.error(f"❌ Ошибка при отправке фото (попытка {attempt}): {e}")
                if max_retries > 0 and attempt >= max_retries:
                    raise

                await asyncio.sleep(retry_delay * 2)  # Увеличиваем задержку при ошибках
                continue  # Продолжаем цикл

        # Удаляем сообщение "Загрузка..." после успешной отправки
        if photo_sent:
            try:
                await waiting.delete()
            except Exception as e:
                logger.warning(f"Не удалось удалить сообщение 'Загрузка...': {e}")

        # Удаляем сжатый временный файл
        try:
            if os.path.exists(INPUT_DIR + "temp_compressed.jpg"):
                os.remove(INPUT_DIR + "temp_compressed.jpg")
        except Exception as e:
            logger.warning(f"Не удалось удалить временный файл: {e}")

    except asyncio.TimeoutError:
        logger.error("❌ Превышен общий таймаут отправки фото")
        # Удаляем сообщение "Загрузка..."
        try:
            await waiting.delete()
        except:
            pass

        # Показываем пользователю ошибку
        await callback.message.answer(
            "❌ Не удалось отправить фото из-за проблем с сетью. Попробуйте позже.",
            reply_markup=keyboards.keyboardH(callback_1="parking:back")
        )

    except Exception as e:
        logger.error(f"❌ Критическая ошибка в get_parking: {e}")
        await callback.message.answer(
            "❌Попробуйте позже.",
            reply_markup=keyboards.keyboardH(callback_1="parking:back")
        )
        # Удаляем сообщение "Загрузка..."
        try:
            await waiting.delete()
        except:
            pass

        # Показываем пользователю ошибку
        await callback.answer(f"Ошибка: {str(e)[:50]}", show_alert=True)


@router.callback_query(F.data == "parking:back")
async def back_from_parking(callback: types.CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id

    await callback.answer()
    try:
        await bot.delete_message(chat_id, callback.message.message_id - 1)
    except:
        pass
    # 3. Удаляем сообщение с кнопкой "Назад"
    try:
        await bot.delete_message(chat_id, callback.message.message_id)
    except:
        pass

    # 4. Редактируем заглушку в меню
    if whitelist.valid_user_permissions(user_id, 1):
        await callback.message.answer(
            text = user_keyboard_letter,
            reply_markup=user_keyboard()
        )
    else:
        await callback.message.edit_text(
            "⛔ У вас нет доступа к этому меню",
            reply_markup=keyboards.keyboardH(callback_1="new:menu:get")
        )


 # ================= Остальное ================

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
            reply_markup=keyboards.keyboardH(callback_1="user:menu:get"),
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
                    reply_markup=keyboards.keyboardH(callback_1 ="user:menu:get", callback_2 ="admin:menu:get", text_2="Администрирование"),
                    parse_mode="Markdown",
                )
            case 1:
                await callback.message.edit_text(
                    text,
                    reply_markup=keyboards.keyboardH(callback_1="user:menu:get"),
                    parse_mode="Markdown",
                )
            case _:
                await callback.message.edit_text(
                    text,
                    reply_markup=keyboards.keyboardH(callback_1="new:menu:get"),
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
            reply_markup=keyboards.keyboardH(callback_1="user:menu:get"),
            parse_mode="Markdown"
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в show_help: {e}")


########debug
@router.callback_query(F.data == "parking:get2")
async def get_parking2(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer("Получаем данные...")

    # Просто отправь текст без фото для теста
    await callback.message.answer(
        "✅ Данные получены!\nТестовая информация о парковке",
        reply_markup=keyboards.keyboardH(callback_1="parking:back")
    )
