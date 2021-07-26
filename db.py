import aiosqlite
import sqlite3
import logging

from typing import Optional


queries = {
    'create_db': """ CREATE TABLE IF NOT EXISTS "user_token" 
                    (
                        "user_id" TEXT NOT NULL UNIQUE,
                        "token" TEXT NOT NULL
                    );
                 """,
    'create_file_table': """   CREATE TABLE IF NOT EXISTS "file_id" (
                                "pk"	INTEGER NOT NULL UNIQUE,
                                "file_id"	INTEGER NOT NULL UNIQUE,
                                "filename"	TEXT NOT NULL UNIQUE,
                                PRIMARY KEY("pk" AUTOINCREMENT)
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
                """,
    'save_file': """
                    INSERT INTO file_id
                    (
                        file_id,
                        filename
                    )
                    VALUES (?, ?);
                 """,
    'get_file_id': """
                    SELECT file_id FROM file_id WHERE filename = ?;
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
                cursor.execute(queries['create_file_table'])
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

    async def get_file(self, file_name: str) -> Optional[str]:
        try:
            async with aiosqlite.connect('main.sqlite3') as db:
                cursor = await db.cursor()
                executed = await cursor.execute(queries['get_file_id'], (file_name, ))
                data = await executed.fetchone()
                if data:
                    return data[0]
                return None
        except aiosqlite.Error as e:
            logging.error(e)

    async def save_file_to_db(self, file_name: int, file_id: int):
        try:
            async with aiosqlite.connect('main.sqlite3') as db:
                cursor = await db.cursor()
                await cursor.execute(queries['save_file'], (file_id, file_name))
                await db.commit()
        except aiosqlite.Error as e:
            logging.error(e)
