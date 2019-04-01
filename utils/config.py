import json
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys

log = logging.getLogger()
handler = TimedRotatingFileHandler(filename='data/discord.log', encoding='utf-8', when='midnight', backupCount=7)
handler.setFormatter(logging.Formatter('{asctime} [{levelname}] {name}: {message}', style='{'))
log.addHandler(handler)


def clamp(n, lowest, highest):
    return max(lowest, min(highest, n))


if not os.path.isfile('config/config.json'):
    if not os.path.isfile('config/config.json.example'):
        log.critical("config/config.json could not be found! Please get the example copy from GitHub and "
                     "rename it to config.json!")
        sys.exit(1)
    else:
        log.critical("config/config.json could not be found! (Did you rename config/config.json.example to "
                     "config/config.json yet?)")
        sys.exit(1)

config_file = "config/config.json"
with open(config_file, "r+") as j:
    data = json.load(j)

TOKEN = data.get('token', None)
PREFIX = data.get('prefix', "g!")
NAME = data.get('name', 'Starlight Glimmer')
INVITE = data.get('invite', "https://discordapp.com/oauth2/authorize?&client_id=405480380930588682&scope"
                                 "=bot&permissions=35840")
PZ_API_KEY = data.get('pixelzone_api_key', None)

PREVIEW_H = clamp(data.get('preview_height', 240), 0, 896)
PREVIEW_W = clamp(data.get('preview_width', 400), 0, 896)
MAX_TEMPLATES_PER_GUILD = clamp(data.get('max_templates_per_guild'), 1, data.get('max_templates_per_guild'))
MAX_TEMPLATE_NAME_LENGTH = clamp(data.get('max_template_name_length'), 1, 64)

LOGGING_CHANNEL_ID = data.get('logging_channel_id', None)
CHANNEL_LOG_GUILD_RENAMES = data.get('channel_log_guild_renames', False)
CHANNEL_LOG_GUILD_JOINS = data.get('channel_log_guild_joins', False)
CHANNEL_LOG_GUILD_KICKS = data.get('channel_log_guild_kicks', False)

INVERT = data.get('invert', False)

if data.get('debug', False):
    log.setLevel(logging.DEBUG)
else:
    log.setLevel(logging.INFO)

if TOKEN is None:
    log.critical("No bot token was specified!")
    sys.exit(1)
