import logging
from vkbottle.bot import BotLabeler, Message
from vkbottle import Keyboard, Callback, KeyboardButtonColor

from VKBot.handlers.config import whitelist

labeler = BotLabeler()
logger = logging.getLogger(__name__)

@labeler.message(text=["/start", "Начать"])
async def start_command(message: Message):
    user_id = message.from_id
    if whitelist.check_user(user_id):
        kb = Keyboard(inline=True)
        kb.add(Callback("Войти", payload={"cmd": "user:menu:get"}), color=KeyboardButtonColor.PRIMARY)
        await message.answer("✅ У вас уже есть доступ!\n", keyboard=kb.get_json())
    else:
        kb = Keyboard(inline=True)
        kb.add(Callback("Войти", payload={"cmd": "new:menu:get"}), color=KeyboardButtonColor.PRIMARY)
        await message.answer(
            "Добро пожаловать в CamParking!\nДля начала работы вам необходимо запросить доступ",
            keyboard=kb.get_json()
        )
    logger.info(f"Вызов команды /start от пользователя {user_id}")

@labeler.message(text=["/goadmin"])
async def goadmin_command(message: Message):
    user_id = message.from_id
    if whitelist.valid_user_permissions(user_id, 2):
        kb = Keyboard(inline=True)
        kb.add(Callback("Войти", payload={"cmd": "admin:menu:get"}), color=KeyboardButtonColor.PRIMARY)
        await message.answer("✅ Добро пожаловать Админку!\n", keyboard=kb.get_json())
    elif whitelist.valid_user_permissions(user_id, 1):
        kb = Keyboard(inline=True)
        kb.add(Callback("Войти", payload={"cmd": "new:menu:get"}), color=KeyboardButtonColor.PRIMARY)
        await message.answer(
            "Недостаточно прав!",
            keyboard=kb.get_json()
        )
    else:
        kb = Keyboard(inline=True)
        kb.add(Callback("Войти", payload={"cmd": "user:menu:get"}), color=KeyboardButtonColor.PRIMARY)
        await message.answer(
            "Недостаточно прав!",
            keyboard=kb.get_json()
        )
    logger.info(f"Вызов команды /goadmin от пользователя {user_id}")

