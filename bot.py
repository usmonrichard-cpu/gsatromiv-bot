import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from dotenv import load_dotenv

import db

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    # Foydalanuvchini bazaga saqlash
    await db.save_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        language_code=message.from_user.language_code or "uz",
    )
    await db.save_message(message.from_user.id, "in", message.text)
    await db.set_state(message.from_user.id, step="start")

    reply = "Assalomu alaykum! Botga xush kelibsiz."
    await message.answer(reply)
    await db.save_message(message.from_user.id, "out", reply)


@dp.message()
async def echo_handler(message: types.Message):
    await db.save_message(message.from_user.id, "in", message.text)
    reply = f"Siz yozdingiz: {message.text}"
    await message.answer(reply)
    await db.save_message(message.from_user.id, "out", reply)


async def main():
    await db.init_db()
    try:
        await dp.start_polling(bot)
    finally:
        await db.close_db()


if __name__ == "__main__":
    asyncio.run(main())
