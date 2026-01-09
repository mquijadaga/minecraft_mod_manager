import json
import aiosqlite
from config import DB_PATH

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id    TEXT PRIMARY KEY,
                version     TEXT,
                loader      TEXT,
                created_at  TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS mods (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id    TEXT,
                mod_id      TEXT,
                name        TEXT,
                url         TEXT,
                is_library   INTEGER NOT NULL DEFAULT 0,
                UNIQUE(guild_id, mod_id),
                FOREIGN KEY(guild_id) REFERENCES guild_settings(guild_id) ON DELETE CASCADE
            );               
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS mod_dependencies (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id    TEXT,
                mod_row_id  INTEGER,
                dep_row_id  INTEGER,
                FOREIGN KEY(guild_id) REFERENCES guild_settings(guild_id) ON DELETE CASCADE,
                FOREIGN KEY(mod_row_id) REFERENCES mods(id) ON DELETE CASCADE,
                FOREIGN KEY(dep_row_id) REFERENCES mods(id) ON DELETE CASCADE
            );
        """)
        await db.commit()

async def get_guild_settings(guild_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT version, loader FROM guild_settings WHERE guild_id = ?", (guild_id,))
        row = await cursor.fetchone()
        if row:
            return {"version": row[0], "loader": row[1]}
        return None

async def set_guild_settings(guild_id, version, loader):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO guild_settings (guild_id, version, loader)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET version=excluded.version, loader=excluded.loader;
        """, (guild_id, version, loader))
        await db.commit()

async def add_mod(guild_id, mod_id, name, url, is_library=False):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO mods (guild_id, mod_id, name, url, is_library)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(guild_id, mod_id) DO UPDATE SET name=excluded.name, url=excluded.url, is_library=excluded.is_library;
        """, (guild_id, mod_id, name, url, int(is_library)))
        await db.commit()

async def get_mods(guild_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM mods WHERE guild_id = ?", (guild_id,))
        return await cursor.fetchall()

async def add_mod_dependency(guild_id, mod_id, dep_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO mod_dependencies (guild_id, mod_row_id, dep_row_id) VALUES (?, ?, ?)", (guild_id, mod_id, dep_id))
        await db.commit()

async def get_mod_dependencies(guild_id, mod_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT dep_row_id FROM mod_dependencies
            WHERE guild_id = ? AND mod_row_id = ?
        """, (guild_id, mod_id))
        return await cursor.fetchall()

async def remove_mod(guild_id, mod_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM mods WHERE guild_id = ? AND mod_id = ?", (guild_id, mod_id))
        await db.execute("DELETE FROM mod_dependencies WHERE guild_id = ? AND mod_row_id = ?", (guild_id, mod_id))
        await db.commit()

async def remove_mod_dependency(guild_id, mod_id, dep_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM mod_dependencies WHERE guild_id = ? AND mod_row_id = ? AND dep_row_id = ?", (guild_id, mod_id, dep_id))
        await db.commit()

async def clear_guild_data(guild_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM guild_settings WHERE guild_id = ?", (guild_id,))
        await db.commit()

async def export_guild_data(guild_id):
    async with aiosqlite.connect(DB_PATH) as db:
        data = {}
        cursor = await db.execute("SELECT * FROM guild_settings WHERE guild_id = ?", (guild_id,))
        data['guild_settings'] = await cursor.fetchall()
        
        cursor = await db.execute("SELECT * FROM mods WHERE guild_id = ?", (guild_id,))
        data['mods'] = await cursor.fetchall()
        
        cursor = await db.execute("SELECT * FROM mod_dependencies WHERE guild_id = ?", (guild_id,))
        data['mod_dependencies'] = await cursor.fetchall()
        
        return json.dumps(data, default=str)
