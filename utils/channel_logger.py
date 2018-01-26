import discord
import time

from utils.logger import Log
from utils.config import Config

log = Log(__name__)
cfg = Config()


class ChannelLogger:
    def __init__(self, bot):
        self.bot = bot

    async def log_to_channel(self, msg):
        if cfg.logging_channel_id is not None:
            channel = self.bot.get_channel(cfg.logging_channel_id)
            if not channel:
                log.warning("Can't find logging channel")
            else:
                try:
                    await channel.send("`{}` {}".format(time.strftime('%H:%M:%S', time.localtime()), msg))
                except discord.errors.Forbidden:
                    log.warning("Forbidden from logging channel!")
