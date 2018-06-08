import sqlite3
import os
import time

from objects.config import Config
from objects.template import Template
from utils.version import VERSION

if not os.path.exists('data'):
    os.makedirs('data')
conn = sqlite3.connect('data/glimmer.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()
cfg = Config()


def _create_tables():
    c.execute("""CREATE TABLE IF NOT EXISTS animote_users(id INTEGER);""")
    c.execute("""
        CREATE TABLE IF NOT EXISTS guilds(
          id                  INTEGER
            PRIMARY KEY,
          name                TEXT    NOT NULL,
          join_date           INTEGER NOT NULL,
          prefix              TEXT    DEFAULT NULL,
          alert_channel       INTEGER DEFAULT NULL,
          emojishare          INTEGER DEFAULT 0 NOT NULL,
          autoscan            INTEGER DEFAULT 1 NOT NULL,
          canvas              TEXT    DEFAULT 'pixelcanvas' NOT NULL,
          language            TEXT    DEFAULT 'en-us' NOT NULL,
          template_admin      INTEGER DEFAULT NULL,
          template_adder      INTEGER DEFAULT NULL,
          bot_admin           INTEGER DEFAULT NULL
        );
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS menu_locks(
          channel_id INTEGER NOT NULL,
          user_id    INTEGER NOT NULL,
          date_added INTEGER NOT NULL,
          CONSTRAINT menu_locks_pk
          PRIMARY KEY (channel_id, user_id)
        );
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS templates(
          guild_id      INTEGER NOT NULL
            CONSTRAINT templates_guilds_id_fk
            REFERENCES guilds,
          name          TEXT    NOT NULL,
          url           TEXT    NOT NULL,
          canvas        TEXT    NOT NULL,
          x             INTEGER NOT NULL,
          y             INTEGER NOT NULL,
          w             INTEGER NOT NULL,
          h             INTEGER NOT NULL,
          date_added    INTEGER NOT NULL,
          date_modified INTEGER NOT NULL,
          md5           TEXT    NOT NULL,
          owner         INTEGER NOT NULL,
          CONSTRAINT templates_pk
          PRIMARY KEY (guild_id, name)
        );
    """)
    c.execute("""
      CREATE TABLE IF NOT EXISTS version(
        id      INTEGER
          PRIMARY KEY,
        version REAL,
        CHECK (id = 1)
      );
    """)


def _update_tables(v):
    if v is not None:
        if v < 1.2:
            c.execute("""ALTER TABLE guilds ADD COLUMN language TEXT NOT NULL DEFAULT 'en_us' """)
        if v < 1.3:
            c.execute("""UPDATE guilds SET default_canvas='pixelcanvas' WHERE default_canvas='pixelcanvas.io'""")
            c.execute("""UPDATE guilds SET default_canvas='pixelzio' WHERE default_canvas='pixelz.io'""")
            c.execute("""UPDATE guilds SET default_canvas='pixelzone' WHERE default_canvas='pixelzone.io'""")
        if v < 1.4:
            c.execute("""UPDATE guilds SET language='en-US' WHERE language='en_US'""")
        if v < 1.5:
            c.executescript("""
                UPDATE guilds SET language = LOWER(language);
                PRAGMA FOREIGN_KEYS = OFF;
                BEGIN TRANSACTION;
                ALTER TABLE guilds RENAME TO temp_guilds;
                CREATE TABLE guilds
                (
                  id                  INTEGER
                    PRIMARY KEY,
                  name                TEXT    NOT NULL,
                  join_date           INTEGER NOT NULL,
                  prefix              TEXT    DEFAULT NULL,
                  alert_channel       INTEGER DEFAULT NULL,
                  emojishare          INTEGER DEFAULT 0 NOT NULL,
                  autoscan            INTEGER DEFAULT 1 NOT NULL,
                  canvas              TEXT    DEFAULT 'pixelcanvas' NOT NULL,
                  language            TEXT    DEFAULT 'en-us' NOT NULL,
                  template_admin      INTEGER DEFAULT NULL,
                  template_adder      INTEGER DEFAULT NULL,
                  bot_admin           INTEGER DEFAULT NULL
                );
                INSERT INTO guilds(id, name, join_date, prefix, alert_channel, emojishare, autoscan, canvas, language)
                  SELECT id, name, join_date, prefix, alert_channel, emojishare, autoscan, default_canvas, language
                  FROM temp_guilds;
                DROP TABLE temp_guilds;
                COMMIT;
                PRAGMA FOREIGN_KEYS = ON;
            """)


# ================================
#      Animotes Users queries
# ================================

def animotes_users_add(uid):
    c.execute("""INSERT INTO animote_users(id) VALUES(?)""", (uid,))
    conn.commit()


def animotes_users_delete(uid):
    c.execute("""DELETE FROM animote_users WHERE id=?""", (uid,))
    conn.commit()


def animotes_users_is_registered(uid):
    c.execute("""SELECT * FROM animote_users WHERE id=?""", (uid,))
    return c.fetchone() is not None


# ========================
#      Guilds queries
# ========================

def guild_add(gid, name, join_date):
    c.execute("INSERT INTO guilds(id, name, join_date, canvas, language) VALUES(?, ?, ?, ?, ?)",
              (gid, name, join_date, "pixelcanvas", "en-us"))
    conn.commit()


def guild_delete(gid):
    c.execute("""DELETE FROM guilds WHERE id=?""", (gid,))
    conn.commit()


def guild_delete_role(role_id):
    c.execute("UPDATE guilds SET bot_admin=NULL WHERE bot_admin=?", (role_id,))
    c.execute("UPDATE guilds SET template_adder=NULL WHERE template_adder=?", (role_id,))
    c.execute("UPDATE guilds SET template_admin=NULL WHERE template_admin=?", (role_id,))
    conn.commit()


def guild_get_all():
    c.execute("SELECT * FROM guilds")
    return c.fetchall()


def guild_get_by_id(gid):
    c.execute("SELECT * FROM guilds WHERE id=?", (gid,))
    return c.fetchone()


def guild_get_canvas_by_id(gid):
    c.execute("SELECT canvas FROM guilds WHERE id=?", (gid,))
    ca = c.fetchone()
    return ca[0] if ca else None


def guild_get_language_by_id(gid):
    c.execute("""SELECT language FROM guilds WHERE id=?""", (gid,))
    g = c.fetchone()
    return g[0] if c else None


def guild_get_prefix_by_id(gid):
    g = guild_get_by_id(gid)
    return g['prefix'] if g and g['prefix'] else cfg.prefix


def guild_is_autoscan(gid):
    c.execute("SELECT autoscan FROM guilds WHERE id=?", (gid,))
    return bool(c.fetchone())


def guild_is_emojishare(gid):
    c.execute("""SELECT emojishare FROM guilds WHERE id=?""", (gid,))
    return bool(c.fetchone())


def guild_update(gid, name=None, prefix=None, alert_channel=None, emojishare=None, autoscan=None, canvas=None,
                 language=None, template_admin=None, template_adder=None, bot_admin=None):
    if name:
        c.execute("UPDATE guilds SET name=? WHERE id=?", (name, gid))
    if prefix:
        c.execute("UPDATE guilds SET prefix=? WHERE id=?", (prefix, gid))
    if alert_channel:
        c.execute("UPDATE guilds SET alert_channel=? WHERE id=?", (alert_channel, gid))
    if emojishare:
        c.execute("UPDATE guilds SET emojishare=? WHERE id=?", (emojishare, gid))
    if autoscan:
        c.execute("UPDATE guilds SET autoscan=? WHERE id=?", (autoscan, gid))
    if canvas:
        c.execute("UPDATE guilds SET canvas=? WHERE id=?", (canvas, gid))
    if language:
        c.execute("UPDATE guilds SET language=? WHERE id=?", (language, gid))
    if template_admin:
        c.execute("UPDATE guilds SET template_admin=? WHERE id=?", (template_admin, gid))
    if template_adder:
        c.execute("UPDATE guilds SET template_adder=? WHERE id=?", (template_adder, gid))
    if bot_admin:
        c.execute("UPDATE guilds SET bot_admin=? WHERE id=?", (bot_admin, gid))
    conn.commit()


# ============================
#      Menu Locks queries
# ============================

def menu_locks_add(cid, uid):
    c.execute('INSERT INTO menu_locks(channel_id, user_id, date_added) VALUES(?, ?, ?)', (cid, uid, int(time.time())))
    conn.commit()


def menu_locks_delete(cid, uid):
    c.execute('DELETE FROM menu_locks WHERE channel_id=? AND user_id=?', (cid, uid))
    conn.commit()


def menu_locks_delete_all():
    c.execute('DELETE FROM menu_locks')
    conn.commit()


def menu_locks_get_all():
    c.execute('SELECT * FROM menu_locks')
    return c.fetchall()


# ===========================
#      Templates queries
# ===========================

def template_add(template):
    c.execute('INSERT INTO templates(guild_id, name, url, canvas, x, y, w, h, date_added, date_modified, md5, owner)'
              'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', template.to_tuple())
    conn.commit()


def template_count_by_guild_id(gid):
    c.execute('SELECT COUNT(*) FROM templates WHERE guild_id=?', (gid,))
    ct = c.fetchone()
    return ct[0] if ct else 0


def template_delete(gid, name):
    c.execute('DELETE FROM templates WHERE guild_id=? AND name=?', (gid, name))
    conn.commit()


def template_get_all_by_guild_id(gid):
    c.execute('SELECT * FROM templates WHERE guild_id=? ORDER BY name DESC, canvas DESC', (gid,))
    templates = []
    for t in c.fetchall():
        templates.append(Template(*t))
    return templates


def template_get_by_hash(gid, md5):
    c.execute('SELECT * FROM templates WHERE guild_id=? AND md5=?', (gid, md5))
    templates = []
    for t in c.fetchall():
        templates.append(Template(*t))
    return templates


def template_get_by_name(gid, name):
    c.execute('SELECT * FROM templates WHERE guild_id=? AND name=?', (gid, name))
    t = c.fetchone()
    return Template(*t) if t else None


def template_update(template):
    c.execute('UPDATE templates '
              'SET url = ?, canvas=?, x=?, y=?, w=?, h=?, date_added=?, date_modified=?, md5=?, owner=?'
              'WHERE guild_id=? AND name=?', template.to_tuple()[2:] + (template.gid, template.name))
    conn.commit()


# =========================
#      Version queries
# =========================

def version_get():
    v = c.execute("""SELECT version FROM version""")
    if not v:
        version_init(VERSION)
        return VERSION
    return c.fetchone()[0]


def version_init(version):
    print("version initialized to {}".format(version))
    c.execute("""INSERT INTO version(version) VALUES(?)""", (version,))
    conn.commit()


def version_update(version):
    print("updated to {}".format(version))
    c.execute("""UPDATE version SET version=?""", (version,))
    conn.commit()


_create_tables()
_update_tables(version_get())
