from discord import TextChannel
from discord.ext import commands

from utils.exceptions import NoPermission
from utils.language import getlang, langs
import utils.sqlite as sql
from utils.logger import Log


class Configuration:
    def __init__(self, bot):
        self.bot = bot
        self.log = Log(__name__)

    @commands.group(name="alertchannel", invoke_without_command=True)
    @commands.guild_only()
    async def alertchannel(self, ctx):
        pass

    @alertchannel.command(name="set")
    @commands.guild_only()
    async def alertchannel_set(self, ctx, channel: TextChannel):
        self.log.command("alertchannel set", ctx.author, ctx.guild)
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        sql.update_guild(ctx.guild.id, alert_channel=channel.id)
        self.log.info("Alert channel for {0.name} set to {1.name} (GID:{0.id} CID:{1.name})".format(ctx.guild, channel))
        await ctx.send(getlang(ctx.guild.id, "configuration.alert_channel_set").format(channel.mention))

    @alertchannel.command(name="clear")
    @commands.guild_only()
    async def alertchannel_clear(self, ctx):
        self.log.command("alertchannel clear", ctx.author, ctx.guild)
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        sql.update_guild(ctx.guild.id, alert_channel=0)
        self.log.info("Alert channel for {0.name} cleared (GID:{0.id})".format(ctx.guild))
        await ctx.send(getlang(ctx.guild.id, "configuration.alert_channel_cleared"))

    @commands.command()
    @commands.guild_only()
    async def prefix(self, ctx, prefix):
        self.log.command("prefix", ctx.author, ctx.guild)
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        if len(prefix) > 5:
            raise commands.BadArgument
        sql.update_guild(ctx.guild.id, prefix=prefix)
        self.log.info("Prefix for {0.name} set to {1} (GID: {0.id})".format(ctx.guild, prefix))
        await ctx.send(getlang(ctx.guild.id, "configuration.prefix_set").format(prefix))

    @commands.command()
    @commands.guild_only()
    async def autoscan(self, ctx):
        self.log.command("autoscan", ctx.author, ctx.guild)
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        if sql.select_guild_by_id(ctx.guild.id)['autoscan'] == 0:
            sql.update_guild(ctx.guild.id, autoscan=1)
            self.log.info("Autoscan enabled for {0.name} (GID: {0.id})".format(ctx.guild))
            await ctx.send(getlang(ctx.guild.id, "configuration.autoscan_enabled"))
        else:
            sql.update_guild(ctx.guild.id, autoscan=0)
            self.log.info("Autoscan disabled for {0.name} (GID: {0.id})".format(ctx.guild))
            await ctx.send(getlang(ctx.guild.id, "configuration.autoscan_disabled"))

    @commands.group(name="canvas", invoke_without_command=True)
    @commands.guild_only()
    async def canvas(self, ctx):
        self.log.command("canvas", ctx.author, ctx.guild)
        g = sql.select_guild_by_id(ctx.guild.id)
        c = {
            'pixelcanvas': 'Pixelcanvas.io',
            'pixelzio': 'Pixelz.io',
            'pixelzone': 'Pixelzone.io',
            'pxlsspace': 'Pxls.space'
        }[g['default_canvas']]
        await ctx.send(getlang(ctx.guild.id, "configuration.canvas_check")
                       .format(c, sql.get_guild_prefix(ctx.guild.id)))

    @canvas.command(name="pixelcanvas", aliases=["pc"])
    @commands.guild_only()
    async def canvas_pixelcanvas(self, ctx):
        self.log.command("canvas pixelcanvas", ctx.author, ctx.guild)
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        sql.update_guild(ctx.guild.id, default_canvas="pixelcanvas")
        self.log.info("Default canvas for {0.name} set to pixelcanvas (GID:{0.id})".format(ctx.guild))
        await ctx.send(getlang(ctx.guild.id, "configuration.canvas_set").format("Pixelcanvas.io"))

    @canvas.command(name="pixelzio", aliases=["pzi"])
    @commands.guild_only()
    async def canvas_pixelzio(self, ctx):
        self.log.command("canvas pixelzio", ctx.author, ctx.guild)
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        sql.update_guild(ctx.guild.id, default_canvas="pixelzio")
        self.log.info("Default canvas for {0.name} set to pixelzio (GID:{0.id})".format(ctx.guild))
        await ctx.send(getlang(ctx.guild.id, "configuration.canvas_set").format("Pixelz.io"))

    @canvas.command(name="pixelzone", aliases=["pz"])
    @commands.guild_only()
    async def canvas_pixelzone(self, ctx):
        self.log.command("canvas pixelzone", ctx.author, ctx.guild)
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        sql.update_guild(ctx.guild.id, default_canvas="pixelzone")
        self.log.info("Default canvas for {0.name} set to pixelzone (GID:{0.id})".format(ctx.guild))
        await ctx.send(getlang(ctx.guild.id, "configuration.canvas_set").format("Pixelzone.io"))

    @canvas.command(name="pxlsspace", aliases=["ps"])
    @commands.guild_only()
    async def canvas_pxlsspace(self, ctx):
        self.log.command("canvas pxlsspace", ctx.author, ctx.guild)
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        sql.update_guild(ctx.guild.id, default_canvas="pxlsspace")
        self.log.info("Default canvas for {0.name} set to pxlsspace (GID:{0.id})".format(ctx.guild))
        await ctx.send(getlang(ctx.guild.id, "configuration.canvas_set").format("Pxls.space"))

    @commands.command()
    @commands.guild_only()
    async def language(self, ctx, option=None):
        self.log.command("language", ctx.author, ctx.guild)
        if not option:
            lang_list = ""
            for i, (code, name) in enumerate(langs.items(), 1):
                lang_list = lang_list + "{0} - {1}".format(code, name)
                if i < len(langs):
                    lang_list = lang_list + "\n"
            current_lang = langs[sql.get_guild_language(ctx.guild.id).lower()]
            await ctx.send(getlang(ctx.guild.id, "configuration.language_check").format(lang_list, current_lang))
            return
        if option.lower() not in langs:
            return
        sql.update_guild(ctx.guild.id, language=option.lower())
        self.log.info("Language for {0.name} set to {1} (GID:{0.id})".format(ctx.guild, option.lower()))
        await ctx.send(getlang(ctx.guild.id, "configuration.language_set").format(langs[option.lower()]))


def setup(bot):
    bot.add_cog(Configuration(bot))
