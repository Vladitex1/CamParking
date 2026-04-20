import logging
import os
import ssl
import certifi
import aiohttp
from vkbottle.bot import Bot

HARDCODED_GROUP_TOKEN = "vk1.a.j_nqQitKOtFGMa3n6Qw0FkeJh9W7Zpe2KI3sKMgZmCb_KSNWueg1esQbRQm1xAk19AzWV-B6Oge3HwF_SgcwCehgZS8fJKDUhEB4Fi9-AgSJH7VOD3_lGyjE8IW5OCCzce5JHHOAblKjOBoUA8ns7Ux5IK5Xn3Yphs_GBcYwR6h4Y1vZD07nF0IiDaJOFfNzPJcebzCPrNwxL576w-1cQg"
GROUP_TOKEN = os.environ.get("VK_GROUP_TOKEN") or HARDCODED_GROUP_TOKEN

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("../logs/bot_log.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

bot = Bot(token=GROUP_TOKEN)


async def on_startup():
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    bot.api.http_client.session = aiohttp.ClientSession(connector=connector)


bot.loop_wrapper.on_startup.append(on_startup())

# --- Загрузка лейблеров ---
try:
    from VKBot.handlers.commands import labeler as commands_labeler
    bot.labeler.load(commands_labeler)
    logger.info("Модуль commands загружен")
except ImportError as e:
    logger.warning(f"Модуль commands не найден: {e}")

try:
    from VKBot.handlers.admin_handler import labeler as admin_labeler
    bot.labeler.load(admin_labeler)
    logger.info("Модуль admin_handler загружен")
except ImportError as e:
    logger.warning(f"Модуль admin_handler не найден: {e}")

try:
    from VKBot.handlers.user_handler import labeler as user_labeler
    bot.labeler.load(user_labeler)
    from VKBot.handlers.user_handler import setup_uploader
    setup_uploader(bot.api)
    logger.info("Модуль user_handler загружен")
except ImportError as e:
    logger.warning(f"Модуль user_handler не найден: {e}")

try:
    from VKBot.handlers.debug_handler import labeler as debug_labeler
    bot.labeler.load(debug_labeler)
    logger.info("Модуль debug_handler загружен")
except ImportError as e:
    logger.warning(f"Модуль debug_handler не найден: {e}")

try:
    from VKBot.handlers.new_user_handler import labeler as new_user_labeler
    bot.labeler.load(new_user_labeler)
    logger.info("Модуль new_user_handler загружен")
except ImportError as e:
    logger.warning(f"Модуль new_user_handler не найден: {e}")

if __name__ == "__main__":
    logger.info("Запуск VK бота...")
    bot.run_forever()