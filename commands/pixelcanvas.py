import re
from discord.ext import commands

from utils.render import preview, diff


class Pixelcanvas():
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def diff(self, ctx, *, coordinates: str):
        """Takes an uploaded template and checks the canvas to see how complete it is.
        Add -e at the end to check against the experimental canvas.

        You do not need to explicitly invoke this command -- any valid coordinates in the same message as a attachment
        will trigger this command.
        If triggered implicitly, the preview command will take precedence over this one if they both match the input.

        Usage examples (with uploaded attachment):
        - 0,0
        - 0, 0
        - (0, 0) -e
        """
        m = re.search('\(?(-?\d+), ?(-?\d+)\)?(?: (-e)?)?', coordinates)
        if m is not None and len(ctx.message.attachments) > 0:
            x = int(m.group(1))
            y = int(m.group(2))
            att = ctx.message.attachments[0]
            is_exp = m.group(3) is not None
            await diff(ctx, x, y, att, is_exp)

    @commands.command()
    async def preview(self, ctx, *, coordinates: str):
        """Render a preview of the canvas centered at the given url/coordinates.
        Add #2, #4, or #8 to the end of the url/coordinates to zoom the preview by the corresponding factor.
        Add the experimental subdomain to the URL or add -e at the end to render on the experimental canvas.

        You do not need to explicitly invoke this command -- any message containing coordinates prefixed with '@'
        will trigger this command.

        Usage examples:
        - http://pixelcanvas.io/@0,0
        - pixelcanvas.io/@0,0 #2
        - experimental.pixelcanvas.io/@0,0 #8
        - @0, 0
        - @0, 0 #4 -e
        """
        m = re.search('(?:(experimental)?\.pixelcanvas\.io/)?@(-?\d+), ?(-?\d+)/?\s?#?([248])?(?:\d+)?(?: ?(-e))?',
                      coordinates)
        if m is not None:
            x = int(m.group(2))
            y = int(m.group(3))
            zoom = int(m.group(4)) if m.group(4) is not None else 1
            is_exp = m.group(1) is not None or m.group(5) is not None
            await preview(ctx, x, y, zoom, is_exp)


def setup(bot):
    bot.add_cog(Pixelcanvas(bot))
