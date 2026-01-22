from datetime import datetime
from aiogram import Router, types, F,Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton,FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import logging
import asyncio
from TelegramBot.handlers.config import whitelist
from TelegramBot.handlers import keyboards
import logic.detector as detector
import logic.visualizer as visualizer
from datetime import date

import logic.camera_control as camera
from PIL import Image
import os

user_keyboard_letter:str = "Выберите действие в меню ниже:\n"
def user_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🅿️ Свободные места", callback_data="parking:get")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="parking:settings")],
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


class Form(StatesGroup):
    waiting_camera = State()
    load_file = State()

 # ================= Обнаружение ================



@router.callback_query(F.data == "parking:get")
async def start_edit(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_camera)
    await state.update_data(user_id=callback.from_user.id)
    await process_camera_request(callback.message, state, callback.bot)
    await callback.answer()


@router.message(Form.waiting_camera)
async def process_camera_request(message: types.Message, state: FSMContext, bot: Bot):
    state_data = await state.get_data()
    user_id = state_data.get('user_id', message.from_user.id)
    chat_id = message.chat.id  # БЫЛО: message.message.chat.id

    print("начало работы системы")
    logger.info(f"запрос парковочных мест user_id={user_id}")
    try:
        # Удаляем меню
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message.message_id
        )

        INPUT_DIR = "../img/results/"
        #image = "last_result.jpg"
        another_img = "output_open.jpg"
        mask = whitelist.get_settings('mask',user_id)
        config = whitelist.get_settings('config',user_id)
        # Получение данных с камеры
        waittext = "Загрузка: "
        waiting = await message.answer(text = waittext+keyboards.loading(0))
        image = await camera.get_img_PyAV()
        print(f"фото получено")
        await waiting.edit_text(text = waittext+keyboards.loading(2))
        # Получаем данные о парковке ============== Обработка фото
        print(f"{mask}{image}{config}{user_id}")
        occupied, free = detector.check_auto(mask=mask, processed_image=image, config_name=config)
        await waiting.edit_text(text = waittext+keyboards.loading(5))
        print(f"фото обработано ИИ")

        image,filename = visualizer.detect(image_path=image, mask=mask, occupied_data=[occupied,free],draw_name=False)
        await waiting.edit_text(text = waittext+keyboards.loading(8))
        print(f"фото обработано для вывода")
        #await message.answer()

        # Формируем текст
        free_text = f"\n Свободные места: \n"
        occupied_text = f"\n Занятые места: \n"
        free_max, occupied_max = 0, 0

        for slot in free:
            free_text += f"🟢 {slot}\n"
            free_max += 1
        for slot in occupied:
            occupied_text += f"🔴 {slot}\n"
            occupied_max += 1
        text = (f"{datetime.today().strftime('📅 %Y-%m-%d 🕔 %H:%M:%S')}\n"
                f"ℹ️ **Информация по парковочным местам:**\n"
                f"\nИспользованная маска: {whitelist.get_settings('mask',user_id)}\n"
                f"{free_text}"
                f"{occupied_text}"
                f"\nСвободных мест: {free_max} из {len(free) + len(occupied)}")
        # Сжимаем фото
        try:
            img = Image.open(filename)
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
        await waiting.edit_text(text = waittext+keyboards.loading(10))
        while max_retries == 0 or attempt < max_retries:
            try:
                attempt += 1
                logger.info(f"Попытка отправки фото #{attempt}")
                # Используем оригинальный файл, если сжатый не создался
                photo_path = INPUT_DIR + another_img
                if os.path.exists(INPUT_DIR + "temp_compressed.jpg"):
                    photo_path = INPUT_DIR + "temp_compressed.jpg"
                # Пытаемся отправить фото с таймаутом
                await asyncio.wait_for(
                    message.answer_photo(
                        photo=FSInputFile(photo_path),
                        caption=text,
                        parse_mode="Markdown",
                        reply_markup=keyboards.keyboardH(callback_1="parking:back", text_2="Повторить попытку",
                                                         callback_2="parking:get")  ##
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

                await asyncio.sleep(retry_delay)
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
            await message.answer(
                "❌ Попробуйте позже.",
                reply_markup=keyboards.keyboardH(callback_1="parking:back")
            )
        except:
            pass

    except Exception as e:
        logger.error(f"❌ Критическая ошибка в get_parking: {e}")
        await message.answer(
            "❌ Попробуйте позже.",
            reply_markup=keyboards.keyboardH(callback_1="parking:back")
        )
    finally:
        await state.clear()


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

 # ================= Настройки обнаружения ================

@router.callback_query(F.data == "parking:settings")
async def parking_settings(callback: types.CallbackQuery):

    user_id = callback.from_user.id
    await callback.answer()
    buttons = [#["Включить стандартную маску",f"parking:settigns:set_{'mask'}_{user_id}_{whitelist.default_mask}"],
               ["Стандартная маска", f"parking:settings:set_mask_{user_id}_{whitelist.default_mask}"],
               ["Включить test4", f"parking:settings:set_mask_{user_id}_test4"],
               ["Загрузить маску", f"parking:settings:load_mask"],
               ["Назад","user:menu:get"]]


    text = (f"🔧 Настройки 🔧\n\n"
            f"🤿Выбранная маска = {whitelist.get_settings('mask',user_id)}\n"
            f"🔤Включение подписей на местах = {whitelist.get_settings('letters',user_id)}\n"
            f"📋Доступные маски:\n")
    text += f"{" "*5} - Стандартная маска\n"
    text += f"{" "*5} - {whitelist.get_settings('user_mask_slot_1',user_id)}\n"
    text += f"{" "*5} - маска3\n"

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=buttons[0][0], callback_data=buttons[0][1]),InlineKeyboardButton(text=buttons[1][0], callback_data=buttons[1][1])],
            #[InlineKeyboardButton(text=buttons[2][0], callback_data=buttons[2][1])],
            [InlineKeyboardButton(text=buttons[3][0], callback_data=buttons[3][1])],
        ]),
        parse_mode="Markdown",
    )
    await callback.answer()

@router.callback_query(F.data.startswith("parking:settings:set_"))
async def parking_settings_set(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    whitelist.set_settings(param_name = parts[1], user_id = parts[2], param_value = parts[3])
    #print(parts)
    await parking_settings(callback)

@router.callback_query(F.data == "parking:settings:load_mask")
async def start_edi2t(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.load_file) ###
    await state.update_data(user_id=callback.from_user.id)
    await load_mask(callback.message, state, callback.bot)
    await callback.answer()


@router.message(Form.load_file)
async def load_mask(message: types.Message, state: FSMContext, bot: Bot):
    #await message.edit_text(text="Отправьте в чат файл маски",
            #             reply_markup=keyboards.keyboardH(callback_1="parking:settings"))
    state_data = await state.get_data()
    user_id = state_data.get('user_id', message.from_user.id)
    chat_id = message.chat.id  # БЫЛО: message.message.chat.id

    if message.message_id:
        file_name = message

        print(f"Получен файл: {file_name}")

        # Проверяем формат файла
        if file_name.endswith('.mask'):
            # Скачиваем файл
            await message.answer("✅ Файл маски получен, загружаю...")

            # Здесь код для скачивания файла
            # file_path = f"../saves/{file_name}"
            # await bot.download_file(await bot.get_file(file.file_id), file_path)

            await message.answer(f"📁 Файл '{file_name}' успешно загружен!")
        else:
            await message.answer(f"❌ Неверный формат файла. Ожидается .mask, получен: {file_name}")
        await state.clear()
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
