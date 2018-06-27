import re

from discord import TextChannel
from discord.ext import commands
from discord.utils import get as dget

from utils import checks, sqlite as sql, utils
from objects.logger import Log


class Configuration:
    def __init__(self, bot):
        self.bot = bot
        self.log = Log(__name__)

    @checks.admin_only()
    @commands.guild_only()
    @commands.group(name="alertchannel", invoke_without_command=True)
    async def alertchannel(self, ctx):
        channel = dget(ctx.guild.channels, id=sql.guild_get_by_id(ctx.guild.id)['alert_channel'])
        if channel:
            await ctx.send("Alert channel is currently set to {0}.".format(channel.mention))
        else:
            await ctx.send("No alert channel has been set.")

    @checks.admin_only()
    @commands.guild_only()
    @alertchannel.command(name="set")
    async def alertchannel_set(self, ctx, channel: TextChannel):
        sql.guild_update(ctx.guild.id, alert_channel=channel.id)
        self.log.info("Alert channel for {0.name} set to {1.name} (GID:{0.id} CID:{1.name})".format(ctx.guild, channel))
        await ctx.send(ctx.s("configuration.alert_channel_set").format(channel.mention))

    @checks.admin_only()
    @commands.guild_only()
    @alertchannel.command(name="clear")
    async def alertchannel_clear(self, ctx):
        sql.guild_update(ctx.guild.id, alert_channel=0)
        self.log.info("Alert channel for {0.name} cleared (GID:{0.id})".format(ctx.guild))
        await ctx.send(ctx.s("configuration.alert_channel_cleared"))

    @checks.admin_only()
    @commands.guild_only()
    @commands.command()
    async def prefix(self, ctx, prefix):
        if len(prefix) > 5:
            raise commands.BadArgument
        sql.guild_update(ctx.guild.id, prefix=prefix)
        self.log.info("Prefix for {0.name} set to {1} (GID: {0.id})".format(ctx.guild, prefix))
        await ctx.send(ctx.s("configuration.prefix_set").format(prefix))

    @checks.admin_only()
    @commands.guild_only()
    @commands.command()
    async def autoscan(self, ctx):
        if sql.guild_is_autoscan(ctx.guild.id):
            sql.guild_update(ctx.guild.id, autoscan=1)
            self.log.info("Autoscan enabled for {0.name} (GID: {0.id})".format(ctx.guild))
            await ctx.send(ctx.s("configuration.autoscan_enabled"))
        else:
            sql.guild_update(ctx.guild.id, autoscan=0)
            self.log.info("Autoscan disabled for {0.name} (GID: {0.id})".format(ctx.guild))
            await ctx.send(ctx.s("configuration.autoscan_disabled"))

    @checks.admin_only()
    @commands.guild_only()
    @commands.group(name="canvas", invoke_without_command=True)
    async def canvas(self, ctx):
        await ctx.send(ctx.s("configuration.canvas_check").format(ctx.canvas_pretty, ctx.prefix))

    @checks.admin_only()
    @commands.guild_only()
    @canvas.command(name="pixelcanvas", aliases=["pc"])
    async def canvas_pixelcanvas(self, ctx):
        sql.guild_update(ctx.guild.id, canvas="pixelcanvas")
        self.log.info("Default canvas for {0.name} set to pixelcanvas (GID:{0.id})".format(ctx.guild))
        await ctx.send(ctx.s("configuration.canvas_set").format("Pixelcanvas.io"))

    @checks.admin_only()
    @commands.guild_only()
    @canvas.command(name="pixelzio", aliases=["pzi"])
    async def canvas_pixelzio(self, ctx):
        sql.guild_update(ctx.guild.id, canvas="pixelzio")
        self.log.info("Default canvas for {0.name} set to pixelzio (GID:{0.id})".format(ctx.guild))
        await ctx.send(ctx.s("configuration.canvas_set").format("Pixelz.io"))

    @checks.admin_only()
    @commands.guild_only()
    @canvas.command(name="pixelzone", aliases=["pz"])
    async def canvas_pixelzone(self, ctx):
        sql.guild_update(ctx.guild.id, canvas="pixelzone")
        self.log.info("Default canvas for {0.name} set to pixelzone (GID:{0.id})".format(ctx.guild))
        await ctx.send(ctx.s("configuration.canvas_set").format("Pixelzone.io"))

    @checks.admin_only()
    @commands.guild_only()
    @canvas.command(name="pxlsspace", aliases=["ps"])
    async def canvas_pxlsspace(self, ctx):
        sql.guild_update(ctx.guild.id, canvas="pxlsspace")
        self.log.info("Default canvas for {0.name} set to pxlsspace (GID:{0.id})".format(ctx.guild))
        await ctx.send(ctx.s("configuration.canvas_set").format("Pxls.space"))

    @checks.admin_only()
    @commands.guild_only()
    @commands.command()
    async def language(self, ctx, option=None):
        if not option:
            lang_list = ""
            for i, (code, name) in enumerate(ctx.langs.items(), 1):
                lang_list = lang_list + "{0} - {1}".format(code, name)
                if i < len(ctx.langs):
                    lang_list = lang_list + "\n"
            await ctx.send(ctx.s("configuration.language_check").format(lang_list, ctx.lang))
            return
        if option.lower() not in ctx.langs:
            return
        sql.guild_update(ctx.guild.id, language=option.lower())
        self.log.info("Language for {0.name} set to {1} (GID:{0.id})".format(ctx.guild, option.lower()))
        await ctx.send(ctx.s("configuration.language_set").format(ctx.langs[option.lower()]))

    @checks.admin_only()
    @commands.guild_only()
    @commands.group(name="role", invoke_without_command=True)
    async def role(self, ctx):
        await ctx.send(ctx.s("configuration.role_list"))

    @checks.admin_only()
    @commands.guild_only()
    @role.group(name="botadmin", invoke_without_command=True)
    async def role_botadmin(self, ctx):
        r = utils.get_botadmin_role(ctx)
        if r:
            await ctx.send(ctx.s("configuration.role_bot_admin_check").format(r.name))
        else:
            await ctx.send(ctx.s("configuration.role_bot_admin_not_set"))

    @checks.admin_only()
    @commands.guild_only()
    @role_botadmin.command(name="set")
    async def role_botadmin_set(self, ctx, role=None):
        m = re.match('<@&(\d+)>', role)
        r = dget(ctx.guild.role_hierarchy, id=int(m.group(1))) if m else dget(ctx.guild.role_hierarchy, name=role)
        if r:
            sql.guild_update(ctx.guild.id, bot_admin=r.id)
            await ctx.send(ctx.s("configuration.role_bot_admin_set").format(r.name))
        else:
            await ctx.send(ctx.s("configuration.role_not_found"))

    @checks.admin_only()
    @commands.guild_only()
    @role_botadmin.command(name="clear")
    async def role_botadmin_clear(self, ctx):
        sql.guild_update(ctx.guild.id, bot_admin=None)
        await ctx.send(ctx.s("configuration.role_bot_admin_cleared"))

    @checks.admin_only()
    @commands.guild_only()
    @role.group(name="templateadder", invoke_without_command=True)
    async def role_templateadder(self, ctx):
        r = utils.get_templateadder_role(ctx)
        if r:
            await ctx.send(ctx.s("configuration.role_template_adder_check").format(r.name))
        else:
            await ctx.send(ctx.s("configuration.role_template_adder_not_set"))

    @checks.admin_only()
    @commands.guild_only()
    @role_templateadder.command(name="set")
    async def role_templateadder_set(self, ctx, role=None):
        m = re.match('<@&(\d+)>', role)
        r = dget(ctx.guild.role_hierarchy, id=int(m.group(1))) if m else dget(ctx.guild.role_hierarchy, name=role)
        if r:
            sql.guild_update(ctx.guild.id, template_adder=r.id)
            await ctx.send(ctx.s("configuration.role_template_adder_set").format(r.name))
        else:
            await ctx.send(ctx.s("configuration.role_not_found"))

    @checks.admin_only()
    @commands.guild_only()
    @role_templateadder.command(name="clear")
    async def role_templateadder_clear(self, ctx):
        sql.guild_update(ctx.guild.id, template_adder=None)
        await ctx.send(ctx.s("configuration.role_template_adder_cleared"))

    @checks.admin_only()
    @commands.guild_only()
    @role.group(name="templateadmin", invoke_without_command=True)
    async def role_templateadmin(self, ctx):
        r = utils.get_templateadmin_role(ctx)
        if r:
            await ctx.send(ctx.s("configuration.role_template_admin_check").format(r.name))
        else:
            await ctx.send(ctx.s("configuration.role_template_admin_not_set"))

    @checks.admin_only()
    @commands.guild_only()
    @role_templateadmin.command(name="set")
    async def role_templateadmin_set(self, ctx, role=None):
        m = re.match('<@&(\d+)>', role)
        r = dget(ctx.guild.role_hierarchy, id=int(m.group(1))) if m else dget(ctx.guild.role_hierarchy, name=role)
        if r:
            sql.guild_update(ctx.guild.id, template_admin=r.id)
            await ctx.send(ctx.s("configuration.role_template_admin_set").format(r.name))
        else:
            await ctx.send(ctx.s("configuration.role_not_found"))

    @checks.admin_only()
    @commands.guild_only()
    @role_templateadmin.command(name="clear")
    async def role_templateadmin_clear(self, ctx):
        sql.guild_update(ctx.guild.id, template_admin=None)
        await ctx.send(ctx.s("configuration.role_template_admin_cleared"))


def setup(bot):
    bot.add_cog(Configuration(bot))
