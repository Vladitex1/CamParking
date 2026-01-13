from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.types import FSInputFile

router = Router()

##### Сделать конфиг из файла отдельного для модели

# Сделать ХЕШ модель, чтоб не так долго все грузилось. хотя мб оно и так работает



@router.message(Command("menu"))
async def show_menu(message: types.Message):
    # Используем HTML-разметку для формирования текста
    text = (
        "<b>Меню возможностей:</b>\n\n"
        "<i>Этот бот демонстрирует:</i>\n"
        " - Отправку форматированного текста\n"
        " - Отправку изображений и документов\n\n"
        "Воспользуйтесь командой /send_photo, чтобы получить картинку.\n\n"
        "Больше информации о фреймворке вы найдете в "
        "<a href='https://aiogram.dev/'>документации aiogram 3</a>."
    )

    # Отправляем сообщение, обязательно указав parse_mode
    await message.answer(text, parse_mode="HTML")

@router.message(Command("admin_panel"))
async def cmd_start(message: types.Message):
    kb = [
        [types.KeyboardButton(text="🔍 Узнать мой ID")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    await message.answer("Как подавать котлеты?", reply_markup=keyboard)


# 2. Новый хэндлер для команды /send_photo
@router.message(Command("cat"))
async def send_photo_command(message: types.Message):
    # Создаем объект файла для загрузки
    image_from_pc = FSInputFile("cat.jpeg")

    # Отправляем фото с подписью и форматированием
    await message.answer_photo(
        photo=image_from_pc,
        caption="<b>Вот ваш котик!</b> ᓚᘏᗢ\n\n"
                "<em>Этот котик был загружен с компьютера.</em>",
        parse_mode="HTML"
    )

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

        waiting = await callback.message.answer(f"⏳ Загрузка...")
        # Получение данных с камеры
        img = await camera.get_img()
        # Получаем данные о парковке ============== Обработка фото
        occupied, free = detector.check_auto(mask="test4.mask", img=img, config_name="confwn")
        await callback.answer()

        # Формируем текст
        free_text = f"\n Свободные места: \n"
        occupied_text = f"\n Занятые места: \n"
        free_max,occupied_max = 0,0

        for slot in free:
            free_text += f"🟢 {slot}\n"
            free_max += 1
        for slot in occupied:
            occupied_text += f"🔴 {slot}\n"
            occupied_max += 1
        text = (f"{datetime.today().strftime('📅 %Y-%m-%d 🕔 %H:%M:%S')}\n"
                f"ℹ️ **Информация по парковочным местам:**\n"
                f""
                f"{free_text}"
                f"{occupied_text}"
                f""
                f"\nСвободных мест: {free_max} из {len(free) + len(occupied)}")
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
                        caption=text,
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