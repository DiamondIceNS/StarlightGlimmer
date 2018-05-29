import sqlite3
import os
import time

from utils.config import Config
from objects.template import Template

if not os.path.exists('data'):
    os.makedirs('data')
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
                        default_canvas TEXT NOT NULL DEFAULT "pixelcanvas",
                        language TEXT NOT NULL DEFAULT "en-US"
                    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS version(id INTEGER PRIMARY KEY CHECK (id = 1), version REAL)""")

    c.execute("""CREATE TABLE IF NOT EXISTS animote_users(id INTEGER)""")


def update_tables(v):
    # print("updating tables... "+v)
    if v is not None:
        if v < 1.2:
            c.execute("""ALTER TABLE guilds ADD COLUMN language TEXT NOT NULL DEFAULT "en_US" """)
        if v < 1.3:
            c.execute("""UPDATE guilds SET default_canvas='pixelcanvas' WHERE default_canvas='pixelcanvas.io'""")
            c.execute("""UPDATE guilds SET default_canvas='pixelzio' WHERE default_canvas='pixelz.io'""")
            c.execute("""UPDATE guilds SET default_canvas='pixelzone' WHERE default_canvas='pixelzone.io'""")
        if v < 1.4:
            c.execute("""UPDATE guilds SET language='en-US' WHERE language='en_US'""")


def add_guild(gid, name, join_date):
    c.execute("""INSERT INTO guilds(id, name, join_date, default_canvas, language) VALUES(?, ?, ?, ?, ?)""",
              (gid, name, join_date, "pixelcanvas", "en-US"))
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


def update_guild(gid, name=None, prefix=None, alert_channel=None, emojishare=None, autoscan=None, default_canvas=None,
                 language=None):
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
    if language is not None:
        c.execute("""UPDATE guilds SET language=? WHERE id=?""", (language, gid))
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


def init_version(version):
    print("version initialized to {}".format(version))
    c.execute("""INSERT INTO version(version) VALUES(?)""", (version,))
    conn.commit()


def update_version(version):
    print("updated to {}".format(version))
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


def get_guild_language(gid):
    c.execute("""SELECT language FROM guilds WHERE id=?""", (gid,))
    return c.fetchone()[0]


def get_guild_prefix(gid):
    row = select_guild_by_id(gid)
    if row is not None and row['prefix'] is not None:
        return row['prefix']
    return cfg.prefix


def get_template_by_name(gid, name):
    c.execute('SELECT * FROM templates WHERE guild_id=? AND name=?', (gid, name))
    try:
        return Template(*c.fetchone())
    except:
        return None


def get_templates_by_hash(gid, md5):
    c.execute('SELECT * FROM templates WHERE guild_id=? AND md5=?', (gid, md5))
    try:
        templates = []
        for t in c.fetchall():
            templates.append(Template(*t))
        return templates
    except:
        return None


def get_templates_by_guild(gid):
    c.execute('SELECT * FROM templates WHERE guild_id=?', (gid,))
    try:
        templates = []
        for t in c.fetchall():
            templates.append(Template(*t))
        return templates
    except:
        return None


def add_template(template):
    c.execute('INSERT INTO templates(guild_id, name, url, canvas, x, y, w, h, date_added, date_modified, md5, owner)'
              'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', template.to_tuple())
    conn.commit()


def update_template(template):
    c.execute('UPDATE templates '
              'SET url = ?, canvas=?, x=?, y=?, w=?, h=?, date_added=?, date_modified=?, md5=?, owner=?'
              'WHERE guild_id=? AND name=?', template.to_tuple()[2:] + (template.gid, template.name))
    conn.commit()


def drop_template(gid, name):
    c.execute('DELETE FROM templates WHERE guild_id=? AND name=?', (gid, name))
    conn.commit()


def count_templates(gid):
    c.execute('SELECT COUNT(*) FROM templates WHERE guild_id=?', (gid,))
    return c.fetchone()[0]


def add_menu_lock(cid, uid):
    c.execute('INSERT INTO menu_locks(channel_id, user_id, date_added) VALUES(?, ?, ?)', (cid, uid, int(time.time())))
    conn.commit()


def remove_menu_lock(cid, uid):
    c.execute('DELETE FROM menu_locks WHERE channel_id=? AND user_id=?', (cid, uid))
    conn.commit()


def get_menu_locks():
    c.execute('SELECT * FROM menu_locks')
    return c.fetchall()


def reset_locks():
    c.execute('DELETE FROM menu_locks')
    conn.commit()


create_tables()
update_tables(get_version())
