import asyncio
import aiosqlite
from encrypt import pm
import os

async def create_table() -> None:
    async with aiosqlite.connect("my_database.db") as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS servers (
        user_id TEXT NOT NULL,
        servername TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        address TEXT NOT NULL
        )
        """
                           )
        await conn.commit()


class Database:
    def __init__(self, db_name: str = "my_database.db") -> None:
        self.db_name = db_name
        if not os.path.isfile('my_database.db'): raise FileNotFoundError("Файл таблицы не найден")

    async def add_server(
            self, user_id: str, servername: str, username: str, password: str, address: str
    ) -> None:
        async with aiosqlite.connect(self.db_name) as conn:
            await conn.execute(
                "INSERT INTO servers (user_id, servername, username, password, address) VALUES (?, ?, ?, ?, ?)",
                (user_id, servername, username, pm.encrypt(password), address),
            )
            await conn.commit()

    async def get_servers(self, user_id: str) -> list[str]:
        async with aiosqlite.connect(self.db_name) as conn:
            cursor = await conn.execute("SELECT servername FROM servers WHERE user_id = ?", (user_id,))
            rows = await cursor.fetchall()
        return [row[0] for row in rows]

    async def get_connection_data(self, user_id: str, servername: str) -> list[str]:
        async with aiosqlite.connect(self.db_name) as conn:
            cursor = await conn.execute(
                "SELECT username, password, address FROM servers WHERE servername = ? AND user_id = ?",
                (servername, user_id,)
            )
            result = await cursor.fetchone()
            if result:
                username, password, address = result
                password = pm.decrypt(password)
                return [username, password, address]
            return []

    async def delete_server(self, user_id: str, servername: str) -> None:
        async with aiosqlite.connect(self.db_name) as conn:
            await conn.execute(
                "DELETE FROM servers WHERE servername = ? AND user_id = ?", (servername, user_id,)
            )
            await conn.commit()

    async def change_servername(
            self, user_id: str, servername_old: str, servername_new: str
    ) -> None:
        async with aiosqlite.connect(self.db_name) as conn:
            await conn.execute(
                "UPDATE servers SET servername = ? WHERE servername = ? AND user_id = ?",
                (
                    servername_new,
                    servername_old,
                    user_id,
                ),
            )
            await conn.commit()

    async def change_username(
            self, user_id: str, servername: str, username: str
    ) -> None:
        async with aiosqlite.connect(self.db_name) as conn:
            await conn.execute(
                "UPDATE servers SET username = ? WHERE servername = ? AND user_id = ?",
                (
                    username,
                    servername,
                    user_id,
                ),
            )
            await conn.commit()

    async def change_password(
            self, user_id: str, servername: str, password: str
    ) -> None:
        async with aiosqlite.connect(self.db_name) as conn:
            await conn.execute(
                "UPDATE servers SET password = ? WHERE servername = ? AND user_id = ?",
                (
                    pm.encrypt(password),
                    servername,
                    user_id,
                ),
            )
            await conn.commit()

    async def change_address(self, user_id: str, servername: str, address: str) -> None:
        async with aiosqlite.connect(self.db_name) as conn:
            await conn.execute(
                "UPDATE servers SET address = ? WHERE servername = ? AND user_id = ?",
                (
                    address,
                    servername,
                    user_id,
                ),
            )
            await conn.commit()


if __name__ == "__main__":
    asyncio.run(create_table())
