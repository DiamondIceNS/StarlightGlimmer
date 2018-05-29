import re
import io
import hashlib
import discord
import aiohttp
import asyncio
import time
import datetime
from PIL import Image
from discord.ext import commands
from discord.ext.commands import BucketType
from utils.language import getlang

import utils.sqlite as sql
import utils.canvases as canvases
from utils.logger import Log
from utils.config import Config
from objects.template import Template as T2

log = Log(__name__)
cfg = Config()

# TODO:
# - enforce per-guild template limit
# - allow Admin to bypass owner check
# - add ability to give bot permissions to arbitrary roles
# - link templates to canvas commands
# - add "check all" feature
# - cap template name length
# - paginate template list
# - add faction support
# - add cross-guild template sharing


class Template:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='templates', invoke_without_command=True, aliases=['t'])
    @commands.cooldown(1, 5, BucketType.guild)
    async def templates(self, ctx):
        ts = sql.get_templates_by_guild(ctx.guild.id)
        if len(ts) > 0:
            w1 = max(max(map(lambda tx: len(tx.name), ts)) + 2, len("Name"))
            w2 = max(max(map(lambda tx: len(str(tx.x)) + len(str(tx.y)), ts)) + 4, len("Coords"))
            out = "**Template list:**\n```xl\n"
            out = out + "{0:<{w1}}  {1:<14}  {2:<{w2}}  {3}\n".format("Name", "Canvas", "Coords", "Owner", w1=w1, w2=w2)
            for t in ts:
                owner = self.bot.get_user(t.owner_id)
                owner_name = owner.name + "#" + owner.discriminator
                coords = "({}, {})".format(t.x, t.y)
                out = out + "{0:<{w1}}  {1:<14}  {2:<{w2}}  {3}\n".format("'" + t.name + "'", canvases.canvas_list[t.canvas], coords, owner_name, w1=w1, w2=w2)
            out = out + "```"
            await ctx.send(out)

    @templates.group(name='add', invoke_without_command=True)
    @commands.cooldown(1, 5, BucketType.guild)
    async def templates_add(self, ctx):
        await canvases.use_default_canvas(ctx, self.bot, "templates.add")

    @templates_add.command(name="pixelcanvas", aliases=['pc'])
    @commands.cooldown(1, 5, BucketType.guild)
    async def templates_add_pixelcanvas(self, ctx, name, x, y, url=None):
        await self.add_template(ctx, "pixelcanvas", name, x, y, url)

    @templates_add.command(name="pixelzio", aliases=['pzi'])
    @commands.cooldown(1, 5, BucketType.guild)
    async def templates_add_pixelzio(self, ctx, name, x, y, url=None):
        await self.add_template(ctx, "pixelzio", name, x, y, url)

    @templates_add.command(name="pixelzone", aliases=['pz'])
    @commands.cooldown(1, 5, BucketType.guild)
    async def templates_add_pixelzone(self, ctx, name, x, y, url=None):
        await self.add_template(ctx, "pixelzone", name, x, y, url)

    @templates_add.command(name="pxlsspace", aliases=['ps'])
    @commands.cooldown(1, 5, BucketType.guild)
    async def templates_add_pxlsspace(self, ctx, name, x, y, url=None):
        await self.add_template(ctx, "pxlsspace", name, x, y, url)

    @templates.command(name='remove', aliases=['rm'])
    @commands.cooldown(1, 5, BucketType.guild)
    async def templates_remove(self, ctx, name):
        t = sql.get_template_by_name(ctx.guild.id, name)
        if not t:
            await ctx.send("There is no template named '{0}'.".format(name))  # TODO: Localize string
            return
        if t.owner_id != ctx.author.id:
            await ctx.send("You don't have permission to do that.")  # TODO: Localize string
            return
        sql.drop_template(t.gid, t.name)
        await ctx.send("Successfully removed '{0}'.".format(name))  # TODO: Localize string

    @templates.command(name='info')
    @commands.cooldown(1, 5, BucketType.guild)
    async def templates_info(self, ctx, name):
        t = sql.get_template_by_name(ctx.guild.id, name)
        if not t:
            await ctx.send("Could not find template with name '{0}`.".format(t.name))  # TODO: Localize string

        canvas_url = canvases.canvas_url_templates[t.canvas].format(*t.center())
        owner = self.bot.get_user(t.owner_id)
        time_added = datetime.date.fromtimestamp(t.date_created)
        time_modified = datetime.date.fromtimestamp(t.date_updated)
        e = discord.Embed(title=t.name, url=canvas_url, color=13594340)\
            .set_image(url=t.url)\
            .add_field(name="Canvas", value=canvases.canvas_list[t.canvas], inline=True)\
            .add_field(name="Location", value="({0}, {1})".format(t.x, t.y), inline=True)\
            .add_field(name="Size", value="{0}x{1}px".format(t.width, t.height), inline=True)\
            .add_field(name="Completion", value="TODO", inline=True)\
            .add_field(name="Added By", value=owner.name + "#" + owner.discriminator, inline=True)\
            .add_field(name="Date Added", value=time_added.strftime("%d %b, %Y"), inline=True)\
            .add_field(name="Date Modified", value=time_modified.strftime("%d %b, %Y"), inline=True)
        await ctx.send(embed=e)

    @staticmethod
    async def select_url(ctx, input_url=None):
        if len(ctx.message.attachments) > 0:
            return ctx.message.attachments[0].url
        if input_url is not None:
            if re.search('^(?:https?://)cdn\.discordapp\.com/', input_url) is not None:
                return input_url
            await ctx.send("I can only accept Discord attachment URLs.")  # TODO: localize string

    @staticmethod
    async def build_template(ctx, name, x, y, input_url, canvas):
        try:
            async with aiohttp.ClientSession() as sess:
                async with sess.get(input_url) as resp:
                    if resp.status != 200:
                        print("Response not OK")  # TODO: Add output and localize string
                        return
                    if resp.content_type == "image/jpg" or resp.content_type == "image/jpeg":
                        try:
                            f = discord.File("assets/disdain_for_jpegs.gif", "disdain_for_jpegs.gif")
                            await ctx.send(getlang(ctx.guild.id, "bot.error.jpeg"), file=f)
                        except IOError:
                            await ctx.send(getlang(ctx.guild.id, "bot.error.jpeg"))
                        return
                    if resp.content_type != "image/png":
                        await ctx.send(getlang(ctx.guild.id, "bot.error.no_png"))
                        return
                    data = await resp.read()
                    with io.BytesIO(data) as bio:
                        with Image.open(bio) as tmp:
                            md5 = hashlib.md5(bio.getvalue()).hexdigest()
                            w, h = tmp.size
                            created = int(time.time())
                            return T2(ctx.guild.id, name, input_url, canvas, x, y, w, h, created, created, md5, ctx.author.id)
        except aiohttp.client_exceptions.InvalidURL:
            print("Not a URL.")  # TODO: Add output and localize string
        except IOError:
            await ctx.send(getlang(ctx.guild.id, "bot.error.bad_png")
                           .format(sql.get_guild_prefix(ctx.guild.id), getlang(ctx.guild.id, "command.quantize")))

    async def wait_for_confirm(self, ctx, query_msg):
        sql.add_menu_lock(ctx.channel.id, ctx.author.id)

        def check(m):
            return ctx.channel.id == m.channel.id and ctx.author.id == m.author.id

        try:
            resp_msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            while not (resp_msg.content == "0" or resp_msg.content == "1"):
                await ctx.send("That is not a valid option. Please try again.")  # TODO: localize string
                resp_msg = await self.bot.wait_for('message', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await query_msg.edit(content="Command timed out.")  # TODO: localize string
            return False
        finally:
            sql.remove_menu_lock(ctx.channel.id, ctx.author.id)
        return resp_msg.content == "1"

    async def add_template(self, ctx, canvas, name, x, y, url):
        ct = sql.count_templates(ctx.guild.id)
        if ct >= cfg.max_templats_per_guild:
            await ctx.send("This guild already has the maximum number of templates. Please remove a template before adding another.")  # TODO: Localize string
            return
        url = await self.select_url(ctx, url)
        if url is None:
            return
        t = await self.build_template(ctx, name, x, y, url, canvas)
        if not t:
            return

        t_by_name = sql.get_template_by_name(ctx.guild.id, t.name)
        ts_by_mdd5 = sql.get_templates_by_hash(ctx.guild.id, t.md5)
        if t_by_name:
            query_msg = await ctx.send(
                "A template with the name '{0}' already exists for {1} at ({2}, {3}). Replace it?\n  `0` - No\n  `1` - Yes".format(
                    t_by_name.name, canvases.canvas_list[t_by_name.canvas], t_by_name.x, t_by_name.y))  # TODO: localize string
            if not await self.wait_for_confirm(ctx, query_msg):
                return
            if ts_by_mdd5:
                ts_by_mdd5 = [z for z in ts_by_mdd5 if z.name != t.name]
                if len(ts_by_mdd5) > 0:
                    m = "The following templates already match this image:\n```xl\n"
                    maxlength = max(map(lambda c: len(t_by_name.name), ts_by_mdd5))
                    for t_by_name in ts_by_mdd5:
                        m = m + "'{0:<{width}}' {1:>15} ({2}, {3})\n".format(t_by_name.name, canvases.canvas_list[t_by_name.canvas], t_by_name.x, t_by_name.y,
                                                                             width=maxlength)
                    m = m + "```\nCreate a new template anyway?\n  `0` - No\n  `1` - Yes"  # TODO: localize string
                    query_msg = await ctx.send(m)
                    if not await self.wait_for_confirm(ctx, query_msg):
                        return
            # TODO: If mod, update owner
            sql.update_template(t)
            await ctx.send("Template '{0}' updated!".format(name))  # TODO: localize string
            return
        elif len(ts_by_mdd5) > 0:
            m = "The following templates already match this image:\n```xl\n"
            maxlength = max(map(lambda tx: len(tx.name), ts_by_mdd5)) + 2
            for t_by_name in ts_by_mdd5:
                m = m + "{0:<{width}} {1:>15} ({2}, {3})\n".format("'" + t_by_name.name + "'", canvases.canvas_list[t_by_name.canvas], t_by_name.x, t_by_name.y,
                                                                   width=maxlength)
            m = m + "```\nCreate a new template anyway?\n  `0` - No\n  `1` - Yes"  # TODO: localize string
            query_msg = await ctx.send(m)
            if not await self.wait_for_confirm(ctx, query_msg):
                return
        sql.add_template(t)
        await ctx.send("Template '{0}' added!".format(name))  # TODO: localize string


def setup(bot):
    bot.add_cog(Template(bot))
