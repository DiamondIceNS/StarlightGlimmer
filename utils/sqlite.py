import sqlite3

from utils.config import Config

conn = sqlite3.connect('data/glimmer.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()
cfg = Config()


def create_tables():
    c.execute("""CREATE TABLE IF NOT EXISTS guilds(
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        join_date INTEGER,
                        prefix TEXT,
                        alert_channel INTEGER,
                        emojishare INTEGER NOT NULL DEFAULT 0,
                        autoscan INTEGER NOT NULL DEFAULT 1,
                        default_canvas TEXT NOT NULL DEFAULT "pixelcanvas.io"
                    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS version(id INTEGER PRIMARY KEY CHECK (id = 1), version REAL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS animote_users(id INTEGER)""")


def add_guild(gid, name, join_date):
    c.execute("""INSERT INTO guilds(id, name, join_date) VALUES(?, ?, ?)""", (gid, name, join_date))
    conn.commit()


def select_guild_by_id(gid):
    c.execute("""SELECT * FROM guilds WHERE id=?""", (gid,))
    try:
        return c.fetchone()
    except:
        return None


def get_all_guilds():
    c.execute("""SELECT * FROM guilds""")
    return c.fetchall()


def update_guild(gid, name=None, prefix=None, alert_channel=None, emojishare=None, autoscan=None, default_canvas=None):
    if name is not None:
        c.execute("""UPDATE guilds SET name=? WHERE id=?""", (name, gid))
    if prefix is not None:
        c.execute("""UPDATE guilds SET prefix=? WHERE id=?""", (prefix, gid))
    if alert_channel is not None:
        c.execute("""UPDATE guilds SET alert_channel=? WHERE id=?""", (alert_channel, gid))
    if emojishare is not None:
        c.execute("""UPDATE guilds SET emojishare=? WHERE id=?""", (emojishare, gid))
    if autoscan is not None:
        c.execute("""UPDATE guilds SET autoscan=? WHERE id=?""", (autoscan, gid))
    if default_canvas is not None:
        c.execute("""UPDATE guilds SET default_canvas=? WHERE id=?""", (default_canvas, gid))
    conn.commit()


def delete_guild(gid):
    c.execute("""DELETE FROM guilds WHERE id=?""", (gid,))
    conn.commit()


def get_version():
    c.execute("""SELECT version FROM version""")
    result = c.fetchone()
    if result is None:
        return None
    return result[0]


def update_version(version):
    c.execute("""UPDATE version SET version=?""", (version,))
    conn.commit()


def add_animote_user(uid):
    c.execute("""INSERT INTO animote_users(id) VALUES(?)""", (uid,))
    conn.commit()


def delete_animote_user(uid):
    c.execute("""DELETE FROM animote_users WHERE id=?""", (uid,))
    conn.commit()


def is_user_animote_user(uid):
    c.execute("""SELECT * FROM animote_users WHERE id=?""", (uid,))
    return c.fetchone() is not None


def is_server_emojishare_server(gid):
    c.execute("""SELECT * FROM guilds WHERE id=? AND emojishare=1""", (gid,))
    return c.fetchone() is not None


create_tables()
