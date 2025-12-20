from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.types import FSInputFile

router = Router()


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
