import io
import math
import re

import discord
from discord.ext import commands
from discord.ext.commands import BucketType

from objects.glimcontext import GlimContext
from utils import colors, http, render, sqlite as sql, utils
from objects.logger import Log
from objects import errors

log = Log(__name__)


class Canvas:
    def __init__(self, bot):
        self.bot = bot

    # =======================
    #          DIFF
    # =======================

    @commands.cooldown(1, 5, BucketType.guild)
    @commands.group(name="diff", invoke_without_command=True, aliases=["d"])
    async def diff(self, ctx, *args):
        if len(args) < 1:
            return
        list_pixels = False
        iter_args = iter(args)
        a = next(iter_args, None)
        if a == "-e":
            list_pixels = True
            a = next(iter_args, None)
        if a == "-f":
            fac = next(iter_args, None)
            if fac is None:
                await ctx.send(ctx.s("error.missing_arg_faction"))
                return
            f = sql.guild_get_by_faction_name_or_alias(fac)
            if not f:
                await ctx.send(ctx.s("error.faction_not_found"))
                return
            name = next(iter_args, None)
            zoom = next(iter_args, 1)
            t = sql.template_get_by_name(f.id, name)
        else:
            name = a
            zoom = next(iter_args, 1)
            t = sql.template_get_by_name(ctx.guild.id, name)

        try:
            if type(zoom) is not int:
                if zoom.startswith("#"):
                    zoom = zoom[1:]
                zoom = int(zoom)
        except ValueError:
            zoom = 1

        if t:
            async with ctx.typing():
                log.debug("(T:{} | GID:{})".format(t.name, t.gid))
                data = await http.get_template(t.url)
                max_zoom = int(math.sqrt(4000000 // (t.width * t.height)))
                zoom = max(1, min(zoom, max_zoom))

                fetchers = {
                    'pixelcanvas': render.fetch_pixelcanvas,
                    'pixelzone': render.fetch_pixelzone,
                    'pxlsspace': render.fetch_pxlsspace,
                    'pixelplace': render.fetch_pixelplace,
                }

                diff_img, tot, err, bad, err_list \
                    = await render.diff(t.x, t.y, data, zoom, fetchers[t.canvas], colors.by_name[t.canvas])

                done = tot - err
                perc = done / tot
                if perc < 0.00005 and done > 0:
                    perc = ">0.00%"
                elif perc >= 0.99995 and err > 0:
                    perc = "<100.00%"
                else:
                    perc = "{:.2f}%".format(perc * 100)
                out = ctx.s("canvas.diff") if bad == 0 else ctx.s("canvas.diff_bad_color")
                out = out.format(done, tot, err, perc, bad=bad)

                with io.BytesIO() as bio:
                    diff_img.save(bio, format="PNG")
                    bio.seek(0)
                    f = discord.File(bio, "diff.png")
                    await ctx.send(content=out, file=f)

                if list_pixels and len(err_list) > 0:
                    out = ["```xl"]
                    for p in err_list:
                        x, y, current, target = p
                        current = ctx.s("color.{}.{}".format(t.canvas, current))
                        target = ctx.s("color.{}.{}".format(t.canvas, target))
                        out.append("({}, {}) is {}, should be {}".format(x + t.x, y + t.y, current, target))
                    if err > 15:
                        out.append("...")
                    out.append("```")
                    await ctx.send('\n'.join(out))

                return
        await ctx.invoke_default("diff")

    @commands.cooldown(1, 5, BucketType.guild)
    @diff.command(name="pixelcanvas", aliases=["pc"])
    async def diff_pixelcanvas(self, ctx, *args):
        await _diff(ctx, args, "pixelcanvas", render.fetch_pixelcanvas, colors.pixelcanvas)

    @commands.cooldown(1, 5, BucketType.guild)
    @diff.command(name="pixelzone", aliases=["pz"])
    async def diff_pixelzone(self, ctx, *args):
        await _diff(ctx, args, "pixelzone", render.fetch_pixelzone, colors.pixelzone)

    @commands.cooldown(1, 5, BucketType.guild)
    @diff.command(name="pxlsspace", aliases=["ps"])
    async def diff_pxlsspace(self, ctx, *args):
        await _diff(ctx, args, "pxlsspace", render.fetch_pxlsspace, colors.pxlsspace)

    @commands.cooldown(1, 5, BucketType.guild)
    @diff.command(name="pixelplace", aliases=["pp"])
    async def diff_pixelcanvas(self, ctx, *args):
        await _diff(ctx, args, "pixelplace", render.fetch_pixelcanvas, colors.pixelcanvas)

    # =======================
    #        PREVIEW
    # =======================

    @commands.cooldown(1, 5, BucketType.guild)
    @commands.group(name="preview", invoke_without_command=True, aliases=["p"])
    async def preview(self, ctx, *args):
        if len(args) < 1:
            return
        preview_template_region = False
        iter_args = iter(args)
        a = next(iter_args, None)
        if a == "-t":
            preview_template_region = True
            a = next(iter_args, None)
        if a == "-f":
            fac = next(iter_args, None)
            if fac is None:
                await ctx.send(ctx.s("error.missing_arg_faction"))
                return
            f = sql.guild_get_by_faction_name_or_alias(fac)
            if not f:
                await ctx.send(ctx.s("error.faction_not_found"))
                return
            name = next(iter_args, None)
            zoom = next(iter_args, 1)
            t = sql.template_get_by_name(f.id, name)
        else:
            name = a
            zoom = next(iter_args, 1)
            t = sql.template_get_by_name(ctx.guild.id, name)

        try:
            if type(zoom) is not int:
                if zoom.startswith("#"):
                    zoom = zoom[1:]
                zoom = int(zoom)
        except ValueError:
            zoom = 1

        if t:
            async with ctx.typing():
                log.debug("(T:{} | GID:{})".format(t.name, t.gid))
                max_zoom = int(math.sqrt(4000000 // (t.width * t.height)))
                zoom = max(-8, min(zoom, max_zoom))

                fetchers = {
                    'pixelcanvas': render.fetch_pixelcanvas,
                    'pixelzone': render.fetch_pixelzone,
                    'pxlsspace': render.fetch_pxlsspace,
                    'pixelplace': render.fetch_pixelplace
                }

                if preview_template_region:
                    preview_img = await render.preview(*t.center(), zoom, fetchers[t.canvas])
                else:
                    preview_img = await render.preview_template(t, zoom, fetchers[t.canvas])

                with io.BytesIO() as bio:
                    preview_img.save(bio, format="PNG")
                    bio.seek(0)
                    f = discord.File(bio, "preview.png")
                    await ctx.send(file=f)

                return
        await ctx.invoke_default("preview")

    @commands.cooldown(1, 5, BucketType.guild)
    @preview.command(name="pixelcanvas", aliases=["pc"])
    async def preview_pixelcanvas(self, ctx, *args):
        await _preview(ctx, args, render.fetch_pixelcanvas)

    @commands.cooldown(1, 5, BucketType.guild)
    @preview.command(name="pixelzone", aliases=["pz"])
    async def preview_pixelzone(self, ctx, *args):
        await _preview(ctx, args, render.fetch_pixelzone)

    @commands.cooldown(1, 5, BucketType.guild)
    @preview.command(name="pxlsspace", aliases=["ps"])
    async def preview_pxlsspace(self, ctx, *args):
        await _preview(ctx, args, render.fetch_pxlsspace)

    @commands.cooldown(1, 5, BucketType.guild)
    @preview.command(name="pixelplace", aliases=["pp"])
    async def preview_pixelplace(self, ctx, *args):
        await _preview(ctx, args, render.fetch_pixelplace)

    # =======================
    #        QUANTIZE
    # =======================

    @commands.cooldown(1, 5, BucketType.guild)
    @commands.group(name="quantize", invoke_without_command=True, aliases=["q"])
    async def quantize(self, ctx):
        await ctx.invoke_default("quantize")

    @commands.cooldown(1, 5, BucketType.guild)
    @quantize.command(name="pixelcanvas", aliases=["pc"])
    async def quantize_pixelcanvas(self, ctx, *args):
        await _quantize(ctx, args, "pixelcanvas", colors.pixelcanvas)

    @commands.cooldown(1, 5, BucketType.guild)
    @quantize.command(name="pixelzone", aliases=["pz"])
    async def quantize_pixelzone(self, ctx, *args):
        await _quantize(ctx, args, "pixelzone", colors.pixelzone)

    @commands.cooldown(1, 5, BucketType.guild)
    @quantize.command(name="pxlsspace", aliases=["ps"])
    async def quantize_pxlsspace(self, ctx, *args):
        await _quantize(ctx, args, "pxlsspace", colors.pxlsspace)

    @commands.cooldown(1, 5, BucketType.guild)
    @quantize.command(name="pixelplace", aliases=["pp"])
    async def quantize_pixelcanvas(self, ctx, *args):
        await _quantize(ctx, args, "pixelplace", colors.pixelcanvas)

    # =======================
    #         GRIDIFY
    # =======================

    @commands.cooldown(1, 5, BucketType.guild)
    @commands.command(name="gridify", aliases=["g"])
    async def gridify(self, ctx, *args):
        faction = None
        color = 0x808080
        iter_args = iter(args)
        name = next(iter_args, None)
        while name in ["-f", "-c"]:
            if name == "-f":
                fac = next(iter_args, None)
                if fac is None:
                    await ctx.send(ctx.s("error.missing_arg_faction"))
                    return
                f = sql.guild_get_by_faction_name_or_alias(fac)
                if not faction:
                    await ctx.send(ctx.s("error.faction_not_found"))
                    return
            if name == "-c":
                try:
                    color = abs(int(next(iter_args, None), 16) % 0xFFFFFF)
                    name = next(iter_args, None)
                except ValueError:
                    await ctx.send(ctx.s("error.invalid_color"))
                    return

        def parse_zoom(z):
            try:
                if type(z) is int:
                    return z
                if type(z) is str:
                    if z.startswith("#"):
                        z = z[1:]
                    return int(z)
                if z is None:
                    return 8
            except ValueError:
                return 8

        t = sql.template_get_by_name(faction.id, name) if faction else sql.template_get_by_name(ctx.guild.id, name)
        if t:
            log.debug("(T:{} | GID:{})".format(t.name, t.gid))
            data = await http.get_template(t.url)
            max_zoom = int(math.sqrt(4000000 // (t.width * t.height)))
            zoom = max(1, min(parse_zoom(next(iter_args, 1)), max_zoom))
            template = await render.gridify(data, color, zoom)
        else:
            att = await utils.verify_attachment(ctx)
            data = io.BytesIO()
            await att.save(data)
            max_zoom = int(math.sqrt(4000000 // (att.width * att.height)))
            zoom = max(1, min(parse_zoom(name), max_zoom))
            template = await render.gridify(data, color, zoom)

        with io.BytesIO() as bio:
            template.save(bio, format="PNG")
            bio.seek(0)
            f = discord.File(bio, "gridded.png")
            await ctx.send(file=f)

    # ======================
    #       DITHERCHART
    # ======================

    @commands.group(name="ditherchart", invoke_without_command=True)
    async def ditherchart(self, ctx):
        await ctx.invoke_default("ditherchart")

    @ditherchart.command(name="pixelcanvas", aliases=["pc"])
    async def ditherchart_pixelcanvas(self, ctx):
        await ctx.send(file=discord.File("assets/dither_chart_pixelcanvas.png", "dither_chart_pixelcanvas.png"))

    @ditherchart.command(name="pixelzone", aliases=["pz"])
    async def ditherchart_pixelzone(self, ctx):
        await ctx.send(file=discord.File("assets/dither_chart_pixelzone.png", "dither_chart_pixelzone.png"))

    @ditherchart.command(name="pxlsspace", aliases=["ps"])
    async def ditherchart_pxlsspace(self, ctx):
        await ctx.send(file=discord.File("assets/dither_chart_pxlsspace.png", "dither_chart_pxlsspace.png"))

    @ditherchart.command(name="pixelplace", aliases=["pp"])
    async def ditherchart_pixelplace(self, ctx):
        await ctx.send(file=discord.File("assets/dither_chart_pixelcanvas.png", "dither_chart_pixelcanvas.png"))

    # ======================
    #         REPEAT
    # ======================

    @commands.cooldown(1, 5, BucketType.guild)
    @commands.command(name="repeat", aliases=["r"])
    async def repeat(self, ctx):
        async for msg in ctx.history(limit=50, before=ctx.message):
            new_ctx = await self.bot.get_context(msg, cls=GlimContext)
            new_ctx.is_repeat = True

            match = re.match('^{}(diff|d|preview|p)'.format(ctx.prefix), msg.content)
            if match:
                await self.bot.invoke(new_ctx)
                return

            if await utils.autoscan(new_ctx):
                return
        await ctx.send(ctx.s("canvas.repeat_not_found"))

    # ======================
    #         ONLINE
    # ======================

    @commands.cooldown(1, 5, BucketType.guild)
    @commands.group(name="online", aliases=["o"], invoke_without_command=True)
    async def online(self, ctx):
        await ctx.invoke_default("online")

    @online.command(name="pixelcanvas", aliases=["pc"])
    async def online_pixelcanvas(self, ctx):
        ct = await http.fetch_online_pixelcanvas()
        await ctx.send(ctx.s("canvas.online").format(ct, "Pixelcanvas"))

    @online.command(name="pixelzone", aliases=["pz"])
    async def online_pixelzone(self, ctx):
        async with ctx.typing():
            msg = await ctx.send(ctx.s("canvas.online_await"))
            ct = await http.fetch_online_pixelzone()
            await msg.edit(content=ctx.s("canvas.online").format(ct, "Pixelzone"))

    @online.command(name="pxlsspace", aliases=["ps"])
    async def online_pxlsspace(self, ctx):
        async with ctx.typing():
            msg = await ctx.send(ctx.s("canvas.online_await"))
            ct = await http.fetch_online_pxlsspace()
            await msg.edit(content=ctx.s("canvas.online").format(ct, "Pxls.space"))

    @online.command(name="pixelplace", aliases=["pp"])
    async def online_pixelplace(self, ctx):
        ct = await http.fetch_online_pixelplace()
        await ctx.send(ctx.s("canvas.online").format(ct, "Pixelplace"))


async def _diff(ctx, args, canvas, fetch, palette):
    async with ctx.typing():
        att = await utils.verify_attachment(ctx)
        list_pixels = False
        iter_args = iter(args)
        a = next(iter_args, None)
        if a == "-e":
            list_pixels = True
            a = next(iter_args, None)
        if a and ',' in a:
            x, y = a.split(',')
        else:
            x = a
            y = next(iter_args, None)

        try:
            x = int(x)
            y = int(y)
        except (ValueError, TypeError):
            await ctx.send(ctx.s("canvas.invalid_input"))
            return

        zoom = next(iter_args, 1)
        try:
            if type(zoom) is not int:
                if zoom.startswith("#"):
                    zoom = zoom[1:]
                zoom = int(zoom)
        except ValueError:
            zoom = 1

        data = io.BytesIO()
        await att.save(data)
        max_zoom = int(math.sqrt(4000000 // (att.width * att.height)))
        zoom = max(1, min(zoom, max_zoom))
        diff_img, tot, err, bad, err_list = await render.diff(x, y, data, zoom, fetch, palette)

        done = tot - err
        perc = done / tot
        if perc < 0.00005 and done > 0:
            perc = ">0.00%"
        elif perc >= 0.99995 and err > 0:
            perc = "<100.00%"
        else:
            perc = "{:.2f}%".format(perc * 100)
        out = ctx.s("canvas.diff") if bad == 0 else ctx.s("canvas.diff_bad_color")
        out = out.format(done, tot, err, perc, bad=bad)

        with io.BytesIO() as bio:
            diff_img.save(bio, format="PNG")
            bio.seek(0)
            f = discord.File(bio, "diff.png")
            await ctx.send(content=out, file=f)

        if list_pixels and len(err_list) > 0:
            out = ["```xl"]
            for p in err_list:
                err_x, err_y, current, target = p
                current = ctx.s("color.{}.{}".format(canvas, current))
                target = ctx.s("color.{}.{}".format(canvas, target))
                out.append(ctx.s("canvas.diff_error_list").format(err_x + x, err_y + y, current, target))
            if err > 15:
                out.append("...")
            out.append("```")
            await ctx.send('\n'.join(out))


async def _preview(ctx, args, fetch):
    async with ctx.typing():
        iter_args = iter(args)
        a = next(iter_args, None)
        if a and ',' in a:
            x, y = a.split(',')
        else:
            x = a
            y = next(iter_args, None)

        try:
            x = int(x)
            y = int(y)
        except (ValueError, TypeError):
            await ctx.send(ctx.s("canvas.invalid_input"))
            return

        zoom = next(iter_args, 1)
        try:
            if type(zoom) is not int:
                if zoom.startswith("#"):
                    zoom = zoom[1:]
                zoom = int(zoom)
        except ValueError:
            zoom = 1
        zoom = max(min(zoom, 16), -8)

        preview_img = await render.preview(x, y, zoom, fetch)

        with io.BytesIO() as bio:
            preview_img.save(bio, format="PNG")
            bio.seek(0)
            f = discord.File(bio, "preview.png")
            await ctx.send(file=f)


async def _quantize(ctx, args, canvas, palette):
    gid = ctx.guild.id
    iter_args = iter(args)
    name = next(iter_args, None)
    if name == "-f":
        fac = next(iter_args, None)
        if fac is None:
            await ctx.send(ctx.s("error.missing_arg_faction"))
            return
        faction = sql.guild_get_by_faction_name_or_alias(fac)
        if not faction:
            raise errors.FactionNotFound
        gid = faction.id
        name = next(iter_args, None)
    t = sql.template_get_by_name(gid, name)

    data = None
    if t:
        log.debug("(T:{} | GID:{})".format(t.name, t.gid))
        if t.canvas == canvas:
            raise errors.IdempotentActionError
        data = await http.get_template(t.url)
    else:
        att = await utils.verify_attachment(ctx)
        if att:
            data = io.BytesIO()
            await att.save(data)

    if data:
        template, bad_pixels = await render.quantize(data, palette)

        with io.BytesIO() as bio:
            template.save(bio, format="PNG")
            bio.seek(0)
            f = discord.File(bio, "template.png")
            return await ctx.send(ctx.s("canvas.quantize").format(bad_pixels), file=f)


def setup(bot):
    bot.add_cog(Canvas(bot))
