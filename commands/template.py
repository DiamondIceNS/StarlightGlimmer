import aiohttp
import asyncio
import datetime
import discord
import hashlib
import re
import time
from PIL import Image
from discord.ext import commands
from discord.ext.commands import BucketType

from objects.template import Template as Template_
from utils import canvases, checks, colors, render, sqlite as sql, utils
from objects.logger import Log
from objects.config import Config

log = Log(__name__)
cfg = Config()


class Template:
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.cooldown(1, 5, BucketType.guild)
    @commands.group(name='template', invoke_without_command=True, aliases=['t'])
    async def template(self, ctx, page: int=1):
        ts = sql.template_get_all_by_guild_id(ctx.guild.id)
        if len(ts) > 0:
            pages = 1 + len(ts) // 10
            page = min(max(page, 1), pages)
            w1 = max(max(map(lambda tx: len(tx.name), ts)) + 2, len(ctx.get_str("template.info_name")))
            msg = [
                ctx.get_str("template.list_open").format(page, pages),
                "{0:<{w1}}  {1:<14}  {2}\n".format(ctx.get_str("template.info_name"),
                                                   ctx.get_str("template.info_canvas"),
                                                   ctx.get_str("template.info_coords"), w1=w1)
            ]
            for t in ts[(page-1)*10:page*10]:
                coords = "({}, {})".format(t.x, t.y)
                name = '"{}"'.format(t.name)
                canvas_name = canvases.pretty_print[t.canvas]
                msg.append("{0:<{w1}}  {1:<14}  {2}\n".format(name, canvas_name, coords, w1=w1))
            msg.append(ctx.get_str("template.list_close").format(ctx.prefix))
            await ctx.send(''.join(msg))
        else:
            await ctx.send(ctx.get_str("template.list_no_templates"))

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
    @commands.cooldown(1, 5, BucketType.guild)
    @template.command(name='info')
    async def template_info(self, ctx, name):
        t = sql.template_get_by_name(ctx.guild.id, name)
        if not t:
            await ctx.send(ctx.get_str("template.name_not_found").format(name))
            return

        canvas_url = canvases.url_templates[t.canvas].format(*t.center())
        canvas_name = canvases.pretty_print[t.canvas]
        coords = "({}, {})".format(t.x, t.y)
        size = "{} x {}".format(t.width, t.height)
        owner = self.bot.get_user(t.owner_id)
        added_by = owner.name + "#" + owner.discriminator
        date_added = datetime.date.fromtimestamp(t.date_created).strftime("%d %b, %Y")
        date_modified = datetime.date.fromtimestamp(t.date_updated).strftime("%d %b, %Y")

        e = discord.Embed(title=t.name, url=canvas_url, color=13594340) \
            .set_image(url=t.url) \
            .add_field(name=ctx.get_str("template.info_canvas"), value=canvas_name, inline=True) \
            .add_field(name=ctx.get_str("template.info_coords"), value=coords, inline=True) \
            .add_field(name=ctx.get_str("template.info_size"), value=size, inline=True) \
            .add_field(name=ctx.get_str("template.info_added_by"), value=added_by, inline=True) \
            .add_field(name=ctx.get_str("template.info_date_added"), value=date_added, inline=True) \
            .add_field(name=ctx.get_str("template.info_date_modified"), value=date_modified, inline=True)
        await ctx.send(embed=e)

    @commands.guild_only()
    @commands.cooldown(1, 5, BucketType.guild)
    @checks.template_adder_only()
    @template.command(name='remove', aliases=['rm'])
    async def template_remove(self, ctx, name):
        t = sql.template_get_by_name(ctx.guild.id, name)
        if not t:
            await ctx.send(ctx.get_str("template.no_template_named").format(name))
            return
        if t.owner_id != ctx.author.id and not utils.is_template_admin(ctx) and not utils.is_admin(ctx):
            await ctx.send(ctx.get_str("template.not_owner"))
            return
        sql.template_delete(t.gid, t.name)
        await ctx.send(ctx.get_str("template.remove").format(name))

    @staticmethod
    async def add_template(ctx, canvas, name, x, y, url):
        if len(name) > cfg.max_template_name_length:
            await ctx.send(ctx.get_str("template.name_too_long").format(cfg.max_template_name_length))
            return
        if sql.template_count_by_guild_id(ctx.guild.id) >= cfg.max_templates_per_guild:
            await ctx.send(ctx.get_str("template.max_templates"))
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
            await ctx.send(ctx.get_str("template.updated").format(name))
            return
        elif await Template.check_for_duplicates_by_md5(ctx, t) is False:
            return
        sql.template_add(t)
        await ctx.send(ctx.get_str("template.added").format(name))

    @staticmethod
    async def build_template(ctx, name, x, y, url, canvas):
        try:
            with await utils.get_template(url) as data:
                md5 = hashlib.md5(data.getvalue()).hexdigest()
                with Image.open(data).convert("RGBA") as tmp:
                    w, h = tmp.size
                    quantized = await Template.check_colors(tmp, colors.by_name[canvas])
                if not quantized:
                    if not await utils.yes_no(ctx, ctx.get_str("template.not_quantized")):
                        return
                    new_msg = await render.quantize(ctx, data, colors.by_name[canvas])
                    url = new_msg.attachments[0].url
                    with await utils.get_template(url) as data2:
                        md5 = hashlib.md5(data2.getvalue()).hexdigest()
                created = int(time.time())
                return Template_(ctx.guild.id, name, url, canvas, x, y, w, h, created, created, md5, ctx.author.id)
        except aiohttp.client_exceptions.InvalidURL:
            raise checks.UrlError
        except IOError:
            raise checks.PilImageError

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
            msg = [ctx.get_str("template.duplicate_list_open")]
            w = max(map(lambda tx: len(tx.name), dups)) + 2
            for d in dups:
                name = '"{}"'.format(d.name)
                canvas_name = canvases.pretty_print[d.canvas]
                msg.append("{0:<{w}} {1:>15} ({2}, {3})\n".format(name, canvas_name, d.x, d.y, w=w))
            msg.append(ctx.get_str("template.duplicate_list_close"))
            return await utils.yes_no(ctx, ''.join(msg))

    @staticmethod
    async def check_for_duplicate_by_name(ctx, template):
        dup = sql.template_get_by_name(ctx.guild.id, template.name)
        if dup:
            if template.owner_id != ctx.author.id and not utils.is_admin(ctx):
                await ctx.send(ctx.get_str("template.name_exists_no_permission"))
                return False
            print(dup.x)
            q = ctx.get_str("template.name_exists_ask_replace")\
                .format(dup.name, canvases.pretty_print[dup.canvas], dup.x, dup.y)
            return await utils.yes_no(ctx, q)

    @staticmethod
    async def select_url(ctx, input_url):
        if input_url:
            if re.search('^(?:https?://)cdn\.discordapp\.com/', input_url):
                return input_url
            raise checks.UrlError
        if len(ctx.message.attachments) > 0:
            return ctx.message.attachments[0].url


def setup(bot):
    bot.add_cog(Template(bot))
