"""
The database module of the bot.
"""

from typing import Dict

import aiosqlite


class Database:
    """
    The database class of the bot.
    """

    def __init__(self, path: str) -> None:
        self.path = path

    async def initialize(self) -> None:
        """
        Initializes the database.
        """
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    opt_out INTEGER DEFAULT 0,
                    language TEXT DEFAULT 'en-US'
                )
                """
            )

    async def get_user(self, user_id: int) -> Dict[str, str]:
        """
        Gets a user from the database.
        """
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cursor:
                return await cursor.fetchone()

    async def opt_out(self, user_id: int, opt_out: bool = True) -> None:
        """
        Opt out of the bot.
        """
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT INTO users (id, opt_out) VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET opt_out = ?",
                (user_id, opt_out, opt_out),
            )
            await db.commit()

    async def set_language(self, user_id: int, language: str) -> None:
        """
        Sets the language of a user or guild.
        """
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT INTO users (id, language) VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET language = ?",
                (user_id, language, language),
            )
            await db.commit()
