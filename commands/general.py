from time import time

from discord.ext import commands
from discord.ext.commands import BucketType

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
    async def help(self, ctx, *commands: str):
        """Shows this message."""
        bot = ctx.bot

        def repl(obj):
            return ctx.bot._mentions_transforms.get(obj.group(0), '')

        # help by itself just lists our own commands.
        if len(commands) == 0:
            out = await self.bot.formatter.format_help_for(ctx, self.bot)

        elif len(commands) == 1:
            # try to see if it is a cog name
            # name = _mention_pattern.sub(repl, commands[0])  # TODO: Filter @everyone here?
            name = commands[0]
            command = bot.all_commands.get(name)
            if command is None:
                await ctx.send(bot.command_not_found.format(name))
                return

            out = await self.bot.formatter.format_help_for(ctx, command)

        else:
            # name = _mention_pattern.sub(repl, commands[0])
            name = commands[0]
            command = bot.all_commands.get(name)
            if command is None:
                await ctx.send(bot.command_not_found.format(name))
                return
            for key in commands[1:]:
                try:
                    # key = _mention_pattern.sub(repl, key)
                    command = command.all_commands.get(key)
                    if command is None:
                        await ctx.send(bot.command_not_found.format(key))
                        return
                except AttributeError:
                    await ctx.send(bot.command_has_no_subcommands.format(command, key))
                    return
            out = await bot.formatter.format_help_for(ctx, command)

        if out:
            await ctx.send('\n'.join(out))

    @commands.command()
    async def invite(self, ctx):
        await ctx.send(self.cfg.invite)

    @commands.command()
    async def ping(self, ctx):
        ping_start = time()
        ping_msg = await ctx.send(ctx.get("bot.ping"))
        ping_time = time() - ping_start
        self.log.debug("(Ping:{0}ms)".format(int(ping_time * 1000)))
        await ping_msg.edit(content=ctx.get("bot.pong").format(int(ping_time * 1000)))

    @commands.cooldown(1, 5, BucketType.guild)
    @commands.command()
    async def suggest(self, ctx, *, suggestion: str):
        self.log.debug("Suggestion: {0}".format(suggestion))
        await self.ch_log.log("New suggestion from **{0.name}#{0.discriminator}** (ID: `{0.id}`) in guild "
                              "**{1.name}** (ID: `{1.id}`):".format(ctx.author, ctx.guild))
        await self.ch_log.log("> `{}`".format(suggestion))
        await ctx.send(ctx.get(ctx.guild.id, "bot.suggest"))

    @commands.command()
    async def version(self, ctx):
        await ctx.send(ctx.get("bot.version").format(VERSION))


def setup(bot):
    bot.add_cog(General(bot))
