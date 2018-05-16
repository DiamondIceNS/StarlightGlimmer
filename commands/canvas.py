import re
from discord.ext import commands
from discord.ext.commands import BucketType
from discord.utils import get as dget
from utils.language import getlang

import utils.colors as colors
import utils.render as render
import utils.sqlite as sql
from utils.logger import Log

log = Log(__name__)


class Canvas:
    def __init__(self, bot):
        self.bot = bot

    # =======================
    #          DIFF
    # =======================

    @commands.group(name="diff", invoke_without_command=True, aliases=["d"])
    @commands.cooldown(1, 5, BucketType.guild)
    async def diff(self, ctx):
        default_canvas = sql.select_guild_by_id(ctx.guild.id)['default_canvas']
        if default_canvas == "pixelcanvas":
            ctx.command = dget(dget(self.bot.commands, name='diff').commands, name='pixelcanvas')
        elif default_canvas == "pixelzio":
            ctx.command = dget(dget(self.bot.commands, name='diff').commands, name='pixelzio')
        elif default_canvas == "pixelzone":
            ctx.command = dget(dget(self.bot.commands, name='diff').commands, name='pixelzone')
        elif default_canvas == "pxlsspace":
            ctx.command = dget(dget(self.bot.commands, name='diff').commands, name='pxlsspace')
        if ctx.command is not None:
            await self.bot.invoke(ctx)

    @staticmethod
    async def parse_diff(ctx, coords):
        if len(ctx.message.attachments) < 1:
            await ctx.send(getlang(ctx.guild.id, "bot.error.missing_attachment"))
            return
        att = ctx.message.attachments[0]
        if att.filename[-4:].lower() != ".png":
            if att.filename[-4:].lower() == ".jpg" or att.filename[-5:].lower() == ".jpeg":
                await ctx.send(getlang(ctx.guild.id, "bot.error.jpeg"))
                return
            await ctx.send(getlang(ctx.guild.id, "bot.error.no_png"))
            return
        if att.width is None or att.height is None:
            await ctx.send(getlang(ctx.guild.id, "bot.error.bad_png")
                           .format(sql.get_guild_prefix(ctx.guild.id), getlang(ctx.guild.id, "command.quantize")))
            return
        m = re.search('\(?(-?\d+), ?(-?\d+)\)?\s?#?(\d+)?', coords)
        if m is not None:
            x = int(m.group(1))
            y = int(m.group(2))
            zoom = int(m.group(3)) if m.group(3) is not None else 1
            zoom = max(1, min(zoom, 400 // att.width, 400 // att.height))
            return ctx, x, y, att, zoom

    @diff.command(name="pixelcanvas", aliases=["pc"])
    @commands.cooldown(1, 5, BucketType.guild)
    async def diff_pixelcanvas(self, ctx, *, coordinates: str):
        args = await Canvas.parse_diff(ctx, coordinates)
        if args is not None:
            log.debug("Pixelcanvas diff invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            await render.diff(*args, render.fetch_pixelcanvas, colors.pixelcanvas)

    @diff.command(name="pixelzio", aliases=["pzi"])
    @commands.cooldown(1, 5, BucketType.guild)
    async def diff_pixelzio(self, ctx, *, coordinates: str):
        args = await Canvas.parse_diff(ctx, coordinates)
        if args is not None:
            log.debug("Pixelzio diff invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            await render.diff(*args, render.fetch_pixelzio, colors.pixelzio)

    @diff.command(name="pixelzone", aliases=["pz"])
    @commands.cooldown(1, 5, BucketType.guild)
    async def diff_pixelzone(self, ctx, *, coordinates: str):
        args = await Canvas.parse_diff(ctx, coordinates)
        if args is not None:
            log.debug("Pixelzone diff invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            await render.diff(*args, render.fetch_pixelzone, colors.pixelzone)

    @diff.command(name="pxlsspace", aliases=["ps"])
    @commands.cooldown(1, 5, BucketType.guild)
    async def diff_pxlsspace(self, ctx, *, coordinates: str):
        args = await Canvas.parse_diff(ctx, coordinates)
        if args is not None:
            log.debug("Pxlsspace diff invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            await render.diff(*args, render.fetch_pxlsspace, colors.pxlsspace)

    # =======================
    #        PREVIEW
    # =======================

    @commands.group(name="preview", invoke_without_command=True, aliases=["p"])
    @commands.cooldown(1, 5, BucketType.guild)
    async def preview(self, ctx):
        default_canvas = sql.select_guild_by_id(ctx.guild.id)['default_canvas']
        if default_canvas == "pixelcanvas":
            ctx.command = dget(dget(self.bot.commands, name='preview').commands, name='pixelcanvas')
        elif default_canvas == "pixelzio":
            ctx.command = dget(dget(self.bot.commands, name='preview').commands, name='pixelzio')
        elif default_canvas == "pixelzone":
            ctx.command = dget(dget(self.bot.commands, name='preview').commands, name='pixelzone')
        elif default_canvas == "pxlsspace":
            ctx.command = dget(dget(self.bot.commands, name='preview').commands, name='pxlsspace')
        if ctx.command is not None:
            await self.bot.invoke(ctx)

    @staticmethod
    async def parse_preview(ctx, coords):
        m = re.search('(-?\d+)(?:,|&y=) ?(-?\d+)(?:(?:,|&scale=)(\d+))?/?\s?#?(\d+)?', coords)
        if m is not None:
            x = int(m.group(1))
            y = int(m.group(2))
            if m.group(4) is not None:
                zoom = int(m.group(4))
            elif m.group(3) is not None:
                zoom = int(m.group(3))
            else:
                zoom = 1
            zoom = max(min(zoom, 16), 1)
            return ctx, x, y, zoom

    @preview.command(name="pixelcanvas", aliases=["pc"])
    @commands.cooldown(1, 5, BucketType.guild)
    async def preview_pixelcanvas(self, ctx, *, coordinates: str):
        args = await Canvas.parse_preview(ctx, coordinates)
        if args is not None:
            log.debug("Pixelcanvas preview invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            await render.preview(*args, render.fetch_pixelcanvas)

    @preview.command(name="pixelzio", aliases=["pzi"])
    @commands.cooldown(1, 5, BucketType.guild)
    async def preview_pixelzio(self, ctx, *, coordinates: str):
        args = await Canvas.parse_preview(ctx, coordinates)
        if args is not None:
            log.debug("Pixelzio preview invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            await render.preview(*args, render.fetch_pixelzio)

    @preview.command(name="pixelzone", aliases=["pz"])
    @commands.cooldown(1, 5, BucketType.guild)
    async def preview_pixelzone(self, ctx, *, coordinates: str):
        args = await Canvas.parse_preview(ctx, coordinates)
        if args is not None:
            log.debug("Pixelzone preview invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            await render.preview(*args, render.fetch_pixelzone)

    @preview.command(name="pxlsspace", aliases=["ps"])
    @commands.cooldown(1, 5, BucketType.guild)
    async def preview_pxlsspace(self, ctx, *, coordinates: str):
        args = await Canvas.parse_preview(ctx, coordinates)
        if args is not None:
            log.debug("Pxlsspace preview invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            x = max(0, min(1279, args[1]))
            y = max(0, min(719, args[2]))
            await render.preview(ctx, x, y, args[3], render.fetch_pxlsspace)

    # =======================
    #        QUANTIZE
    # =======================

    @commands.group(name="quantize", invoke_without_command=True, aliases=["q"])
    @commands.cooldown(1, 5, BucketType.guild)
    async def quantize(self, ctx):
        default_canvas = sql.select_guild_by_id(ctx.guild.id)['default_canvas']
        if default_canvas == "pixelcanvas":
            ctx.command = dget(dget(self.bot.commands, name='quantize').commands, name='pixelcanvas')
        elif default_canvas == "pixelzio":
            ctx.command = dget(dget(self.bot.commands, name='quantize').commands, name='pixelzio')
        elif default_canvas == "pixelzone":
            ctx.command = dget(dget(self.bot.commands, name='quantize').commands, name='pixelzone')
        elif default_canvas == "pxlsspace":
            ctx.command = dget(dget(self.bot.commands, name='quantize').commands, name='pxlsspace')
        if ctx.command is not None:
            await self.bot.invoke(ctx)

    @staticmethod
    async def check_attachment(ctx):
        if len(ctx.message.attachments) < 1:
            await ctx.send(getlang(ctx.guild.id, "bot.error.missing_attachment"))
            return False
        filename = ctx.message.attachments[0].filename
        if filename[-4:].lower() != ".png":
            if filename[-4:].lower() == ".jpg" or filename[-5:].lower() == ".jpeg":
                await ctx.send(getlang(ctx.guild.id, "bot.error.jpeg"))
                return False
            await ctx.send(getlang(ctx.guild.id, "bot.error.no_png"))
            return False
        return True

    @quantize.command(name="pixelcanvas", aliases=["pc"])
    @commands.cooldown(1, 5, BucketType.guild)
    async def quantize_pixelcanvas(self, ctx):
        if await Canvas.check_attachment(ctx):
            log.debug("Pixelcanvas quantize invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            await render.quantize(ctx, ctx.message.attachments[0], colors.pixelcanvas)

    @quantize.command(name="pixelzio", aliases=["pzi"])
    @commands.cooldown(1, 5, BucketType.guild)
    async def quantize_pixelzio(self, ctx):
        if await Canvas.check_attachment(ctx):
            log.debug("Pixelzio quantize invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            await render.quantize(ctx, ctx.message.attachments[0], colors.pixelzio)

    @quantize.command(name="pixelzone", aliases=["pz"])
    @commands.cooldown(1, 5, BucketType.guild)
    async def quantize_pixelzone(self, ctx):
        if await Canvas.check_attachment(ctx):
            log.debug("Pixelzone quantize invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            await render.quantize(ctx, ctx.message.attachments[0], colors.pixelzone)

    @quantize.command(name="pxlsspace", aliases=["ps"])
    @commands.cooldown(1, 5, BucketType.guild)
    async def quantize_pxlsspace(self, ctx):
        if await Canvas.check_attachment(ctx):
            log.debug("Pxlsspace quantize invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            await render.quantize(ctx, ctx.message.attachments[0], colors.pxlsspace)

    # =======================
    #         GRIDIFY
    # =======================

    @commands.command(name="gridify", aliases=["g"])
    @commands.cooldown(1, 5, BucketType.guild)
    async def gridify(self, ctx, zoom: int = 1):
        if await Canvas.check_attachment(ctx):
            log.debug("Gridify invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                      .format(ctx.author, ctx.guild))
            att = ctx.message.attachments[0]
            zoom = max(1, min(zoom, 1000 // att.width, 1000 // att.height))
            await render.gridify(ctx, att, zoom)

    @commands.command(name="repeat", aliases=["r"])
    @commands.cooldown(1, 5, BucketType.guild)
    async def repeat(self, ctx):
        async for msg in ctx.history(limit=50, before=ctx.message):
            log_msg = "repeated by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})" \
                .format(ctx.author, ctx.guild)
            regex = ctx.prefix + '(diff|d|preview|p) ((?:pixel(?:canvas|zio|zone))|pxlsspace|p(?:c|z|zi|s))(?: (' \
                                 '-?\d+), ?(-?\d+)/?\s?#?(\d+)?) '
            match = re.match(regex, msg.content)

            if match:
                cmd = match.group(1)
                sub_cmd = match.group(2)
                x = int(match.group(3))
                y = int(match.group(4))
                zoom = int(match.group(5)) if match.group(5) is not None else 1
                print("cmd: {}, scmd: {}, x: {}, y: {}".format(cmd, sub_cmd, x, y))
                if (cmd == "diff" or cmd == "d") and len(msg.attachments) > 0 \
                        and msg.attachments[0].filename[-4:].lower() == ".png":
                    att = msg.attachments[0]
                    if att.width is None or att.height is None:
                        await ctx.send(getlang(ctx.guild.id, "bot.error.bad_png")
                                       .format(sql.get_guild_prefix(ctx.guild.id),
                                               getlang(ctx.guild.id, "command.quantize")))
                        return
                    zoom = max(1, min(zoom, 400 // att.width, 400 // att.height))
                    if sub_cmd == "pixelcanvas" or sub_cmd == "pc":
                        log.debug("Pixelcanvas diff " + log_msg)
                        await render.diff(ctx, x, y, att, zoom, render.fetch_pixelcanvas, colors.pixelcanvas)
                        return
                    elif sub_cmd == "pixelzio" or sub_cmd == "pzi":
                        log.debug("Pixelzio diff " + log_msg)
                        await render.diff(ctx, x, y, att, zoom, render.fetch_pixelzio, colors.pixelzio)
                        return
                    elif sub_cmd == "pixelzone" or sub_cmd == "pz":
                        log.debug("Pixelzone diff " + log_msg)
                        await render.diff(ctx, x, y, att, zoom, render.fetch_pixelzone, colors.pixelzone)
                        return
                    elif sub_cmd == "pxlsspace" or sub_cmd == "ps":
                        log.debug("Pxlsspace diff " + log_msg)
                        await render.diff(ctx, x, y, att, zoom, render.fetch_pxlsspace, colors.pxlsspace)
                        return
                if cmd == "preview" or cmd == "p":
                    zoom = max(1, min(16, zoom))
                    if sub_cmd == "pixelcanvas" or sub_cmd == "pc":
                        log.debug("Pixelcanvas preview " + log_msg)
                        await render.preview(ctx, x, y, zoom, render.fetch_pixelcanvas)
                        return
                    elif sub_cmd == "pixelzio" or sub_cmd == "pzi":
                        log.debug("Pixelzio preview " + log_msg)
                        await render.preview(ctx, x, y, zoom, render.fetch_pixelzio)
                        return
                    elif sub_cmd == "pixelzone" or sub_cmd == "pz":
                        log.debug("Pixelzone preview " + log_msg)
                        await render.preview(ctx, x, y, zoom, render.fetch_pixelzone)
                        return
                    elif sub_cmd == "pxlsspace" or sub_cmd == "ps":
                        log.debug("Pxlsspace preview " + log_msg)
                        await render.preview(ctx, x, y, zoom, render.fetch_pxlsspace)
                        return

            default_canvas = sql.select_guild_by_id(ctx.guild.id)['default_canvas']
            pc_match = re.search('(?:pixelcanvas\.io/)@(-?\d+),(-?\d+)/?(?:\s?#?(\d+))?', msg.content)
            pzio_match = re.search('(?:pixelz\.io/)@(-?\d+),(-?\d+)(?:\s?#?(\d+))?', msg.content)
            pzone_match = re.search('(?:pixelzone\.io/)\?p=(-?\d+),(-?\d+)(?:,(\d+))?(?:\s?#?(\d+))?', msg.content)
            pxlsp_match = re.search('pxls\.space/#x=(\d+)&y=(\d+)(?:&scale=(\d+))?\s?#?(\d+)?', msg.content)
            prev_match = re.search('@\(?(-?\d+), ?(-?\d+)\)?(?: ?#(\d+))?', msg.content)
            diff_match = re.search('\(?(-?\d+), ?(-?\d+)\)?(?: ?#(\d+))?', msg.content)

            if pc_match is not None:
                x = int(pc_match.group(1))
                y = int(pc_match.group(2))
                zoom = int(pc_match.group(3)) if pc_match.group(3) is not None else 1
                zoom = max(min(zoom, 16), 1)
                log.debug("Pixelcanvas preview " + log_msg)
                await render.preview(ctx, x, y, zoom, render.fetch_pixelcanvas)
                return

            if pzio_match is not None:
                x = int(pzio_match.group(1))
                y = int(pzio_match.group(2))
                zoom = int(pzio_match.group(3)) if pzio_match.group(3) is not None else 1
                zoom = max(min(zoom, 16), 1)
                log.debug("Pixelzio preview " + log_msg)
                await render.preview(ctx, x, y, zoom, render.fetch_pixelzio)
                return

            if pzone_match is not None:
                x = int(pzone_match.group(1))
                y = int(pzone_match.group(2))
                if pzone_match.group(4) is not None:
                    zoom = int(pzone_match.group(4))
                elif pzone_match.group(3) is not None:
                    zoom = int(pzio_match.group(3))
                else:
                    zoom = 1
                zoom = max(min(zoom, 16), 1)
                log.debug("Pixelzone preview " + log_msg)
                await render.preview(ctx, x, y, zoom, render.fetch_pixelzone)
                return

            if pxlsp_match is not None:
                x = int(pxlsp_match.group(1))
                y = int(pxlsp_match.group(2))
                if pxlsp_match.group(4) is not None:
                    zoom = int(pxlsp_match.group(4))
                elif pxlsp_match.group(3) is not None:
                    zoom = int(pxlsp_match.group(3))
                else:
                    zoom = 1
                zoom = max(min(zoom, 16), 1)
                log.debug("Pxlsspace preview " + log_msg)
                await render.preview(ctx, x, y, zoom, render.fetch_pxlsspace)
                return

            if prev_match is not None:
                x = int(prev_match.group(1))
                y = int(prev_match.group(2))
                zoom = int(prev_match.group(3)) if prev_match.group(3) is not None else 1
                zoom = max(min(zoom, 16), 1)
                if default_canvas == "pixelcanvas":
                    log.debug("Pixelcanvas preview " + log_msg)
                    await render.preview(ctx, x, y, zoom, render.fetch_pixelcanvas)
                elif default_canvas == "pixelzio":
                    log.debug("Pixelzio preview " + log_msg)
                    await render.preview(ctx, x, y, zoom, render.fetch_pixelzio)
                elif default_canvas == "pixelzone":
                    log.debug("Pixelzone preview " + log_msg)
                    await render.preview(ctx, x, y, zoom, render.fetch_pixelzone)
                elif default_canvas == "pxlsspace":
                    log.debug("Pxlsspace preview " + log_msg)
                    await render.preview(ctx, x, y, zoom, render.fetch_pxlsspace)
                return

            if diff_match is not None and len(msg.attachments) > 0 \
                    and msg.attachments[0].filename[-4:].lower() == ".png":
                att = msg.attachments[0]
                if att.width is None or att.height is None:
                    await ctx.send(getlang(ctx.guild.id, "bot.error.bad_png")
                                   .format(sql.get_guild_prefix(ctx.guild.id),
                                           getlang(ctx.guild.id, "command.quantize")))
                    return
                x = int(diff_match.group(1))
                y = int(diff_match.group(2))
                zoom = int(diff_match.group(3)) if diff_match.group(3) is not None else 1
                zoom = max(1, min(zoom, 400 // att.width, 400 // att.height))
                if default_canvas == "pixelcanvas":
                    log.debug("Pixelcanvas diff " + log_msg)
                    await render.diff(ctx, x, y, att, zoom, render.fetch_pixelcanvas, colors.pixelcanvas)
                elif default_canvas == "pixelzio":
                    log.debug("Pixelzio diff " + log_msg)
                    await render.diff(ctx, x, y, att, zoom, render.fetch_pixelzio, colors.pixelzio)
                elif default_canvas == "pixelzone":
                    log.debug("Pixelzone diff " + log_msg)
                    await render.diff(ctx, x, y, att, zoom, render.fetch_pixelzone, colors.pixelzone)
                elif default_canvas == "pxlsspace":
                    log.debug("Pxlsspace diff " + log_msg)
                    await render.diff(ctx, x, y, att, zoom, render.fetch_pxlsspace, colors.pxlsspace)
                return

            ctx.send(getlang(ctx.guild.id, "render.repeat_not_found"))


def setup(bot):
    bot.add_cog(Canvas(bot))
