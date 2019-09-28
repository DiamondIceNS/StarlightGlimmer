import asyncio
import datetime
import hashlib
import io
import itertools
import logging
import math
import re
import time
from typing import List

import aiohttp
import discord
import numpy as np
from discord.ext import commands
from discord.ext.commands import BucketType
from PIL import Image, ImageChops

from objects import DbTemplate
from objects.chunks import BigChunk, ChunkPz, PxlsBoard
from objects.errors import FactionNotFoundError, NoTemplatesError, PilImageError, TemplateNotFoundError, UrlError
import utils
from utils import canvases, checks, colors, config, http, render, sqlite as sql

log = logging.getLogger(__name__)


class Template(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.cooldown(1, 5, BucketType.guild)
    @commands.group(name='template', invoke_without_command=True, aliases=['t'])
    async def template(self, ctx, *args):
        gid = ctx.guild.id
        iter_args = iter(args)
        page = next(iter_args, 1)
        if page == "-f":
            fac = next(iter_args, None)
            if fac is None:
                await ctx.send(ctx.s("error.missing_arg_faction"))
                return
            faction = sql.guild_get_by_faction_name_or_alias(fac)
            if not faction:
                raise FactionNotFoundError
            gid = faction.id
            page = next(iter_args, 1)
        try:
            page = int(page)
        except ValueError:
            page = 1

        ts = sql.template_get_all_by_guild_id(gid)
        if len(ts) < 1:
            raise NoTemplatesError()

        pages = 1 + len(ts) // 10
        page = min(max(page, 1), pages)
        w1 = max(max(map(lambda tx: len(tx.name), ts)) + 2, len(ctx.s("bot.name")))
        msg = [
            "**{}** - {} {}/{}".format(ctx.s("template.list_header"), ctx.s("bot.page"), page, pages),
            "```xl",
            "{0:<{w1}}  {1:<14}  {2}".format(ctx.s("bot.name"),
                                             ctx.s("bot.canvas"),
                                             ctx.s("bot.coordinates"), w1=w1)
        ]
        for t in ts[(page - 1) * 10:page * 10]:
            coords = "({}, {})".format(t.x, t.y)
            name = '"{}"'.format(t.name)
            canvas_name = canvases.pretty_print[t.canvas]
            msg.append("{0:<{w1}}  {1:<14}  {2}".format(name, canvas_name, coords, w1=w1))
        msg.append("")
        msg.append("// " + ctx.s("template.list_footer_1").format(ctx.gprefix))
        msg.append("// " + ctx.s("template.list_footer_2").format(ctx.gprefix))
        msg.append("```")
        await ctx.send('\n'.join(msg))

    @commands.guild_only()
    @commands.cooldown(1, 5, BucketType.guild)
    @template.command(name='all')
    async def template_all(self, ctx, page: int = 1):
        gs = [x for x in sql.guild_get_all_factions() if x.id not in sql.faction_hides_get_all(ctx.guild.id)]
        ts = [x for x in sql.template_get_all() if x.gid in [y.id for y in gs]]

        def by_faction_name(template):
            for g in gs:
                if template.gid == g.id:
                    return g.faction_name

        ts = sorted(ts, key=by_faction_name)
        ts_with_f = []
        for faction, ts2 in itertools.groupby(ts, key=by_faction_name):
            for t in ts2:
                ts_with_f.append((t, faction))

        if len(ts) > 0:
            pages = 1 + len(ts) // 10
            page = min(max(page, 1), pages)
            w1 = max(max(map(lambda tx: len(tx.name), ts)) + 2, len(ctx.s("bot.name")))
            msg = [
                "**{}** - {} {}/{}".format(ctx.s("template.list_header"), ctx.s("bot.page"), page, pages),
                "```xl",
                "{0:<{w1}}  {1:<34}  {2:<14}  {3}".format(ctx.s("bot.name"),
                                                          ctx.s("bot.faction"),
                                                          ctx.s("bot.canvas"),
                                                          ctx.s("bot.coordinates"), w1=w1)
            ]
            for t, f in ts_with_f[(page - 1) * 10:page * 10]:
                coords = "({}, {})".format(t.x, t.y)
                faction = '"{}"'.format(f)
                name = '"{}"'.format(t.name)
                canvas_name = canvases.pretty_print[t.canvas]
                msg.append("{0:<{w1}}  {1:<34}  {2:<14}  {3}".format(name, faction, canvas_name, coords, w1=w1))
            msg.append("")
            msg.append("// " + ctx.s("template.list_all_footer_1").format(ctx.gprefix))
            msg.append("// " + ctx.s("template.list_all_footer_2").format(ctx.gprefix))
            msg.append("```")
            await ctx.send('\n'.join(msg))
        else:
            await ctx.send(ctx.s("template.err.no_public_templates"))

    @commands.guild_only()
    @commands.cooldown(1, 5, BucketType.guild)
    @checks.template_adder_only()
    @template.group(name='add', invoke_without_command=True)
    async def template_add(self, ctx):
        await ctx.invoke_default("template.add")

    @commands.guild_only()
    @commands.cooldown(1, 5, BucketType.guild)
    @checks.template_adder_only()
    @template_add.command(name="pixelcanvas", aliases=['pc'])
    async def template_add_pixelcanvas(self, ctx, name: str, x: int, y: int, url=None):
        await self.add_template(ctx, "pixelcanvas", name, x, y, url)

    @commands.guild_only()
    @commands.cooldown(1, 5, BucketType.guild)
    @checks.template_adder_only()
    @template_add.command(name="pixelzone", aliases=['pz'])
    async def template_add_pixelzone(self, ctx, name: str, x: int, y: int, url=None):
        await self.add_template(ctx, "pixelzone", name, x, y, url)

    @commands.guild_only()
    @commands.cooldown(1, 5, BucketType.guild)
    @checks.template_adder_only()
    @template_add.command(name="pxlsspace", aliases=['ps'])
    async def template_add_pxlsspace(self, ctx, name: str, x: int, y: int, url=None):
        await self.add_template(ctx, "pxlsspace", name, x, y, url)

    @commands.guild_only()
    @commands.cooldown(1, 60, BucketType.guild)
    @template.group(name='check')
    async def template_check(self, ctx):
        if not ctx.invoked_subcommand or ctx.invoked_subcommand.name == "check":
            ts = sql.template_get_all_by_guild_id(ctx.guild.id)

            if len(ts) < 1:
                ctx.command.parent.reset_cooldown(ctx)
                raise NoTemplatesError(False)

            msg = None
            ts = sorted(ts, key=lambda tx: tx.name)
            ts = sorted(ts, key=lambda tx: tx.canvas)
            for canvas, canvas_ts in itertools.groupby(ts, lambda tx: tx.canvas):
                ct = list(canvas_ts)
                msg = await _check_canvas(ctx, ct, canvas, msg=msg)

            await msg.delete()
            await _build_template_report(ctx, ts)

    @commands.guild_only()
    @template_check.command(name='pixelcanvas', aliases=['pc'])
    async def template_check_pixelcanvas(self, ctx):
        ts = [x for x in sql.template_get_all_by_guild_id(ctx.guild.id) if x.canvas == 'pixelcanvas']
        if len(ts) <= 0:
            ctx.command.parent.reset_cooldown(ctx)
            raise NoTemplatesError(True)
        ts = sorted(ts, key=lambda tx: tx.name)
        msg = await _check_canvas(ctx, ts, "pixelcanvas")
        await msg.delete()
        await _build_template_report(ctx, ts)

    @commands.guild_only()
    @template_check.command(name='pixelzone', aliases=['pz'])
    async def template_check_pixelzone(self, ctx):
        ts = [x for x in sql.template_get_all_by_guild_id(ctx.guild.id) if x.canvas == 'pixelzone']
        if len(ts) <= 0:
            ctx.command.parent.reset_cooldown(ctx)
            raise NoTemplatesError(True)
        ts = sorted(ts, key=lambda tx: tx.name)
        msg = await _check_canvas(ctx, ts, "pixelzone")
        await msg.delete()
        await _build_template_report(ctx, ts)

    @commands.guild_only()
    @template_check.command(name='pxlsspace', aliases=['ps'])
    async def template_check_pxlsspace(self, ctx):
        ts = [x for x in sql.template_get_all_by_guild_id(ctx.guild.id) if x.canvas == 'pxlsspace']
        if len(ts) <= 0:
            ctx.command.parent.reset_cooldown(ctx)
            raise NoTemplatesError(True)
        ts = sorted(ts, key=lambda tx: tx.name)
        msg = await _check_canvas(ctx, ts, "pxlsspace")
        await msg.delete()
        await _build_template_report(ctx, ts)

    @commands.guild_only()
    @commands.cooldown(1, 5, BucketType.guild)
    @template.command(name='info', aliases=['i'])
    async def template_info(self, ctx, *args):
        gid = ctx.guild.id
        iter_args = iter(args)
        name = next(iter_args, 1)
        image_only = False
        if name == "-r":
            image_only = True
            name = next(iter_args, 1)
        if name == "-f":
            fac = next(iter_args, None)
            if fac is None:
                await ctx.send(ctx.s("error.missing_arg_faction"))
                return
            faction = sql.guild_get_by_faction_name_or_alias(fac)
            if not faction:
                raise FactionNotFoundError
            gid = faction.id
            name = next(iter_args, 1)
        else:
            faction = sql.guild_get_by_id(gid)
        t = sql.template_get_by_name(gid, name)
        if not t:
            raise TemplateNotFoundError

        if image_only:
            zoom = next(iter_args, 1)
            try:
                if type(zoom) is not int:
                    if zoom.startswith("#"):
                        zoom = zoom[1:]
                    zoom = int(zoom)
            except ValueError:
                zoom = 1
            max_zoom = int(math.sqrt(4000000 // (t.width * t.height)))
            zoom = max(1, min(zoom, max_zoom))

            img = render.zoom(await http.get_template(t.url, t.name), zoom)

            with io.BytesIO() as bio:
                img.save(bio, format="PNG")
                bio.seek(0)
                f = discord.File(bio, t.name + ".png")
                await ctx.send(file=f)
            return

        canvas_name = canvases.pretty_print[t.canvas]
        coords = "({}, {})".format(t.x, t.y)
        dimensions = "{} x {}".format(t.width, t.height)
        size = t.size
        visibility = ctx.s("bot.private") if bool(t.private) else ctx.s("bot.public")
        owner = self.bot.get_user(t.owner_id)
        if owner is None:
            added_by = ctx.s("error.account_deleted")
        else:
            added_by = owner.name + "#" + owner.discriminator
        date_added = datetime.date.fromtimestamp(t.date_created).strftime("%d %b, %Y")
        date_modified = datetime.date.fromtimestamp(t.date_updated).strftime("%d %b, %Y")
        color = faction.faction_color
        description = "[__{}__]({})".format(ctx.s("template.link_to_canvas"),
                                            canvases.url_templates[t.canvas].format(*t.center()))

        if size == 0:
            t.size = await render.calculate_size(await http.get_template(t.url, t.name))
            sql.template_update(t)

        e = discord.Embed(title=t.name, color=color, description=description) \
            .set_image(url=t.url) \
            .add_field(name=ctx.s("bot.canvas"), value=canvas_name, inline=True) \
            .add_field(name=ctx.s("bot.coordinates"), value=coords, inline=True) \
            .add_field(name=ctx.s("bot.dimensions"), value=dimensions, inline=True) \
            .add_field(name=ctx.s("bot.size"), value=size, inline=True) \
            .add_field(name=ctx.s("bot.visibility"), value=visibility, inline=True) \
            .add_field(name=ctx.s("bot.added_by"), value=added_by, inline=True) \
            .add_field(name=ctx.s("bot.date_added"), value=date_added, inline=True) \
            .add_field(name=ctx.s("bot.date_modified"), value=date_modified, inline=True)

        if faction.id != ctx.guild.id and faction.faction_name:
            e = e.set_author(name=faction.faction_name, icon_url=faction.faction_emblem or discord.Embed.Empty)

        await ctx.send(embed=e)

    @commands.guild_only()
    @commands.cooldown(1, 5, BucketType.guild)
    @checks.template_adder_only()
    @template.command(name='remove', aliases=['rm'])
    async def template_remove(self, ctx, name):
        t = sql.template_get_by_name(ctx.guild.id, name)
        if not t:
            raise TemplateNotFoundError
        log.info("(T:{})".format(t.name, t.gid))
        if t.owner_id != ctx.author.id and not utils.is_template_admin(ctx) and not utils.is_admin(ctx):
            await ctx.send(ctx.s("template.err.not_owner"))
            return
        sql.template_delete(t.gid, t.name)
        await ctx.send(ctx.s("template.remove").format(name))

    @staticmethod
    async def add_template(ctx, canvas, name, x, y, url):
        if len(name) > config.MAX_TEMPLATE_NAME_LENGTH:
            await ctx.send(ctx.s("template.err.name_too_long").format(config.MAX_TEMPLATE_NAME_LENGTH))
            return
        if sql.template_count_by_guild_id(ctx.guild.id) >= config.MAX_TEMPLATES_PER_GUILD:
            await ctx.send(ctx.s("template.err.max_templates"))
            return
        url = await Template.select_url(ctx, url)
        if url is None:
            return

        t = await Template.build_template(ctx, name, x, y, url, canvas)
        if not t:
            return
        log.info("(T:{} | X:{} | Y:{} | Dim:{})".format(t.name, t.x, t.y, t.size))
        chk = await Template.check_for_duplicate_by_name(ctx, t)
        if chk is not None:
            if not chk or await Template.check_for_duplicates_by_md5(ctx, t) is False:
                return
            sql.template_update(t)
            await ctx.send(ctx.s("template.updated").format(name))
            return
        elif await Template.check_for_duplicates_by_md5(ctx, t) is False:
            return
        sql.template_add(t)
        await ctx.send(ctx.s("template.added").format(name))

    @staticmethod
    async def build_template(ctx, name, x, y, url, canvas):
        try:
            with await http.get_template(url, name) as data:
                size = await render.calculate_size(data)
                md5 = hashlib.md5(data.getvalue()).hexdigest()
                with Image.open(data).convert("RGBA") as tmp:
                    w, h = tmp.size
                    quantized = await Template.check_colors(tmp, colors.by_name[canvas])
                if not quantized:
                    if not await utils.yes_no(ctx, ctx.s("template.not_quantized")):
                        return

                    template, bad_pixels = await render.quantize(data, colors.by_name[canvas])
                    with io.BytesIO() as bio:
                        template.save(bio, format="PNG")
                        bio.seek(0)
                        f = discord.File(bio, "template.png")
                        new_msg = await ctx.send(ctx.s("canvas.quantize").format(bad_pixels), file=f)

                    url = new_msg.attachments[0].url
                    with await http.get_template(url, name) as data2:
                        md5 = hashlib.md5(data2.getvalue()).hexdigest()
                created = int(time.time())
                return DbTemplate(ctx.guild.id, name, url, canvas, x, y, w, h, size, created, created, md5,
                                  ctx.author.id)
        except aiohttp.client_exceptions.InvalidURL:
            raise UrlError
        except IOError:
            raise PilImageError

    @staticmethod
    async def check_colors(img, palette):
        for py in range(img.height):
            await asyncio.sleep(0)
            for px in range(img.width):
                pix = img.getpixel((px, py))
                if pix[3] == 0:
                    continue
                if pix[3] != 255:
                    return False
                if pix[:3] not in palette:
                    return False
        return True

    @staticmethod
    async def check_for_duplicates_by_md5(ctx, template):
        dups = sql.template_get_by_hash(ctx.guild.id, template.md5)
        if len(dups) > 0:
            msg = [ctx.s("template.duplicate_list_open"),
                   "```xl"]
            w = max(map(lambda tx: len(tx.name), dups)) + 2
            for d in dups:
                name = '"{}"'.format(d.name)
                canvas_name = canvases.pretty_print[d.canvas]
                msg.append("{0:<{w}} {1:>15} ({2}, {3})\n".format(name, canvas_name, d.x, d.y, w=w))
            msg.append("```")
            msg.append(ctx.s("template.duplicate_list_close"))
            return await utils.yes_no(ctx, '\n'.join(msg))

    @staticmethod
    async def check_for_duplicate_by_name(ctx, template):
        dup = sql.template_get_by_name(ctx.guild.id, template.name)
        if dup:
            if template.owner_id != ctx.author.id and not utils.is_admin(ctx):
                await ctx.send(ctx.s("template.err.name_exists"))
                return False
            print(dup.x)
            q = ctx.s("template.name_exists_ask_replace") \
                .format(dup.name, canvases.pretty_print[dup.canvas], dup.x, dup.y)
            return await utils.yes_no(ctx, q)

    @staticmethod
    async def select_url(ctx, input_url):
        if input_url:
            if re.search('^(?:https?://)cdn\.discordapp\.com/', input_url):
                return input_url
            raise UrlError
        if len(ctx.message.attachments) > 0:
            return ctx.message.attachments[0].url


async def _build_template_report(ctx, ts: List[DbTemplate]):
    name = ctx.s("bot.name")
    tot = ctx.s("bot.total")
    err = ctx.s("bot.errors")
    perc = ctx.s("bot.percent")

    w1 = max(max(map(lambda tx: len(tx.name), ts)) + 2, len(name))
    w2 = max(max(map(lambda tx: len(str(tx.height * tx.width)), ts)), len(tot))
    w3 = max(max(map(lambda tx: len(str(tx.errors)), ts)), len(err))
    w4 = max(len(perc), 6)

    out = [
        "**{}**".format(ctx.s("template.template_report_header")),
        "```xl",
        "{0:<{w1}}  {1:>{w2}}  {2:>{w3}}  {3:>{w4}}".format(name, tot, err, perc, w1=w1, w2=w2, w3=w3, w4=w4)
    ]
    for t in ts:
        tot = t.size
        if tot == 0:
            t.size = await render.calculate_size(await http.get_template(t.url, t.name))
            sql.template_update(t)
        name = '"{}"'.format(t.name)
        perc = "{:>6.2f}%".format(100 * (tot - t.errors) / tot)
        out.append('{0:<{w1}}  {1:>{w2}}  {2:>{w3}}  {3:>{w4}}'
                   .format(name, tot, t.errors, perc, w1=w1, w2=w2, w3=w3, w4=w4))
    out.append("```")
    await ctx.send(content='\n'.join(out))


async def _check_canvas(ctx, templates, canvas, msg=None):
    chunk_classes = {
        'pixelcanvas': BigChunk,
        'pixelzone': ChunkPz,
        'pxlsspace': PxlsBoard
    }

    chunks = set()
    for t in templates:
        empty_bcs, shape = chunk_classes[canvas].get_intersecting(t.x, t.y, t.width, t.height)
        chunks.update(empty_bcs)

    if msg is not None:
        await msg.edit(content=ctx.s("template.fetching_data").format(canvases.pretty_print[canvas]))
    else:
        msg = await ctx.send(ctx.s("template.fetching_data").format(canvases.pretty_print[canvas]))
    await http.fetch_chunks(chunks)

    await msg.edit(content=ctx.s("template.calculating"))
    example_chunk = next(iter(chunks))
    for t in templates:
        empty_bcs, shape = example_chunk.get_intersecting(t.x, t.y, t.width, t.height)
        tmp = Image.new("RGBA", (example_chunk.width * shape[0], example_chunk.height * shape[1]))
        for i, ch in enumerate(empty_bcs):
            ch = next((x for x in chunks if x == ch))
            if ch.is_in_bounds():
                tmp.paste(ch.image, ((i % shape[0]) * ch.width, (i // shape[0]) * ch.height))

        x, y = t.x - empty_bcs[0].p_x, t.y - empty_bcs[0].p_y
        tmp = tmp.crop((x, y, x + t.width, y + t.height))
        template = Image.open(await http.get_template(t.url, t.name)).convert('RGBA')
        alpha = Image.new('RGBA', template.size, (255, 255, 255, 0))
        template = Image.composite(template, alpha, template)
        tmp = Image.composite(tmp, alpha, template)
        tmp = ImageChops.difference(tmp.convert('RGB'), template.convert('RGB'))
        t.errors = np.array(tmp).any(axis=-1).sum()

    return msg
