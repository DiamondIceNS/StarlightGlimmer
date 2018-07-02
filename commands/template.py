import asyncio
import datetime
import hashlib
import io
import itertools
import re
import time
from typing import List, Set

import aiohttp
import discord
import numpy as np
from discord.ext import commands
from discord.ext.commands import BucketType
from PIL import Image, ImageChops

from objects import errors
from objects.chunks import Chunky, BigChunk, ChunkPzi, ChunkPz, PxlsBoard
from objects.config import Config
from objects.logger import Log
from objects.template import Template as Template_
from utils import canvases, checks, colors, http, render, sqlite as sql, utils

log = Log(__name__)
cfg = Config()


class Template:
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.cooldown(1, 5, BucketType.guild)
    @commands.group(name='template', invoke_without_command=True, aliases=['t'])
    async def template(self, ctx, *args):
        gid = ctx.guild.id
        guild = sql.guild_get_prefix_by_id(gid)
        iter_args = iter(args)
        page = next(iter_args, 1)
        if page == "-f":
            faction = sql.guild_get_by_faction_name_or_alias(next(iter_args, None))
            if not faction:
                await ctx.send(ctx.s("faction.not_found"))
                return
            gid = faction.id
            page = next(iter_args, 1)
        try:
            page = int(page)
        except ValueError:
            page = 1
        ts = sql.template_get_all_by_guild_id(gid)
        if len(ts) > 0:
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
            for t in ts[(page-1)*10:page*10]:
                coords = "({}, {})".format(t.x, t.y)
                name = '"{}"'.format(t.name)
                canvas_name = canvases.pretty_print[t.canvas]
                msg.append("{0:<{w1}}  {1:<14}  {2}".format(name, canvas_name, coords, w1=w1))
            msg.append("")
            msg.append(ctx.s("template.list_footer_1").format(guild))
            msg.append(ctx.s("template.list_footer_2").format(guild))
            msg.append("```")
            await ctx.send('\n'.join(msg))
        else:
            await ctx.send(ctx.s("template.list_no_templates"))

    @commands.guild_only()
    @commands.cooldown(1, 5, BucketType.guild)
    @template.command(name='all')
    async def template_all(self, ctx, page: int = 1):  # TODO: Add brief, help, and signature strings to lang files
        gs = [x for x in sql.guild_get_all_factions() if x.id not in sql.faction_hides_get_all(ctx.guild.id)]
        ts = [x for x in sql.template_get_all() if x.gid in [y.id for y in gs]]
        guild = sql.guild_get_prefix_by_id(ctx.guild.id)

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
            msg.append(ctx.s("template.list_all_footer_1").format(guild))
            msg.append(ctx.s("template.list_all_footer_2").format(guild))
            msg.append("```")
            await ctx.send('\n'.join(msg))
        else:
            await ctx.send(ctx.s("template.list_all_no_templates"))

    @commands.guild_only()
    @commands.cooldown(1, 5, BucketType.guild)
    @checks.template_adder_only()
    @template.group(name='add', invoke_without_command=True)
    async def template_add(self, ctx):
        await ctx.invoke_default("templates.add")

    @commands.guild_only()
    @commands.cooldown(1, 5, BucketType.guild)
    @checks.template_adder_only()
    @template_add.command(name="pixelcanvas", aliases=['pc'])
    async def template_add_pixelcanvas(self, ctx, name: str, x: int, y: int, url=None):
        await self.add_template(ctx, "pixelcanvas", name, x, y, url)

    @commands.guild_only()
    @commands.cooldown(1, 5, BucketType.guild)
    @checks.template_adder_only()
    @template_add.command(name="pixelzio", aliases=['pzi'])
    async def template_add_pixelzio(self, ctx, name: str, x: int, y: int, url=None):
        await self.add_template(ctx, "pixelzio", name, x, y, url)

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
    #@commands.cooldown(1, 300, BucketType.guild)  # TODO: Cooldown
    @template.group(name='check')
    async def template_check(self, ctx):
        pass  # TODO: Check all logic + custom cooldown

    @commands.guild_only()
    # @commands.cooldown(1, 300, BucketType.guild)  # TODO: Cooldown
    @template_check.command(name='pixelcanvas', aliases=['pc'])
    async def template_check_pixelcanvas(self, ctx):
        await self.check_canvas(ctx, "pixelcanvas", BigChunk, http.fetch_chunks_pixelcanvas)

    @commands.guild_only()
    # @commands.cooldown(1, 300, BucketType.guild)  # TODO: Cooldown
    @template_check.command(name='pixelzio', aliases=['pzi'])
    async def template_check_pixelzio(self, ctx):
        await self.check_canvas(ctx, "pixelzio", ChunkPzi, http.fetch_chunks_pixelzio)

    @commands.guild_only()
    # @commands.cooldown(1, 300, BucketType.guild)  # TODO: Cooldown
    @template_check.command(name='pixelzone', aliases=['pz'])
    async def template_check_pixelzone(self, ctx):
        await self.check_canvas(ctx, "pixelzone", ChunkPz, http.fetch_chunks_pixelzone)

    @commands.guild_only()
    # @commands.cooldown(1, 300, BucketType.guild)  # TODO: Cooldown
    @template_check.command(name='pxlsspace', aliases=['ps'])
    async def template_check_pxlsspace(self, ctx):
        await self.check_canvas(ctx, "pxlsspace", PxlsBoard, http.fetch_pxlsspace)

    @commands.guild_only()
    @commands.cooldown(1, 5, BucketType.guild)
    @template.command(name='info')
    async def template_info(self, ctx, *args):
        if len(args) < 1:
            return
        if args[0] == "-f":
            if len(args) < 3:
                return
            g = sql.guild_get_by_faction_name_or_alias(args[1])
            if not g:
                await ctx.send(ctx.s("faction.not_found"))
                return
            name = args[2]
            t = sql.template_get_by_name(g.id, name)
        else:
            name = args[0]
            t = sql.template_get_by_name(ctx.guild.id, name)
        if not t:
            await ctx.send(ctx.s("template.name_not_found").format(name))
            return

        canvas_url = canvases.url_templates[t.canvas].format(*t.center())
        canvas_name = canvases.pretty_print[t.canvas]
        coords = "({}, {})".format(t.x, t.y)
        dimensions = "{} x {}".format(t.width, t.height)
        size = t.size
        visibility = "Private" if bool(t.private) else "Public"
        owner = self.bot.get_user(t.owner_id)
        added_by = owner.name + "#" + owner.discriminator
        date_added = datetime.date.fromtimestamp(t.date_created).strftime("%d %b, %Y")
        date_modified = datetime.date.fromtimestamp(t.date_updated).strftime("%d %b, %Y")

        e = discord.Embed(title=t.name, url=canvas_url, color=13594340) \
            .set_image(url=t.url) \
            .add_field(name=ctx.s("bot.canvas"), value=canvas_name, inline=True) \
            .add_field(name=ctx.s("bot.coordinates"), value=coords, inline=True) \
            .add_field(name=ctx.s("bot.dimensions"), value=dimensions, inline=True) \
            .add_field(name=ctx.s("bot.size"), value=size, inline=True) \
            .add_field(name=ctx.s("bot.visibility"), value=visibility, inline=True) \
            .add_field(name=ctx.s("bot.added_by"), value=added_by, inline=True) \
            .add_field(name=ctx.s("bot.date_added"), value=date_added, inline=True) \
            .add_field(name=ctx.s("bot.date_modified"), value=date_modified, inline=True)
        await ctx.send(embed=e)

    @commands.guild_only()
    @commands.cooldown(1, 5, BucketType.guild)
    @checks.template_adder_only()
    @template.command(name='remove', aliases=['rm'])
    async def template_remove(self, ctx, name):
        t = sql.template_get_by_name(ctx.guild.id, name)
        if not t:
            await ctx.send(ctx.s("template.no_template_named").format(name))
            return
        if t.owner_id != ctx.author.id and not utils.is_template_admin(ctx) and not utils.is_admin(ctx):
            await ctx.send(ctx.s("template.not_owner"))
            return
        sql.template_delete(t.gid, t.name)
        await ctx.send(ctx.s("template.remove").format(name))

    @staticmethod
    async def add_template(ctx, canvas, name, x, y, url):
        if len(name) > cfg.max_template_name_length:
            await ctx.send(ctx.s("template.name_too_long").format(cfg.max_template_name_length))
            return
        if sql.template_count_by_guild_id(ctx.guild.id) >= cfg.max_templates_per_guild:
            await ctx.send(ctx.s("template.max_templates"))
            return
        url = await Template.select_url(ctx, url)
        if url is None:
            return

        t = await Template.build_template(ctx, name, x, y, url, canvas)
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
            with await http.get_template(url) as data:
                md5 = hashlib.md5(data.getvalue()).hexdigest()
                with Image.open(data).convert("RGBA") as tmp:
                    w, h = tmp.size
                    quantized = await Template.check_colors(tmp, colors.by_name[canvas])
                    size = await render.calculate_size(tmp)
                if not quantized:
                    if not await utils.yes_no(ctx, ctx.s("template.not_quantized")):
                        return

                    template, bad_pixels = await canvas.quantize(data, colors.by_name[canvas])
                    with io.BytesIO() as bio:
                        template.save(bio, format="PNG")
                        bio.seek(0)
                        f = discord.File(bio, "template.png")
                        new_msg = await ctx.send(ctx.s("canvas.quantize").format(bad_pixels), file=f)

                    url = new_msg.attachments[0].url
                    with await http.get_template(url) as data2:
                        md5 = hashlib.md5(data2.getvalue()).hexdigest()
                        size = await render.calculate_size(Image.open(data2))
                created = int(time.time())
                return Template_(ctx.guild.id, name, url, canvas, x, y, w, h, size, created, created, md5, ctx.author.id)
        except aiohttp.client_exceptions.InvalidURL:
            raise errors.UrlError
        except IOError:
            raise errors.PilImageError

    @staticmethod
    def build_template_report(ctx, ts: List[Template_]):
        name = ctx.s("bot.name")
        tot = ctx.s("bot.total")
        err = ctx.s("bot.errors")
        perc = ctx.s("bot.percent")

        ts = sorted(ts, key=lambda tx: tx.name)
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
            name = '"{}"'.format(t.name)
            perc = "{:>6.2f}%".format(100 * (tot - t.errors) / tot)
            out.append('{0:<{w1}}  {1:>{w2}}  {2:>{w3}}  {3:>{w4}}'
                       .format(name, tot, t.errors, perc, w1=w1, w2=w2, w3=w3, w4=w4))
        out.append("```")
        return '\n'.join(out)

    @staticmethod
    async def calculate_errors(ts: List[Template_], chunks: Set[Chunky]):
        cls = type(next(iter(chunks)))
        for t in ts:
            empty_bcs, shape = cls.get_intersecting(t.x, t.y, t.width, t.height)
            tmp = Image.new("RGBA", tuple([cls.size * x for x in shape]))
            for i, ch in enumerate(empty_bcs):
                ch = next((x for x in chunks if x == ch))
                tmp.paste(ch.image, ((i % shape[0]) * cls.size, (i // shape[0]) * cls.size))

            x, y = t.x - empty_bcs[0].p_x, t.y - empty_bcs[0].p_y
            tmp = tmp.crop((x, y, x + t.width, y + t.height))
            template = Image.open(await http.get_template(t.url)).convert('RGBA')
            alpha = Image.new('RGBA', template.size, (255, 255, 255, 0))
            template = Image.composite(template, alpha, template)
            tmp = Image.composite(tmp, alpha, template)
            tmp = ImageChops.difference(tmp.convert('RGB'), template.convert('RGB'))
            t.errors = np.array(tmp).any(axis=-1).sum()

    @staticmethod
    async def check_canvas(ctx, canvas, chunk_type, fetch):
        ts = [x for x in sql.template_get_all_by_guild_id(ctx.guild.id) if x.canvas == canvas]
        if len(ts) > 0:
            chunks = set()
            for t in ts:
                empty_bcs, shape = chunk_type.get_intersecting(t.x, t.y, t.width, t.height)
                chunks.update(empty_bcs)

            msg = await ctx.send(ctx.s("template.fetching_data").format(canvases.pretty_print[canvas]))
            await fetch(chunks)

            await msg.edit(content=ctx.s("template.calculating"))
            await Template.calculate_errors(ts, chunks)

            await msg.edit(content=Template.build_template_report(ctx, ts))
        # TODO: No templates

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
            msg = [ctx.s("template.duplicate_list_open")]
            w = max(map(lambda tx: len(tx.name), dups)) + 2
            for d in dups:
                name = '"{}"'.format(d.name)
                canvas_name = canvases.pretty_print[d.canvas]
                msg.append("{0:<{w}} {1:>15} ({2}, {3})\n".format(name, canvas_name, d.x, d.y, w=w))
            msg.append(ctx.s("template.duplicate_list_close"))
            return await utils.yes_no(ctx, ''.join(msg))

    @staticmethod
    async def check_for_duplicate_by_name(ctx, template):
        dup = sql.template_get_by_name(ctx.guild.id, template.name)
        if dup:
            if template.owner_id != ctx.author.id and not utils.is_admin(ctx):
                await ctx.send(ctx.s("template.name_exists_no_permission"))
                return False
            print(dup.x)
            q = ctx.s("template.name_exists_ask_replace")\
                .format(dup.name, canvases.pretty_print[dup.canvas], dup.x, dup.y)
            return await utils.yes_no(ctx, q)

    @staticmethod
    async def select_url(ctx, input_url):
        if input_url:
            if re.search('^(?:https?://)cdn\.discordapp\.com/', input_url):
                return input_url
            raise errors.UrlError
        if len(ctx.message.attachments) > 0:
            return ctx.message.attachments[0].url


def setup(bot):
    bot.add_cog(Template(bot))
