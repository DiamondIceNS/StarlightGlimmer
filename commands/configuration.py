from discord import TextChannel
from discord.ext import commands

from utils.exceptions import NoPermission
from utils.language import getlang
import utils.sqlite as sql


class Configuration:
    def __init__(self, bot):
        self.bot = bot
        self.langs = {
            'en-US': "English (US)",
            'pt-BR': "Português (BR)",
        }

    @commands.group(name="alertchannel", invoke_without_command=True)
    @commands.guild_only()
    async def alertchannel(self, ctx):
        await ctx.send(getlang(ctx.guild.id, "bot.error.no_subcommand"))

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

    @commands.group(name="setdefaultcanvas", invoke_without_command=True)
    @commands.guild_only()
    async def setdefaultcanvas(self, ctx):
        await ctx.send(getlang(ctx.guild.id, "bot.error.no_subcommand"))

    @setdefaultcanvas.command(name="pixelcanvas")
    @commands.guild_only()
    async def setdefaultcanvas_pixelcanvas(self, ctx):
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        sql.update_guild(ctx.guild.id, default_canvas="pixelcanvas")
        await ctx.send(getlang(ctx.guild.id, "configuration.default_canvas_set").format("Pixelcanvas.io"))

    @setdefaultcanvas.command(name="pixelzio")
    @commands.guild_only()
    async def setdefaultcanvas_pixelzio(self, ctx):
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        sql.update_guild(ctx.guild.id, default_canvas="pixelzio")
        await ctx.send(getlang(ctx.guild.id, "configuration.default_canvas_set").format("Pixelz.io"))

    @setdefaultcanvas.command(name="pixelzone")
    @commands.guild_only()
    async def setdefaultcanvas_pixelzone(self, ctx):
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        sql.update_guild(ctx.guild.id, default_canvas="pixelzone")
        await ctx.send(getlang(ctx.guild.id, "configuration.default_canvas_set").format("Pixelzone.io"))

    @setdefaultcanvas.command(name="pxlsspace")
    @commands.guild_only()
    async def setdefaultcanvas_pxlsspace(self, ctx):
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        sql.update_guild(ctx.guild.id, default_canvas="pxlsspace")
        await ctx.send(getlang(ctx.guild.id, "configuration.default_canvas_set").format("Pxls.space"))

    @commands.command()
    @commands.guild_only()
    async def language(self, ctx, option=None):
        if not option:
            lang_list = ""
            for i, (code, name) in enumerate(self.langs.items(), 1):
                lang_list = lang_list + "{0} - {1}".format(code, name)
                if i < len(self.langs):
                    lang_list = lang_list + "\n"
            current_lang = self.langs[sql.get_guild_language(ctx.guild.id)]
            await ctx.send(getlang(ctx.guild.id, "configuration.language_list").format(lang_list, current_lang))
            return
        if option not in self.langs:
            await ctx.send(getlang(ctx.guild.id, "configuration.language_invalid"))
            return
        sql.update_guild(ctx.guild.id, language=option)
        await ctx.send(getlang(ctx.guild.id, "configuration.language_set"))


def setup(bot):
    bot.add_cog(Configuration(bot))
