from discord.ext import commands
from discord.ext.commands import BucketType
from time import time

from objects.channel_logger import ChannelLogger
from objects.config import Config
from objects.logger import Log
from utils.version import VERSION


class General:
    def __init__(self, bot):
        self.bot = bot
        self.ch_log = ChannelLogger(bot)
        self.cfg = Config()
        self.log = Log(__name__)

    @commands.command()
    async def changelog(self, ctx):
        await ctx.send("https://github.com/DiamondIceNS/StarlightGlimmer/releases")

    @commands.command()
    async def github(self, ctx):
        await ctx.send("https://github.com/DiamondIceNS/StarlightGlimmer")

    @commands.command()
    async def invite(self, ctx):
        await ctx.send(self.cfg.invite)

    @commands.command()
    async def ping(self, ctx):
        ping_start = time()
        ping_msg = await ctx.send(ctx.get_str("bot.ping"))
        ping_time = time() - ping_start
        self.log.debug("(Ping:{0}ms)".format(int(ping_time * 1000)))
        await ping_msg.edit(content=ctx.get_str("bot.pong").format(int(ping_time * 1000)))

    @commands.cooldown(1, 5, BucketType.guild)
    @commands.command()
    async def suggest(self, ctx, *, suggestion: str):
        self.log.debug("Suggestion: {0}".format(suggestion))
        await self.ch_log.log("New suggestion from **{0.name}#{0.discriminator}** (ID: `{0.id}`) in guild "
                              "**{1.name}** (ID: `{1.id}`):".format(ctx.author, ctx.guild))
        await self.ch_log.log("> `{}`".format(suggestion))
        await ctx.send(ctx.get_str("bot.suggest"))

    @commands.command()
    async def version(self, ctx):
        await ctx.send(ctx.get_str("bot.version").format(VERSION))


def setup(bot):
    bot.add_cog(General(bot))
