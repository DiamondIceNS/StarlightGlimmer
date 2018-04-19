from discord import TextChannel
from discord.ext import commands

from utils.exceptions import NoPermission
from utils.language import getlang
import utils.sqlite as sql


class Configuration:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="alertchannel")
    @commands.guild_only()
    async def alertchannel(self, ctx):
        pass

    @alertchannel.command(name="set")
    @commands.guild_only()
    async def alertchannel_set(self, ctx, channel: TextChannel):
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        sql.update_guild(ctx.guild.id, alert_channel=channel.id)
        await ctx.send(getlang(ctx.guild.id, "configuration.alert_channel_set").format(channel.mention))

    @alertchannel.command(name="clear")
    @commands.guild_only()
    async def alertchannel_clear(self, ctx):
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        sql.update_guild(ctx.guild.id, alert_channel=0)
        await ctx.send(getlang(ctx.guild.id, "configuration.alert_channel_cleared"))

    @commands.command()
    @commands.guild_only()
    async def setprefix(self, ctx, prefix):
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        if len(prefix) > 10:
            raise commands.BadArgument
        sql.update_guild(ctx.guild.id, prefix=prefix)
        await ctx.send(getlang(ctx.guild.id, "configuration.prefix_set").format(prefix))

    @commands.command()
    @commands.guild_only()
    async def autoscan(self, ctx):
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        if sql.select_guild_by_id(ctx.guild.id)['autoscan'] == 0:
            sql.update_guild(ctx.guild.id, autoscan=1)
            await ctx.send(getlang(ctx.guild.id, "configuration.autoscan_enabled"))
        else:
            sql.update_guild(ctx.guild.id, autoscan=0)
            await ctx.send(getlang(ctx.guild.id, "configuration.autoscan_disabled"))

    @commands.group(name="setdefaultcanvas")
    @commands.guild_only()
    async def setdefaultcanvas(self, ctx):
        pass  # TODO

    @setdefaultcanvas.command(name="pixelcanvas")
    @commands.guild_only()
    async def setdefaultcanvas_pixelcanvas(self, ctx):
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        sql.update_guild(ctx.guild.id, default_canvas="pixelcanvas.io")
        await ctx.send(getlang(ctx.guild.id, "configuration.default_canvas_set").format("Pixelcanvas.io"))

    @setdefaultcanvas.command(name="pixelzio")
    @commands.guild_only()
    async def setdefaultcanvas_pixelzio(self, ctx):
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        sql.update_guild(ctx.guild.id, default_canvas="pixelz.io")
        await ctx.send(getlang(ctx.guild.id, "configuration.default_canvas_set").format("Pixelz.io"))

    @setdefaultcanvas.command(name="pixelzone")
    @commands.guild_only()
    async def setdefaultcanvas_pixelzone(self, ctx):
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        sql.update_guild(ctx.guild.id, default_canvas="pixelzone.io")
        await ctx.send(getlang(ctx.guild.id, "configuration.default_canvas_set").format("Pixelzone.io"))


def setup(bot):
    bot.add_cog(Configuration(bot))
