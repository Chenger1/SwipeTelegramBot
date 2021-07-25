import aiosqlite
import sqlite3
import logging


queries = {
    'create_db': """ CREATE TABLE IF NOT EXISTS "user_token" 
                    (
                        "user_id" TEXT NOT NULL UNIQUE,
                        "token" TEXT NOT NULL
                    );
                """,
    'add_token': """
                    INSERT OR REPLACE INTO user_token 
                    (
                        user_id,
                        token
                    ) 
                    VALUES (?, ?);
                """,
    'get_token': """
                    SELECT token from user_token WHERE user_id = ?; 
                """
}


class DB:
    def __init__(self):
        self.create_table()

    def create_table(self):
        conn = sqlite3.connect('main.sqlite3')
        cursor = conn.cursor()
        try:
            with conn:
                cursor.execute(queries['create_db'])
            conn.close()
        except aiosqlite.Error as e:
            logging.error(e)
            conn.close()

    async def get_token(self, user_id: int) -> str:
        try:
            async with aiosqlite.connect('main.sqlite3') as db:
                cursor = await db.cursor()
                executed = await cursor.execute(queries['get_token'], (user_id,))
                data = await executed.fetchone()
                return data[0]
        except aiosqlite.Error as e:
            logging.error(e)

    async def update_token(self, user_id: int, data: str):
        try:
            async with aiosqlite.connect('main.sqlite3') as db:
                cursor = await db.cursor()
                await cursor.execute(queries['add_token'], (user_id, data))
                await db.commit()
        except aiosqlite.Error as e:
            logging.error(e)
