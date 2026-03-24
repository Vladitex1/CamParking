
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Импортируем роутеры
from handlers import admin_handler, user_handler, new_user_handler,commands,debug_handler

logging.basicConfig(
    level=logging.DEBUG,  # Можно поменять на INFO для менее подробных логов
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/bot_log.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
# Хранилище для FSM нужно для состояний
storage = MemoryStorage()
#bot = Bot(token='8034081320:AAHWQZRf5LNS8bzdyDLXpiMYQvFdKGKWmUU', proxy='http://127.0.0.1:2080')
bot = Bot(token="8034081320:AAHWQZRf5LNS8bzdyDLXpiMYQvFdKGKWmUU")
dp = Dispatcher(storage=storage)


async def main():
    try:
        # ВАЖНО: Порядок имеет значение!
        dp.include_router(commands.router) #подключение команд
        # 1. Админские команды (самые специфичные)
        dp.include_router(admin_handler.router)
        # 2. Пользовательские команды
        dp.include_router(user_handler.router)
        # 3. Команды для новых пользователей (самые общие)
        dp.include_router(new_user_handler.router)
        # 4. debug команды
        dp.include_router(debug_handler.router) #подключение команд

        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        print("не удалось запустить бота")
        print(e)
        return


if __name__ == "__main__":
    asyncio.run(main())