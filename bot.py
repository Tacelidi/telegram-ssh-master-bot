import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from dotenv import load_dotenv
import os
from handlers import router

logging.basicConfig(level=logging.INFO)  # логирование

load_dotenv()
bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)


async def main():
    dp = Dispatcher()
    dp.include_routers(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
