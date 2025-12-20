# main.py
import asyncio
import logging

# 1. Импортируем Router
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters.command import Command

logging.basicConfig(level=logging.INFO)

# Импортируем наш роутер из пакета handlers
from handlers import basic_handlers, menu_handlers, login

bot = Bot(token="8034081320:AAE6KBHZPeCXvu6QpiT1jDnwfty5hqvmBMg")
dp = Dispatcher()


async def main():
    #Регистрируем роутер в диспетчере
    dp.include_router(basic_handlers.router)
    dp.include_router(menu_handlers.router) # Новый роутер
    dp.include_router(login.router) # Новый роутер

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())