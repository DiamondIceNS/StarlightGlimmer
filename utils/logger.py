import logging
from utils.config import Config

cfg = Config()


class Log:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename='data/discord.log', encoding='utf-8', mode='a')
        handler.setFormatter(logging.Formatter('{asctime} [{levelname}] {name}: {message}', style='{'))
        self.logger.addHandler(handler)

    def command(self, cmd, author, guild, autoscan=False, repeat=False):
        invocation_type = "I"
        if autoscan:
            invocation_type = "A"
        if repeat:
            invocation_type = invocation_type + "R"
        self.debug("[{0}] {1.name}#{1.discriminator} used '{2}' in {3.name} (UID:{1.id} GID:{3.id})"
                   .format(invocation_type, author, cmd, guild))

    def debug(self, msg):
        if cfg.debug:
            self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)
