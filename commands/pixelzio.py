import re
from discord.ext import commands

from utils.render import *


class Pixelzio:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pziodiff(self, ctx, *, coordinates: str):
        """Takes an uploaded template and checks the canvas to see how complete it is.

        If autoscan is enabled and Pixelz.io is set as your default canvas, you do not need to explicitly invoke this
        command -- any valid coordinates in the same message as a attachment will trigger this command automatically.
        See help for 'autoscan' and 'setdefaultcanvas' commands for more information.

        Usage examples (with uploaded attachment):
        - 0,0
        - 0, 0
        - (0, 0) -e
        """
        m = re.search('\(?(-?\d+), ?(-?\d+)\)?', coordinates)
        if m is not None and len(ctx.message.attachments) > 0:
            x = int(m.group(1))
            y = int(m.group(2))
            att = ctx.message.attachments[0]
            await pixelzio_diff(ctx, x, y, att)

    @commands.command()
    async def pziopreview(self, ctx, *, coordinates: str):
        """Render a preview of the canvas centered at the given url/coordinates.
        Add a number like #2 to the end of the url/coordinates to zoom the preview by the corresponding factor. (Max 16)

        If autoscan is enabled and Pixelz.io is set to your default canvas, you do not need to explicitly invoke this
        command -- any message containing coordinates prefixed with '@' will trigger this command automatically.
        See help for 'autoscan' and 'setdefaultcanvas' commands for more information.

        Usage examples:
        - http://pixelz.io/@0,0
        - pixelz.io/@0,0 #2
        - @0, 0
        """
        m = re.search('@(-?\d+), ?(-?\d+)/?\s?#?(\d+)?', coordinates)
        if m is not None:
            x = int(m.group(1))
            y = int(m.group(2))
            zoom = int(m.group(3)) if m.group(3) is not None else 1
            zoom = max(min(zoom, 16), 1)
            await pixelzio_preview(ctx, x, y, zoom)


def setup(bot):
    bot.add_cog(Pixelzio(bot))
