import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

pool = None

async def init_pool():
    
    global pool

    pool = await asyncpg.create_pool(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=5432,
        min_size=5,
        max_size=20
    )

async def get_pool():
    return pool


async def close_pool():
    global pool
    if pool:
        await pool.close()

async def get_db():
    global pool
    async with pool.acquire() as connection:
        yield connection
