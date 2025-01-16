import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.admin import admin
from app.database.models import async_main
from app.user import user
from config import TOKEN


async def main():
    bot = Bot(
        token=TOKEN,
        # default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()
    dp.include_router(admin)
    dp.include_routers(user)

    dp.startup.register(startup)
    dp.shutdown.register(shutdown)

    await dp.start_polling(bot)


async def startup(dispatcher: Dispatcher):
    await async_main()
    print("Starting up...")


async def shutdown(dispatcher: Dispatcher):
    print("Shutting down...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
