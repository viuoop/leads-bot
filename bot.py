import asyncio
import logging

from aiogram import Bot, Dispatcher

import config
import db
import handlers


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    db.init(config.DB_PATH)
    dp = Dispatcher()
    dp.include_router(handlers.router)
    await dp.start_polling(Bot(config.BOT_TOKEN))


if __name__ == "__main__":
    asyncio.run(main())
