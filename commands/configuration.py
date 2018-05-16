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
    async def prefix(self, ctx, prefix):
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        if len(prefix) > 5:
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

    @commands.group(name="canvas", invoke_without_command=True)
    @commands.guild_only()
    async def canvas(self, ctx):
        g = sql.select_guild_by_id(ctx.guild.id)
        c = {
            'pixelcanvas': 'Pixelcanvas.io',
            'pixelzio': 'Pixelz.io',
            'pixelzone': 'Pixelzone.io',
            'pxlsspace': 'Pxls.space'
        }[g['default_canvas']]
        await ctx.send(getlang(ctx.guild.id, "configuration.canvas_check").format(c, g['prefix']))

    @canvas.command(name="pixelcanvas", aliases=["pc"])
    @commands.guild_only()
    async def canvas_pixelcanvas(self, ctx):
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        sql.update_guild(ctx.guild.id, default_canvas="pixelcanvas")
        await ctx.send(getlang(ctx.guild.id, "configuration.canvas_set").format("Pixelcanvas.io"))

    @canvas.command(name="pixelzio", aliases=["pzi"])
    @commands.guild_only()
    async def canvas_pixelzio(self, ctx):
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        sql.update_guild(ctx.guild.id, default_canvas="pixelzio")
        await ctx.send(getlang(ctx.guild.id, "configuration.canvas_set").format("Pixelz.io"))

    @canvas.command(name="pixelzone", aliases=["pz"])
    @commands.guild_only()
    async def canvas_pixelzone(self, ctx):
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        sql.update_guild(ctx.guild.id, default_canvas="pixelzone")
        await ctx.send(getlang(ctx.guild.id, "configuration.canvas_set").format("Pixelzone.io"))

    @canvas.command(name="pxlsspace", aliases=["ps"])
    @commands.guild_only()
    async def canvas_pxlsspace(self, ctx):
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        sql.update_guild(ctx.guild.id, default_canvas="pxlsspace")
        await ctx.send(getlang(ctx.guild.id, "configuration.canvas_set").format("Pxls.space"))

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
            await ctx.send(getlang(ctx.guild.id, "configuration.language_check").format(lang_list, current_lang))
            return
        if option not in self.langs:
            await ctx.send(getlang(ctx.guild.id, "configuration.language_invalid"))
            return
        sql.update_guild(ctx.guild.id, language=option)
        await ctx.send(getlang(ctx.guild.id, "configuration.language_set").format(self.langs[option]))


def setup(bot):
    bot.add_cog(Configuration(bot))
