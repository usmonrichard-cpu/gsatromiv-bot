import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

pool: asyncpg.Pool = None


async def init_db():
    """Bot ishga tushganda bir marta chaqiriladi (connection pool yaratadi)."""
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)


async def close_db():
    """Bot to'xtaganda chaqiriladi."""
    await pool.close()


async def save_user(telegram_id: int, username: str, first_name: str, last_name: str, language_code: str = "uz"):
    """Yangi foydalanuvchini saqlaydi, agar mavjud bo'lsa - yangilaydi."""
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users (telegram_id, username, first_name, last_name, language_code)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (telegram_id)
            DO UPDATE SET username = $2, first_name = $3, last_name = $4
            """,
            telegram_id, username, first_name, last_name, language_code,
        )


async def save_message(user_id: int, direction: str, text: str):
    """Xabarni tarixga yozadi. direction: 'in' yoki 'out'."""
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO messages (user_id, direction, text) VALUES ($1, $2, $3)",
            user_id, direction, text,
        )


async def set_state(user_id: int, step: str, data: dict = None):
    """Foydalanuvchi holatini (FSM bosqichini) saqlaydi."""
    import json
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO states (user_id, step, data, updated_at)
            VALUES ($1, $2, $3, NOW())
            ON CONFLICT (user_id)
            DO UPDATE SET step = $2, data = $3, updated_at = NOW()
            """,
            user_id, step, json.dumps(data or {}),
        )


async def get_state(user_id: int):
    """Foydalanuvchining joriy holatini o'qiydi."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT step, data FROM states WHERE user_id = $1", user_id
        )
        return dict(row) if row else None
