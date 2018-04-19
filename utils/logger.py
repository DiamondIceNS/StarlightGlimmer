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
