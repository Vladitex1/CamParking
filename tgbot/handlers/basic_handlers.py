from aiogram import Router, types, F
from aiogram.filters.command import Command

router = Router()


# Хэндлер на команду /start (самый специфичный)
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Это бот для приложения CamParking!")
        # Используем HTML-разметку для формирования текста
    text = (
        "<b>CamParkingBot</b>\n\n"
        "<i>Для начала запросите доступ у админисратора</i>\n"
        "Воспользуйтесь командой /request или кнопкой снизу, чтобы получить доступ.\n\n"
    )
    kb = [
        [types.KeyboardButton(text="Запросить доступ")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    # Отправляем сообщение, обязательно указав parse_mode
    await message.answer(text, parse_mode="HTML")


# Хэндлер на получение фото
@router.message(F.photo)
async def handle_photo(message: types.Message):
    await message.answer("Отличное фото! Спасибо.")


# Хэндлер на получение стикера
@router.message(F.sticker)
async def handle_sticker(message: types.Message):
    # message.sticker.file_id - можно получить id стикера
    await message.answer("Милый стикер!")


# Хэндлер на любой текст (самый общий, должен быть последним)
@router.message(F.text, lambda message: "дурак" in message.text.lower())
async def handle_text(message: types.Message):
    await message.answer(f"Ты прислал текст: {message.text}")