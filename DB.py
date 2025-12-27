import aiosqlite

class DataBase:
    def __init__(self):
        self.db_name = 'my_database.db'

    async def table_exists(self, user_id):
        async with aiosqlite.connect(self.db_name) as conn:
            cursor = await conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (user_id,))
            result = await cursor.fetchone()
            return result is not None

    async def create_table(self, user_id):
        async with aiosqlite.connect(self.db_name) as conn:
            await conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {user_id} (
            servername TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            address TEXT NOT NULL
            )
            ''')
            await conn.commit()

    async def add_server(self, user_id, servername, username, password, address):
        async with aiosqlite.connect(self.db_name) as conn:
            await conn.execute(f'INSERT INTO {user_id} (servername, username, password, address) VALUES (?, ?, ?, ?)',
                           (servername, username, password, address))
            await conn.commit()

    async def get_servers(self, user_id):
        async with aiosqlite.connect(self.db_name) as conn:
            cursor = await conn.execute(f'SELECT servername FROM {user_id}')
            rows = await cursor.fetchall()
        return [row[0] for row in rows]

    async def get_connection_data(self, user_id, servername):
        async with aiosqlite.connect(self.db_name) as conn:
            cursor = await conn.execute(f'SELECT username, password, address FROM {user_id} WHERE servername = ?', (servername,))
            result = await cursor.fetchone()
            return list(result)

    async def delete_server(self, user_id, servername):
        async with aiosqlite.connect(self.db_name) as conn:
            await conn.execute(f'DELETE FROM {user_id} WHERE servername = ?', (servername,))
            await conn.commit()

    async def change_servername(self, user_id, servername_old, servername_new):
        async with aiosqlite.connect(self.db_name) as conn:
            await conn.execute(f"UPDATE {user_id} SET servername = ? WHERE servername = ?",
                           (servername_new, servername_old,))
            await conn.commit()

    async def change_username(self, user_id, servername, username):
        async with aiosqlite.connect(self.db_name) as conn:
            await conn.execute(f"UPDATE {user_id} SET username = ? WHERE servername = ?", (username, servername,))
            await conn.commit()

    async def change_password(self, user_id, servername, password):
        async with aiosqlite.connect(self.db_name) as conn:
            await conn.execute(f"UPDATE {user_id} SET password = ? WHERE servername = ?", (password, servername,))
            await conn.commit()

    async def change_address(self, user_id, servername, address):
        async with aiosqlite.connect(self.db_name) as conn:
            await conn.execute(f"UPDATE {user_id} SET address = ? WHERE servername = ?", (address, servername,))
            await conn.commit()

