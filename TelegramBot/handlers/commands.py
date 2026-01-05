from aiogram import Router, types
from aiogram.filters import Command
from .config import whitelist, usermanager
from . import keyboards
import logging
logger = logging.getLogger(__name__)
router = Router()


# ========== КОМАНДЫ ==========
@router.message(Command("start"))
async def start_command(message: types.Message):  # Исправлено: message, а не callback
    user_id = message.from_user.id
    if whitelist.check_user(user_id):
        await message.answer(  # Исправлено: message.answer
            "✅ У вас уже есть доступ!\n",
            reply_markup=keyboards.keyboard("Войти","user:menu:get")
            )
        await message.delete()
    else:
        await message.answer("Добро пожаловать в CamParking!\n"
                             "для начала работы вам необходимо запросить доступ"
                             ,callback_data="new:menu:get")
    logger.info(f"Вызов команды /start от пользователя {user_id}")


@router.message(Command("goadmin"))
async def goadmin_command(message: types.Message):  # ← message, а не callback!
    from .admin_handler import admin_menu
    class FakeCallback:
        def __init__(self, msg):
            self.id = "fake"
            self.from_user = msg.from_user
            self.message = msg  # передаем message как часть callback
            self.data = "admin:menu:get"
            self.chat_instance = "fake"
        async def answer(self):
            pass
    fake_callback = FakeCallback(message)
    await admin_menu(fake_callback)
