from discord.ext import commands
from discord import TextChannel

from utils.exceptions import NoPermission
import utils.sqlite as sql


class Configuration:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def setalertchannel(self, ctx, channel: TextChannel):
        """Sets the preferred channel for update alerts.

        If set, I will post there every time I update so you know when new features are ready.
        Use the #channel syntax to ensure the correct channel is selected if multiple channels have the same name.
        I need permission to post in the specified channel for this to have effect.

        Only users with the Administrator role can use this command."""
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        sql.update_guild(ctx.guild.id, alert_channel=channel.id)
        await ctx.send("Alert channel set!")

    @commands.command()
    @commands.guild_only()
    async def clearalertchannel(self, ctx):
        """Clears the preferred channel for update alerts.

        If this is cleared, I will no longer alert this server when the update version has changed.

        Only users with the Administrator role can use this command."""
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        sql.update_guild(ctx.guild.id, alert_channel=0)
        await ctx.send("Alert channel cleared!")

    @commands.command()
    @commands.guild_only()
    async def setprefix(self, ctx, prefix):
        """Sets my command prefix for this server.

        The prefix is the substring one types immediately before any command to use that command. Set it to something
        short that doesn't conflict with another bot on the server! Maximum 10 characters. You really shouldn't need
        anything longer. Default prefix is 'g!'.

        Only users with the Administrator role can use this command."""
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        if len(prefix) > 10:
            raise commands.BadArgument
        sql.update_guild(ctx.guild.id, prefix=prefix)
        await ctx.send("Prefix for this server has been set to `{}`".format(prefix))

    @commands.command()
    @commands.guild_only()
    async def autoscan(self, ctx):
        """Toggles whether I will automatically scan all messages for preview or diff requests.

        If this is on, any post that contains valid coordinate pairs will be treated as either an invocation of
        the 'preview' command or 'diff' command for one of the supported canvas websites. If a full URL is posted, the
        canvas in the URL will be used. If only a coordinate pair is posted, the default canvas will be used.

        'diff' will only fire if the same message also contains an image attachment. 'preview' will take precedence over
        'diff' if the coordinates are preceeded by the '@' character, even if an attachment is provided.

        See each command's help page for a given canvas for more information on the syntax for each.
        See `setdefaultcanvas` for more info on setting a default canvas.

        Only users with the Administrator role can use this command."""
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        if sql.select_guild_by_id(ctx.guild.id)['autoscan'] == 0:
            sql.update_guild(ctx.guild.id, autoscan=1)
            await ctx.send("Autoscan has been enabled.")
        else:
            sql.update_guild(ctx.guild.id, autoscan=0)
            await ctx.send("Autoscan has been disabled.")

    @commands.command()
    @commands.guild_only()
    async def setdefaultcanvas(self, ctx, *args):
        """Sets the default canvas used for autoscan.

        Valid canvas options:
        - pixelcanvas.io
        - pixelz.io

        Use this command without an argument to see which canvas is currently set. Default is pixelcanvas.io.
        See the 'autoscan' command for more information.

        Only users with the Administrator role can use this command."""
        if not ctx.author.permissions_in(ctx.channel).administrator:
            raise NoPermission
        canvas = args[0] if len(args) > 0 else None
        if canvas is None or canvas == "":
            g = sql.select_guild_by_id(ctx.guild.id)
            await ctx.send("Current default canvas for this server is **{0}**".format(g['default_canvas']))
            return
        if canvas == "pixelcanvas.io":
            sql.update_guild(ctx.guild.id, default_canvas="pixelcanvas.io")
            await ctx.send("Default canvas set to **pixelcanvas.io**")
        elif canvas == "pixelz.io":
            sql.update_guild(ctx.guild.id, default_canvas="pixelz.io")
            await ctx.send("Default canvas set to **pixelz.io**")
        else:
            raise commands.BadArgument


def setup(bot):
    bot.add_cog(Configuration(bot))
