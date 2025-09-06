import os
import asyncio
import logging

from aiogram import Bot, Dispatcher

from handlers import router
from database import create_table
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

BOT_TOKEN = os.getenv('TOKEN')

# Объект бота
bot = Bot(token=BOT_TOKEN)
# Диспетчер
dp = Dispatcher()

dp.include_router(router)

# Запуск процесса поллинга новых апдейтов
async def main():
    # Запускаем создание таблицы базы данных
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Включаем логирование
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Stop')
